import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

import back
import db
from config import community_token, access_token
from keyboard import *


class BotInterface():
    # def __init__(self, community_token, access_token):
    def __init__(self, community_token, access_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = back.VkTools(access_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0
        self.user_states = {}  # добавить эту строку для инициализации атрибута user_states
        print('\U0001F916 "Работаем!', sep='\n')

    def store_user_state(self, user_id, state):
        self.user_states[user_id] = state

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id(),
                        'keyboard': keyboard.get_keyboard()}
                       )

    def get_user_photo(self, user_id):
        photos = self.vk_tools.get_photos(user_id)
        photo_string = ''
        for photo in photos:
            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
        return photo_string

    def find_city(self, user_id):
        self.message_send(user_id, 'Введите название города для поиска: ')
        message, user_id = self.event_handler()
        hometown = str(message)
        cities = self.get_cities(user_id)

        # Добавьте код для поиска анкет по введенному городу
        found_profiles = self.search_profiles_by_city(hometown.title())

        if found_profiles:
            self.message_send(user_id, f'Ищу в городе {hometown.title()}')
            # обработка найденных анкет
        else:
            self.message_send(user_id,
                              f'В городе {hometown.title()} не найдено анкет')

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.handle_hello(event)
                elif event.text.lower() == 'поиск':
                    self.handle_search(event)
                elif event.text.lower() == 'стереть':
                    self.clear_database(event)
                else:
                    self.handle_unrecognized(event)

    def handle_hello(self, event):
        self.params = self.vk_tools.get_profile_info(event.user_id)
        if self.params["city"] is None:
            self.message_send(
                event.user_id,
                f'Здарово, {self.params["name"].split()[0]}!\n'
                f'Для продолжения работы укажи город')
            # сохранение состояния пользователя для следующего ввода
            self.store_user_state(event.user_id, "awaiting_city")
        else:
            self.message_send(event.user_id,
                              f'Приветствую тебя, '
                              f'{self.params["name"].split()[0]}!')

    def handle_search(self, event):
        worksheet = self.get_next_worksheet()
        shown_users = set()

        if worksheet is None:
            # Тут я делаю сразу аторизацию одной кнопкой и поиск анкет
            self.params = self.vk_tools.get_profile_info(event.user_id)
            self.worksheets = self.vk_tools.search_worksheet(self.params,
                                                             self.offset)
            worksheet = self.get_next_worksheet()
            connection = db.connect_to_database()
            db.create_table_seen_users(connection)

        if worksheet is not None and str(worksheet['id']) not in shown_users:
            shown_users.add(str(worksheet['id']))
            connection = db.connect_to_database()

            if db.check_seen_user(connection, str(worksheet['id'])):
                self.message_send(event.user_id,
                                  f"{worksheet['name']}. \nЭту анкету мы "
                                  f"уже видели.")
            else:
                photo_string = self.get_user_photo(worksheet['id'])
                self.offset += 50
                self.message_send(event.user_id,
                                  f'Посмотри, это - {worksheet["name"]}.\n'
                                  f'Вот страница VK: '
                                  f'https://vk.com/id{worksheet["id"]}',
                                  attachment=photo_string)
                db.insert_data_seen_users(connection, str(worksheet["id"]), 0)

    def get_next_worksheet(self):
        if self.worksheets:
            return self.worksheets.pop()
        else:
            return None

    def clear_database(self, event):
        try:
            self.message_send(
                event.user_id,
                'База просмотренных анкет стёрта. Можно смотреть всех снова!')
            connection = db.connect_to_database()
            db.remove_table_seen_users(connection)
            db.disconnect_from_database(connection)
        except Exception as e:
            print('Ошибка при удалении базы данных:', e)
            # Дополнительные действия при обработке ошибки, если необходимо

    def handle_unrecognized(self, event):
        self.message_send(event.user_id, 'Херню несёшь!')
        # self.find_city(event.user_id)


if __name__ == '__main__':
    bot_interface = BotInterface(community_token, access_token)
    bot_interface.event_handler()
