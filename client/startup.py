import requests
import json
import os

Parent = os.path.dirname(os.path.realpath(__file__))
data = requests.get("http://127.0.0.1:8444").json()

user_files= os.listdir(f"{Parent}/users")
num_files = len(user_files)
uuid = None
is_uuid_found = False
if len(user_files) > 1:
    usernames = []
    for file in user_files:
        with open(f"{Parent}/users/{file}") as user_file:
            userdata = json.load(user_file)
            usernames.append(userdata["username"])
    print(f"You have multiple accounts, which one do you want to use?\n{usernames}")
    choice = input()
    if choice in usernames:
        # find the uuid of the file with the username, then save that to the uuid variable
        for file in user_files:
            with open(f"{Parent}/users/{file}") as user_file:
                userdata = json.load(user_file)
                if userdata["username"] == choice:
                    uuid = userdata["user_id"]
                    is_uuid_found = True
elif len(user_files) == 1:
    # only one account, so just use that
        print("Do you want to sign out or login?\n1. Login\n2. Sign out")
        choice = input()
        if choice == "1":
            #use userdata.json to login
            with open(f"{uuid}.json") as file:
                userdata = json.load(file)
            login = requests.post("http://127.0.0.1:8444/login", json={"username": userdata["username"], "password": userdata["password"]})
            if login.status_code == 200:
                print("Login successful!")
            else:
                print("Login failed!")
        if choice == "2":
            print("Signing out...")
            print("Signing out entails deleting your userdata.json file, and logging out of your account.")
            print("This will be changed at a later date, although if you need multiple accounts, you can temporarily delete your user file in the users folder, sign up your second account and then restore your original user file. Don't worry, there is a user switching feature setup if you have multiple accounts saved.")
            #delete userdata.json
            os.remove(f"{uuid}.json")
            print("Signed out!")
            # re-execute the script
            os.system(f"python {Parent}/main.py")
else:
    if data.get("message") == "Connection successful, next create an account":
        print("Do you want to sign up or login?\n1. Login\n2. Sign up")
        choice = input()
        if choice == "1":
            print("Enter username:")
            username = input()
            print("Enter password:")
            password = input()
            login = requests.post("http://127.0.0.1:8444/login", json={"username": username, "password": password})
            if login.status_code == 200:
                stored_userdata_server = login.json()
                dump = {"username": username, "password": password, "uuid": stored_userdata_server["user_id"]}
                with open(f"{stored_userdata_server['user_id']}.json", "w") as file:
                    json.dump(dump, file)
                    print(f"Login successful! Welcome back {username}!")
                    print("Login successful!")
        if choice == "2":
            print("Creating account...")
            print("Enter username:")
            username = input()
            print("Enter password:")
            password = input()
            accountcreation = requests.post("http://127.0.0.1:8444/signup", json={"username": username, "password": password})
            if accountcreation.status_code == 200:
                response_data = accountcreation.json()
                dump = {"username": username, "password": password, "uuid": response_data["user_id"]}
                uuid = response_data["user_id"]
                with open(f"{uuid}.json", "w") as file:
                    json.dump(dump, file)
                    print("Account created!")
            else:
                print("Account creation failed!")
    elif data.get("message") == "Connection successful, next create an account" and os.path.isfile(f"{Parent}/{uuid}.json") == True:
        print("Do you want to sign out or login?\n1. Login\n2. Sign out")
        choice = input()
        if choice == "1":
            #use userdata.json to login
            with open(f"{uuid}.json") as file:
                userdata = json.load(file)
            login = requests.post("http://127.0.0.1:8444/login", json={"username": userdata["username"], "password": userdata["password"]})
            if login.status_code == 200:
                print("Login successful!")
            else:
                print("Login failed!")
        if choice == "2":
            #delete userdata.json
            os.remove(f"{uuid}.json")
            print("Signed out!")
            # re-execute the script
            os.system(f"python {Parent}/main.py")
    else:
        print("Unable to connect to servers. Check your internet connection, or try again later.")