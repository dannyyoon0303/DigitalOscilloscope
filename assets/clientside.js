window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {

        displayIntervalCount: function(n_intervals) {
            return `Interval count: ${n_intervals}`;
        },

        updateSliderProps: function(decimation, factor) {
            const total_time_ms = (decimation / 125000000) * 16384 * factor * 1000;

            const left_label = `${(0).toFixed(2)} ms`;
            const right_label = `${(total_time_ms).toFixed(2)} ms`;
            const min = -8192 * factor;
            const max = 8192 * factor;

            const marks = {};
            marks[min] = left_label;
            marks[max] = right_label;

           
            return [marks, min, max];
        },

        addChannel: function(n_clicks, channel_text, store) {
            if (!channel_text || !channel_text.includes(":")) {
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }

            const parts = channel_text.split(":");
            const key = parts[0].trim();
            const label = parts[1].trim();
            store[key] = label;

            const options = Object.entries(store).map(([k, v]) => ({
                label: `${k}: ${v}`,
                value: k
            }));

            return [options, store];
        },

        updateTriggerChannelDropdown: function(selected_channels, channel_map) {
            if (!selected_channels || selected_channels.length === 0) {
                return [];
            }

            return selected_channels.map(ch => ({
                label: `${ch}: ${channel_map[ch] || ch}`,
                value: ch
            }));
        },

        updateStatus: function(runClicks, stopClicks, acquireClicks) {
            const ctx = dash_clientside.callback_context;
            if (!ctx.triggered.length) return "Status: Stopped";

            const id = ctx.triggered[0].prop_id.split('.')[0];
            return id === 'run-btn' ? "Status: Running..." : "Status: Stopped";
        },

        showDelayTime: function(decimation, delayValue) {
            const fs = 125000000 / decimation;
            const dt = 1 / fs;
            const delayTime = (8192 + delayValue) * dt * 1000;
            return `Current Trigger Delay: ${delayTime.toFixed(4)}ms`;
        },

        displayZoomInfo: function(relayoutData) {
            if (!relayoutData) return "Zoom to view details.";
            const xmin = relayoutData['xaxis.range[0]'];
            const xmax = relayoutData['xaxis.range[1]'];
            const ymin = relayoutData['yaxis.range[0]'];
            const ymax = relayoutData['yaxis.range[1]'];

            if ([xmin, xmax, ymin, ymax].some(v => v === undefined)) {
                return "Zoom box not detected.";
            }

            const xRange = xmax - xmin;
            const yRange = ymax - ymin;

            return `Zoomed window: Δt = ${xRange.toFixed(4)} ms, ΔV = ${yRange.toFixed(4)} V`;
        }
    }
});
