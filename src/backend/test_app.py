import os
import unittest
from io import BytesIO
from flask import current_app, jsonify
from flask_testing import TestCase
from flask_jwt_extended import create_access_token
from cryptography.fernet import Fernet
from app import create_app, db, User, bcrypt  # Add bcrypt import here

class FlaskTestCase(TestCase):
    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['UPLOAD_FOLDER'] = './test_uploads'
        app.config['WAV_UPLOAD_FOLDER'] = './test_wav_uploads'
        app.config['ENCRYPTION_KEY'] = Fernet.generate_key().decode()
        return app

    def setUp(self):
        db.create_all()
        self.client = self.app.test_client()
        # Create test directories if they don't exist
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['WAV_UPLOAD_FOLDER'], exist_ok=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        # Clean up test directories
        for folder in [self.app.config['UPLOAD_FOLDER'], self.app.config['WAV_UPLOAD_FOLDER']]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            os.rmdir(folder)

    def test_register(self):
        response = self.client.post('/register', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], 'User registered successfully')
        self.assertTrue('token' in data)

    def test_login(self):
        user = User(username='testuser', password=bcrypt.generate_password_hash('testpass').decode('utf-8'))
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue('token' in data)

    def test_get_user(self):
        user = User(username='testuser', password=bcrypt.generate_password_hash('testpass').decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity={'username': 'testuser'})

        response = self.client.get('/user', headers={
            'Authorization': f'Bearer {token}'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], 'testuser')

    def test_upload_file(self):
        user = User(username='testuser', password=bcrypt.generate_password_hash('testpass').decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity={'username': 'testuser'})

        # Use a valid webm file for testing
        with open('uploads/user_sam_motto.webm', 'rb') as f:
            data = {
                'file': (BytesIO(f.read()), 'test.webm')
            }

            response = self.client.post('/upload', content_type='multipart/form-data', headers={
                'Authorization': f'Bearer {token}'
            }, data=data)

        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
