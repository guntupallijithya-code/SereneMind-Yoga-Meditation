import os
import base64
import logging

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from google import genai

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Replace these sample values with valid voice IDs from your Murf account.
# Set them as environment variables rather than hard-coding API keys.
VOICE_IDS = {
    "English": os.getenv("MURF_VOICE_ENGLISH", "YOUR_ENGLISH_MURF_VOICE_ID"),
    "Hindi": os.getenv("MURF_VOICE_HINDI", "YOUR_HINDI_MURF_VOICE_ID"),
    "Telugu": os.getenv("MURF_VOICE_TELUGU", "YOUR_TELUGU_MURF_VOICE_ID"),
    "Tamil": os.getenv("MURF_VOICE_TAMIL", "YOUR_TAMIL_MURF_VOICE_ID"),
}
LOCALES = {
    "English": "en-US",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
    "Tamil": "ta-IN",
}

SESSION_TYPES = {"Meditation", "Yoga", "Breathing"}
DURATIONS = {"3 minutes": 3, "5 minutes": 5, "10 minutes": 10}
LEVELS = {"Beginner", "Gentle", "Intermediate"}


@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def frontend_files(filename):
    # Serves CSS and JavaScript from the frontend folder.
    return send_from_directory(FRONTEND_DIR, filename)


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "SereneMind backend is running",
        "gemini_configured": bool(GEMINI_API_KEY),
        "murf_configured": bool(MURF_API_KEY),
    })


def build_prompt(session_type, focus, duration, language, level):
    safety_note = (
        "This is general wellness guidance, not medical advice. "
        "Avoid promising cures or diagnosing conditions. "
        "Use gentle, accessible instructions. Tell the listener to stop if they feel pain, "
        "dizziness, breathlessness, or discomfort. Do not recommend breath-holding."
    )
    if session_type == "Meditation":
        activity = (
            "Create a calming guided meditation with a gentle welcome, settling posture, "
            "soft attention to natural breathing, a body relaxation scan, a simple focus "
            "exercise, and a gradual closing. Use pauses indicated by short phrases like "
            "'pause for a few breaths'; do not include stage directions that should not be spoken."
        )
    elif session_type == "Yoga":
        activity = (
            "Create a beginner-friendly spoken yoga flow. Include a gentle opening, "
            "4 to 6 accessible poses, clear alignment cues, reminders to move within a "
            "comfortable range, and a relaxing closing. Offer a simple alternative for "
            "any pose that may be difficult. Do not assume props or equipment."
        )
    else:
        activity = (
            "Create a gentle guided breathing session using natural, comfortable breathing. "
            "Do not prescribe breath retention, forceful breathing, or strict counts. "
            "Invite the listener to return to normal breathing whenever comfortable."
        )

    return f"""
You are SereneMind, a calm and responsible wellness audio guide.
Write a spoken script in {language} for a {session_type.lower()} session.
Focus or intention: {focus}.
Target duration: about {duration} minutes.
Experience level: {level}.

{activity}

Safety requirements: {safety_note}
Use a warm, unhurried, supportive voice. Avoid markdown, headings, bullet points,
emoji, medical claims, and excessive repetition. Make the script suitable for text-to-speech.
Respond only in {language}.
""".strip()


def generate_script(session_type, focus, duration, language, level):
    if not client:
        raise RuntimeError("GEMINI_API_KEY is not configured in your environment.")
    prompt = build_prompt(session_type, focus, duration, language, level)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
    script = (response.text or "").strip()
    if not script:
        raise RuntimeError("Gemini returned an empty script.")
    return script




def generate_murf_audio(script, voice_id, locale):
    import base64
    import requests
    from murf import Murf

    api_key = os.getenv("MURF_API_KEY")
    if not api_key:
        raise RuntimeError("MURF_API_KEY is not configured.")

    client = Murf(api_key=api_key)

    try:
        response = client.text_to_speech.generate(
            voice_id=voice_id or "Natalie",
            text=script,
            locale=locale,
            format="MP3",
        )

        audio_url = response.audio_file
        if not audio_url:
            raise RuntimeError("Murf returned no audio URL.")

        audio_response = requests.get(audio_url, timeout=60)
        audio_response.raise_for_status()

        return base64.b64encode(
            audio_response.content
        ).decode("utf-8")

    except Exception:
        app.logger.exception("Murf SDK audio generation failed")
        raise




@app.post("/api/generate-session")
def generate_session():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Send a valid JSON request body."}), 400

    session_type = payload.get("sessionType", "Meditation")
    focus = str(payload.get("focus", "relaxation")).strip()[:120]
    duration = payload.get("duration", "5 minutes")
    language = payload.get("language", "English")
    level = payload.get("level", "Beginner")

    if session_type not in SESSION_TYPES:
        return jsonify({"error": "Choose Meditation, Yoga, or Breathing."}), 400
    if duration not in DURATIONS:
        return jsonify({"error": "Choose a supported session duration."}), 400
    if language not in LOCALES:
        return jsonify({"error": "Choose a supported language."}), 400
    if level not in LEVELS:
        return jsonify({"error": "Choose a supported experience level."}), 400
    if not focus:
        focus = "relaxation"

    voice_id = VOICE_IDS.get(language, "")
    if not voice_id or voice_id.startswith("YOUR_"):
        return jsonify({
            "error": f"Configure a valid Murf voice ID for {language} in the environment first."
        }), 400

    try:
        script = generate_script(
            session_type, focus, duration, language, level
        )
        audio_base64 = generate_murf_audio(
            script, voice_id, LOCALES[language]
        )
        return jsonify({
            "script": script,
            "audioBase64": audio_base64,
            "sessionType": session_type,
            "duration": duration,
            "language": language,
        })
    except requests.RequestException:
        app.logger.exception("Murf API request failed")
        return jsonify({"error": "Murf could not generate audio. Check the voice ID, locale, and API access."}), 502
    except Exception as exc:
        app.logger.exception("Session generation failed")
        # A concise error is returned to the UI; details remain in the terminal.
        message = str(exc)
        if "GEMINI_API_KEY" in message or "MURF_API_KEY" in message:
            return jsonify({"error": message}), 500
        return jsonify({"error": "Could not generate the session. Check the backend terminal for details."}), 500


if __name__ == "__main__":
    app.run(debug=True)
