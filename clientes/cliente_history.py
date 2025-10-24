import os, json, argparse, requests

def auth_headers():
    token = os.getenv("ID_TOKEN", "")
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def main(base):
    H = auth_headers()

    # LIST (por userId)
    r = requests.get(f"{base}/history?userId=uid123&limit=5", headers=H)
    print("LIST history:", r.status_code, json.dumps(r.json(), indent=2, ensure_ascii=False))

    # CREATE
    payload = {
        "userId": "uid123",
        "sourceLang": "es",
        "targetLang": "en",
        "inputType": "text",
        "text": "hola",
        "result": "hello"
    }
    r = requests.post(f"{base}/history", headers=H, json=payload)
    print("CREATE history:", r.status_code, r.json())
    hid = r.json().get("id")

    # GET
    r = requests.get(f"{base}/history/{hid}", headers=H)
    print("GET history:", r.status_code, json.dumps(r.json(), indent=2, ensure_ascii=False))

    # UPDATE
    r = requests.put(f"{base}/history/{hid}", headers=H, json={"result": "hello!"})
    print("UPDATE history:", r.status_code, r.json())

    # DELETE
    r = requests.delete(f"{base}/history/{hid}", headers=H)
    print("DELETE history:", r.status_code)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8080/api/v1")
    args = ap.parse_args()
    main(args.base)
