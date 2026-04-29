import requests
import os

FREEIMAGE_API_KEY = os.environ.get('FREEIMAGE_API_KEY')
FREEIMAGE_API_URL = 'https://freeimage.host/api/1/upload'

def image_freeimage(file):
    print("=== FreeImage.Host загрузка ===")
    if not file or not file.filename:
        print("Ошибка: файл пустой")
        return None
    files = {
        'source': (file.filename, file.stream, file.mimetype),
    }
    data = {
        'key': FREEIMAGE_API_KEY,
        'action': 'upload',
        'format': 'json'
    }
    print(f"Отправка файла {file.filename}...")
    response = requests.post(
        FREEIMAGE_API_URL,
        data=data,
        files=files
    )
    print(f"Код ответа: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"=== ПОЛНЫЙ ОТВЕТ ===")
        print(result)
        if result.get('status_code') == 200:
            image_url = result['image']['url']
            print(f"✅ УСПЕХ! URL: {image_url}")
            return image_url
        error_msg = result.get('error', {}).get('message', 'Неизвестная ошибка')
        print(f"❌ Ошибка API: {error_msg}")
        return None
    print(f"❌ HTTP ошибка: {response.status_code}")
    print(f"Ответ: {response.text[:200]}")
    return None