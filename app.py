"""
GeoGuessr Backend API
Flask application with endpoints for random location retrieval and guess scoring.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import random
from dotenv import load_dotenv
from locations import LOCATIONS
from scoring import calculate_distance, calculate_score

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend access
# Replace with your actual GitHub Pages URL when you deploy frontend
CORS(app, origins=[
    "http://localhost:3000",      # Local frontend testing
    "http://localhost:5500",      # Live Server (VS Code)
    "http://127.0.0.1:3000",      # Alternative local
    "http://127.0.0.1:5500",      # Alternative local
    # Add your GitHub Pages URL here: "https://yourusername.github.io"
])

# Get API key from environment (not used yet, but will be for frontend)
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

@app.route('/')
def home():
    """Root endpoint - API info"""
    return jsonify({
        "message": "GeoGuessr Backend API",
        "endpoints": {
            "GET /random-location": "Get random coordinates with Street View coverage",
            "POST /guess": "Submit guess and get distance/score"
        }
    })

@app.route('/random-location', methods=['GET'])
def random_location():
    """
    Returns a random location from the pre-defined list.

    Response:
        {
            "lat": float,
            "lng": float,
            "country": string
        }
    """
    location = random.choice(LOCATIONS)
    return jsonify({
        "lat": location["lat"],
        "lng": location["lng"],
        "country": location.get("country", "Unknown")
    })


@app.route('/guess', methods=['POST'])
def guess():
    """
    Calculate distance and score between player's guess and actual location.

    Request Body:
        {
            "actual_lat": float,
            "actual_lng": float,
            "guess_lat": float,
            "guess_lng": float
        }

    Response:
        {
            "distance_km": float,
            "score": int
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['actual_lat', 'actual_lng', 'guess_lat', 'guess_lng']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing: {field}"}), 400

        # Convert to floats and validate
        try:
            actual_lat = float(data['actual_lat'])
            actual_lng = float(data['actual_lng'])
            guess_lat = float(data['guess_lat'])
            guess_lng = float(data['guess_lng'])
        except (ValueError, TypeError):
            return jsonify({"error": "Coordinates must be numbers"}), 400

        # Validate coordinate ranges
        if not (-90 <= actual_lat <= 90) or not (-90 <= guess_lat <= 90):
            return jsonify({"error": "Latitude must be -90 to 90"}), 400
        if not (-180 <= actual_lng <= 180) or not (-180 <= guess_lng <= 180):
            return jsonify({"error": "Longitude must be -180 to 180"}), 400

        # Calculate distance and score
        distance_km = calculate_distance(actual_lat, actual_lng, guess_lat, guess_lng)
        score = calculate_score(distance_km)

        return jsonify({
            "distance_km": round(distance_km, 2),
            "score": score
        })

    except (ValueError, TypeError):
        return jsonify({"error": "Coordinates must be numbers"}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Use PORT environment variable if available (for Render), otherwise default to 5001
    # Note: Port 5000 is often used by macOS Control Center (AirPlay)
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
