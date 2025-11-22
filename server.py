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

    smokedata = smokedata_pb2.SmokeData()
    smokedata.data.extend([ 0, 1, 2, 3, 4, 5])
    smokedata.width = 3
    smokedata.height = 2
    smokedata.t = float(timestep)
    smokedata.delta_x = 0.1
    smokedata.delta_y = 0.1
    smokedata.data.extend(smoke(float(timestep)))

    return Response(
        smokedata.SerializeToString(),
        mimetype='application/octet-stream'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
