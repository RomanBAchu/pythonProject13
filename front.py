import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

import db
from back import VkTools
from config import community_token, access_token
from keyboard import *


class Bot_interface():
    def __init__(self, community_token, access_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(access_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0

        print(' \n V\n K\n i\n n       готов!\n d\n e\n r\n', sep='\n')

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
        # Функция получения города в случае его отсутствия в профиле
        self.message_send(user_id, 'Введи название города для поиска: ')
        message, user_id = self.event_handler()
        hometown = str(message)
        cities = self.vk_tools.get_cities(user_id)
        for city in cities:
            if city['title'] == hometown.title():
                self.message_send(user_id, f'Ищу в городе {hometown.title()}')
                return hometown.title()

        self.message_send(user_id, 'Непонятно')
        self.find_city(user_id)

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет' or event.text.lower() == 'поиск':
                    '''Логика для получения данных о пользователе'''
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    # Запрос доп. информации, в случае если она отсутствует в профиле
                    if self.params["city"] is None:
                        self.message_send(
                            event.user_id, f'Привет, привет {self.params["name"]}!\n'
                                           f'Для продолжения работы с ботом укажи свой город')
                        event.to_me = self.find_city(event.user_id)
                    else:

                        if event.text.lower() == 'привет':
                            name_parts = self.params["name"].split()
                            first_name = name_parts[0]

                            self.message_send(event.user_id, f'Здарова, {first_name}! &#128587;&#8205;&#9794;&#65039;')





                        elif event.text.lower() == 'поиск':

                            photo_string = None  # Значение по умолчанию

                            if self.worksheets:

                                try:
                                    worksheet = self.worksheets.pop()

                                    photo_string = self.get_user_photo(worksheet['id'])



                                except IndexError:

                                    self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)

                                    worksheet = self.worksheets.pop()

                            else:

                                self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)

                                if len(self.worksheets) > 0:

                                    worksheet = self.worksheets.pop()

                                else:

                                    # обработка случая, когда список пустой

                                    worksheet = None  # или выполните нужные действия вместо использования метода pop()

                            connection = db.connect_to_database()

                            db.create_table_seen_users(connection)

                            num_users_shown = 0  # Количество показанных пользователей

                            shown_users = set()  # Множество показанных пользователей

                            print(f"Показано {num_users_shown} анкет")

                            # Выполнение кода

                            # worksheet = None
                            num_users_shown = 0

                            while num_users_shown < 1:
                                if 'worksheet' in locals() or 'worksheet' in globals():
                                    if worksheet is not None:
                                        # Преобразование словаря в кортеж
                                        worksheet_tuple = tuple(worksheet.items())
                                        if worksheet_tuple not in shown_users:
                                            shown_users.add(worksheet_tuple)
                                            num_users_shown += 1

                                            # Проверка наличия пользователя в БД
                                            if db.check_seen_user(connection, str(worksheet['id'])):
                                                self.message_send(event.user_id,
                                                                  f"{worksheet['name']}\n\n Мы с тобой уже видели эту анкету. &#128522;")
                                                continue



                                self.offset += 50

                                if 'worksheet' in locals() or 'worksheet' in globals():
                                    if worksheet is not None:
                                        self.message_send(event.user_id,
                                                          f'Посмотри, это - {worksheet["name"]}.\nВот страница VK: https://vk.com/id{worksheet["id"]}',
                                                          attachment=photo_string)




                                        connection = db.connect_to_database()
                                        db.insert_data_seen_users(connection, str(worksheet["id"]), 0)

                                # Добавить анкету в бд в соответствие с event.user_id
                                connection = db.connect_to_database()
                                if 'worksheet' in locals() or 'worksheet' in globals():
                                    if worksheet is not None and "id" in worksheet:
                                        db.insert_data_seen_users(connection, str(worksheet["id"]), 0)

                                        print(f"Новая {num_users_shown} анкет")



                elif event.text.lower() == 'выкл':

                    self.message_send(event.user_id, 'ВЫКЛЮЧАЮ ПРОГУ')

                    # Очистка сохраненных данных (если они есть)

                    connection = db.connect_to_database()

                    db.remove_table_seen_users(connection)

                    db.disconnect_from_database(connection)








                else:
                    self.message_send(event.user_id, 'Если хочешь, что бы я находил тебе '
                                                     'подходящих людей, то поздоровайся со мной, а потом ищи!\n\n Если '
                                                     'сразу будешь искать, то я буду находить кого попало.\n\n Так же можешь '
                                                     'нажимать на мои кнопочки. &#128077;')


if __name__ == '__main__':
    bot_interface = Bot_interface(community_token, access_token)
    bot_interface.event_handler()
