import csv
from pathlib import Path


# Return the nearest measured ID/W in µA/µm (numerically equal to A/m).
def retrieve_current_per_width(device_type, gm_over_id, length_um):
    filename = {"nmos": "nmos.csv", "pmos": "pmos.csv"}[device_type.lower()]
    density_by_ratio = {}
    with (Path(__file__).parent / "data" / filename).open(newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            if float(row["length_m"]) * 1e6 == length_um:
                current_a = float(row["id_a"])
                measured_ratio = float(row["gm_s"]) / current_a
                density_by_ratio[measured_ratio] = current_a / float(row["width_m"])

    low = max(ratio for ratio in density_by_ratio if ratio <= gm_over_id)
    high = min(ratio for ratio in density_by_ratio if ratio >= gm_over_id)
    if gm_over_id - low <= high - gm_over_id:
        return density_by_ratio[low]
    return density_by_ratio[high]
