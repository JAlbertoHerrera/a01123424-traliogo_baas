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

    # LIST
    r = requests.get(f"{base}/prompts?limit=3", headers=H)
    print("LIST:", r.status_code, json.dumps(r.json(), indent=2))

    # CREATE (invoca Gemini y guarda en Firestore)
    r = requests.post(f"{base}/prompts", json={
        "prompt": "Resume en una sola oración qué es TralioGo."
    }, headers=H)
    print("CREATE:", r.status_code, r.json())
    pid = r.json()["id"]

    # GET
    r = requests.get(f"{base}/prompts/{pid}", headers=H)
    print("GET:", r.status_code, json.dumps(r.json(), indent=2))

    # PUT (agregar nota)
    r = requests.put(f"{base}/prompts/{pid}", json={"note":"respuesta usada en demo"}, headers=H)
    print("PUT:", r.status_code, r.json())

    # DELETE
    r = requests.delete(f"{base}/prompts/{pid}", headers=H)
    print("DELETE:", r.status_code)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8080/api/v1")
    args = ap.parse_args()
    main(args.base)
