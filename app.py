"""
GeoGuessr Backend API
Flask application with endpoints for random location retrieval and guess scoring.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import random
import hmac
import hashlib
import base64
from urllib.parse import urlparse, urlencode
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
    "http://127.0.0.1:5501",      # Live Server (VS Code)
    # Add your GitHub Pages URL here: "https://yourusername.github.io"
])

# Get API credentials from environment
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
GOOGLE_MAPS_SIGNING_SECRET = os.getenv('GOOGLE_MAPS_SIGNING_SECRET')

def sign_url(input_url, secret):
    """
    Sign a URL with a secret key using HMAC-SHA1.

    Args:
        input_url: Full URL including domain
        secret: Base64-encoded signing secret from Google Cloud Console

    Returns:
        Signed URL with &signature= parameter appended
    """
    # Decode the secret from base64 (Google provides it base64-encoded)
    decoded_secret = base64.urlsafe_b64decode(secret)

    # Parse the URL to get the path and query string
    url_obj = urlparse(input_url)
    url_to_sign = url_obj.path + "?" + url_obj.query

    # Create HMAC-SHA1 hash
    signature = hmac.new(decoded_secret, url_to_sign.encode('utf-8'), hashlib.sha1)

    # Encode the signature in base64 (URL-safe)
    encoded_signature = base64.urlsafe_b64encode(signature.digest()).decode('utf-8')

    # Remove any trailing = signs (URL-safe base64 doesn't use padding)
    encoded_signature = encoded_signature.replace('=', '')

    # Append signature to original URL
    return f"{input_url}&signature={encoded_signature}"

@app.route('/')
def home():
    """Root endpoint - API info"""
    return jsonify({
        "message": "GeoGuessr Backend API",
        "endpoints": {
            "GET /random-location": "Get random coordinates with Street View coverage",
            "POST /guess": "Submit guess and get distance/score",
            "GET /street-view-url": "Get signed Street View URL for coordinates (params: lat, lng)"
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


@app.route('/street-view-url', methods=['GET'])
def street_view_url():
    """
    Generate a signed Google Street View Static API URL.

    Query Parameters:
        lat: Latitude (-90 to 90)
        lng: Longitude (-180 to 180)

    Response:
        {
            "url": "https://maps.googleapis.com/maps/api/streetview?...&signature=..."
        }
    """
    try:
        # Get query parameters
        lat = request.args.get('lat')
        lng = request.args.get('lng')

        # Validate required fields
        if not lat or not lng:
            return jsonify({"error": "Missing required parameters: lat and lng"}), 400

        # Convert to floats and validate
        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            return jsonify({"error": "lat and lng must be numbers"}), 400

        # Validate coordinate ranges
        if not (-90 <= lat <= 90):
            return jsonify({"error": "Latitude must be between -90 and 90"}), 400
        if not (-180 <= lng <= 180):
            return jsonify({"error": "Longitude must be between -180 and 180"}), 400

        # Check if API key and signing secret are configured
        if not GOOGLE_MAPS_API_KEY:
            return jsonify({"error": "Server configuration error: API key not set"}), 500
        if not GOOGLE_MAPS_SIGNING_SECRET:
            return jsonify({"error": "Server configuration error: Signing secret not set"}), 500

        # Build the unsigned URL
        base_url = "https://maps.googleapis.com/maps/api/streetview"
        params = {
            "size": "800x600",
            "location": f"{lat},{lng}",
            "fov": "90",
            "heading": "0",
            "pitch": "0",
            "key": GOOGLE_MAPS_API_KEY
        }

        # Create query string
        query_string = urlencode(params)
        unsigned_url = f"{base_url}?{query_string}"

        # Sign the URL
        signed_url = sign_url(unsigned_url, GOOGLE_MAPS_SIGNING_SECRET)

        return jsonify({"url": signed_url})

    except Exception as e:
        return jsonify({"error": "Failed to generate signed URL"}), 500


if __name__ == '__main__':
    # Use PORT environment variable if available (for Render), otherwise default to 5001
    # Note: Port 5000 is often used by macOS Control Center (AirPlay)
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
