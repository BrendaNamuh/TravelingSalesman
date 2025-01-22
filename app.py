from dash import Dash, dcc, html, dash,  Input, Output, State
import plotly.graph_objects as go
import googlemaps
from genetic_algorithm import run_gen_algo 
import googlemaps

BACKGROUND_COLOUR = '#ffffff'
# Replace this with your Google API key
GOOGLE_API_KEY = "AIzaSyBhzRSUol2dYgsnyjxixu7XIyQEqi4KaXY"


# Google Maps API client
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# memory['locations'] = []
# memory['postal_codes'] = []

# Initial empty lists for nodes and edges
# memory['node_x'] = []
# memory['node_y'] = []
# memory['node_labels'] = []


# Function to get latitude and longitude from postal code
def get_coordinates_from_postal_code(postal_code):
    geocode_result = gmaps.geocode(postal_code)
    if geocode_result:
        lat = geocode_result[0]['geometry']['viewport']['northeast']['lat']
        lng = geocode_result[0]['geometry']['viewport']['northeast']['lng']
        return lat, lng
    return None, None

# Create a function to add nodes dynamically based on postal code
def add_node(postal_code,memory):
    latitude, longitude = get_coordinates_from_postal_code(postal_code)
    if latitude and longitude and postal_code not in memory['postal_codes']:
        memory['postal_codes'].append(postal_code)
        memory['locations'].append([longitude,latitude,postal_code])
        memory['node_x'].append(longitude)
        memory['node_y'].append(latitude)
        memory['node_labels'].append(postal_code)
        return True
    return False

# Create the node trace (dynamic, based on nodes added)
def create_node_trace(memory):
    node_colors = ['red']
    if  memory['node_x']:
        node_colors = ['blue' for i in range(len(memory['node_x']))]  # Default color for all nodes
        print('node_colors: ',node_colors)
        node_colors[0] = 'red'  # Highlight the first node with a different value
    print('Current LOCATIONS: ',memory['locations'])
    return go.Scatter(
        x=memory['node_x'],
        y=memory['node_y'],
        mode='markers+text',
        marker=dict(
            symbol='star', # square, star, cross
            size=10,
            color= node_colors,
        ),
        text=memory['node_labels'],  # Node labels
        textposition="bottom center",
    )

# Create edge trace (arrows between nodes)
def create_edge_trace(path,memory):
    edge_x = []
    edge_y = []
    annotations = []  # List to hold annotations for arrows
    # print('Curent Path: ',path)
    for i, pos in enumerate(path):
        if i +1 == len(path):
            continue
        # print('Curent Path: ',path)
        ending_pos = path[i +1] 
        x0, y0,_ = memory['locations'][path[i]]  # Start node position
        x1, y1,_ = memory['locations'][ending_pos]  # End node position
        edge_x.append(x0)
        edge_x.append(x1)
        edge_y.append(y0)
        edge_y.append(y1)
        
        # Add arrow annotations
        annotations.append(dict(
            x=x1, y=y1,
            ax=x0, ay=y0,
            axref="x", ayref="y",  # Start point reference
            xref="x", yref="y",  # End point reference
            showarrow=True,
            arrowhead=3,  # Arrowhead style
            arrowsize=2,
            arrowcolor='black'
        ))
    
    return go.Scatter(
        x=edge_x, 
        y=edge_y,
        mode='lines',
        line=dict(width=2, color='blue'),
        hoverinfo='none'
    ), annotations


# Initialize the app
app = dash.Dash(__name__)
server=app.server



# Create an empty figure for initial setup
fig = go.Figure(
    data=[],
    layout=go.Layout(
          xaxis=dict(
                    title='Longitude',  # Title of the X-axis
                    titlefont=dict(
                        size=14,  
                        family='Montserrat',  
                        color='black'  
                    ),
                     showgrid=True,
                    gridcolor='#cb58fc',
                    gridwidth=0.2,
                ),
                yaxis=dict(
                    title='Latitude',  # Title of the Y-axis
                    titlefont=dict(
                        size=14,  
                        family='Montserrat', 
                        color='black' 
                    ),
                     showgrid=True,
                    gridcolor='#cb58fc',
                    gridwidth=0.2,
                ),
        updatemenus=[{
            'buttons': [
                # Initially no buttons for play/pause in the Plotly layout
            ],
           
        }],
        plot_bgcolor=BACKGROUND_COLOUR, 
        paper_bgcolor=BACKGROUND_COLOUR,  
        height = 720
        
    ),
    frames=[]
)

# Set title in tab
app.title = 'GenePath'

# Define the layout for Dash
app.layout = html.Div([

      # Link to Google Fonts (example: Roboto font)
    html.Link(
        href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700&display=swap", 
        rel="stylesheet"
    ),
   
    html.H1("GenePath - Evolving the Shortest Route", style={'textAlign': 'center','border':'solid 2px transparent','width':'fit-content','z-index': '2','position':'absolute','margin-left':'5%'}),
    html.P("Discover the shortest route among the entered locations using a genetic algorithm.", style={'width':'20%','textAlign': 'center','border':'solid 2px transparent','width':'fit-content','z-index': '2','position':'absolute','margin-left':'5%','top':'7%','font-weight':'2em',}),
    # Text beneath
    html.Div(id='search-output', style={'padding': '10px','border':'solid transparent 2px','position':'absolute','bottom':'-10px','z-index':'2','left':'50%','transform':'translate(-50%,-50%)'}),
    # Search Bar
    html.Div([
        #Search Bar
        dcc.Input(
            id='search-bar',
            type='text',
            placeholder='Enter a postal code',
            debounce=True,
            autoComplete='off',
            # value='',
            style={'width': '40%','border':'solid black 2px', 'margin-left':'100px','padding': '10px','border':'solid black 1px', 'background':BACKGROUND_COLOUR}
        ),
        
        # Wrapper for whole 
    ], style={'width': '20%', 'padding': '10px','border':'solid transparent 2px','background':BACKGROUND_COLOUR,'z-index':'2','right':'0px','margin-top':'15px','position':'absolute'}),
    

    # Graph component
    dcc.Graph(
        id='network-graph',
        figure=fig,
        style={'height': '720px','width':'101%','position': 'absolute', 'top':'3%','z-index': '1'},
        config={'staticPlot':True, }
    ),
    dcc.Store(id='memory', data={
    'postal_codes': [],
    'locations': [],
    'node_x': [],
    'node_y': [],
    'node_labels': []
})
], style={'background':BACKGROUND_COLOUR,'height':'100vh','width':'100vw'})


# Define the callback to update the graph
@app.callback(
    [Output('network-graph', 'figure'),
     Output('search-output', 'children'),
     Output('memory', 'data')],
    [Input('search-bar', 'value'),
     Input('network-graph', 'relayoutData')],
    [State('memory', 'data')]
)


def update_graph(value,relayoutData,memory):
    print(f'Callback Running...\nValue: {value}\nRelayoutData: {relayoutData}')
    
    if not memory:
        memory = {
            'postal_codes': [],
            'locations': [],
            'node_x': [],
            'node_y': [],
            'node_labels': []
        }
    message = ""
    #global memory['postal_codes'], memory['locations'], memory['node_x'], memory['node_y'], memory['node_labels'] 

    # On page refresh
    if not value: 
        memory['postal_codes'] = []
        memory['locations'] = []
        memory['node_x'] = []
        memory['node_y'] = []
        memory['node_labels'] = []
        return fig,'',memory
    
    value = value.upper().replace(" ", "")
    if value:
        added = add_node(value,memory)
        if added:
            message = f"Location '{value}' added."
        else:
            message = f"Location '{value}' not found or already added."
    else:
        message = ""

    # Create node trace
    node_trace = create_node_trace(memory)

    # Create edge trace
    frames = []
    
    # 'Find path' is clicked and the requirement to execute the genetic algo is satisfied
    if relayoutData and len(memory['node_y'])>1:
        sorted_paths = run_gen_algo(memory['locations'])
        #sorted_paths = [[0, 3, 1, 2], [2, 1, 3, 0], [0, 1, 2, 3]]
        print('sorted_paths: ',sorted_paths)
        print(memory['locations'])

        for path in sorted_paths:
            print('Current Path: ', path)
            # edges_subset = predefined_edges[:i]
            edge_trace, annotations = create_edge_trace(path,memory)
            print('Edge Trace X:', edge_trace['x'])
            print('Edge Trace Y:', edge_trace['y'])
            postal_path = [memory['locations'][pos][2] for pos in path]
            postal_path = ' -> '.join(postal_path)
            # Add edges progressively as frames
            frames.append(go.Frame(
                data=[node_trace,edge_trace],
                layout=go.Layout(
                      xaxis=dict(
                            title='Longitude',  # Title of the X-axis
                            titlefont=dict(
                                size=14,  
                                family='Montserrat',  
                                color='black'  
                            ),
                             showgrid=True,
                            gridcolor='#cb58fc',
                            gridwidth=0.2,
                        ),
                        yaxis=dict(
                            title='Latitude',  # Title of the Y-axis
                            titlefont=dict(
                                size=14,  
                                family='Montserrat', 
                                color='black' 
                            ),
                             showgrid=True,
                    gridcolor='#cb58fc',
                    gridwidth=0.2,
                        ),
                    annotations=annotations,
                    title=f"Shortest Path: {postal_path} ",
                     title_x=0.05,  # Centered horizontally
                     title_y=0.88,  # Close to the top
                     title_font=dict(  # Custom font settings for the title
                        family='Montserrat',  # Font family (you can choose other fonts like 'Verdana', 'Courier', etc.)
                        size=14,  # Font size (increase for larger text)
                        color='black',  # Font color (you can use any color code like 'rgb(255, 0, 0)', or a named color)
                    )
                    
                ),
            ))
        
      
        # Final figure with frames and animation settings
        updated_fig = go.Figure(
            data=[node_trace],
            layout=go.Layout(
                  xaxis=dict(
                    title='Longitude',  # Title of the X-axis
                    titlefont=dict(
                        size=14,  
                        family='Montserrat',  
                        color='black'  
                    ),
                     showgrid=True,
                    gridcolor='#cb58fc',
                    gridwidth=0.2,
                ),
                yaxis=dict(
                    title='Latitude',  # Title of the Y-axis
                    titlefont=dict(
                        size=14,  
                        family='Montserrat', 
                        color='black' 
                    ),
                     showgrid=True,
                    gridcolor='#cb58fc',
                    gridwidth=0.2,
                ),
                updatemenus=[
                    {
                        'buttons': [
                            {
                                'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True}],
                                'label': 'Find Shortest Path',
                                'method': 'animate',
                            }
                        ],
                        'x': 0.896,  # Position at the right edge of the plot
                        'xanchor': 'left',  # Anchor the button to the right
                        'yanchor': 'bottom',  # Anchor the button to the top
                        'type': 'buttons',  # Ensure it's a button type menu
                    }
                ],

                plot_bgcolor=BACKGROUND_COLOUR,  # Set the background color of the plot area
                paper_bgcolor=BACKGROUND_COLOUR, 
                height = 720
               
            ),
            frames=frames
        )
    # Update graph with new memory['locations'] (button not clicked)
    elif memory['node_y']:
        # If no play button click, return a static figure with just the nodes
        #updated_fig = go.Figure(data=[node_trace])
        updated_fig  = go.Figure(
            data=[node_trace],
            layout=go.Layout(
                xaxis=dict(
                    title='Longitude',  # Title of the X-axis
                    titlefont=dict(
                        size=14,  
                        family='Montserrat',  
                        color='black'  
                    ),
                     showgrid=True,
                    gridcolor='#cb58fc',
                    gridwidth=0.2,
                ),
                yaxis=dict(
                    title='Latitude',  # Title of the Y-axis
                    titlefont=dict(
                        size=14,  
                        family='Montserrat', 
                        color='black' 
                    ),
                     showgrid=True,
                    gridcolor='#cb58fc',
                    gridwidth=0.2,
                ),
                updatemenus=[
                        {
                            'buttons': [
                                {
                                    'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True}],
                                    'label': 'Find Shortest Path',
                                    'method': 'animate',
                                }
                            ],
                            'x': 0.896,  # Position at the right edge of the plot
                            'xanchor': 'left',  # Anchor the button to the right
                            'yanchor': 'bottom',  # Anchor the button to the top
                            'type': 'buttons',  # Ensure it's a button type menu
                        }
                    ],
                plot_bgcolor=BACKGROUND_COLOUR,  # Set the background color of the plot area
                paper_bgcolor=BACKGROUND_COLOUR, 
            ),
            frames=[]
        )
    # No button click, one or no memory['locations']
    else:
        updated_fig = go.Figure(
            layout=go.Layout(
                plot_bgcolor=BACKGROUND_COLOUR, 
                paper_bgcolor=BACKGROUND_COLOUR,
                  xaxis=dict(
                    title='Longitude',  # Title of the X-axis
                    titlefont=dict(
                        size=14,  
                        family='Montserrat',  
                        color='black'  
                    ),
                     showgrid=True,
                    gridcolor='#cb58fc',
                    gridwidth=0.2,
                ),
                
                yaxis=dict(
                    title='Latitude',  # Title of the Y-axis
                    titlefont=dict(
                        size=14,  
                        family='Montserrat', 
                        color='black' 
                    ),
                     showgrid=True,
                    gridcolor='#cb58fc',
                    gridwidth=0.2,
                ),
                
            ),
            frames=[])

    
    return updated_fig, message,memory

# Run the app
if __name__ == '__main__':
        app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False)
