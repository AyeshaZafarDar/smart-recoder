# smart recorder

#### Description

Smart Recorder is a full-stack application that combines Flask for the backend API and React for the frontend. It allows users to record audio snippets, transcribe them, and securely store and display the transcriptions. This project aims to demonstrate integration of authentication, version management, audio recording, encryption, and asynchronous processing.

#### Technologies Used

- **Backend:**

  - Flask: Python-based micro web framework for building APIs.
  - SQLAlchemy: Python SQL toolkit and Object-Relational Mapping (ORM) library.
  - Celery: Asynchronous task queue/job queue based on distributed message passing.
  - Flask-JWT-Extended: Flask extension that adds support for JSON Web Tokens (JWT) authentication.
  - Flask-CORS: Flask extension for handling Cross-Origin Resource Sharing (CORS).
  - Bcrypt: Library for hashing passwords.

- **Frontend:**

  - React: JavaScript library for building user interfaces.
  - TypeScript: Strict syntactical superset of JavaScript adding types to the language.
  - TailwindCSS: Utility-first CSS framework for styling components.
  - Axios: Promise-based HTTP client for making API requests.

- **Database:**
  - SQLite: Lightweight SQL database engine used for development.
  - (Optional) PostgreSQL, MySQL, etc., for production deployments.

#### Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd smart_recorder
   ```

2. **Backend Setup:**

   - Navigate to the backend directory:

     ```bash
     cd src/backend
     ```

   - Create a virtual environment (optional but recommended):

     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```

   - Install dependencies:

     ```bash
     pip install -r requirements.txt
     ```

   - Set up environment variables:
     Create a `.env` file in the `src/backend` directory with the following content:

     ```
      UPLOAD_FOLDER=
      WAV_UPLOAD_FOLDER=
      CELERY_BROKER_URL=
      CELERY_RESULT_BACKEND=
      SQLALCHEMY_DATABASE_URI=
      JWT_SECRET_KEY=
      SECRET_KEY=
     ```

     Replace the values with your own configurations.

   - Create folders for audio and wav uploads:

     ```bash
     mkdir uploads
     mkdir wav_uploads
     ```

   - Run the Flask application:
     ```bash
     python app.py
     ```
     The backend will run on `http://localhost:3002/`.

3. **Frontend Setup:**

   - Navigate to the frontend directory:

     ```bash
     cd src/frontend
     ```

   - Install dependencies:

     ```bash
     npm install
     ```

   - Start the React development server:
     ```bash
     npm start
     ```
     The frontend will run on `http://localhost:5173/`.

#### Directory Structure

```
smart_recorder/
│
├── src/
│   ├── backend/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── .env
│   │   ├── instance/
│   │   │   └── site.db
│   │   ├── uploads/
│   │   ├── wav_uploads/
│   │   └── venv/
│   │
│   └── frontend/
│       ├── public/
│       ├── src/
│       │   ├── components/
│       │   │   ├── AudioRecorder.tsx
│       │   │   ├── Home.tsx
│       │   │   ├── Login.tsx
│       │   │   ├── Profile.tsx
│       │   │   └── Register.tsx
│       │   ├── config/
│       │   │   └── config.ts
│       │   ├── services/
│       │   │   └── APIService.ts
│       │   └── App.tsx
│       ├── .env
│       ├── package.json
│       ├── package-lock.json
│       └── README.md
│
├── .gitignore
└── README.md
```

#### Contributions

```
- Contributions are welcome! Please fork this repository and submit your pull requests.
```
