import time
import telebot
from telebot import types
import os
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

TOKEN = "YOURS_TOKEN_KEY"

bot = telebot.TeleBot(TOKEN)

stop = 0
count_photo = 0

# processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
# model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

processor = torch.load('E:/NLP/processor.pth')
model = torch.load('E:/NLP/model.pth')


@bot.message_handler(content_types=['photo'])
def handle_photo_1(message):
    global model, processor
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = 'E:/NLP/photo.jpg'  # message.photo.file_name
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.from_user.id, 'Фотография сохранена и обрабатывается')
    image = Image.open(save_path).convert('RGB')
    pixel_values = processor(images=image, return_tensors='pt')
    generated_ids = model.generate(**pixel_values)
    generated_text = processor.decode(generated_ids[0], skip_special_tokens=True)
    bot.send_message(message.from_user.id, 'На фотографии изображено/написано - ' + generated_text)
    os.remove(save_path)


@bot.message_handler(content_types=['document', 'video', 'audio', 'voice', 'sticker'])
def handle_photo_2(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = 'E:/NLP/' + message.document.file_name
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.from_user.id, 'Фотография сохранена и обрабатывается')
    image = Image.open(save_path).convert('RGB')
    pixel_values = processor(images=image, return_tensors='pt')
    generated_ids = model.generate(**pixel_values)
    generated_text = processor.decode(generated_ids[0], skip_special_tokens=True)
    bot.send_message(message.from_user.id, 'На фотографии изображено/написано - ' + generated_text)
    os.remove(save_path)


@bot.message_handler(content_types=['text'])
def start(message):
    if (message.text.lower() == "/help") or (message.text.lower() == "help"):
        bot.send_message(message.from_user.id,
                         "- Вы можете запустить светофор для этого напишите start traffic light, "
                         "а для остановки напиши stop traffic")
        bot.send_message(message.from_user.id,
                         "- Вы можете загрузить фотографию и я напишу, что там изображено")
    elif message.text == "hi":
        bot.send_message(message.from_user.id, "Привет!")
    elif message.text == "start traffic light":
        bot.send_message(message.from_user.id,
                         "Введите интервалы через запятую [3,1,2] или [-] для значений по умолчанию [7,2,5]")
        bot.register_next_step_handler(message, light_traffic_start)
    elif message.text == "stop traffic":
        traffic(message, 1)
    else:
        bot.send_message(message.from_user.id, "На пишите help для вызова подсказки")


@bot.message_handler(content_types=['text'])
def light_traffic_start(message):
    if len(message.text) == 0:
        bot.send_message(message.from_user.id,
                         "Введите интервалы через запятую [3,1,2] или [-] для значений по умолчанию [7,2,5]")
    else:
        traffic(message, 0)


def traffic(message, stopper):
    global stop

    interval = []

    if stopper == 0:
        msg = message.text
        stop = 0
        bot.send_message(message.from_user.id, 'Traffic light is START')
        bot.send_message(message.from_user.id, "'To stop process write 'stop traffic'")
    else:
        stop = 1
        bot.send_message(message.from_user.id, 'Traffic light is STOP')
        msg = '-'

    if msg == '-':
        interval = [7, 2, 5]
    else:
        while len(interval) < 3:
            try:
                delay = msg.split(',')
                try:
                    len(delay) == 3
                except Exception:
                    bot.send_message(message.from_user.id, 'Enter 3 values')
                interval = [int(i) for i in delay if i.isdigit()]
            except Exception:
                bot.send_message(message.from_user.id, 'Enter numbers like 7,2,5')

    traffic_light = {'Red': interval[0], 'Yellow': interval[1], 'Green': interval[2]}

    while stop != 1:
        for k, v in traffic_light.items():
            if stop == 1:
                break
            bot.send_message(message.from_user.id, f'Now light {k}')
            time.sleep(v)


bot.polling(none_stop=True, interval=0)
