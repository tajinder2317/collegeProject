import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime, timedelta
import jwt

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Mock data storage
complaints = []
users = []
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    for user in users:
        if user['email'] == data['email']:
            return jsonify({'error': 'User already exists'}), 400
    
    new_user = {
        'id': str(uuid.uuid4()),
        'email': data['email'],
        'password': data['password'],
        'created_at': datetime.now().isoformat()
    }
    users.append(new_user)
    
    return jsonify({'message': 'User registered successfully', 'user_id': new_user['id']}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = None
    for u in users:
        if u['email'] == data['email'] and u['password'] == data['password']:
            user = u
            break
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'user_id': user['id'],
        'email': user['email'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, JWT_SECRET, algorithm='HS256')
    
    return jsonify({'token': token, 'user': {'id': user['id'], 'email': user['email']}})

@app.route('/api/complaints', methods=['GET'])
def get_complaints():
    return jsonify({'complaints': complaints})

@app.route('/api/complaints', methods=['POST'])
def create_complaint():
    data = request.get_json()
    if not data or not data.get('text'):
        return jsonify({'error': 'Complaint text required'}), 400
    
    new_complaint = {
        'id': str(uuid.uuid4()),
        'text': data['text'],
        'category': data.get('category', 'General'),
        'severity': data.get('severity', 'Medium'),
        'status': 'Open',
        'created_at': datetime.now().isoformat()
    }
    complaints.append(new_complaint)
    
    return jsonify({'complaint': new_complaint}), 201

@app.route('/api/analyze', methods=['POST'])
def analyze_complaint():
    data = request.get_json()
    if not data or not data.get('text'):
        return jsonify({'error': 'Text to analyze required'}), 400
    
    text = data['text']
    
    # Simple mock analysis
    analysis = {
        'sentiment': 'negative' if len(text) > 50 else 'neutral',
        'category': 'General',
        'severity': 'Medium',
        'keywords': text.split()[:5],
        'confidence': 0.75
    }
    
    return jsonify({'analysis': analysis})

def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        query_params = event.get('queryStringParameters', {}) or {}
        body = event.get('body', '')
        
        with app.test_client() as client:
            response = client.open(
                path=path,
                method=method,
                headers=headers,
                query_string=query_params,
                data=body,
                content_type=headers.get('content-type', 'application/json')
            )
            
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
