import os, json, requests
from dotenv import load_dotenv

# === CONFIG ===
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE = "https://api.mdi.milestonesys.com/api/v1"
AUTH = {"Authorization": f"ApiKey {API_KEY}"}
# Cambia el nombre del clip según quieras probar manualmente
clip_path = "gettingintocar_robbery_long.mp4"

# === 1) Upload asset ===
with open(clip_path, "rb") as f:
    up = requests.post(f"{BASE}/assets", headers=AUTH, files={"file": f}, timeout=120)
print("Status code:", up.status_code)
print("Response text:", up.text)
asset_id = up.json()["id"]
print(f"Uploaded asset_id: {asset_id}")

# === 2) Chat completion ===
system_prompt = """You are an AI security assistant that validates video alerts from parking cameras. Your main objective
is to decide if the people in the video are the actual owners of the parked cars or thiefs trying to steal things from the cars
or even robbing the cars. The video to process is a temporal composite, representing a continous blend of frames. This should give
you more information about the motion of the person. Follow exactly this JSON schema; if uncertain, use "uncertain". 
Give a 1 to 10 score of your confidence about the decision

<format>
{
  "verdict": "true|false|uncertain",
  "confidence": "number",
  "reason": "short natural-language explanation"]
}
</format>

Criteria:
- "true" = The person interacts with the vehicle in a suspicious or unauthorized way (possible theft attempt).
- "false" = The person’s behavior is normal and authorized.
- "uncertain" = The video is ambiguous or inconclusive.
Be precise with timing and reasoning."""

user_prompt = """Validate the 'car_theft' alert in this clip. Indicate if the person is the actual owner of the 
                car or a thief. Explain why you get the final decision. Check for the person looking around, the pace,
                if he has a tool, the lights of the car, a possible alarm system of the car (blinking lights)"""

payload = {
    "messages": [
        {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
        {"role": "user", "content": [
            {"type": "text", "text": user_prompt},
            {"type": "asset_id", "asset_id": asset_id}
        ]}
    ]
}

resp = requests.post(
    f"{BASE}/chat/completions",
    headers={**AUTH, "Content-Type": "application/json"},
    data=json.dumps(payload),
    timeout=180
)

result = resp.json()
print(json.dumps(result, indent=2))

# === 3) (Optional) Delete asset ===
requests.delete(f"{BASE}/assets/{asset_id}", headers=AUTH, timeout=60)
