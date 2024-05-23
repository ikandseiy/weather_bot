import requests
import datetime
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Напиши мне название города, и я пришлю сводку погоды! Используй команду /forecast <город> для прогноза на 3 дня.")

@dp.message_handler(commands=["forecast"])
async def get_forecast(message: types.Message):
    args = message.get_args()
    if not args:
        await message.reply("Пожалуйста, укажите город после команды, например: /forecast Moscow")
        return

    city = args
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={open_weather_token}&units=metric&lang=ru"
        )

        data = r.json()

        if data["cod"] != "200":
            await message.reply("Не удалось получить данные. Проверьте правильность названия города.")
            return


        forecast_data = data["list"]
        if len(forecast_data) < 24 * 3 / 8:
            await message.reply("Недостаточно данных для составления прогноза на 3 дня.")
            return

        forecast_message = f"Прогноз погоды для города {city} на 3 дня:\n"
        for i in range(0, min(24 * 3, len(forecast_data)), 8):
            date = datetime.datetime.fromtimestamp(forecast_data[i]["dt"]).strftime('%Y-%m-%d %H:%M')
            temp = forecast_data[i]["main"]["temp"]
            desc = forecast_data[i]["weather"][0]["description"]
            forecast_message += f"Дата: {date}, Температура: {temp}°C, Погода: {desc}\n"

        await message.reply(forecast_message)
    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")

@dp.message_handler()
async def get_weather(message: types.Message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Морось \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
        )
        data = r.json()


        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "У нас нет смайлика для описания такой погоды ;)"

        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        await message.reply(f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
              f"\nПогода в городе: {city}\n{'-' * 100}\nТемпература: {cur_weather}C° {wd}\n"
              f"{'-' * 100}\n"  
              f"Влажность: {humidity}%\n{'-' * 100}\nВетер: {wind} м/с\n"
              f"{'-' * 100}\n"  
              f"Восход солнца: {sunrise_timestamp}\n{'-' * 100}\nЗакат солнца: {sunset_timestamp}\n{'-' * 100}\nПродолжительность дня: {length_of_the_day}"
              )

    except:
        await message.reply("\U00002620\U0001F622 Проверьте название города \U0001F622\U00002620")


if __name__ == '__main__':
    executor.start_polling(dp)