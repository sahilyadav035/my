from flask import Flask, render_template, request, jsonify
import requests
import os
import folium

app = Flask(__name__)

# Ensure 'static' directory exists to store map files
if not os.path.exists('static'):
    os.makedirs('static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    data = request.get_json()

    origin_lat = data['origin_lat']
    origin_lon = data['origin_lon']
    dest_lat = data['dest_lat']
    dest_lon = data['dest_lon']
    mode = data['mode']

    # OSRM request for route calculation
    url = f"http://router.project-osrm.org/route/v1/{mode}/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?overview=full&geometries=geojson"
    response = requests.get(url)
    route_data = response.json()

    # Check if route calculation was successful
    if 'routes' in route_data:
        route = route_data['routes'][0]['geometry']['coordinates']
        travel_time = route_data['routes'][0]['duration'] / 60  # Convert seconds to minutes

        # Create a folium map centered on the origin location
        m = folium.Map(location=[origin_lat, origin_lon], zoom_start=12)

        # Add the route to the map
        folium.PolyLine(locations=[[lat, lon] for lon, lat in route], color='blue', weight=5).add_to(m)

        # Save the map to the static folder
        map_file = 'static/map.html'
        m.save(map_file)

        return jsonify({'travel_time': travel_time, 'map_url': map_file})
    else:
        return jsonify({'error': 'Route calculation failed'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
