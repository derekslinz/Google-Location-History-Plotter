import json
import random
from datetime import datetime

import folium
import pandas as pd
from folium.plugins import TimestampedGeoJson


def extract_lat_lon(location):
    if location:
        _, coords = location.split(":")
        lat, lon = coords.split(",")
        return float(lat), float(lon)
    return None, None


def parse_location_history(json_file):
    with open(json_file, 'r') as file:
        json_data = json.load(file)

    visits_data = []
    activities_data = []

    for record in json_data:
        start_time = record.get("startTime")
        end_time = record.get("endTime")

        if start_time and end_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration = (end_dt - start_dt).total_seconds() / 60
            duration = round(duration, 2)
        else:
            duration = None

        if 'visit' in record:
            place_location = record["visit"]["topCandidate"].get("placeLocation")
            lat, lon = None, None
            if place_location:
                lat, lon = extract_lat_lon(place_location)
            visit_data = {
                "startTime": start_time,
                "endTime": end_time,
                "duration (minutes)": duration,
                "type": "visit",
                "hierarchyLevel": record["visit"].get("hierarchyLevel"),
                "placeID": record["visit"]["topCandidate"].get("placeID"),
                "latitude": lat,
                "longitude": lon,
                "probability": record["visit"]["topCandidate"].get("probability")
            }
            visits_data.append(visit_data)
        elif 'activity' in record:
            start_location = record["activity"].get("start")
            end_location = record["activity"].get("end")

            start_lat, start_lon = extract_lat_lon(start_location)
            end_lat, end_lon = extract_lat_lon(end_location)

            distance_meters = record["activity"].get("distanceMeters")
            if distance_meters is not None:
                distance_meters = float(distance_meters)
                distance_meters = round(distance_meters, 2)

            activity_data = {
                "startTime": start_time,
                "endTime": end_time,
                "duration (minutes)": duration,
                "type": "activity",
                "distanceMeters": distance_meters,
                "activityType": record["activity"]["topCandidate"].get("type"),
                "startLatitude": start_lat,
                "startLongitude": start_lon,
                "endLatitude": end_lat,
                "endLongitude": end_lon
            }
            activities_data.append(activity_data)

    visits_df = pd.DataFrame(visits_data)
    activities_df = pd.DataFrame(activities_data)

    visits_df.to_csv('visits.csv', index=False)
    activities_df.to_csv('activities.csv', index=False)


def generate_timeline_map(visits_csv, activities_csv):
    visits_df = pd.read_csv(visits_csv)
    activities_df = pd.read_csv(activities_csv)

    features_visits = []
    for _, row in visits_df.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['longitude'], row['latitude']]
            },
            'properties': {
                'time': row['startTime'],
                'style': {'color': 'blue'},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': 'blue',
                    'fillOpacity': 0.6,
                    'stroke': 'false',
                    'radius': 5
                }
            }
        }
        features_visits.append(feature)

    features_activities = []
    activity_colors = {}
    color_palette = ['green', 'orange', 'purple', 'cyan', 'gray',
                     'brown', 'pink', 'lightgreen', 'red', 'lightblue',
                     'darkblue', 'gold', 'black']

    activity_counts = activities_df['activityType'].value_counts()
    top_activities = activity_counts.nlargest(5).index.tolist()
    other_count = activity_counts.sum() - activity_counts.nlargest(5).sum()

    used_colors = set()

    for _, row in activities_df.iterrows():
        activity_type = row['activityType']

        if activity_type not in activity_colors:
            available_colors = [color for color in color_palette if color not in used_colors]
            if available_colors:
                selected_color = random.choice(available_colors)
                activity_colors[activity_type] = selected_color
                used_colors.add(selected_color)

        color = activity_colors[activity_type]

        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [row['startLongitude'], row['startLatitude']],
                    [row['endLongitude'], row['endLatitude']]
                ]
            },
            'properties': {
                'time': row['startTime'],
                'style': {'color': color},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': color,
                    'fillOpacity': 0.1,
                    'stroke': 'true',
                    'strokeColor': color,
                    'radius': 3
                }
            }
        }
        features_activities.append(feature)

    features = features_visits + features_activities

    map_center = [visits_df['latitude'].mean(), visits_df['longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=4)

    timestamped_geojson = TimestampedGeoJson(
        {
            'type': 'FeatureCollection',
            'features': features
        },
        transition_time=50,
        loop=True,
        auto_play=True,
        time_slider_drag_update=True,
    ).add_to(m)

    legend_html = """
    <div style="position: fixed; 
                 bottom: 20px; right: 20px; width: 150px; height: auto; 
                 background-color: rgba(255, 255, 255, 0.7); z-index:9999; border:2px solid grey; 
                 padding: 10px; border-radius: 5px;">
        <h4>Activity Legend</h4>
    """

    for activity_type in top_activities:
        color = activity_colors[activity_type]
        legend_html += f'<i style="background: {color}; width: 20px; height: 20px; display: inline-block;"></i> {activity_type}<br>'

    if other_count > 0:
        legend_html += f'<i style="background: gray; width: 20px; height: 20px; display: inline-block;"></i> Other<br>'

    legend_html += "</div>"

    folium.Marker(
        location=map_center,
        icon=folium.DivIcon(html=legend_html)
    ).add_to(m)

    m.save('animated_time_lapse_with_speed.html')


def main():
    json_file = 'location_history.json'
    visits_csv = 'visits.csv'
    activities_csv = 'activities.csv'

    parse_location_history(json_file)
    generate_timeline_map(visits_csv, activities_csv)


if __name__ == "__main__":
    main()
