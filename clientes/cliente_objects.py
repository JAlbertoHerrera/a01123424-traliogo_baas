import os, json, argparse, requests

def auth_headers():
    token = os.getenv("ID_TOKEN", "")
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def main(base):
    H = auth_headers()

    # LIST (por createdBy)
    r = requests.get(f"{base}/objects?createdBy=uid_carlos&limit=5", headers=H)
    print("LIST objects:", r.status_code, json.dumps(r.json(), indent=2, ensure_ascii=False))

    # CREATE
    payload = {
        "label": "bottle",
        "confidence": 0.98,
        "imageUrl": "https://example.com/img.png",
        "langs": ["es","en"],
        "createdBy": "uid_carlos"
    }
    r = requests.post(f"{base}/objects", headers=H, json=payload)
    print("CREATE object:", r.status_code, r.json())
    oid = r.json().get("id")

    # GET
    r = requests.get(f"{base}/objects/{oid}", headers=H)
    print("GET object:", r.status_code, json.dumps(r.json(), indent=2, ensure_ascii=False))

    # UPDATE
    r = requests.put(f"{base}/objects/{oid}", headers=H, json={"label": "water bottle", "confidence": 0.99})
    print("UPDATE object:", r.status_code, r.json())

    # DELETE
    r = requests.delete(f"{base}/objects/{oid}", headers=H)
    print("DELETE object:", r.status_code)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8080/api/v1")
    args = ap.parse_args()
    main(args.base)
