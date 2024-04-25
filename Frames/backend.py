from flask import Flask, request, jsonify, send_file, render_template
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('frontend.html')  # Serve the frontend HTML

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        try:
            # Retrieve files and parameter
            front_lens = request.files['frontLens']
            top_lens = request.files['topLens']
            bridge_length = request.form['bridgeLength']

            # Generate unique IDs for the session or use the timestamp
            unique_id = uuid.uuid4().hex
            uploads_dir = 'uploads'
            outputs_dir = 'outputs'
            front_lens_filename = f"{unique_id}_front.dxf"
            top_lens_filename = f"{unique_id}_top.dxf"
            front_lens_path = os.path.join(uploads_dir, front_lens_filename).replace('\\', '/')
            top_lens_path = os.path.join(uploads_dir, top_lens_filename).replace('\\', '/')
            output_stl_path = os.path.join(outputs_dir, f"{unique_id}_frame.stl").replace('\\', '/')

            # Ensure uploads and outputs directories exist
            os.makedirs(uploads_dir, exist_ok=True)
            os.makedirs(outputs_dir, exist_ok=True)

            # Save files
            front_lens.save(front_lens_path)
            top_lens.save(top_lens_path)

            # Verify file existence before executing OpenSCAD
            if not os.path.isfile(front_lens_path) or not os.path.isfile(top_lens_path):
                return jsonify({"error": "DXF file not found"}), 404

            # OpenSCAD executable path
            openscad_path = r"C:\Program Files\OpenSCAD\openscad.exe"

            # Construct the OpenSCAD command
            command = [
                openscad_path,                                  # OpenSCAD executable
                "-o", os.path.abspath(output_stl_path),         # Output file format STL
                "-D", f'front_view="{front_lens_path}"',        # Inject front view DXF path
                "-D", f'top_view="{top_lens_path}"',           # Inject top view DXF path
                "-D", f'bridge_length={bridge_length}',         # Inject bridge length
                "Frame.scad"                                    # OpenSCAD script
            ]

            # Log command for debugging
            print("OpenSCAD command:", ' '.join(command))

            # Run OpenSCAD command
            subprocess.run(command, check=True)

            # Send the generated STL file back to the client
            return send_file(os.path.abspath(output_stl_path), as_attachment=True)
        except Exception as e:
            # If any error occurs, return the error message
            return jsonify({"error": str(e)}), 500

    # If no files were uploaded
    return jsonify({"error": "No files uploaded"}), 400

if __name__ == '__main__':
    app.run(debug=True)
