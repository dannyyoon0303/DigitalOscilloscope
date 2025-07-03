import plotly.graph_objects as go
import dash 
from dash import dcc, html
from dash.dependencies import Input, Output, State
from utils import acquire_data, DMA
import numpy as np

def register_callbacks(app):
    @app.callback(
    Output('refresh-interval', 'disabled'),
    [Input('run-btn', 'n_clicks'),
     Input('stop-btn', 'n_clicks')],
    prevent_initial_call=True
    )
    def toggle_interval(run_clicks, stop_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Run → enabled (False), Stop → disabled (True)
        return triggered_id != 'run-btn'

    '''@app.callback(
        Output('channel-dropdown', 'options'),
        Output('channel-store', 'data'),
        Input('add-channel-btn', 'n_clicks'),
        State('channel-input', 'value'),
        State('channel-store', 'data'),
        prevent_initial_call=True
    )
    def add_channel(n_clicks, channel_text, store):
        if not channel_text or ':' not in channel_text:
            return dash.no_update, dash.no_update

        key, label = map(str.strip, channel_text.split(':', 1))
        store[key] = label
        options = [{'label': f"{key}: {label}", 'value': key} for key, label in store.items()]
        return options, store

    @app.callback(
    Output('trigger-channel-dropdown', 'options'),
    Input('channel-dropdown', 'value'),
    State('channel-store', 'data')
    )
    def update_trigger_channel_dropdown(selected_channels, channel_map):
        if not selected_channels:
            return []

        return [
            {'label': f"{ch}: {channel_map.get(ch, ch)}", 'value': ch}
            for ch in selected_channels
        ]'''

    @app.callback(
        Output('scope-graph', 'figure'),
        Input('acquire-btn', 'n_clicks'),
        Input('refresh-interval', 'n_intervals'),
        State('input-decimation', 'value'),
        State('input-delay', 'value'),
        State('input-level', 'value'),
        State('timeframe', 'value'),
        State('channel-dropdown', 'value'),
        State('channel-store', 'data'),
        State('trigger-channel-dropdown', 'value'),
        State('trigger-edge-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_scope(acquire_clicks, n_intervals, decimation, delay, level, factor, selected_channels, channel_map, trigger_channel, trigger_edge):
        ctx = dash.callback_context
        summary_lines = []
        if not ctx.triggered or not selected_channels:
            return dash.no_update

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id in ['acquire-btn', 'refresh-interval']:
            if factor == 1:
                print("Using normal acquisition")
                time_axis, data1, data2, t_trigger = acquire_data(decimation, -delay, level, trigger_channel, trigger_edge)
            else:
                print("Using DMA")
                #DMA_delay = delay+8192*factor
                time_axis, data1, data2, t_trigger = DMA(decimation, -delay, level, trigger_channel, trigger_edge, factor)
            # Build the figure based on selected channels
            fig = go.Figure()
            if 'CH1' in selected_channels:
                ch1_label = f"CH1: {channel_map.get('CH1', 'CH1')}"
                fig.add_trace(go.Scatter(x=time_axis, y=data1, mode='lines', name=ch1_label))
                vmin = np.min(data1)
                vmax = np.max(data1)
                summary_lines.append(f"<b>CH1</b><br>Min: {vmin:.3f} V<br>Max: {vmax:.3f} V")
            if 'CH2' in selected_channels:
                ch2_label = f"CH2: {channel_map.get('CH2', 'CH2')}"
                fig.add_trace(go.Scatter(x=time_axis, y=data2, mode='lines', name=ch2_label))
                vmin = np.min(data2)
                vmax = np.max(data2)
                summary_lines.append(f"<b>CH2</b><br>Min: {vmin:.3f} V<br>Max: {vmax:.3f} V")

            fig.add_vline(x=t_trigger, line=dict(color='#8a0101', width=3, dash='dot'), editable = True)
            fig.add_hline(y=level, line=dict(color='#8a0101', width=3, dash='dot'), editable = True)

            fig.update_layout(
                xaxis_title="Time (ms)",
                yaxis_title="Voltage (V)",
                legend=dict(title='Channels'),
                template='simple_white',
                margin=dict(l=40, r=40, t=60, b=40),
                hovermode='x unified',
                xaxis=dict(
                    showspikes=True, spikemode='across', spikesnap='cursor',
                    showline=True, showgrid=True, spikedash='solid',
                    spikecolor='gray', spikethickness=1, nticks=40
                ),
                yaxis=dict(
                    showspikes=True, spikemode='across', spikesnap='cursor',
                    showline=True, showgrid=True, spikedash='solid',
                    spikecolor='gray', spikethickness=1, nticks=20
                ),
                annotations=[
                    dict(
                        xref="paper", yref="paper",
                        x=1.08, y=0.55, showarrow=False,
                        align="left",
                        text="<br><br>".join(summary_lines),
                        bgcolor="white",
                        font=dict(size=10),
                    )
                ]
            )

            return fig

        return dash.no_update


    '''@app.callback(
        Output('interval-counter-display', 'children'),
        Input('refresh-interval', 'n_intervals')
    )
    def display_interval_count(n_intervals):
        return f"Interval count: {n_intervals}"


    @app.callback(
        Output('input-delay', 'marks'),
        Output('input-delay', 'min'),
        Output('input-delay', 'max'),
        Input('input-decimation', 'value'),
        Input('timeframe', 'value')
    )
    def update_slider_marks(decimation, factor):
        total_time_ms = (decimation / 125_000_000) * 16384 * factor * 1000  # total time window
        t_start = 0
        t_end = total_time_ms

        left_label = f"{(t_start):.2f} ms"
        right_label = f"{(t_end):.2f} ms"

        return {
            -8192: left_label,
            8192: right_label
        }, -8192*factor, 8192*factor
        '''

    '''@app.callback(
        Output('oscilloscope-status', 'children'),
        Input('run-btn', 'n_clicks'),
        Input('stop-btn', 'n_clicks'),
        Input('acquire-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_status(run_clicks, stop_clicks, acquire_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return "Status: Stopped"

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if triggered_id == 'run-btn':
            return "Status: Running..."
        else:  # 'stop-btn' or 'acquire-btn'
            return "Status: Stopped"


    @app.callback(
            Output('delay-time-display', 'children'),
            Input('input-decimation', 'value'),
            Input('input-delay', 'value')
    )
    def show_delay_time(decimation, delay_value):
        fs = 125000000 / decimation
        dt = 1 / fs
        delay_time =  (8192 + delay_value) * dt * 1000
        return f"Current Trigger Delay: {delay_time:.4f}ms"

    @app.callback(
        Output('zoom-info', 'children'),
        Input('scope-graph', 'relayoutData'),
        prevent_initial_call=True
    )
    def display_zoom_info(relayout_data):
        if not relayout_data:
            return "Zoom to view details."

        try:
            xmin = relayout_data.get('xaxis.range[0]')
            xmax = relayout_data.get('xaxis.range[1]')
            ymin = relayout_data.get('yaxis.range[0]')
            ymax = relayout_data.get('yaxis.range[1]')

            if None in (xmin, xmax, ymin, ymax):
                return "Zoom box not detected."

            x_range = xmax - xmin
            y_range = ymax - ymin

            return f"Zoomed window: Δt = {x_range:.4f} ms, ΔV = {y_range:.4f} V"
        except Exception:
            return "Unable to compute zoom range."'''
    
    #Client-side callback for counting intervals when run 
    app.clientside_callback(
        """
        function(n_intervals) {
            return window.dash_clientside.clientside.displayIntervalCount(n_intervals);
        }
        """,
        Output('interval-counter-display', 'children'),
        Input('refresh-interval', 'n_intervals')
    )

    #Client-side callback for dynamically updating the slider min max value based on decimation
    app.clientside_callback(
        """
        function(decimation, factor) {
            return window.dash_clientside.clientside.updateSliderProps(decimation, factor);
        }
        """,
        Output('input-delay', 'marks'),
        Output('input-delay', 'min'),
        Output('input-delay', 'max'),
        Input('input-decimation', 'value'),
        Input('timeframe', 'value')
    )

    # Client-side callback for adding channels
    app.clientside_callback(
        """
        function(n_clicks, channel_text, store) {
            return window.dash_clientside.clientside.addChannel(n_clicks, channel_text, store);
        }
        """,
        Output('channel-dropdown', 'options'),
        Output('channel-store', 'data'),
        Input('add-channel-btn', 'n_clicks'),
        State('channel-input', 'value'),
        State('channel-store', 'data'),
        prevent_initial_call=True
    )

    # Client-side callback for updating trigger dropdown
    app.clientside_callback(
        """
        function(selected_channels, channel_map) {
            return window.dash_clientside.clientside.updateTriggerChannelDropdown(selected_channels, channel_map);
        }
        """,
        Output('trigger-channel-dropdown', 'options'),
        Input('channel-dropdown', 'value'),
        State('channel-store', 'data')
    )

    # Update Oscilloscope Status
    app.clientside_callback(
        """
        function(runClicks, stopClicks, acquireClicks) {
            return window.dash_clientside.clientside.updateStatus(runClicks, stopClicks, acquireClicks);
        }
        """,
        Output('oscilloscope-status', 'children'),
        Input('run-btn', 'n_clicks'),
        Input('stop-btn', 'n_clicks'),
        Input('acquire-btn', 'n_clicks'),
        prevent_initial_call=True
    )

    # Show Trigger Delay Time
    app.clientside_callback(
        """
        function(decimation, delayValue) {
            return window.dash_clientside.clientside.showDelayTime(decimation, delayValue);
        }
        """,
        Output('delay-time-display', 'children'),
        Input('input-decimation', 'value'),
        Input('input-delay', 'value')
    )

    # Display Zoom Info
    app.clientside_callback(
        """
        function(relayoutData) {
            return window.dash_clientside.clientside.displayZoomInfo(relayoutData);
        }
        """,
        Output('zoom-info', 'children'),
        Input('scope-graph', 'relayoutData'),
        prevent_initial_call=True
    )