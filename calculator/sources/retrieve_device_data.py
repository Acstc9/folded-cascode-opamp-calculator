import csv
from pathlib import Path


SATURATION_REGION = "2"


def _read_device_sweep(device_type, length_um=None, mirror_reference=None):
    filename = {"nmos": "nmos.csv", "pmos": "pmos.csv"}[device_type.lower()]
    with (Path(__file__).parent / "data" / filename).open(newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            reference = None
            if row.get("ref_current_ua"):
                reference = (
                    float(row["ref_width_um"]), float(row["ref_length_um"]), float(row["ref_current_ua"])
                )
            if reference != mirror_reference:
                continue
            if length_um is None or float(row["length_m"]) * 1e6 == length_um:
                yield row


def _bracketing_measurements(samples, target):
    low = max(key for key in samples if key <= target)
    high = min(key for key in samples if key >= target)
    if target - low <= high - target:
        return samples[low], samples[high]
    return samples[high], samples[low]


def _gate_sweeps(device_type, length_um=None):
    sweeps = {}
    for row in _read_device_sweep(device_type, length_um):
        size = (float(row["length_m"]) * 1e6, float(row["width_m"]) * 1e6)
        sweeps.setdefault(size, {})[float(row["id_a"]) * 1e6] = row

    for (length_um, width_um), samples in sorted(sweeps.items()):
        yield width_um, length_um, samples


def _saturated_neighbors(samples, target_ua):
    saturated = [current for current, row in samples.items() if row["region"] == SATURATION_REGION]
    if not saturated or not min(saturated) <= target_ua <= max(saturated):
        return ()
    nearest, other = _bracketing_measurements(samples, target_ua)
    if nearest["region"] != SATURATION_REGION:
        return ()
    return (nearest, other) if other["region"] == SATURATION_REGION else (nearest,)


def _saturated_at_or_above(samples, floor_ua):
    for current in sorted(samples):
        if current >= floor_ua and samples[current]["region"] == SATURATION_REGION:
            yield samples[current]


def select_fold_branch_point(device_type, length_um, current_ua):
    for width_um, _, samples in _gate_sweeps(device_type, length_um):
        if length_um == 1 and width_um != 2:
            continue
        if min(samples) <= current_ua <= max(samples):
            point = next(_saturated_at_or_above(samples, current_ua), None)
            if point is not None:
                return point
    return None


def select_nmos_by_gm(drain_current_ua, target_gm_us, length_um=None, starting_width_um=0, *, current_floor=False):
    for width_um, measured_length_um, samples in _gate_sweeps("nmos", length_um):
        if width_um < starting_width_um:
            continue
        if current_floor:
            row = next(_saturated_at_or_above(samples, drain_current_ua), None)
        else:
            points = _saturated_neighbors(samples, drain_current_ua)
            row = points[0] if points else None
        if row is not None and float(row["gm_s"]) * 1e6 >= target_gm_us:
            return width_um, measured_length_um, row
    raise ValueError("No measured NMOS size meets the requested current and gm in saturation.")


def select_m11_size(config, target_current_ua, available_vds_v):
    reference = (config.mb12_width_um, config.reference_mirror_length_um, config.reference_current_ua)
    tail_sweeps = {}
    for row in _read_device_sweep("nmos", mirror_reference=reference):
        size = (float(row["length_m"]) * 1e6, float(row["width_m"]) * 1e6)
        tail_sweeps.setdefault(size, {})[round(float(row["vds_v"]), 12)] = row

    for (length_um, width_um), sweep in sorted(tail_sweeps.items()):
        if not min(sweep) <= available_vds_v <= max(sweep):
            continue
        row, _ = _bracketing_measurements(sweep, available_vds_v)
        if row["region"] == SATURATION_REGION and float(row["id_a"]) * 1e6 >= target_current_ua:
            return width_um, length_um, row
    raise ValueError("No measured M11 meets the tail-current floor in saturation at this drain voltage and reference.")


# Match the two target currents, then read both devices at the bias that meets the M3/M4 floor.
def select_pmos_mirror(branch_current_ua, load_current_ua, length_um, required_ro_kohm):
    sweeps = list(_gate_sweeps("pmos", length_um))
    load_widths_by_vgs = {}
    loads = {}
    for width_um, _, samples in sweeps:
        for point in _saturated_neighbors(samples, load_current_ua):
            load_widths_by_vgs.setdefault(float(point["vgs_v"]), set()).add(width_um)
        for point in samples.values():
            if point["region"] == SATURATION_REGION and float(point["ro_ohm"]) / 1000 >= required_ro_kohm:
                loads[width_um, float(point["vgs_v"])] = point

    for width_um, _, samples in sweeps:
        target_width_um = width_um * load_current_ua / branch_current_ua
        for index, branch in enumerate(_saturated_at_or_above(samples, branch_current_ua)):
            vgs = float(branch["vgs_v"])
            widths = set(load_widths_by_vgs.get(vgs, ()))
            if index == 0:
                for point in _saturated_neighbors(samples, branch_current_ua):
                    widths.update(load_widths_by_vgs.get(float(point["vgs_v"]), ()))
            eligible = [width for width in widths if (width, vgs) in loads]
            if eligible:
                load_width = min(eligible, key=lambda width: (abs(width - target_width_um), width))
                return width_um, load_width, branch, loads[load_width, vgs]
    raise ValueError("No measured PMOS pair meets both current targets and M13 output resistance at a shared gate bias.")


# A/m and µA/µm have the same numerical value.
def retrieve_current_per_width(device_type, gm_over_id, length_um):
    density_by_ratio = {}
    for row in _read_device_sweep(device_type, length_um):
        if row["region"] != SATURATION_REGION:
            continue
        current_a = float(row["id_a"])
        measured_ratio = float(row["gm_s"]) / current_a
        density_by_ratio[measured_ratio] = current_a / float(row["width_m"])
    density, _ = _bracketing_measurements(density_by_ratio, gm_over_id)
    return density
