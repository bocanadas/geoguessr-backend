# GeoGuessr Backend

A simple Flask API for my GeoGuessr clone project. Returns random locations and scores guesses based on how close you are.

**Live API:** (add Render URL here when deployed)

---

## What It Does

Two main endpoints:
- **GET /random-location** - Gives you random coordinates from famous landmarks
- **POST /guess** - Calculates distance and score (0-5000 points)

Built with Flask, deployed on Render, frontend is on GitHub Pages.

---

## API Docs

### GET /random-location

Returns random coordinates with Street View coverage.

**Example:**
```bash
curl http://localhost:5001/random-location
```

**Response:**
```json
{
  "lat": 48.8584,
  "lng": 2.2945,
  "country": "France"
}
```

### POST /guess

Submit a guess and get your score.

**Request:**
```json
{
  "actual_lat": 48.8584,
  "actual_lng": 2.2945,
  "guess_lat": 48.8600,
  "guess_lng": 2.3000
}
```

**Response:**
```json
{
  "distance_km": 0.44,
  "score": 4999
}
```

**Example:**
```bash
curl -X POST http://localhost:5001/guess \
  -H "Content-Type: application/json" \
  -d '{"actual_lat": 48.8584, "actual_lng": 2.2945, "guess_lat": 48.8600, "guess_lng": 2.3000}'
```

---

## Running Locally

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   (On macOS you might need: `python3 -m pip install --break-system-packages -r requirements.txt`)

2. **Create .env file** with your Google Maps API key:
   ```
   GOOGLE_MAPS_API_KEY=your_key_here
   FLASK_ENV=development
   ```

3. **Run the server:**
   ```bash
   python3 app.py
   ```

4. **Test it:**
   Open test.html in your browser or hit the endpoints with curl

Server runs on http://localhost:5001 (using 5001 because macOS uses 5000 for AirPlay)

---

## Deploying to Render

1. Push code to GitHub
2. Go to render.com → New Web Service
3. Connect your repo
4. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
5. Add environment variable `GOOGLE_MAPS_API_KEY` in Render dashboard
6. Deploy

Once deployed, update CORS in app.py with your GitHub Pages URL and push again.

**Note:** Free tier sleeps after 15 min - first request takes ~30 seconds (cold start).

---

## How It Works

### Scoring

Uses exponential decay formula: `score = 5000 × e^(-distance / 2000)`

- 0 km = 5000 points (perfect)
- 100 km = ~3800 points
- 1000 km = ~1200 points
- 10000 km = ~37 points
- 20000+ km = 0 points

### CORS

Enabled with flask-cors so the frontend (GitHub Pages) can call the backend (Render). Without it, browsers block cross-origin requests.

### Frontend Integration

Example frontend code:
```javascript
// Get random location
const response = await fetch('https://your-backend.onrender.com/random-location');
const location = await response.json();

// Submit guess
const result = await fetch('https://your-backend.onrender.com/guess', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    actual_lat: location.lat,
    actual_lng: location.lng,
    guess_lat: guessLat,
    guess_lng: guessLng
  })
});
const score = await result.json();
```

---

## File Structure

```
geoguessr-backend/
├── app.py              # Main Flask app, routes, CORS
├── locations.py        # 15 pre-defined famous landmarks
├── scoring.py          # Distance calc (geopy) + scoring formula
├── requirements.txt    # Python dependencies
├── .env                # API key (don't commit this!)
├── .gitignore
├── README.md
└── test.html           # Quick test page
```

---

## Common Issues

**CORS errors?**
- Add your GitHub Pages URL to CORS origins in app.py

**Environment variables not working?**
- Locally: make sure .env file exists
- On Render: set in dashboard under Environment

**Cold starts on Render?**
- Free tier sleeps after inactivity - add loading message in frontend

**Port already in use?**
- macOS uses port 5000, that's why this uses 5001

---

## Tech Stack

- Flask 3.1.2
- geopy 2.4.1 (Haversine distance formula)
- flask-cors 6.0.2
- Gunicorn 25.1.0 (production server)
- Deployed on Render.com
