<p align="center">
  <img src="assets/logo.png" alt="drone-trace Logo" width="300">
</p>

# drone-trace

A simple library for parsing, processing, and visualizing drone flight data from DJI SRT files.

## Installation

```bash
pip install drone-trace
```

Or with uv:

```bash
uv add drone-trace
```

## Features

- Parse DJI SRT subtitle files containing flight metadata
- Extract GPS coordinates (latitude/longitude), altitude (relative and absolute)
- Extract camera settings (ISO, shutter, f-number, EV, color temperature, focal length, digital zoom)
- Process entire directories of SRT files into pandas DataFrames
- Summarize flight data with aggregated statistics per file

## Usage

```python
from drone_trace.process import process_dir, summarize_data

# Process all SRT files in a directory
df = process_dir("/path/to/srt/files")

# Get summary statistics per flight
summary = summarize_data(df)

# Export to CSV
df.to_csv("flight_data.csv")
summary.to_csv("flight_summary.csv", index=False)
```

## Requirements

- Python >= 3.12
- pandas >= 2.3.3

