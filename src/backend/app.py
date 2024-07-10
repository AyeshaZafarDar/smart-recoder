"""
Module to create a Flask application for the backend server.
"""

import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from cryptography.fernet import Fernet
from celery import Celery
from celery.result import AsyncResult
from models import db, User

# Load environment variables from .env file
load_dotenv()

bcrypt = Bcrypt()
jwt = JWTManager()
celery = Celery(
    __name__,
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND')
)

ALLOWED_EXTENSIONS = {'webm'}

# Initialize Flask application
def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
    app.config['WAV_UPLOAD_FOLDER'] = os.getenv('WAV_UPLOAD_FOLDER')
    app.config['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY')
    
    if app.config['ENCRYPTION_KEY'] is None:
        raise ValueError("Encryption key not found in environment variables.")

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    @app.before_request
    def check_app_version():
        '''
        Function to check the client application version
        '''
        app_version = request.headers.get("app-version")
        if app_version and app_version < "1.2.0":
            return jsonify({"message": "Please update your client application."}), 426

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        '''
        Function to return the status of the server
        '''
        return jsonify({'status': 200})

    @app.route('/register', methods=['POST'])
    def register():
        '''
        Function to register a new user
        '''
        if 'username' not in request.json or 'password' not in request.json:
            return jsonify({'message': 'Username and password are required'}), 400
        if User.query.filter_by(username=request.json['username']).first():
            return jsonify({'message': 'User already exists'}), 400

        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password=hashed_password, motto=None)
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity={'username': new_user.username})
        return jsonify({
            'message': 'User registered successfully',
            'token': access_token,
            'user': {
                'id': new_user.id,
                'username': new_user.username
            }
        }), 201

    @app.route('/login', methods=['POST'])
    def login():
        '''
        Function to login a user
        '''
        if 'username' not in request.json or 'password' not in request.json:
            return jsonify({'message': 'Username and password are required'}), 400
        if not User.query.filter_by(username=request.json['username']).first():
            return jsonify({'message': 'User does not exist'}), 401
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity={'username': user.username})
            return jsonify({'token': access_token}), 200
        return jsonify({'message': 'Invalid credentials'}), 401

    @app.route('/user', methods=['GET'])
    @jwt_required()
    def user():
        '''
        Function to get user details
        '''
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user['username']).first()
        decrypted_motto = None
        if user.motto:
            decrypted_motto = decrypt_message(user.motto.encode(), app.config['ENCRYPTION_KEY'])
        return jsonify({
            'id': user.id,
            'username': user.username,
            'motto': decrypted_motto
        }), 200

    def encrypt_message(message, key):
        '''
        Function to encrypt a message using Fernet encryption
        '''
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(message.encode())
        return cipher_text

    def decrypt_message(cipher_text, key):
        '''
        Function to decrypt a cipher text using Fernet encryption
        '''
        cipher_suite = Fernet(key)
        plain_text = cipher_suite.decrypt(cipher_text).decode()
        return plain_text

    def local_transcription_service(file_path):
        '''
        Function to transcribe an audio file using a local service
        '''
        # Mocked transcription service, returns a dummy result
        return "This is a dummy transcription result."

    @celery.task
    def process_file(username, file_path):
        '''
        Function to process an uploaded file
        '''
        transcript = local_transcription_service(file_path)
        encrypted_motto = encrypt_message(transcript, os.getenv('ENCRYPTION_KEY'))

        with create_app().app_context():
            user = User.query.filter_by(username=username).first()
            user.motto = encrypted_motto.decode()  # Store encrypted motto in the database
            db.session.commit()

    @app.route('/upload', methods=['POST'])
    @jwt_required()
    def upload_file():
        '''
        Function to upload a file and start transcription
        '''
        current_user = get_jwt_identity()
        username = current_user.get('username')

        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400

        filename_parts = file.filename.rsplit('.', 1)
        if len(filename_parts) < 2 or filename_parts[1].lower() not in ALLOWED_EXTENSIONS:
            return jsonify({"message": "Unsupported file type"}), 400

        filename = f"user_{username}_motto.{filename_parts[1].lower()}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        task = process_file.delay(username, file_path)
        return jsonify({"message": "File uploaded and transcription started",
                        "task_id": task.id}), 201

    @app.route('/task_status/<task_id>', methods=['GET'])
    def task_status(task_id):
        '''
        Function to get the status of a task
        '''
        task = AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'status': task.info.get('status', '')
            }
        else:
            response = {
                'state': task.state,
                'status': str(task.info)
            }
        return jsonify(response)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=3002, debug=True)
