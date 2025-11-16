from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import json
import os
from datetime import datetime
from services.ai_analyzer import analyze_text
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import uuid
from pathlib import Path
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# MongoDB Configuration
# MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
# client = pymongo.MongoClient(MONGODB_URI)
# db = client.complaintsdb  # Database name
# users_collection = db.users

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
COMPLAINTS_FILE = BASE_DIR / 'data' / 'complaints.json'
USERS_FILE = BASE_DIR / 'data' / 'users.json'


# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Initialize complaints file if it doesn't exist
if not COMPLAINTS_FILE.exists():
    with open(COMPLAINTS_FILE, 'w') as f:
        json.dump([], f, indent=2)

# Initialize users file if it doesn't exist
if not USERS_FILE.exists():
    with open(USERS_FILE, 'w') as f:
        json.dump([], f, indent=2)

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'})

# Load users from JSON file
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save users to JSON file
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    users = load_users()
    
    # Check if user already exists
    for user in users:
        if user['email'] == data['email']:
            return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(data['password'])

    new_user = {
        'id': str(uuid.uuid4()),
        'email': data['email'],
        'password': hashed_password,
        'name': data.get('name', ''),
        'role': data.get('role', 'student'),
        'createdAt': datetime.utcnow().isoformat()
    }

    users.append(new_user)
    save_users(users)

    return jsonify({'message': 'User registered successfully', 'user': {'id': new_user['id'], 'email': new_user['email'], 'name': new_user['name'], 'role': new_user['role']}}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    users = load_users()
    user = next((user for user in users if user['email'] == data['email']), None)

    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode({
        'email': user['email'],
        'exp': datetime.utcnow() + timedelta(days=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
    }), 200

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401
    
    # Remove 'Bearer ' prefix if present
    if token.startswith('Bearer '):
        token = token[7:]
    
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        users = load_users()
        user = next((user for user in users if user['email'] == decoded['email']), None)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


@app.route('/api/complaints', methods=['POST'])
def create_complaint():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('description') or not data.get('contactInfo'):
        return jsonify({'error': 'Title, description, and contactInfo are required'}), 400

    complaints = []
    try:
        with open(COMPLAINTS_FILE, 'r') as f:
            complaints = json.load(f)
    except FileNotFoundError:
        pass  # Handle case where file doesn't exist yet

    # Use AI to analyze the complaint
    try:
        # Combine title and description for better analysis
        full_text = f"{data['title']}. {data['description']}"
        ai_analysis = analyze_text(full_text)
        
        category = ai_analysis.get('category', 'General')
        priority = ai_analysis.get('priority', 'Medium')
        department = ai_analysis.get('assignedDepartment', '')
        complaint_type = ai_analysis.get('type', 'General')
        confidence = ai_analysis.get('confidence', 0)
        
    except Exception as e:
        # Fallback to default values if AI analysis fails
        print(f"AI Analysis failed: {e}")
        category = data.get('category', 'General')
        priority = data.get('priority', 'Medium')
        department = data.get('department', '')
        complaint_type = 'General'
        confidence = 0

    new_complaint = {
        'id': str(uuid.uuid4()),
        'title': data['title'],
        'description': data['description'],
        'contactInfo': data['contactInfo'],
        'category': category,
        'department': department,
        'priority': priority,
        'userType': data.get('userType', 'Student'),
        'domain': data.get('domain', 'default'),
        'status': 'pending',
        'createdAt': datetime.utcnow().isoformat(),
        'aiAnalysis': {
            'type': complaint_type,
            'confidence': confidence,
            'analyzedAt': datetime.utcnow().isoformat()
        }
    }

    complaints.append(new_complaint)

    with open(COMPLAINTS_FILE, 'w') as f:
        json.dump(complaints, f, indent=2)

    return jsonify({'message': 'Complaint submitted successfully', 'id': new_complaint['id']}), 201

@app.route('/api/complaints', methods=['GET'])
def get_complaints():
    try:
        with open(COMPLAINTS_FILE, 'r') as f:
            complaints = json.load(f)
        return jsonify({'success': True, 'data': complaints}), 200
    except FileNotFoundError:
        return jsonify({'success': False, 'data': []}), 200

@app.route('/api/complaints/<id>', methods=['DELETE'])
def delete_complaint(id):
    try:
        with open(COMPLAINTS_FILE, 'r') as f:
            complaints = json.load(f)
        
        # Find and remove the complaint with the given ID
        original_length = len(complaints)
        complaints = [c for c in complaints if c.get('id') != id]
        
        if len(complaints) == original_length:
            return jsonify({'error': 'Complaint not found'}), 404
        
        # Save the updated complaints list
        with open(COMPLAINTS_FILE, 'w') as f:
            json.dump(complaints, f, indent=2)
        
        return jsonify({'message': 'Complaint deleted successfully'}), 200
    except FileNotFoundError:
        return jsonify({'error': 'Complaints file not found'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        with open(COMPLAINTS_FILE, 'r') as f:
            complaints = json.load(f)

        total_complaints = len(complaints)
        resolved_count = sum(1 for c in complaints if c['status'] == 'resolved')
        pending_count = sum(1 for c in complaints if c['status'] == 'pending')

        category_distribution = {}
        for c in complaints:
            category = c.get('category', 'Other')
            if category in category_distribution:
                category_distribution[category] += 1
            else:
                category_distribution[category] = 1

        analytics_data = {
            'total_complaints': total_complaints,
            'resolved_count': resolved_count,
            'pending_count': pending_count,
            'category_distribution': category_distribution
        }
        return jsonify(analytics_data), 200
    except FileNotFoundError:
        return jsonify({'error': 'Complaints file not found'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
