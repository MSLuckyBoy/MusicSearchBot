import telebot
import json
import xlwt

import DataBase
import searcher

with open("config.json") as f:
    Config = json.load(f)

bot = telebot.TeleBot(Config["tg_token"])

wb = xlwt.Workbook()
ws = wb.add_sheet("Test", cell_overwrite_ok=True)
style0 = xlwt.easyxf('font: color-index red')
style1 = xlwt.easyxf('font: color-index green')
style2 = xlwt.easyxf('font: color-index black')
style3 = xlwt.easyxf('font: bold on')


@bot.message_handler(commands=['start'])
def cmd_start(msg):
    DataBase.data_add(
        msg.from_user.id,
        msg.from_user.first_name,
        msg.from_user.last_name,
        msg.from_user.username
    )

    bot.send_message(msg.chat.id, f"Привет {msg.from_user.first_name}!")
    bot.send_message(msg.chat.id, "Чтобы искать музыку проста отправьте запись!")


@bot.message_handler(commands=['stat'])
def cmd_stat(msg):
    if msg.from_user.id in Config['admins']:
        ws.write(0, 0, "ID", style3)
        ws.write(0, 1, "First_Name", style3)
        ws.write(0, 2, "Last_Name", style3)
        ws.write(0, 3, "User_Name", style3)
        ws.write(0, 4, "Status", style3)

        x = 1
        for values in DataBase.all_users_info():
            y = 0
            for key, value in values.items():
                if key == 'username' and (value is not None):
                    ws.write(x, y, f"@{value}", style1 if values['id'] in Config['admins'] else style2)
                elif value is None:
                    ws.write(x, y, "None", style0)
                else:
                    ws.write(x, y, value, style1 if values['id'] in Config['admins'] else style2)
                y += 1
            x += 1

        wb.save("writing.xls")
        doc = open("writing.xls", 'rb')
        bot.send_document(msg.chat.id, doc)


@bot.message_handler(content_types=['voice', 'audio'])
def handler(msg):
    DataBase.data_add(
        msg.from_user.id,
        msg.from_user.first_name,
        msg.from_user.last_name,
        msg.from_user.username
    )

    bot_msg = bot.send_message(msg.chat.id, "Уже ищу!")
    bot.last_message_sent = bot_msg.chat.id, bot_msg.message_id
    user = {
        'id': msg.from_user.id,
        'first_name': msg.from_user.first_name,
        'last_name': msg.from_user.last_name,
        'username': msg.from_user.username
    }

    user_info = ""
    for key, value in user.items():
        if key == "username":
            user_info += f'{key}: @{value}\n'
        else:
            user_info += f'{key}: {value}\n'

    try:
        if msg.content_type == "voice":
            file = bot.get_file_url(msg.voice.file_id)
            print(file)
        elif msg.content_type == "audio":
            file = bot.get_file_url(msg.audio.file_id)
        else:
            file = None

        data = json.loads(searcher.search(file))
        print(data)

        music = {
            'artist': data['result']['artist'],
            'title': data['result']['title'],
            'album': data['result']['album'],
            'release_date': data['result']['release_date'],
            'song_link': data['result']['song_link']
        }

        text = f"*Названия:* _{music['title']}_\n" \
            + f"*Исполнитель:* _{music['artist']}_\n" \
            + f"*Альбом:* _{music['album']}_\n" \
            + f"*Дата выпуска:* _{music['release_date']}_\n\n" \
            + f"🎧[Слушать]({music['song_link']})\n" \
            + f"➖➖➖➖➖➖➖➖➖➖➖"

        bot.send_message(msg.chat.id, text, parse_mode="Markdown")
        bot.delete_message(*bot.last_message_sent)
        bot.send_message(Config['channel'], f"Success!\n{user_info}")
        bot.forward_message(Config['channel'], msg.chat.id, msg.message_id)

    except Exception as error:
        bot.send_message(msg.chat.id, "К сожелению я не смог найти эту музыку!\nПовторите попытку ещё раз!")
        bot.send_message(Config['channel'], f"Error: {error}\n{user_info}")
        bot.forward_message(Config['channel'], msg.chat.id, msg.message_id)


if __name__ == "__main__":
    bot.polling(none_stop=True)
