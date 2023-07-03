from vk_api.keyboard import VkKeyboard, VkKeyboardColor

keyboard = VkKeyboard(one_time=False)
keyboard.add_button('Привет', color=VkKeyboardColor.SECONDARY)
# keyboard.add_line()
keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
# keyboard.add_line()
# keyboard.add_button('Далее', color=VkKeyboardColor.NEGATIVE)
# keyboard.add_line()
