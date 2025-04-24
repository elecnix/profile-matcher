from fastapi import FastAPI

app = FastAPI()

@app.get("/get_client_config/{player_id}")
def get_client_config(player_id: str):
    # Placeholder: should call campaigns service, but returns empty for now
    return {}

@app.get("/profiles")
def get_profiles():
    # Placeholder for profile service
    return []
