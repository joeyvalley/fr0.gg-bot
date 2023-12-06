import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
service_account_path = os.path.join(dir_path, 'serviceAccountKey.json')
cred = credentials.Certificate(service_account_path)


firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://fr0gg-1445c-default-rtdb.firebaseio.com/'
})

def insert_data_to_firebase(date, prompt, image_url):
    ref = db.reference('/image_prompts')
    new_entry_ref = ref.push({
        'date': date,
        'prompt': prompt,
        'image_url': image_url
    })
    return new_entry_ref.key  # Return the unique key of the new entry
