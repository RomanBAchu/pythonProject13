from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Создаем объект клавиатуры чтобы клавиатура не исчезала после нажатия на кнопку.
keyboard = VkKeyboard(one_time=False)

# # Добавляем кнопку "Привет" серым цветом
# keyboard.add_button('Привет', color=VkKeyboardColor.SECONDARY)

# Добавляем кнопку "Поиск" зелёным
keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
