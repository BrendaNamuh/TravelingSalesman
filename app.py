import requests
from dash import Dash, dcc, html, dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import math
import googlemaps
from genetic_algorithm import run_gen_algo 
import time



# Replace this with your Google API key
GOOGLE_API_KEY = "AIzaSyBhzRSUol2dYgsnyjxixu7XIyQEqi4KaXY"
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
LOCATIONS = []

def mercator_projection(longitude, latitude):
    """
    Convert geographic coordinates (longitude, latitude) to Mercator projection coordinates (x, y).
    """
    longitude_rad = math.radians(longitude)
    latitude_rad = math.radians(latitude)
    x = longitude_rad
    y = math.log(math.tan(math.pi / 4 + latitude_rad / 2))  # Mercator projection formula

    return x, y

# Function to get latitude and longitude from postal code
def get_coordinates_from_postal_code(postal_code):
    print(f'Postal code entered: {postal_code}')
    geocode_result = gmaps.geocode(postal_code)
    # geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
    
    print(f'geocode_result: {geocode_result}')
    if geocode_result:
        lat  =geocode_result[0]['geometry']['viewport']['northeast']['lat']
        lng = geocode_result[0]['geometry']['viewport']['northeast']['lng']
        print(f'Latitute: {lat}, Longitude: {lng}')
        return lat, lng
    print(f"The address {postal_code} was not found")
    return None, None

    # params = {
    #     'address': postal_code,
    #     'key': GOOGLE_API_KEY
    # }
    
    # response = requests.get(GEOCODE_URL, params=params)
    # data = response.json()
    
    # if data['status'] == 'OK':
    #     # Geocoding an address
       
    #     # Get the latitude and longitude from the response
    #     location = data['results'][0]['geometry']['location']
    #     latitude = location['lat']
    #     longitude = location['lng']
    #     return latitude, longitude
    # else:
    #     print('the response did not work')
    #     print(f"Error: {data['status']}")
    #     return None, None

# Initial locations (using coordinates for CN Tower and Toronto Zoo as placeholders)
locations = [
    ((79.3871, 43.6426), 'CN Tower'),  # CN Tower
    ((79.1854, 43.7715), 'Toronto Zoo')  # Toronto Zoo
]

# Create the Dash app
app = Dash(__name__)

node_x = []
node_y = []
node_labels = []  # To store node labels for search filtering

# Create nodes based on list of tuples (locations)
def create_nodes(locations):
    global node_x, node_y, node_labels
    for location, label in locations: 
        longitude, latitude = location
        x, y = mercator_projection(longitude, latitude)
        node_x.append(x)
        node_y.append(y)
        node_labels.append(label)
    return node_x, node_y, node_labels



def display_path(best_path_indices, fig):          
    # Create node_positions
    node_positions = {}
    for i in best_path_indices:
        x,y,postal = LOCATIONS[i]
        node_positions[postal] = (x,y)
    
    nodes = list(node_positions.items())
    nmbr_nodes = len(node_positions)
    # Remake the nodes
    for i, (node, (x, y)) in enumerate(nodes):
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(size=10, color='blue'),
            text=[node],
            textposition='top center',
            name=node
        ))
        dest_i = i+1
        if dest_i == nmbr_nodes:
            dest_i = 0
        _, dest_coord = nodes[dest_i]
        dest_x, dest_y = dest_coord
        # Redraw the arrows
        # Add arrows (annotations) connecting nodes
        fig.add_annotation(
            x=x, y=y,
            ax=dest_x, ay=dest_y,
            axref="x", ayref="y", xref="x", yref="y",
            showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=2
        )
# node_x, node_y, node_labels = create_nodes(locations)

# Define the edges (connections between nodes)
edge_x = node_x
edge_y = node_y

# Calculate axis range dynamically based on the vertices
margin = 0.1  # 10% margin
# x_min, x_max = min(node_x) - margin, max(node_x) + margin
# y_min, y_max = min(node_y) - margin, max(node_y) + margin
x_min, x_max = 0,0 
y_min, y_max = 0,0 

# Create the Plotly figure
fig = go.Figure()

# Add edges (lines between nodes)
fig.add_trace(go.Scatter(
    x=edge_x, y=edge_y,
    mode='lines',
    line=dict(width=2,  # width of lines
               color='#050A30'  # color of lines
            ),
    hoverinfo='none'
))

# Add nodes (points)
fig.add_trace(go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    marker=dict(size=10, color='#7EC8E3'),
    text=node_labels,
    hoverinfo='text'
))

# Update layout to fit the nodes and edges within the 90% of the screen
fig.update_layout(
    title="2D Representation of Locations",
    showlegend=False,
    xaxis=dict(
        showgrid=True,           # Enable grid lines
        zeroline=False,          # Disable the zero line
        fixedrange=True,         # Disable zooming
        range=[x_min, x_max],
        gridcolor='lightgray',   # Grid line color
        gridwidth=0.5,           # Grid line width
        zerolinecolor='gray',    # Zero line color
        zerolinewidth=2,         # Zero line width
        showline=True,           # Show the axis line
        linewidth=2,             # Axis line width
    ),
    yaxis=dict(
        showgrid=True,           # Enable grid lines
        zeroline=False,          # Disable the zero line
        fixedrange=True,         # Disable zooming
        range=[y_min, y_max],
        gridcolor='lightgray',   # Grid line color
        gridwidth=0.5,           # Grid line width
        zerolinecolor='gray',    # Zero line color
        zerolinewidth=2,         # Zero line width
        showline=True,           # Show the axis line
        linewidth=2,             # Axis line width
    ),
    plot_bgcolor='white',        # Background color
    height=550,                  # 90% of the screen height (assuming 800px height)
    width=950,                  # 90% of the screen width (assuming 800px width)
    dragmode=False,              # Disable panning/zooming
    margin=dict(l=40, r=40, t=40, b=40)  # Ensure there's space around the plot
)

# Define the layout for Dash
app.layout = html.Div([
    # Search Bar
    html.Div([
        dcc.Input(
            id='search-bar',
            type='text',
            placeholder='Enter postal code...',
            debounce=True,  # Allow user to type and then trigger after a delay
            value='',  # Set initial value to an empty string
            style={'width': '100%', 'padding': '10px'}
        ),
        html.Div(id='search-output', style={'padding': '10px'})
    ], style={'width': '80%', 'padding': '10px', 'margin': 'auto'}),

     # Button to trigger the logic
    html.Div([
        html.Button('Run', id='run-button', n_clicks=0, style={'padding': '10px 20px', 'fontSize': 18})
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
        # Interval to trigger updates every 500ms
    dcc.Interval(
        id='interval-component',
        interval=1000,  # 500 ms interval
        n_intervals=0,
        disabled=True  # Initially disabled
    ),
    # Graph
    dcc.Graph(
        id='network-graph',
        figure=fig
    )
])



# Callback to listen for 'Enter' key press, send request to Google API, and update the map
@app.callback(
    #callback function's output will update the 'figure' attribute of the network-graph component
    Output('network-graph', 'figure'), # elements that will be updated based on the callback's function 
    
    #listens for changes to the n_submit property of the search-bar component. n_submit tracks nmbr of enters
    Input('search-bar', 'n_submit'), # events that trigger the callback
    Input('run-button', 'n_clicks'),
    # listens for changes to the value of the search bar
    #Input('search-bar', 'value') # 
    State('search-bar', 'value')  # Callback can acess this var but is not triggered everytime it changes.
)

# This function is triggered when 'n_submit' or 'value' change
def update_map(n_submit, n_clicks ,postal_code):
    # If the user pressed Enter (n_submit), or there's a value in the search field
    if n_submit:
        latitude, longitude = get_coordinates_from_postal_code(postal_code)


        if latitude and longitude:
            LOCATIONS.append([longitude,latitude,postal_code])
        

            # Process and update the graph (this is where you'd get new coordinates)
            fig = go.Figure()

            # Add new node (example, this is static for now, you'd calculate this based on the postal code)
            # fig.add_trace(go.Scatter(
            #     x=[longitude],
            #     y=[latitude],
            #     mode='markers',
            #     marker=dict(size=12, color='red'),
            #     text=[value],  # Use the postal code as label
            #     hoverinfo='text'
            # ))

            node_x.append(longitude)
            node_y.append(latitude)
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                marker=dict(size=10, color='#7EC8E3'),
                text=node_labels,
                hoverinfo='text'
            ))

            # Determine shortesT path
            if len(node_x) > 2 and n_clicks:
                print('Run Button is pressed!')
                # points = zip(node_x,node_y)
                # points = [[x,y] for x,y in points]
                print('WHAT IS BEING INPUTED TO GEN ALGO: ', LOCATIONS)
                best_path_indices,sorted_paths = run_gen_algo(LOCATIONS)
                print(f"Sorted Paths: ",sorted_paths )
                # bestpath_edge_x = [node_x[i] for i in best_path_indices]
                # bestpath_edge_y = [node_y[i] for i in best_path_indices]
                # print(f"Best Path X_EDGE: {bestpath_edge_x}")
                # print(f"Best Path Y_EDGE: {bestpath_edge_y}")
                for path in (sorted_paths):
                    display_path(path,fig)


            # Update layout as needed
            fig.update_layout(
                title="2D Representation of Locations",
                xaxis=dict(title="Longitude"),
                yaxis=dict(title="Latitude")
            )

            return fig  # Return the updated figure

    # Return the same figure if no update is needed
    return dash.no_update



# Run the app with auto-reload enabled
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
    # Staples: H7S 1Y9
    # Carrefour : H7T 1C7
    pass
