from dash import html, dcc
from utils import decimation_options

layout = html.Div([
    html.H1("Digital Oscilloscope", className='page-title'),
    html.Hr(className="title-divider"),
    html.Div(id='oscilloscope-status', children="Status: Stopped", className="status-display"),
    dcc.Graph(id='scope-graph', config = {'editable': True}),
    html.Div(id='interval-counter-display', style={'marginTop': '10px'}),
    html.Div(id='zoom-info', style={'marginTop': '10px', 'fontWeight': 'bold', 'fontSize': '14px', 'marginLeft': '10px'}),
    html.Div([
    # Trigger Settings - Left Column
    html.Div([
        html.H5("Trigger Settings", className="section-title"),
        html.Div([
            html.Div([
                html.Label("Time"),
                dcc.Dropdown(
                    id='input-decimation',
                    options=decimation_options,
                    value=1,
                    clearable=False,
                    className='custom-dropdown'
                )
            ], className="trigger-input"),

            html.Div([
                html.Label("Trigger Delay"),
                dcc.Slider(
                    id='input-delay',
                    min=-8192,
                    max=8192,
                    step=1,
                    value=0,
                    marks={-8192: '0', 8192: '0.13ms'},
                    tooltip={'always_visible': False, 'placement': 'bottom'},
                    className = 'custom-slider'
                ),
                html.Div(id='delay-time-display', style={'marginTop': '5px', 'fontSize': '14px'})
            ], className="trigger-input"),

            html.Div([
                html.Label("Trigger Level (V)"),
                dcc.Input(
                    id='input-level',
                    type='number',
                    value=0.01,
                    step=0.01,
                    className='custom-input'
                )
            ], className="trigger-input"),

            html.Div([
                html.Label("Time Frame"),
                dcc.Slider(
                    id = 'timeframe', 
                    min = 1,
                    max = 16, 
                    value = 1, 
                    step = 1,
                    tooltip={'always_visible': False, 'placement': 'bottom'},
                    className = 'custom-slider'
                )
            ], className = "trigger-input"),

        # Merged button group
        html.Div([
            html.Button('Run', id='run-btn', n_clicks=0, className='control-button'),
            html.Button('Stop', id='stop-btn', n_clicks=0, className='control-button'),
            html.Button('Acquire Single Shot', id='acquire-btn', n_clicks=0, className='control-button')
        ], className='button-group', style={'display': 'flex', 'justifyContent': 'center', 'gap': '10px', 'marginTop': '15px'})
    ], className="trigger-settings")
    ], style={'flex': '1', 'padding': '10px'}),

    # Channel Settings - Right Column
    html.Div([
        html.H5("Channel Settings", className="section-title"),
        html.Div([
            dcc.Input(id='channel-input', type='text', placeholder='Enter e.g. CH1: Laser Ref', className = 'channel-input-field'),
            html.Button('Add Channel', id='add-channel-btn', n_clicks=0, className = 'channel-input-button')
        ], className = 'channel-input'),
        dcc.Dropdown(id='channel-dropdown', multi=True, placeholder="Select channels to plot"),
        dcc.Store(id='channel-store', data={}),  # To hold mapping: CH1 -> Label
        html.Div([
            dcc.Dropdown(id='trigger-channel-dropdown', options =[],placeholder = 'Select trigger channel', className = 'trigger-dropdown'),
            dcc.Dropdown(id ='trigger-edge-dropdown', options = [
                {'label': 'Positive Edge (PE)', 'value': 'PE'},
                {'label': 'Negative Edge (NE)', 'value': 'NE'},
                {'label': 'Force Trigger', 'value': 'NOW'}
            ], placeholder = 'Select edge', className = 'trigger-dropdown')
        ], className = 'two-dropdown-row'
        )
        ],
          style={'flex': '1', 'padding': '10px'})
    ], style={'display': 'flex', 'width': '100%'}),

    dcc.Interval(
    id='refresh-interval',
    interval=5000,  # 1 second
    disabled=True,  # initially OFF
    n_intervals=0
    )
])