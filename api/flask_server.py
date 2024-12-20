import io
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_file
from flask_socketio import SocketIO

from data_logger import DataLogger
from visualization import SensorVisualizer

app = Flask(__name__)
socketio = SocketIO(app)
latest_data = {}
visualizer = SensorVisualizer(max_points=50)  # Store last 50 points
data_logger = DataLogger()


# Serve static files from 'static' directory
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/sensor-data', methods=['POST'])
def update_sensor_data():
    global latest_data
    latest_data = request.json
    data_logger.log_data(latest_data)  # Log the data
    visualizer.add_datapoint(latest_data)
    latest_data['plot'] = visualizer.generate_plot()
    socketio.emit('sensor_update', latest_data)
    return jsonify({"status": "success"})


@app.route('/api/current-data', methods=['GET'])
def get_current_data():
    return jsonify(latest_data)


@app.route('/api/voltage', methods=['GET'])
def get_voltage():
    if not latest_data:
        return jsonify({"error": "No data available yet"}), 404
    return jsonify({
        "voltage": latest_data.get('voltage'),
        "timestamp": latest_data.get('timestamp'),
        "raw": latest_data.get('raw')
    })


@app.route('/api/historical', methods=['GET'])
def get_historical_data():
    """
    Handle historical data requests.
    
    Query parameters:
        start (timestamp): Start time for data range
        end (timestamp): End time for data range
        format (str): Optional 'plot' for graph or 'json' for raw data
        download (bool): Optional flag to force download
    
    :return: JSON data or PNG image
    """
    start = datetime.fromtimestamp(float(request.args.get('start', 0)))
    end = datetime.fromtimestamp(float(request.args.get('end', datetime.now().timestamp())))
    data = data_logger.get_data_range(start, end)

    # Handle plot generation and download
    if request.args.get('format') == 'plot':
        temp_viz = SensorVisualizer(max_points=len(data))
        for entry in data:
            temp_viz.add_datapoint(entry)

        # Create plot buffer
        buffer = io.BytesIO()
        temp_viz.save_plot(buffer)  # New method to save plot
        buffer.seek(0)

        # Force download if requested
        if request.args.get('download'):
            filename = f"moisture_plot_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.png"
            return send_file(
                buffer,
                mimetype='image/png',
                as_attachment=True,
                download_name=filename
            )

        # Return base64 for display
        return jsonify({"plot": temp_viz.generate_plot()})

    return jsonify(data)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8765, debug=True)
