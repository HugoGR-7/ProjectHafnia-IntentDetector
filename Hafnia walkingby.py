import os, json, requests
from dotenv import load_dotenv

# === CONFIG ===
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE = "https://api.mdi.milestonesys.com/api/v1"
AUTH = {"Authorization": f"ApiKey {API_KEY}"}

# Cambia el nombre del clip según quieras probar manualmente
clip_path = "videos/walkingby_full_look.mp4"

# === 1) Upload asset ===
with open(clip_path, "rb") as f:
    up = requests.post(f"{BASE}/assets", headers=AUTH, files={"file": f}, timeout=120)
print("Status code:", up.status_code)
print("Response text:", up.text)
asset_id = up.json()["id"]
print(f"Uploaded asset_id: {asset_id}")

# === 2) Chat completion ===
system_prompt = """You are an AI security assistant that generate alerts from parking cameras.
Follow exactly this JSON schema; if uncertain, use "uncertain".

<format>
{
  "verdict": "thief | normal | uncertain",
  "confidence verdict": "int"
  "reason": "short natural-language explanation",
  "is_interacting": [{"door_handles": boolean, "windows": boolean, "trunk":boolean, "different_cars":boolean}]
}
</format>

Criteria:
- "thief" = The person interacts with the vehicle in a suspicious or unauthorized way (possible theft attempt).
- "normal" = The person’s behavior is normal and authorized.
- "uncertain" = The video is ambiguous or inconclusive.
- Confident verdict should be a number between 0 and 100. 100 meaning you are 100% sure.
"""

user_prompt = """Validate the 'car_tampering' alert in this clip. Explain briefly why you consider it suspicious, normal, or uncertain.
                The most important thing is to check if the person is interacting with different cars, checking door handles and looking 
                through windows. Also check, but with less weight on the final decision, the person clothes and time of the day"""

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
