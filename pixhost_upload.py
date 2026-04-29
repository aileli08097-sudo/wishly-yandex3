import requests

PIXHOST_API_URL = "https://api.pixhost.to/images"


def image_pixhost(file):
    print("=== Pixhost загрузка ===")

    print(f"Файл: {file}")
    print(f"Имя файла: {file.filename if file else 'None'}")
    if not file or not file.filename:
        print("Ошибка: файл пустой или нет имени")
        return None
    files = {
        'img': (file.filename, file.stream, file.mimetype),
    }
    data = {
        'content_type': '0',
        'max_th_size': '420'
    }
    print(f"Отправка файла {file.filename}...")
    response = requests.post(
        PIXHOST_API_URL,
        data=data,
        files=files
    )
    print(f"Код ответа: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"=== ПОЛНЫЙ ОТВЕТ API ===")
        print(result)
        print(f"======================")
        if result.get('status_code') == 200:
            image_url = f"https://img.pixhost.to/images/{result.get('show_url').split('/')[-1]}"
            print(f"✅ УСПЕХ! URL: {image_url}")
            return image_url
        print(f"❌ Не найден URL в ответе")
        return None
    return None
