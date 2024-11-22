import sqlite3
print(sqlite3.sqlite_version)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, action TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# Log actions
def log_action(action):
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs (action, timestamp) VALUES (?, datetime('now'))", (action,))
    conn.commit()
    conn.close()

# Add logging to secure deletion
def secure_delete(file_path):
    if os.path.exists(file_path):
        with open(file_path, "ba+", buffering=0) as f:
            length = os.path.getsize(file_path)
            f.write(b'\x00' * length)
        os.remove(file_path)
        log_action(f"Deleted file: {file_path}")
        return {"status": "success", "message": f"{file_path} deleted securely"}
    else:
        return {"status": "failure", "message": "File not found"}
    
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Function to scan for files
def map_footprints(directory):
    data = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            data.append({
                "file_name": file,
                "file_path": file_path,
                "size": os.path.getsize(file_path)
            })
    return data

# API Endpoint to map files
@app.route('/map', methods=['GET'])
def map_data():
    directory = request.args.get('directory', './')  # Default to the current directory
    footprints = map_footprints(directory)
    return jsonify({"footprints": footprints})

# Secure deletion function
def secure_delete(file_path):
    if os.path.exists(file_path):
        # Overwrite file with zeros
        with open(file_path, "ba+", buffering=0) as f:
            length = os.path.getsize(file_path)
            f.write(b'\x00' * length)
        os.remove(file_path)
        return {"status": "success", "message": f"{file_path} deleted securely"}
    else:
        return {"status": "failure", "message": "File not found"}

# API Endpoint for secure deletion
@app.route('/delete', methods=['POST'])
def delete_file():
    file_path = request.json.get('file_path')
    return jsonify(secure_delete(file_path))