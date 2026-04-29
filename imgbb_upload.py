import requests
import os
import base64

IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY')
IMGBB_API_URL = 'https://api.imgbb.com/1/upload'


def image_imgbb(file):
    print("=== upload_image_to_imgbb ВЫЗВАНА ===")
    print(f"Файл: {file}")
    print(f"Имя файла: {file.filename if file else 'None'}")
    if not file or not file.filename:
        print("Ошибка: файл пустой или нет имени")
        return None
    print(f"API KEY exists: {bool(IMGBB_API_KEY)}")
    if not IMGBB_API_KEY:
        print("ОШИБКА: API ключ ImgBB не найден!")
        return None
    file_data = file.read()
    if not file_data:
        return None
    code_file = base64.b64encode(file_data).decode('utf-8')
    print("Отправка запроса к ImgBB...")
    response = requests.post(
        IMGBB_API_URL,
        data={
            'key': IMGBB_API_KEY,
            'image': code_file,
            'expiration': 0,
            'name': file.filename
        }
    )
    print(f"Код ответа ImgBB: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            image_url = result['data']['url']
            print(f"✅ УСПЕХ! URL: {image_url}")
            return image_url
        error_msg = result.get('error', {}).get('message', 'Неизвестная ошибка')
        print(f"❌ Ошибка API ImgBB: {error_msg}")
        return None
    return None
