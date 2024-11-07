import os
import requests
import firebase_admin
from firebase_admin import credentials, db
from PIL import Image
from io import BytesIO
from datetime import datetime

# Initialize Firebase Admin
dir_path = os.path.dirname(os.path.realpath(__file__))
service_account_key = os.path.join(dir_path, "serviceAccountKey.json")
cred = credentials.Certificate(service_account_key)
firebase_admin.initialize_app(
    cred, {"databaseURL": "https://fr0gg-1445c-default-rtdb.firebaseio.com/"}
)


# Function to display the image
def display(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as file:
            file.write(response.content)
        image = Image.open(filename)
        image.show()
    else:
        print(f"Failed to download image. Status code: {response.status_code}")


def search(date):
    ref = db.reference("image_prompts")
    snapshot = ref.order_by_child("date").equal_to(date).get()

    if snapshot:
        for key, val in snapshot.items():
            url = val["image_url"]
            image_directory = "/home/fr0.gg/Desktop/img"

            # Create the directory if it does not exist
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)

            # Full path for the image file
            filename = os.path.join(image_directory, f"fr-0gg_{date}.jpg")
            display(url, filename)
    else:
        print("No image found for this date.")


# Ask the user for a date
user_date = input("Enter a date (YYYY-MM-DD) to search for an image: ")

# Validate user input (basic validation, can be improved)
try:
    datetime.strptime(user_date, "%Y-%m-%d")
    search(user_date)
except ValueError:
    print("This is the incorrect date string format. It should be YYYY-MM-DD")
