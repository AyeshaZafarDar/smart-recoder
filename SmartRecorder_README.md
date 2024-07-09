### smart_recorder

#### Description
Smart Recorder is a full-stack application that combines Flask for the backend API and React for the frontend. It allows users to record audio snippets, transcribe them, and securely store and display the transcriptions. This project aims to demonstrate integration of authentication, version management, audio recording, encryption, and asynchronous processing.

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
     ENCRYPTION_KEY='YOUR_KEY'
     UPLOAD_FOLDER='uploads'
     WAV_UPLOAD_FOLDER='wav_uploads'
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

#### Contributions

- Contributions are welcome! Please fork this repository and submit your pull requests.