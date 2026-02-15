# Where in the World? (Backend)

This is the Flask backend service for "Where in the World?", a GeoGuessr clone geography game. It handles game logic, score calculation, and securely interacts with the Google Maps Platform.

**Live Deployment:** https://geoguessr-backend-inwf.onrender.com
**Frontend Repository:** https://github.com/bocanadas/geoguessr-frontend

## Core Functionality & Endpoints

The backend exposes a REST API to manage game state and secure API usage.

### 1. Get Random Location
**Endpoint:** `GET /random-location`
* **Function:** Selects a random target from a list of locations with verified Street View coverage.
* **Response:**
    ```json
    {
      "lat": 48.8584,
      "lng": 2.2945,
      "country": "France"
    }
    ```

### 2. Submit Guess & Score
**Endpoint:** `POST /guess`
* **Function:** Calculates the Haversine distance between the user's guess and the actual location. It returns a score (0-5000) based on an exponential decay formula.
* **Request Body:**
    ```json
    {
      "actual_lat": 48.8584,
      "actual_lng": 2.2945,
      "guess_lat": 48.8600,
      "guess_lng": 2.3000
    }
    ```
* **Response:**
    ```json
    {
      "distance_km": 0.44,
      "score": 4999
    }
    ```

### 3. Generate Signed Street View URL
**Endpoint:** `GET /street-view-url`
* **Function:** Generates a signed URL for the Google Street View Static API.
* **Parameters:** `lat` (float), `lng` (float)
* **Why this is necessary:** Google requires requests to be signed with a secret key to prevent quota theft. This endpoint constructs the signature on the server so the secret is never exposed to the client.

## Frontend-Backend Communication

The frontend communicates with this backend via `fetch` requests.

1.  **Game Start:** The frontend calls `GET /random-location` to receive the target coordinates.
2.  **Image Loading:** The frontend immediately calls `GET /street-view-url` with those coordinates. The backend returns a signed URL, which the frontend sets as the `src` for the image tag.
3.  **Scoring:** When the user clicks "Submit", the frontend sends both coordinates to `POST /guess`. The backend performs the math and returns the final score for display.

## Security & Secret Management

* **Environment Variables:** All API credentials are stored as environment variables on the Render server.
* **CORS:** Cross-Origin Resource Sharing is configured to strictly allow requests only from the deployed frontend and local environments.

## Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/bocanadas/geoguessr-backend.git
    cd geoguessr-backend
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    Create a `.env` file in the root directory:
    ```text
    GOOGLE_MAPS_API_KEY=your_api_key
    GOOGLE_MAPS_SIGNING_SECRET=your_signing_secret
    ```

4.  **Run the server:**
    ```bash
    python3 app.py
    ```
    The server will start on `http://0.0.0.0:5001`.