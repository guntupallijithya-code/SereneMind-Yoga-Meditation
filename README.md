# SereneMind – Yoga & Meditation

SereneMind is a yoga and meditation application designed to help users relax and practice mindfulness through guided sessions and AI-generated audio.

## Features

- Generate personalized yoga and meditation sessions.
- Use Google Gemini to generate session content.
- Use Murf AI text-to-speech to create guided audio.
- Support multiple languages, depending on configured voices.
- Simple web interface built with HTML, CSS, and JavaScript.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **AI-generated content:** Google Gemini API
- **Text-to-speech:** Murf AI API

## Project Structure

```text
SereneMind_Yoga_Meditation/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.10 or a compatible version
- A Google Gemini API key
- A Murf API key
- Git (optional)

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/guntupallijithya-code/SereneMind-Yoga-Meditation.git
cd SereneMind-Yoga-Meditation
```

### 2. Install dependencies

Open a terminal in the project folder and run:

```bash
pip install -r backend/requirements.txt
```

### 3. Configure environment variables

Set your API keys as environment variables. For example, in PowerShell:

```powershell
$env:GEMINI_API_KEY = "your_gemini_api_key"
$env:MURF_API_KEY = "your_murf_api_key"
$env:GEMINI_MODEL = "gemini-3.8-flash"
$env:MURF_VOICE_ENGLISH = "Natalie"
```

Replace the placeholder API key values with your own keys. Never commit API keys to GitHub.

### 4. Start the application

Run the Flask backend:

```powershell
cd backend
python app.py
```

Open the local application at:

http://127.0.0.1:5001/

## Security

- Keep API keys private.
- Do not upload `.env` files or secret credentials.
- Store production credentials in your hosting provider's environment-variable settings.

## Project Status

This project is under development. Some features may require additional configuration or testing.

## Author

Jithya Guntupalli
