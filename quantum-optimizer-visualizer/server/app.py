from flask import Flask, request, jsonify
from flask_cors import CORS
from loop import run_workflow, fetch_stabilizer_matrix, convert_to_x_z_parts
import numpy as np
import traceback

from flask import send_from_directory
import os

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'favicon.ico', mimetype='image/vnd.microsoft.icon')

app = Flask(__name__)
CORS(app)

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.json
        print(data)
        n = data['n']
        k = data['k']
        d = data['d']
        # x_part = np.array(data['x_part'])
        # z_part = np.array(data['z_part'])
        matrix = fetch_stabilizer_matrix(n, k)
        initial_x_part, initial_z_part = convert_to_x_z_parts(matrix)
        result = run_workflow(initial_x_part, initial_z_part, n, k, d, num_iterations=25)
        print(result)
        return jsonify(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)