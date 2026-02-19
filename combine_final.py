import json
import sys
from pathlib import Path
import requests


def load_ex1_json() -> dict:
    """
    Read Exercise 1 output JSON from data/ex1_shortages.json
    """
    data_path = Path(__file__).resolve().parent.parent / "data" / "ex1_shortages.json"
    if not data_path.exists():
        raise FileNotFoundError(
            f"Missing {data_path}. Ask your teammate to export Exercise 1 JSON to this file."
        )
    return json.loads(data_path.read_text(encoding="utf-8"))


def get_or_create_user(base_url: str, username: str) -> int:
    """
    Create user. If already exists (409), list users and find matching id.
    """
    r = requests.post(f"{base_url}/users", json={"username": username}, timeout=15)

    if r.status_code == 201:
        return r.json()["id"]

    if r.status_code == 409:
        users = requests.get(f"{base_url}/users", timeout=15).json()
        for u in users:
            if u.get("username") == username:
                return u["id"]
        raise RuntimeError("Username exists but not found in /users list.")

    raise RuntimeError(f"Create user failed: {r.status_code} {r.text}")


def add_json_note(base_url: str, user_id: int, ex1_data: dict) -> dict:
    """
    Save Exercise 1 data as a JSON note for that user.
    """
    payload = {
        "data": {
            "source": "exercise1-openfda",
            "payload": ex1_data
        }
    }
    r = requests.post(f"{base_url}/users/{user_id}/notes/json", json=payload, timeout=30)
    if r.status_code != 201:
        raise RuntimeError(f"Add json note failed: {r.status_code} {r.text}")
    return r.json()


def main():
    # Usage:
    #   python scripts/combine_final.py
    #   python scripts/combine_final.py http://127.0.0.1:8000 final_user
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    username = sys.argv[2] if len(sys.argv) > 2 else "final_user"

    ex1_data = load_ex1_json()
    user_id = get_or_create_user(base_url, username)
    note = add_json_note(base_url, user_id, ex1_data)

    notes = requests.get(f"{base_url}/users/{user_id}/notes", timeout=15).json()
    print(f"OK: user_id={user_id}, username={username}, created_note_id={note.get('id')}, total_notes={len(notes)}")


if __name__ == "__main__":
    main()
