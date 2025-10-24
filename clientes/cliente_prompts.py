import os, json, argparse, requests

def main(base):
    H = {"Content-Type":"application/json"}

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
