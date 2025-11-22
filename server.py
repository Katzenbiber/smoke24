#!/usr/bin/env python3
"""
Simple Flask web server that serves SmokeData protobuf message
with dummy data via an API endpoint.
"""
from flask import Flask, Response, request, send_from_directory
import smokedata_pb2
from smoke_model import smoke

app = Flask(__name__)

# Enable CORS for all routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'frontend/index.html')

@app.route('/style.css')
def style():
    return send_from_directory('.', 'frontend/style.css')

@app.route('/script.js')
def script():
    return send_from_directory('.', 'frontend/script.js')

@app.route('/modules/smokedata_pb2.js')
def smokedata():
    return send_from_directory('.', 'frontend/modules/smokedata_pb2.js')

@app.route('/smokedata', methods=['GET'])
def get_smokedata():
    """API endpoint that returns SmokeData message as protobuf"""
    # Default timestep if not provided
    timestep = request.args.get('timestep', '0.5')
    
    # Ensure timestep is a valid number
    try:
        timestep_float = float(timestep)
    except ValueError:
        timestep_float = 0.5  # Default fallback
    
    output = smoke(timestep_float)
    smokedata = smokedata_pb2.SmokeData()
    smokedata.t = timestep_float
    smokedata.width = output["Nx"]
    smokedata.height = output["Ny"]
    smokedata.delta_x = output["dx"]
    smokedata.delta_y = output["dy"]
    smokedata.data.extend(output["data"])

    return Response(
        smokedata.SerializeToString(),
        mimetype='application/octet-stream'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
