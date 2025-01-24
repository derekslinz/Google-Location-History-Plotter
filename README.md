# README

## Overview

This Python script processes location history data from a JSON file, extracts visit and activity information, and
generates a timeline map visualizing the data using Folium. The output includes two CSV files (`visits.csv` and
`activities.csv`) and an HTML file (`animated_time_lapse_with_speed.html`) that displays the timeline map.

## Requirements

- Python 3.x
- Libraries:
    - `json`
    - `random`
    - `datetime`
    - `folium`
    - `pandas`

You can install the required libraries using pip:

```bash
pip install folium pandas
```

## Usage

1. Place your location history JSON file in the same directory as the script and name it `location_history.json`.
2. Run the script:

```bash
python script_name.py
```

Replace `script_name.py` with the actual name of your Python file.

3. After execution, you will find:
    - `visits.csv`: Contains visit data with timestamps, duration, and location coordinates.
    - `activities.csv`: Contains activity data with timestamps, distance, and start/end location coordinates.
    - `animated_time_lapse_with_speed.html`: An interactive map showing visits and activities over time.

## Functions

- `extract_lat_lon(location)`: Extracts latitude and longitude from a given location string.
- `parse_location_history(json_file)`: Parses the JSON file to extract visit and activity data, saving them to CSV
  files.
- `generate_timeline_map(visits_csv, activities_csv)`: Generates a timeline map using the visit and activity data from
  the provided CSV files.
- `main()`: The main function that orchestrates the parsing and map generation.

## Data Format

The input JSON file should contain records with the following structure:

```json
[
  {
    "startTime": "YYYY-MM-DDTHH:MM:SS",
    "endTime": "YYYY-MM-DDTHH:MM:SS",
    "visit": {
      "topCandidate": {
        "placeLocation": "Place:lat,lon",
        "placeID": "place_id",
        "probability": 0.9
      },
      "hierarchyLevel": "level"
    },
    "activity": {
      "start": "Start:lat,lon",
      "end": "End:lat,lon",
      "distanceMeters": 100,
      "topCandidate": {
        "type": "activity_type"
      }
    }
  }
]
```

## License

This project is licensed under the MIT License.