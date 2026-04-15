import requests
import os
import base64

IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY')
IMGBB_API_URL = 'https://api.imgbb.com/1/upload'


def image_imgbb(file):
    if not file or not file.filename:
        return None
    file_data = file.read()
    if not file_data:
        return None
    code_file = base64.b64encode(file_data).decode('utf-8')
    response = requests.post(
        IMGBB_API_URL,
        data={
            'key': IMGBB_API_KEY,
            'image': code_file,
            'expiration': 0,
            'name': file.filename
        }
    )
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            image_url = result['data']['url']
            return image_url
        return None
    return None
