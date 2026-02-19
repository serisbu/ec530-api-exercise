from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Exercise 2 - Users & Notes")

users_by_id: Dict[int, Dict[str, Any]] = {}
username_to_id: Dict[str, int] = {}
next_user_id: int = 1

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)

class UserResponse(BaseModel):
    id: int
    username: str


class AddNoteRequest(BaseModel):
    # normal note
    text: str = Field(..., min_length=1, max_length=5000)


class AddJSONNoteRequest(BaseModel):
    # this one is for final one (combined with exercise1)
    data: Any


class NoteResponse(BaseModel):
    id: int
    type: str  # "text" or "json"
    text: Optional[str] = None
    data: Optional[Any] = None


# Helpers
def _get_user_or_404(user_id: int) -> Dict[str, Any]:
    user = users_by_id.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Routes (Exercise 2)

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(req: CreateUserRequest):
    """
    User story:
    - As a user, I can create an account with a username.
    - If username already exists -> return 409.
    """
    global next_user_id

    username = req.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Username cannot be empty")

    if username in username_to_id:
        raise HTTPException(status_code=409, detail="Username already exists")

    user_id = next_user_id
    next_user_id += 1

    users_by_id[user_id] = {
        "id": user_id,
        "username": username,
        "notes": [],       # list of note objects
        "next_note_id": 1
    }
    username_to_id[username] = user_id

    return {"id": user_id, "username": username}


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """
    User story:
    - As a user, I can retrieve my account by id.
    """
    user = _get_user_or_404(user_id)
    return {"id": user["id"], "username": user["username"]}


@app.get("/users", response_model=List[UserResponse])
def list_users():
    """
    User story:
    - As a user, I can list all users.
    """
    return [{"id": u["id"], "username": u["username"]} for u in users_by_id.values()]


@app.post("/users/{user_id}/notes", response_model=NoteResponse, status_code=201)
def add_text_note(user_id: int, req: AddNoteRequest):
    """
    User story:
    - As a user, I can add text notes.
    """
    user = _get_user_or_404(user_id)

    note_id = user["next_note_id"]
    user["next_note_id"] += 1

    note = {"id": note_id, "type": "text", "text": req.text}
    user["notes"].append(note)
    return note


@app.get("/users/{user_id}/notes", response_model=List[NoteResponse])
def list_notes(user_id: int):
    """
    User story:
    - As a user, I can read my text notes.
    """
    user = _get_user_or_404(user_id)
    return user["notes"]


# ----------------------------
# Final helper route (Exercise 1 -> Exercise 2)
# ----------------------------

@app.post("/users/{user_id}/notes/json", response_model=NoteResponse, status_code=201)
def add_json_note(user_id: int, req: AddJSONNoteRequest):
    """
    Final:
    Combine exercise 1 and 2.
    Save data from exercise 1 (JSON) as a note for a user.
    """
    user = _get_user_or_404(user_id)

    note_id = user["next_note_id"]
    user["next_note_id"] += 1

    note = {"id": note_id, "type": "json", "data": req.data}
    user["notes"].append(note)
    return note

