# Game High Scores Backend

A Flask-based backend service for managing game high scores with basic authentication and MySQL storage.

## Prerequisites

- Python 3.x
- MySQL Server

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup MySQL:
   - Create a new MySQL database:
   ```sql
   CREATE DATABASE highscores;
   ```
   - The application will automatically create the required table on startup

4. Configure environment:
   - Copy `.env` and configure your settings:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` and set:
     - `AUTH_PASSWORD`: Your desired API authentication password
     - `MYSQL_HOST`: Your MySQL host (default: localhost)
     - `MYSQL_USER`: Your MySQL username
     - `MYSQL_PASSWORD`: Your MySQL password
     - `MYSQL_DATABASE`: Your database name (default: highscores)

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### GET /scores
Returns all scores in CSV format, sorted by score (highest first).

### POST /scores
Submit a new score.

Request body (JSON):
```json
{
    "player": "ABC",  // 3 characters max
    "score": 1000
}
```

## Authentication

All endpoints require Basic Authentication:
- Username: game_client
- Password: (as set in .env file)

## Example Usage

Using curl:
```bash
# Get scores
curl -u game_client:your_secret_here http://localhost:5000/scores

# Submit score
curl -X POST -u game_client:your_secret_here \
     -H "Content-Type: application/json" \
     -d '{"player":"ABC","score":1000}' \
     http://localhost:5000/scores
``` 