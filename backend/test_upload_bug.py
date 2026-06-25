import requests
import uuid

# Load a valid PDF file from project data directory
with open("data/resume.pdf", "rb") as f:
    pdf_data = f.read()

url = "http://localhost:8000/api/uploads/resume"

print("--- Request 1: No X-Session-ID header ---")
files = {"file": ("resume.pdf", pdf_data, "application/pdf")}
try:
    r1 = requests.post(url, files=files)
    print("Status:", r1.status_code)
    print("Response:", r1.json())
except Exception as e:
    print("Request 1 failed:", e)

print("\n--- Request 2: No X-Session-ID header ---")
files = {"file": ("resume.pdf", pdf_data, "application/pdf")}
try:
    r2 = requests.post(url, files=files)
    print("Status:", r2.status_code)
    print("Response:", r2.json())
except Exception as e:
    print("Request 2 failed:", e)

# Test with a stable session ID
session_id = str(uuid.uuid4())
print(f"\n--- Request 3: With X-Session-ID = {session_id} ---")
files = {"file": ("resume.pdf", pdf_data, "application/pdf")}
headers = {"X-Session-ID": session_id}
try:
    r3 = requests.post(url, files=files, headers=headers)
    print("Status:", r3.status_code)
    print("Response:", r3.json())
except Exception as e:
    print("Request 3 failed:", e)

print(f"\n--- Request 4: With SAME X-Session-ID = {session_id} ---")
files = {"file": ("resume.pdf", pdf_data, "application/pdf")}
try:
    r4 = requests.post(url, files=files, headers=headers)
    print("Status:", r4.status_code)
    print("Response:", r4.json())
except Exception as e:
    print("Request 4 failed:", e)
