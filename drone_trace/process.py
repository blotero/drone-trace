import os
import re
import pandas as pd


def parse_raw_metadata(input_str):
    """
    Convert raw metadata string to a dictionary.
    """
    pattern = re.compile(r"\[([^:]+)\s*:\s*([^\]]+)\]")
    matches = pattern.findall(input_str)

    metadata = {}
    for key, value in matches:
        key = key.strip()
        value = value.strip()

        if value.replace(".", "", 1).isdigit():
            value = float(value) if "." in value else int(value)
        elif "/" in value:
            try:
                num, denom = map(float, value.split("/"))
                value = num / denom
            except ValueError:
                pass

        metadata[key] = value

    return metadata


def process_dzoom(meta):
    """
    Process digital zoom metadata.
    """
    zoom_ratio_parts = meta["dzoom_ratio"].split(",")
    meta["dzoom_ratio"] = zoom_ratio_parts[0]
    meta["dzoom_ratio_delta"] = (
        zoom_ratio_parts[1].replace("delta:", "") if len(zoom_ratio_parts) > 1 else None
    )


def process_altitude(meta):
    """
    Process altitude metadata.
    """
    alt_parts = meta["rel_alt"].split(" abs_alt: ")
    meta["rel_alt"] = float(alt_parts[0])
    meta["abs_alt"] = float(alt_parts[1])


def large_dataframe(subsections, file):
    """
    Creates dataframe per log file.
    """
    data = []

    for subsection in subsections:
        if len(subsection) < 3:
            continue
        metadata = parse_raw_metadata(subsection[4])
        process_dzoom(metadata)
        process_altitude(metadata)
        row = {
            "filename": file,
            "frame": int(subsection[0]),
            "time_init": subsection[1].split(" --> ")[0],
            "time_end": subsection[1].split(" --> ")[1],
            "diff_time_ms": int(
                subsection[2].split("DiffTime : ")[1].replace("ms", "")
            ),
            "date": subsection[3].split(" ")[0],
            "time": subsection[3].split(" ")[1],
            **metadata,
        }
        data.append(row)
    as_int_cols = [
        "frame",
        "diff_time_ms",
        "iso",
        "fnum",
        "ct",
        "focal_len",
        "dzoom_ratio",
        "dzoom_ratio_delta",
    ]
    as_float_cols = ["shutter", "ev", "latitude", "longitude", "rel_alt", "abs_alt"]
    df = pd.DataFrame(data)
    df[as_int_cols] = df[as_int_cols].astype(int)
    df[as_float_cols] = df[as_float_cols].astype(float)
    return df


def summarize_data(data: pd.DataFrame):
    summary = data.groupby(["filename", "date"]).agg(
        {
            "diff_time_ms": "sum",
            "rel_alt": ["mean", "min", "max", "first", "last"],
            "abs_alt": ["mean", "min", "max", "first", "last"],
            "time": ["first", "last"],
        }
    )

    summary.columns = ["_".join(map(str, col)) for col in summary.columns]

    summary["diff_time_ms_sum"] /= 1000

    summary.reset_index(inplace=True)

    summary.rename(
        columns={
            "diff_time_ms_sum": "duration_seconds",
            "rel_alt_mean": "mean_rel_altitude",
            "rel_alt_min": "min_rel_altitude",
            "rel_alt_max": "max_rel_altitude",
            "abs_alt_mean": "mean_abs_altitude",
            "abs_alt_min": "min_abs_altitude",
            "abs_alt_max": "max_abs_altitude",
            "rel_alt_first": "first_rel_altitude",
            "rel_alt_last": "last_rel_altitude",
            "abs_alt_first": "first_abs_altitude",
            "abs_alt_last": "last_abs_altitude",
            "time_first": "time_init",
            "time_last": "time_end",
        },
        inplace=True,
    )

    return summary[
        [
            "filename",
            "date",
            "time_init",
            "time_end",
            "duration_seconds",
            "min_rel_altitude",
            "max_rel_altitude",
            "mean_rel_altitude",
            "first_rel_altitude",
            "last_rel_altitude",
            "min_abs_altitude",
            "max_abs_altitude",
            "mean_abs_altitude",
            "first_abs_altitude",
            "last_abs_altitude",
        ]
    ]


def reorder_cols(df, expected_order: list[str]):
    """
    Reorder columns in data frame.
    """
    return df[expected_order]


def process_dir(dirname):
    """
    Processes all logfiles in a directory.
    """
    cols_order = [
        "filename",
        "frame",
        "time_init",
        "time_end",
        "diff_time_ms",
        "date",
        "time",
        "iso",
        "shutter",
        "fnum",
        "ev",
        "ct",
        "color_md",
        "focal_len",
        "dzoom_ratio",
        "dzoom_ratio_delta",
        "latitude",
        "longitude",
        "rel_alt",
        "abs_alt",
    ]
    large_df = pd.DataFrame()
    for file in os.listdir(dirname):
        if file.endswith(".SRT"):
            print("Processing file: ", file)
            with open(dirname + "/" + file, "r", encoding="utf-8") as f:
                data = f.read()
                sections = data.split("\n\n")
                subsections = [section.split("\n") for section in sections]
                large_portion = large_dataframe(subsections, file)
                large_df = pd.concat(
                    [large_df, reorder_cols(large_portion, cols_order)],
                    ignore_index=True,
                )
    return large_df


if __name__ == "__main__":
    data_path = "/home/brandon/manatee/srt_process/SRT"
    df = process_dir(data_path)
    summ = summarize_data(df)
    df.to_csv(f"{data_path}/data.csv")
    summ.to_csv(f"{data_path}/data_summ.csv", index=False)
    print(df.head())
    print(df.columns)
