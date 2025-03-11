from flask import Flask, request, make_response
from functools import wraps
import os
from dotenv import load_dotenv
import csv
from io import StringIO
import json
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MySQL connection configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

def get_db_connection():
    """Create a database connection."""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Initialize the database and create the scores table if it doesn't exist."""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    idscores INT AUTO_INCREMENT PRIMARY KEY,
                    initials VARCHAR(3) NOT NULL,
                    score FLOAT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            """)
            connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")
        finally:
            cursor.close()
            connection.close()

# Initialize database on startup
init_db()

@app.route('/scores/<game>', methods=['GET'])
def get_scores(game):
    """Return all scores in plain text format: 'initials,score' per line."""
    connection = get_db_connection()
    if not connection:
        return {'error': 'Database connection failed'}, 500

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT initials, score, timestamp 
            FROM scores 
            WHERE game = %s
            ORDER BY score DESC
        """, (game,))
        
        # Build plain text response with one score per line
        output_lines = []
        for (initials, score, timestamp) in cursor:
            output_lines.append(f"{initials},{score}")
        
        response = make_response('\n'.join(output_lines))
        response.headers["Content-type"] = "text/plain"
        return response

    except Error as e:
        return {'error': f'Database error: {str(e)}'}, 500
    finally:
        cursor.close()
        connection.close()

@app.route('/scores/<game>', methods=['POST'])
def submit_score(game):
    """Submit a new score."""
    data = request.get_json()
    
    if not data or 'initials' not in data or 'score' not in data:
        return {'error': 'Missing initials or score data'}, 400
    
    # Validate player initials (assuming 3 characters max)
    if not isinstance(data['initials'], str) or len(data['initials']) > 3:
        return {'error': 'Initials must be 3 characters or less'}, 400
    
    # Validate score
    if not isinstance(data['score'], (int, float)) or data['score'] < 0:
        return {'error': 'Score must be a positive number'}, 400
    
    connection = get_db_connection()
    if not connection:
        return {'error': 'Database connection failed'}, 500

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO scores (initials, score, timestamp, game)
            VALUES (%s, %s, %s, %s)
        """, (
            data['initials'].upper(),
            data['score'],
            datetime.now(),
            game
        ))
        
        connection.commit()
        return {'message': 'Score submitted successfully'}, 201

    except Error as e:
        return {'error': f'Database error: {str(e)}'}, 500
    finally:
        cursor.close()
        connection.close()

@app.route("/health")
def index():
    return "ok", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5454)
