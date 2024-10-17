import tkinter as tk
import requests
import folium
import webbrowser
from tkinter import filedialog

# Function to get coordinates (latitude, longitude) using Nominatim Geocoding API
def get_coordinates(place_name):
    # Adding 'India' to be more specific when searching locations in India
    url = f"https://nominatim.openstreetmap.org/search?q={place_name},India&format=json&limit=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return float(lat), float(lon)
        else:
            return None, None
    else:
        return None, None

# Function to get the route from OSRM API
def get_osrm_route(origin_lat, origin_lon, dest_lat, dest_lon, mode="driving"):
    url = f"http://router.project-osrm.org/route/v1/{mode}/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?overview=full&geometries=geojson"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['routes']:
            distance = data['routes'][0]['distance'] / 1000  # Convert to kilometers
            duration = data['routes'][0]['duration'] / 60    # Convert to minutes
            route_geometry = data['routes'][0]['geometry']['coordinates']  # Route coordinates
            return distance, duration, route_geometry
        else:
            return None, None, None
    else:
        return None, None, None

# Function to plot the route on a folium map
def plot_route_on_map(route_geometry, origin, destination):
    # Get the starting and ending points for centering the map
    start_coords = route_geometry[0]
    end_coords = route_geometry[-1]
    
    # Create a folium map centered on the start of the route
    map_obj = folium.Map(location=[start_coords[1], start_coords[0]], zoom_start=6)
    
    # Plot the route
    folium.PolyLine([(coord[1], coord[0]) for coord in route_geometry], color="blue", weight=5).add_to(map_obj)
    
    # Mark the start and end points
    folium.Marker([start_coords[1], start_coords[0]], popup="Start: " + origin).add_to(map_obj)
    folium.Marker([end_coords[1], end_coords[0]], popup="End: " + destination).add_to(map_obj)
    
    # Save the map to an HTML file
    map_file = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
    if map_file:
        map_obj.save(map_file)
        webbrowser.open(map_file)  # Open the map in a browser

# Function to handle user input and display result
def calculate_route():
    origin = entry_origin.get()
    destination = entry_destination.get()
    mode = travel_mode.get()
    
    origin_lat, origin_lon = get_coordinates(origin)
    dest_lat, dest_lon = get_coordinates(destination)
    
    if origin_lat is None or dest_lat is None:
        result_label.config(text="Error: Could not find location coordinates")
        return
    
    distance, duration, route_geometry = get_osrm_route(origin_lat, origin_lon, dest_lat, dest_lon, mode)
    
    if distance and duration and route_geometry:
        result_label.config(text=f"Distance: {distance:.2f} km\nTime: {duration:.2f} minutes")
        # Plot the route on a map and display it
        plot_route_on_map(route_geometry, origin, destination)
    else:
        result_label.config(text="Error: Could not calculate the route")

# GUI setup with Tkinter
root = tk.Tk()
root.title("Route Finder")

# Travel Mode
travel_mode = tk.StringVar(value="driving")

# Labels and Entry fields for Origin and Destination place names
tk.Label(root, text="Origin:").pack()
entry_origin = tk.Entry(root)
entry_origin.pack()

tk.Label(root, text="Destination:").pack()
entry_destination = tk.Entry(root)
entry_destination.pack()

# Dropdown for travel mode selection
tk.Label(root, text="Travel Mode:").pack()
travel_modes = ["driving", "cycling", "walking"]
tk.OptionMenu(root, travel_mode, *travel_modes).pack()

# Button to calculate the route
tk.Button(root, text="Calculate Route", command=calculate_route).pack()

# Label to display results
result_label = tk.Label(root, text="")
result_label.pack()

# Start the GUI main loop
root.mainloop()
