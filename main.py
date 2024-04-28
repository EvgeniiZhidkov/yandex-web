#7138618116:AAHMWU4rmmD-W48pIecOrKBxAl6z6D4ZEbI
#4de6ee8e61214f0182e130103242804

import telebot
from telebot import types
import requests

API_KEY = '4de6ee8e61214f0182e130103242804'

bot = telebot.TeleBot('7138618116:AAHMWU4rmmD-W48pIecOrKBxAl6z6D4ZEbI')

cities = ["Москва", "Лондон", "Париж", "Берлин", "Нью-Йорк", "Токио"]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for city in cities:
        markup.add(types.KeyboardButton(city))
    bot.reply_to(message, "Привет! Я бот, который дает информацию о погоде. Выбери город из списка ниже:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in cities)
def get_weather(message):
    city = message.text
    weather_data = fetch_weather(city)

    if weather_data:
        weather_icon_code = weather_data['current']['condition']['icon']
        weather_image_url = f'http:{weather_icon_code}'
        photo = requests.get(weather_image_url)

        with open('weather_image.png', 'wb') as photo_file:
            photo_file.write(photo.content)

        with open('weather_image.png', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption=f"Текущая погода в {city}: {weather_data['current']['condition']['text']}, температура {weather_data['current']['temp_c']}°C, ощущается как {weather_data['current']['feelslike_c']}°C.")
    else:
        bot.reply_to(message, "Извините, не удалось получить информацию о погоде для этого города.")

def fetch_weather(city):
    url = f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&lang=ru'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


bot.polling()


