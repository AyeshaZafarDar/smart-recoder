import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from cryptography.fernet import Fernet
import speech_recognition as sr
from pydub import AudioSegment
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

ALLOWED_EXTENSIONS = {'webm'}

# Initialize Flask application
def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SECRET_KEY'] = 'secret123'
    app.config['JWT_SECRET_KEY'] = 'secret1234'
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
    app.config['WAV_UPLOAD_FOLDER'] = os.getenv('WAV_UPLOAD_FOLDER')

    # Load encryption key from environment variable
    app.config['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY')

    if app.config['ENCRYPTION_KEY'] is None:
        raise ValueError("Encryption key not found in environment variables.")

    CORS(app, resources={r"/*": {"origins": "*"}} )
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    executor = ThreadPoolExecutor()

    @app.before_request
    def check_app_version():
        app_version = request.headers.get("app-version")
        if app_version and app_version < "1.2.0":
            return jsonify({"message": "Please update your client application."}), 426

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return jsonify({'status': 200})

    @app.route('/register', methods=['POST'])
    def register():
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
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(message.encode())
        return cipher_text

    def decrypt_message(cipher_text, key):
        cipher_suite = Fernet(key)
        plain_text = cipher_suite.decrypt(cipher_text).decode()
        return plain_text

    def local_transcription_service(file_path):
        # Simulate asynchronous processing with random time delay (5-15 seconds)
        async def transcribe_audio():
            await asyncio.sleep(random.randint(5, 15))
            audio = AudioSegment.from_file(file_path)
            wav_file_path = os.path.join(app.config['WAV_UPLOAD_FOLDER'], os.path.basename(file_path).replace('.webm', '.wav'))
            audio.export(wav_file_path, format="wav")

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_file_path) as source:
                try:
                    audio_data = recognizer.record(source)
                    transcript = recognizer.recognize_google(audio_data)
                    return transcript
                except sr.UnknownValueError:
                    return "Unable to transcribe audio: Unknown Value Error"
                except sr.RequestError:
                    return "Unable to transcribe audio: Request Error (check your network connection)"
                except Exception as e:
                    return f"Error during transcription: {str(e)}"

        # Run the transcription asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(transcribe_audio())

    @app.route('/upload', methods=['POST'])
    @jwt_required()
    def upload_file():
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

        transcript = local_transcription_service(file_path)
        encrypted_motto = encrypt_message(transcript, app.config['ENCRYPTION_KEY'])
        
        user = User.query.filter_by(username=username).first()
        user.motto = encrypted_motto.decode()  # Store encrypted motto in the database
        db.session.commit()

        return jsonify({"message": "File uploaded and motto updated successfully"}), 200

    return app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    motto = db.Column(db.String(255), nullable=True)  # Updated to store encrypted motto

if __name__ == '__main__':
    app = create_app()
    app.run(port=3002, debug=True)
