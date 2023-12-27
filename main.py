# get started (ПОЕХАЛИ)

from pprint import pprint
from tqdm import tqdm
import requests
import json
from yadisk import YaDisk
from urllib.parse import urlencode, urlunparse

# Достаём токены из отдельного файла tokens.txt

with open('tokens.txt', 'r') as file:
    tokens = {}
    for line in file:
        key, value = line.strip().split('=')
        tokens[key] = value

VK_ACCESS_TOKEN = tokens.get('VK_ACCESS_TOKEN')
YANDEX_DISK_TOKEN = tokens.get('YANDEX_DISK_TOKEN')
# user_id = input("Введите user_id: ")


user_id = '2426457'

count_photos = int(input("Введите количество фотографий для обработки: "))
oauth_base_url = 'https://oauth.vk.com/authorize'
vk_app_id = '51821951'


# Достаём VK_ACCESS_TOKEN

# params = {
#     'client_id': vk_app_id,
#     'redirect_uri': 'https://oauth.vk.com/blank.html',
#     'display': 'page',
#     'v': '5.131',
#     'scope': 'photos',
#     'response_type': 'token',
#     'state': '123456'
# }

# encoded_params = urlencode(params)

# Создание итогового URL-запроса

# final_url = urlunparse(('https', 'oauth.vk.com', '/authorize', '', encoded_params, ''))

# print("Итоговый URL для авторизации:", final_url)


# Достаём фотки с ВК

def get_photos_from_vk(user_id):
    params = {
        'owner_id': user_id,
        'album_id': 'wall',
        'access_token': VK_ACCESS_TOKEN,
        'v': '5.131',
        'extended': 1,
        'photo_sizes': 1
    }
    response = requests.get('https://api.vk.com/method/photos.get', params=params)
    photos_data = response.json()['response']['items']
    return photos_data


photos_json = get_photos_from_vk(user_id)
# pprint(json.dumps(photos_json, indent=4, ensure_ascii=False))

# Выбираем фото с максимальным разрешением с прогресс баром


def get_max_size_photos(photos_data, count_photos):
    max_size_photos = []

    with tqdm(total=count_photos, desc='Search for photos in VK', unit='photo') as pbar:
        for photo in photos_data[:count_photos]:
            max_photo_size = max(photo['sizes'], key=lambda x: x['width'] * x['height'], default=None)
            if max_photo_size is not None:
                max_size_photos.append({
                    'album_id': photo['album_id'],
                    'date': photo['date'],
                    'id': photo['id'],
                    'owner_id': photo['owner_id'],
                    'max_size': max_photo_size
                })
                pbar.update(1)  # Увеличиваем счетчик прогресса

    return max_size_photos


max_size_photos = get_max_size_photos(photos_json, count_photos)
# print(json.dumps(max_size_photos, indent=4, ensure_ascii=False))

# Начинаем с Яндекс диском

disk = YaDisk(token=YANDEX_DISK_TOKEN)
folder_name = 'photos_from_vk'
disk.mkdir(folder_name)

# Загружаем фотографии в новую папку
for photo in tqdm(max_size_photos, desc='Uploading photos on YaDisk', unit='photo'):
    likes = photo.get('likes', 0)
    upload_date = photo['date']

    # Получаем URL фотографии для загрузки на Яндекс.Диск
    photo_url = photo['max_size']['url']

    # Загружаем файл с URL на компьютер
    file_response = requests.get(photo_url)

    if file_response.status_code == 200:
        # Создаем файл на компьютере с бинарным режимом записи
        with open(f'{likes}_likes_{upload_date}.jpg', 'wb') as file:
            file.write(file_response.content)

        # Загружаем файл с компьютера на Яндекс.Диск
        disk.upload(f'{likes}_likes_{upload_date}.jpg', f'/{folder_name}/{likes}_likes_{upload_date}.jpg')





