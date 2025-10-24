import os, json, argparse, requests

def auth_headers():
    token = os.getenv("ID_TOKEN", "")
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def main(base):
    H = auth_headers()

    # LIST (por scope/key)
    r = requests.get(f"{base}/flags?scope=global&key=feature_x&limit=5", headers=H)
    print("LIST flags:", r.status_code, json.dumps(r.json(), indent=2, ensure_ascii=False))

    # CREATE
    payload = {
        "key": "feature_x",
        "value": True,
        "type": "bool",
        "scope": "global"
    }
    r = requests.post(f"{base}/flags", headers=H, json=payload)
    print("CREATE flag:", r.status_code, r.json())
    fid = r.json().get("id")

    # GET
    r = requests.get(f"{base}/flags/{fid}", headers=H)
    print("GET flag:", r.status_code, json.dumps(r.json(), indent=2, ensure_ascii=False))

    # UPDATE
    r = requests.put(f"{base}/flags/{fid}", headers=H, json={"value": False})
    print("UPDATE flag:", r.status_code, r.json())

    # DELETE
    r = requests.delete(f"{base}/flags/{fid}", headers=H)
    print("DELETE flag:", r.status_code)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8080/api/v1")
    args = ap.parse_args()
    main(args.base)
