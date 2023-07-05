import logging
from datetime import datetime
from pprint import pprint

import requests
import vk_api
from vk_api.exceptions import ApiError

from config import access_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)


# получение данных о пользователе


class VkTools:
    def __init__(self, access_token):
        self.vkapi = vk_api.VkApi(token=access_token)
        self.shown_profiles = []

    def _bdate_to_year(self, bdate):
        user_year = int(bdate.split('.')[2])
        current_year = datetime.now().year
        age = current_year - user_year
        return age

    def get_profile_info(self, user_id):
        # Получение информации о профиле пользователя
        try:
            info, = self.vkapi.method(
                'users.get',
                {'user_id': user_id, 'fields': 'city,sex,relation,bdate'})
            logging.info(
                f"С ботом поздоровался пользователь - "
                f"https://vk.com/id{user_id}")
        except ApiError as e:
            info = {}
            logging.error(
                f"Ошибка при получении информации о профиле "
                f"пользователя {user_id}: {e}")

        result = {
            'name': (
                    info['first_name'] + ' ' + info['last_name']
            ) if 'first_name' in info and 'last_name' in info else None,
            'sex': info.get('sex'),
            'city': info.get('city')['title'] if info.get(
                'city') is not None else None,
            'year': self._bdate_to_year(info.get('bdate'))
        }
        return result

    def search_worksheet(self, params, offset):
        try:
            if 'city' in params:
                hometown = params['city']
            else:
                hometown = ''

            if 'marital_status' in params:  # Добавленная проверка для семейного положения
                marital_status = params['marital_status']
            else:
                marital_status = None

            users = self.vkapi.method('users.search', {
                'count': 50,
                'offset': offset,
                'hometown': hometown,
                'sex': 1 if params.get('sex') == 2 else 2,
                'has_photo': True,
                'age_from': int(params.get('year')) - 10 if params.get(
                    'year') else None,
                'age_to': int(params.get('year')) + 10 if params.get(
                    'year') else None,
                'online': 1,
                'relation': 6,
                'online_mobile': 1
                # Добавленный параметр для поиска только актив

            })
        except ApiError as e:
            users = []
            print(f'error = {e}')

        result = [
            {'name': item['first_name'] + ' ' + item['last_name'],
             'id': item['id']}
            for item in users['items']
            if item['is_closed'] is False and item[
                'id'] not in self.shown_profiles
        ]

        return result

    def get_photos(self, id):
        try:
            photos = self.vkapi.method('photos.get',
                                       {'owner_id': id,
                                        'album_id': 'profile',
                                        'extended': 1
                                        }
                                       )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                   } for item in photos['items']
                  ]
        '''сортировка п лайкам и комментам'''
        result.sort(key=lambda x: x['likes'] + x['comments'], reverse=True)
        return result[:3]

    def get_cities(self, user_id):
        # Функция получения списка городов
        method = 'database.getCities'
        params = {'country_id': 1,
                  'need_all': 0,
                  'count': 1000,
                  'user_id': user_id,
                  'access_token': access_token,
                  'v': '5.131',
                  }
        url = f'https://api.vk.com/method/{method}'
        cities_list = requests.get(url, params=params).json()[
            'response']['items']
        return cities_list


if __name__ == '__main__':

    user_id = 765953848
    tools = VkTools(access_token)
    params = tools.get_profile_info(user_id)
    worksheets = tools.search_worksheet(params, 50)

    if len(worksheets) > 0:
        worksheet = worksheets.pop()
        photos = tools.get_photos(worksheet['id'])
        pprint(worksheets)
    else:
        print("Список worksheets пуст.")
