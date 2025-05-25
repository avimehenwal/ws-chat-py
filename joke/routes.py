from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Dict, Union

# static data for testing purposes
JOKES: List[Dict[str, Union[int, str]]] = [
    {"id": 0, "joke": "Why don't scientists trust atoms? Because they make up everything!"},
    {"id": 1, "joke": "What do you call a fake noodle? An impasta!"},
    {"id": 2, "joke": "Why did the scarecrow win an award? Because he was outstanding in his field!"},
    {"id": 3, "joke": "I told my wife she was drawing her eyebrows too high. She looked surprised."},
    {"id": 4, "joke": "What do you call a sad strawberry? A blueberry!"},
    {"id": 5, "joke": "I'm reading a book about anti-gravity. It's impossible to put down!"},
    {"id": 6, "joke": "Why did the bicycle fall over? Because it was two-tired!"},
    {"id": 7, "joke": "What do you call cheese that isn't yours? Nacho cheese!"},
    {"id": 8, "joke": "Did you hear about the highly addictive new restaurant? People are saying it's crack-er barrel."},
    {"id": 9, "joke": "My wife asked me to stop singing 'Wonderwall' to her. I said maybe..."}
]

# This will ensure new jokes get unique IDs, even after deletions
_next_joke_id = len(JOKES)


joke_router = APIRouter(prefix="/joke", tags=["Joke API"])

@joke_router.get("/", response_model=List[Dict[str, Union[int, str]]])
def get_all_jokes():
    """
    Retrieves all jokes from the static list, each with an ID.
    """
    return JOKES

@joke_router.get("/{joke_id}", response_model=Dict[str, Union[int, str]])
def get_joke_by_id(joke_id: int):
    """
    Retrieves a specific joke by its ID.
    Raises HTTPException 404 if the joke ID is not found.
    """
    for joke_data in JOKES:
        if joke_data["id"] == joke_id:
            return joke_data
    raise HTTPException(status_code=404, detail=f"Joke with ID {joke_id} not found")

@joke_router.post("/", status_code=201, response_model=Dict[str, Union[int, str]])
def create_joke(joke: str):
    """
    Adds a new joke to the static list with a unique ID.
    Returns the newly created joke object (ID and text).
    """
    global _next_joke_id
    new_joke_data = {"id": _next_joke_id, "joke": joke}
    JOKES.append(new_joke_data)
    _next_joke_id += 1
    return new_joke_data

@joke_router.delete("/{joke_id}", status_code=204)
def delete_joke(joke_id: int):
    """
    Deletes a joke by its ID.
    Raises HTTPException 404 if the joke ID is not found.
    """
    found_index = -1
    for i, joke_data in enumerate(JOKES):
        if joke_data["id"] == joke_id:
            found_index = i
            break

    if found_index == -1:
        raise HTTPException(status_code=404, detail=f"Joke with ID {joke_id} not found")

    del JOKES[found_index]
    return

