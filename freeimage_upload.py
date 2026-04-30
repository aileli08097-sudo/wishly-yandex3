import requests
import os

FREEIMAGE_API_KEY = os.environ.get('FREEIMAGE_API_KEY')
FREEIMAGE_API_URL = 'https://freeimage.host/api/1/upload'

def image_freeimage(file):
    if not file or not file.filename:
        return None
    files = {
        'source': (file.filename, file.stream, file.mimetype),
    }
    data = {
        'key': FREEIMAGE_API_KEY,
        'action': 'upload',
        'format': 'json'
    }
    response = requests.post(
        FREEIMAGE_API_URL,
        data=data,
        files=files
    )
    if response.status_code == 200:
        result = response.json()
        if result.get('status_code') == 200:
            image_url = result['image']['url']
            return image_url
        return None
    return None