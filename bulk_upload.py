from datetime import datetime, timedelta
import os
import random
import cloudinary.uploader
from firebaseDB_add import insert_data_to_firebase

# Your Cloudinary configuration here
cloud = os.environ.get("CLOUD_NAME")
cloudinary_api = os.environ.get("CLOUDINARY_API_KEY")
cloudinary_api_secret = os.environ.get("CLOUDINARY_API_SECRET")

cloudinary.config(
    cloud_name=cloud, api_key=cloudinary_api, api_secret=cloudinary_api_secret
)


def upload_image_to_cloudinary(image_path):
    result = cloudinary.uploader.upload(image_path)
    return result.get("url")


def main():
    image_folder = "frogs"
    start_date = datetime(2023, 12, 17)
    valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

    image_files = [
        f
        for f in os.listdir(image_folder)
        if os.path.splitext(f)[1].lower() in valid_extensions
    ]
    random.shuffle(image_files)

    for i, image_name in enumerate(image_files):
        image_path = os.path.join(image_folder, image_name)
        if os.path.isfile(image_path):
            # ISO 8601 date format (without time)
            image_date = start_date - timedelta(days=i)
            image_date_str = image_date.strftime("%Y-%m-%dT%H:%M:%S")

            image_url = upload_image_to_cloudinary(image_path)
            firebase_result = insert_data_to_firebase(image_date_str, "", image_url)

            print(f"Uploaded {image_name} for date {image_date_str}")


if __name__ == "__main__":
    main()
