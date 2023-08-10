from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import uuid
import os
from fastapi.responses import FileResponse
from passlib.context import CryptContext
import uvicorn
import ssl
Parent = os.path.dirname(os.path.realpath(__file__))

server_config = json.load(open(f"{Parent}/config.json", "r"))

if __name__ == "__main__":
    #ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #ssl_context.load_cert_chain("cert.pem", "key.pem")
    config = uvicorn.Config("main:app", port=8443, log_level="info")
    server = uvicorn.Server(config)
    server.run()

userdata_folder_path = os.path.join(Parent, 'userdata')
games_folder_path = os.path.join(Parent, 'games')
app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserData(BaseModel):
    username: str
    password: str

class GameData(BaseModel):
    game_id: str
    name: str
    description: str
    download_url: str



@app.get("/")
async def root():
    return {"message": "Connection successful, next create an account"}


@app.post("/signup")
async def create_userdata(userdata: UserData):
    # Generate a UUID for the user
    user_uuid = str(uuid.uuid4())

    # Create the userdata dictionary
    userdata_dict = userdata.dict()
    userdata_dict["user_id"] = user_uuid

    # Hash the password
    hashed_password = pwd_context.hash(userdata_dict["password"])
    userdata_dict["password"] = hashed_password

    # Specify the file path with the UUID as the filename
    file_path = f"{userdata_folder_path}/{user_uuid}.json"

    # Write the userdata to the JSON file
    with open(file_path, "w") as file:
        json.dump(userdata_dict, file)

    # Return the created userdata
    return userdata_dict

@app.post("/login")
async def login(userdata: UserData):
    stored_userdata = None
    # Search through the files in the userdata folder for the username
    for filename in os.listdir(userdata_folder_path):
        file_path = os.path.join(userdata_folder_path, filename)
        with open(file_path) as file:
            stored_userdata = json.load(file)
            if stored_userdata["username"] == userdata.username:
                # Found the matching user, retrieve the UUID
                user_uuid = stored_userdata["user_id"]
                break
    else:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the password
    if not pwd_context.verify(userdata.password, stored_userdata["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Return a success message or token
    return stored_userdata


@app.get("/games")
async def get_games():
    # Retrieve the list of available games
    games = [
        GameData(game_id="stalker.py", name="stalker placeholder", description="quick one made by hero", download_url="http://127.0.0.1:8000/game1")
        # Add more games as needed
    ]

    # Return the list of games
    return games

@app.get("/games/{game_id}/download")
async def download_game(game_id: str):
    # Logic to retrieve the file path based on the game_id
    file_path = f"{games_folder_path}/{game_id}"

    # Return the file as a response using FileResponse
    return FileResponse(file_path, filename=f"{game_id}", as_attachment=True)
