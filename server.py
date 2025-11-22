#!/usr/bin/env python3
"""
Simple Flask web server that serves SmokeData protobuf message
with dummy data via an API endpoint.
"""

from flask import Flask, Response, request
import json
import smokedata_pb2
from smoke_model import smoke

app = Flask(__name__)

@app.route('/smokedata', methods=['GET'])
def get_smokedata():
    """API endpoint that returns SmokeData message as protobuf"""
    # Dummy data matching the protobuf structure
    timestep = request.args.get('timestep')
    output = smoke(float(timestep))
    smokedata = smokedata_pb2.SmokeData()
    smokedata.t = float(timestep)
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
