#7138618116:AAHMWU4rmmD-W48pIecOrKBxAl6z6D4ZEbI
#4de6ee8e61214f0182e130103242804
#self.cities_en = {}
#self.cities_en["Москва"] = "Moscow"
#self.cities_en["Лондон"] = "London"
#self.cities_en["Париж"] = "Paris"
#self.cities_en["Берлин"] = "Berlin"
#self.cities_en["Нью-Йорк"] = "New-York"
#self.cities_en["Токио"] = "Tokyo"
#18bb59ab-59c0-46a4-889f-24eca41a104f
import telebot
from telebot import types
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

TELEGRAM_BOT_TOKEN = '7138618116:AAHMWU4rmmD-W48pIecOrKBxAl6z6D4ZEbI'
WEATHER_API_KEY = '4de6ee8e61214f0182e130103242804'

class WeatherBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.cities = ["Москва", "Лондон", "Париж", "Берлин", "Нью-Йорк", "Токио"]
        self.cities_en = {
            "Москва": "Moscow",
            "Лондон": "London",
            "Париж": "Paris",
            "Берлин": "Berlin",
            "Нью-Йорк": "New York",
            "Токио": "Tokyo"
        }
        self.registered_users_file = 'registered_users.txt'
        self.feedback_file = 'feedback.txt'
        self.fl = False

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
                local_time_data = self.get_local_time(city)

                if weather_data and local_time_data:
                    weather_icon_code = weather_data['current']['condition']['icon']
                    weather_image_url = f'http:{weather_icon_code}'
                    photo = requests.get(weather_image_url)

                    with open('weather_image.png', 'wb') as photo_file:
                        photo_file.write(photo.content)

                    with open('weather_image.png', 'rb') as photo_file:
                        weather_caption = f"<b>Текущая погода в {city}:</b>\n{weather_data['current']['condition']['text']}, температура {weather_data['current']['temp_c']}°C, ощущается как {weather_data['current']['feelslike_c']}°C, скорость ветра {weather_data['current']['wind_kph']} км/ч."
                        local_time_caption = f"<b>Местное время в {city}:</b>\n{self.format_local_time(local_time_data['datetime'])}"
                        clothing_advice = self.get_clothing_advice(weather_data['current']['temp_c'])

                        self.bot.send_photo(message.chat.id, photo_file, caption=f"{weather_caption}\n\n{local_time_caption}\n\n<b>Совет по одежде:</b>\n{clothing_advice}", parse_mode='HTML')

                        # Добавляем график температуры на 5 дней
                        forecast_data = self.fetch_forecast(city)
                        if forecast_data:
                            self.plot_temperature_forecast(forecast_data)
                            with open('temperature_forecast.png', 'rb') as forecast_file:
                                self.bot.send_photo(message.chat.id, forecast_file, caption="Прогноз температуры на 5 дней")

                            # Добавляем график скорости ветра на 5 дней
                            self.plot_wind_speed_forecast(forecast_data)
                            with open('wind_speed_forecast.png', 'rb') as wind_speed_file:
                                self.bot.send_photo(message.chat.id, wind_speed_file, caption="Прогноз скорости ветра на 5 дней")
                        else:
                            self.bot.reply_to(message, "Извините, не удалось получить прогноз погоды.")

                    # Запрашиваем отзыв
                    self.bot.send_message(message.chat.id, "Пожалуйста, оставьте ваш отзыв о боте, чтобы мы могли улучшить его.")
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

        @self.bot.message_handler(commands=['feedback'])
        def feedback_command(message):
            self.bot.reply_to(message, "Напишите ваш отзыв о боте.")
            self.fl = True

        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            if self.fl:
                self.save_feedback(message)
            elif message.text == '/help' or message.text == '?':
                commands = "\n".join(['/start - начать работу', '/register - зарегистрироваться', '/delete_account - удалить аккаунт', '/feedback - оставить отзыв'])
                self.bot.reply_to(message, f" Вот список доступных команд:\n{commands}\nCписок городов, для которых доступна погода:\n{', '.join(self.cities)}")
            else:
                self.bot.reply_to(message, "К сожалению, такой команды не существует. Если вам нужна помощь, воспользуйтесь командой /help.")

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
        url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=ru'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_local_time(self, city):
        if city == "Нью-Йорк":
            url = 'http://worldtimeapi.org/api/timezone/America/New_York?lang=ru'
        elif city == "Токио":
            url = 'http://worldtimeapi.org/api/timezone/Asia/Tokyo?lang=ru'
        else:
            url = f'http://worldtimeapi.org/api/timezone/Europe/{self.cities_en[city]}?lang=ru'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def format_local_time(self, local_time):
        time_obj = datetime.strptime(local_time, '%Y-%m-%dT%H:%M:%S.%f%z')
        formatted_time = time_obj.strftime('%d.%m.%Y %H:%M:%S')
        return formatted_time

    def get_clothing_advice(self, temperature):
        if temperature < -10:
            return "На улицу лучше выйти в теплой куртке, шапке, шарфе и перчатках."
        elif -10 <= temperature < 0:
            return "На улицу лучше выйти в зимней куртке, шарфе и перчатках."
        elif 0 <= temperature < 10:
            return "На улицу лучше выйти в осенней куртке."
        elif 10 <= temperature < 20:
            return "На улицу лучше выйти в свитере или кофте."
        elif 20 <= temperature < 30:
            return "На улицу лучше выйти в футболке или майке."
        else:
            return "На улицу лучше выйти в легкой одежде, возможно в шортах и футболке."

    def fetch_forecast(self, city):
        url = f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=5&lang=ru'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def plot_temperature_forecast(self, forecast_data):
        dates = []
        temps = []
        for day in forecast_data['forecast']['forecastday']:
            date = datetime.strptime(day['date'], '%Y-%m-%d').date()
            temp = day['day']['avgtemp_c']
            dates.append(date)
            temps.append(temp)
        plt.figure(figsize=(8, 5))
        plt.plot(dates, temps, marker='o', linestyle='-')
        plt.title('Прогноз температуры на 5 дней')
        plt.xlabel('Дата')
        plt.ylabel('Температура, °C')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('temperature_forecast.png')

    def plot_wind_speed_forecast(self, forecast_data):
        dates = []
        wind_speeds = []
        for day in forecast_data['forecast']['forecastday']:
            date = datetime.strptime(day['date'], '%Y-%m-%d').date()
            wind_speed = day['day']['maxwind_kph']
            dates.append(date)
            wind_speeds.append(wind_speed)
        plt.figure(figsize=(8, 5))
        plt.plot(dates, wind_speeds, marker='o', linestyle='-')
        plt.title('Прогноз скорости ветра на 5 дней')
        plt.xlabel('Дата')
        plt.ylabel('Скорость ветра, км/ч')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('wind_speed_forecast.png')

    def save_feedback(self, message):
        feedback = message.text
        with open(self.feedback_file, 'a', encoding='utf-8') as file:
            file.write(feedback + '\n')
        self.fl = False
        self.bot.reply_to(message, "Спасибо за ваш отзыв! Он был сохранен.")

if __name__ == "__main__":
    bot = WeatherBot(TELEGRAM_BOT_TOKEN)
    bot.start()


