import urllib.request
import urllib.parse
import json
import ssl

# Bypass SSL check for localhost
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "http://127.0.0.1:8000"

def login(username, password):
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({
        "username": username,
        "password": password
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            status = response.getcode()
            response_body = response.read().decode("utf-8")
            return status, json.loads(response_body)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)

def get_projects(token):
    url = f"{BASE_URL}/projects/"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            status = response.getcode()
            response_body = response.read().decode("utf-8")
            return status, json.loads(response_body)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)

print("--- Starting Admin Verification ---")

# Step 1: Login as Admin
print("\n[Step 1] Attempting Admin Login (admin / admin9999)...")
status, result = login("admin", "admin9999")

if status == 200 and "access_token" in result:
    print("✅ Admin Login Success: Token received.")
    token = result["access_token"]
    
    # Step 2: Get All Projects
    print("\n[Step 2] Fetching All Projects as Admin...")
    p_status, projects = get_projects(token)
    
    if p_status == 200:
        print(f"✅ Fetch Success: Retrieved {len(projects)} projects.")
        # Print a few examples
        for p in projects[:3]:
            print(f"   - Project: {p.get('name')} (Owner ID: {p.get('owner_id')})")
    else:
        print(f"❌ Fetch Failed: {p_status} - {projects}")

else:
    print(f"❌ Admin Login Failed: {status} - {result}")
