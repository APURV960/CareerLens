import requests

# Load a valid PDF file from project data directory
with open("data/resume.pdf", "rb") as f:
    pdf_data = f.read()

url = "http://localhost:8000/api/uploads/resume"

print("=== STEP 1: Uploading first resume without session ID header ===")
files = {"file": ("resume.pdf", pdf_data, "application/pdf")}
try:
    r1 = requests.post(url, files=files)
    r1_json = r1.json()
    print("Status:", r1.status_code)
    print("Response:", r1_json)
    
    session_id = r1_json.get("session_id")
    print(f"Extracted Session ID from Response: {session_id}")
    
    if not session_id:
        print("ERROR: No session_id returned in response! Fix failed.")
        exit(1)
        
    print("\n=== STEP 2: Uploading second resume with extracted Session ID header ===")
    headers = {"X-Session-ID": session_id}
    r2 = requests.post(url, files=files, headers=headers)
    r2_json = r2.json()
    print("Status:", r2.status_code)
    print("Response:", r2_json)
    
    # Check assertions
    if r2_json.get("version") == 2:
        print("\nSUCCESS: Resume version correctly incremented to 2 under the same user session!")
    else:
        print("\nFAILURE: Version did not increment. Still got version:", r2_json.get("version"))

except Exception as e:
    print("Test run failed with error:", e)
