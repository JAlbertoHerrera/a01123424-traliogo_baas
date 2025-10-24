import os, json, argparse, requests

def get_firebase_token(base_url, user_id="test-user-cliente"):
    """Genera un token automáticamente"""
    try:
        response = requests.post(
            f"{base_url}/auth/token",
            json={"user_id": user_id},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()["token"]
    except Exception as e:
        print(f"Error generando token: {e}")
    return None

def auth_headers(base_url):
    token = os.getenv("ID_TOKEN", "") or get_firebase_token(base_url)
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
        print(f"Usando autenticación con token")
    else:
        print("Sin autenticación")
    return h

def main(base):
    H = auth_headers(base)

    # CREATE
    r = requests.post(f"{base}/secrets", json={
        "key":"demo_api_key",
        "value":"super-123",
        "labels":{"env":"dev","owner":"team"}
    }, headers=H)
    print("CREATE:", r.status_code, r.json())

    # LIST
    r = requests.get(f"{base}/secrets?prefix=demo_", headers=H)
    print("LIST:", r.status_code, json.dumps(r.json(), indent=2))

    # GET latest
    r = requests.get(f"{base}/secrets/demo_api_key", headers=H)
    print("GET:", r.status_code, r.json())

    # UPDATE (nueva versión)
    r = requests.put(f"{base}/secrets/demo_api_key", json={"value":"super-456"}, headers=H)
    print("PUT:", r.status_code, r.json())

    # GET latest again
    r = requests.get(f"{base}/secrets/demo_api_key", headers=H)
    print("GET:", r.status_code, r.json())

    # DELETE
    r = requests.delete(f"{base}/secrets/demo_api_key", headers=H)
    print("DELETE:", r.status_code)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8080/api/v1", help="Base URL")
    args = ap.parse_args()
    main(args.base)
