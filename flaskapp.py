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

@app.route('/<game>', methods=['GET'])
def get_scores(game):
    """Return top 10 scores in plain text format: 'initials,score,color' per line."""
    connection = get_db_connection()
    if not connection:
        return {'error': 'Database connection failed'}, 500

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT initials, score, color, timestamp 
            FROM scores 
            WHERE game = %s
            ORDER BY score DESC
            LIMIT 100
        """, (game,))
        
        # Build plain text response with one score per line
        output_lines = []
        for (initials, score, color, timestamp) in cursor:
            output_lines.append(f"{initials},{score},{color}")
        
        response = make_response('\n'.join(output_lines))
        response.headers["Content-type"] = "text/plain"
        return response

    except Error as e:
        return {'error': f'Database error: {str(e)}'}, 500
    finally:
        cursor.close()
        connection.close()

@app.route('/<game>', methods=['POST'])
def submit_score(game):
    """Submit a new score in plain text format: 'INITIALS,SCORE,COLOR'."""
    try:
        # Get raw text data from request
        data = request.get_data(as_text=True).strip()
        
        # Get client IP address
        ip_addr = request.remote_addr
        
        # Split the input into initials, score, and optional color
        parts = data.split(',')
        if len(parts) < 2 or len(parts) > 3:
            return {'error': 'Invalid format. Expected: INITIALS,SCORE[,COLOR]'}, 400
            
        initials, score_str = parts[0], parts[1]
        color = int(parts[2], 16) if len(parts) == 3 else 0x808080  # Default color
        
        # Validate initials
        if not isinstance(initials, str) or len(initials) > 3:
            return {'error': 'Initials must be 3 characters or less'}, 400
            
        # Convert and validate score
        try:
            score = float(score_str)
            if score < 0:
                return {'error': 'Score must be a positive number'}, 400
        except ValueError:
            return {'error': 'Score must be a valid number'}, 400
        
        connection = get_db_connection()
        if not connection:
            return {'error': 'Database connection failed'}, 500

        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO scores (initials, score, color, timestamp, game, ip_addr)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                initials.upper(),
                score,
                color,
                datetime.now(),
                game,
                ip_addr
            ))
            
            connection.commit()
            return {'message': 'Score submitted successfully'}, 201

        except Error as e:
            return {'error': f'Database error: {str(e)}'}, 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        return {'error': f'Invalid request: {str(e)}'}, 400

@app.route("/health")
def index():
    return "ok", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5454)
