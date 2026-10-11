
import os
from murf import Murf
from murf.core.api_error import ApiError

try:
    api_key = os.getenv("MURF_API_KEY")

    if not api_key:
        print("ERROR: MURF_API_KEY is not set in this terminal.")
    else:
        client = Murf(api_key=api_key)

        response = client.text_to_speech.generate(
            voice_id="Natalie",
            text="Welcome to SereneMind. Take a slow breath in.",
            locale="en-US",
        )

        print("SUCCESS!")
        print("Audio URL:", response.audio_file)

except ApiError as e:
    print("MURF API ERROR")
    print("HTTP status:", e.status_code)
    print("Details:", e.body)

except Exception as e:
    print("OTHER ERROR:", repr(e))
