from flask import Flask
from flask_cors import CORS
import os
from app.routes import create_routes

# Initialize Flask app
app = Flask(__name__, template_folder="app/templates")
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configure upload folder
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Register routes
create_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
