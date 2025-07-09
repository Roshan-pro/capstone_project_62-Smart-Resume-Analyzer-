# # app.py

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# import tempfile
# from run_model  import analyze_resume  # make sure this file exists and is working

# # Initialize Flask App
# app = Flask(__name__)
# CORS(app)  # Allow frontend to access this backend

# # --- API Route ---
# @app.route("/analyze", methods=["POST"])
# def analyze_resume_api():
#     file = request.files.get("resume")

#     if file and file.filename.endswith(".pdf"):
#         try:
#             # Save uploaded file temporarily
#             temp_dir = tempfile.gettempdir()
#             temp_path = os.path.join(temp_dir, file.filename)
#             file.save(temp_path)

#             # Call ML pipeline function
#             result = analyze_resume(temp_path)

#             return jsonify(result)

#         except Exception as e:
#             return jsonify({"error": f"Processing failed: {str(e)}"}), 500
#     else:
#         return jsonify({"error": "Invalid file format. Only PDF allowed."}), 400

# # --- Main Runner ---
# if __name__ == "__main__":
#     app.run(debug=True, port=5000)


from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import tempfile
from run_model import analyze_resume

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_resume_api():
    file = request.files.get("resume")
    if file and file.filename.endswith(".pdf"):
        try:
            temp_path = os.path.join(tempfile.gettempdir(), file.filename)
            file.save(temp_path)
            result = analyze_resume(temp_path)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": f"Processing failed: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file format. Only PDF allowed."}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)