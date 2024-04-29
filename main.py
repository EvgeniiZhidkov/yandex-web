#7138618116:AAHMWU4rmmD-W48pIecOrKBxAl6z6D4ZEbI
#4de6ee8e61214f0182e130103242804

import telebot
from telebot import types
import requests

API_KEY = '4de6ee8e61214f0182e130103242804'

class WeatherBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.cities = ["Москва", "Лондон", "Париж", "Берлин", "Нью-Йорк", "Токио"]
        self.registered_users_file = 'registered_users.txt'

    def start(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            user_id = message.from_user.id
            if not self.is_registered(user_id):
                self.bot.reply_to(message, "Привет! Я бот, который дает информацию о погоде. Пожалуйста, зарегистрируйтесь с помощью команды /register.")
            else:
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                for city in self.cities:
                    markup.add(types.KeyboardButton(city))
                self.bot.reply_to(message, "Привет! Я бот, который дает информацию о погоде. Выбери город из списка ниже:", reply_markup=markup)

        @self.bot.message_handler(func=lambda message: message.text in self.cities)
        def get_weather(message):
            user_id = message.from_user.id
            if self.is_registered(user_id):
                city = message.text
                weather_data = self.fetch_weather(city)

                if weather_data:
                    weather_icon_code = weather_data['current']['condition']['icon']
                    weather_image_url = f'http:{weather_icon_code}'
                    photo = requests.get(weather_image_url)

                    with open('weather_image.png', 'wb') as photo_file:
                        photo_file.write(photo.content)

                    with open('weather_image.png', 'rb') as photo_file:
                        self.bot.send_photo(message.chat.id, photo_file, caption=f"Текущая погода в {city}: {weather_data['current']['condition']['text']}, температура {weather_data['current']['temp_c']}°C, ощущается как {weather_data['current']['feelslike_c']}°C.")
                else:
                    self.bot.reply_to(message, "Извините, не удалось получить информацию о погоде для этого города.")
            else:
                self.bot.reply_to(message, "Пожалуйста, зарегистрируйтесь с помощью команды /register.")

        @self.bot.message_handler(commands=['register'])
        def register_user_command(message):
            user_id = message.from_user.id
            if not self.is_registered(user_id):
                self.register_user(user_id)
                self.bot.reply_to(message, "Вы успешно зарегистрированы.")
            else:
                self.bot.reply_to(message, "Вы уже зарегистрированы.")

        @self.bot.message_handler(commands=['delete_account'])
        def delete_account_command(message):
            user_id = message.from_user.id
            if self.is_registered(user_id):
                self.delete_account(user_id)
                self.bot.reply_to(message, "Ваш аккаунт успешно удален.")
            else:
                self.bot.reply_to(message, "Ваш аккаунт не найден.")

        self.bot.polling()

    def is_registered(self, user_id):
        try:
            with open(self.registered_users_file, 'r') as file:
                registered_users = file.read().splitlines()
            return str(user_id) in registered_users
        except FileNotFoundError:
            return False

    def register_user(self, user_id):
        with open(self.registered_users_file, 'a') as file:
            file.write(str(user_id) + '\n')

    def delete_account(self, user_id):
        with open(self.registered_users_file, 'r') as file:
            lines = file.readlines()
        with open(self.registered_users_file, 'w') as file:
            for line in lines:
                if line.strip() != str(user_id):
                    file.write(line)

    def fetch_weather(self, city):
        url = f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&lang=ru'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

if __name__ == "__main__":
    bot = WeatherBot('7138618116:AAHMWU4rmmD-W48pIecOrKBxAl6z6D4ZEbI')
    bot.start()

