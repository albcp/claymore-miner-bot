#!/usr/bin/python3
import socket
import json
import telebot
import time
from multiprocessing import Process
from config import *
bot = telebot.TeleBot(token)


def contact_miner(r,ip,port):
    if r == "info":
        request = b'{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'
    elif r == "restart_miner":
        request = b'{"id":0,"jsonrpc":"2.0","method":"miner_restart"}'
    elif r == "reboot_rig":
        request = b'{"id":0,"jsonrpc":"2.0","method":"miner_reboot"}'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, port))
        except Exception:
            return None
        s.sendall(request)
        data = s.recv(1024)
        if data != b'':
            return(json.loads(data.decode('utf-8'))['result'])

def is_owner(message):
    if message.from_user.id == my_id:
        return True
    else:
        bot.reply_to(message, "https://github.com/albcp/claymore-miner-bot")


def check_status():
    rigs_status = {}
    while(True):
        report = ''
        for rig in rigs:
            answer = contact_miner("info",rig[1],rig[2])
            if answer != None:
                status = 'on';
            else:
                status = 'off';
            if rig[0] in rigs_status:
                if rigs_status[rig[0]] != status:
                    report += '\n*{}* is now *{}*'.format(rig[0], status)
            rigs_status[rig[0]] = status
        if report != '':
            bot.send_message(my_id, report, parse_mode="markdown")
            report = ''
        time.sleep(60)

		
		
@bot.message_handler(commands=['start','help'])
def send_commands(message):
    if not is_owner(message):
        return None
    bot.reply_to(message, "/hashrate - Отображает хешрейт.\n/main - Отображает хешрейт основной валюты по каждой GPU.\n/dual - Отображает хешрейт вторичной валюты по каждой GPU..\n/gpu_info - Отображает Температуру и обороты кулеров GPU.\n/info - Отображает версию майнера и текущее время работы.\n/restart - Перезапуск майнера Claymore\n/reboot - Перезапуск Рига (Вызывает Reboot.bat(sh) из каталога майнера).\n/status - Отображает список и статус ригов(ВКЛ/ВЫКЛ).\n/help - Отображает это сообщение.")

@bot.message_handler(commands=['hashrate'])
def send_total(message):
    if not is_owner(message):
        return None
    reply=''
    for rig in rigs:
        reply += "\n\n*⛏" + rig[0] + "⛏*\n"
        answer = contact_miner("info",rig[1],rig[2])
        if answer != None:
            main_raw=answer[2].split(';')
            reply += '*Основная валюта*:\n    Хэшрейт: {:0.3f} Mh/s\n    Найдено шар: {}\n    Отклоненых шар: {}'.format(int(main_raw[0])/1000, main_raw[1], main_raw[2])
            if len(answer[7].split(";"))==2:
                dual_raw=answer[4].split(';')
                reply += '\n*Вторичная валюта*:\n    Хэшрейт: {:0.3f} Mh/s\n    Найдено шар: {}\n    Отклоненых шар: {}'.format(int(dual_raw[0])/1000, dual_raw[1], dual_raw[2])
        else:
            reply += "\nНет соединения с ригом *{0[0]}*, проверьте валидность введенных *IP {0[1]}* и *порта {0[2]}* ".format(rig)
    bot.reply_to(message, reply,parse_mode="markdown")

@bot.message_handler(commands=['gpu_info'])
def send_gpu_info(message):
    if not is_owner(message):
        return None
    reply=''
    for rig in rigs:
        reply += "\n\n*⛏" + rig[0] + "⛏*\n"
        answer = contact_miner("info",rig[1],rig[2])
        if answer != None:
            gpus = answer[6].split(';')
            reply += "*Информация о GPU:*"
            for x in range(0,len(gpus)//2):
                reply += "\n    *GPU{}:* 🌡️{}ºC   🌬️{}%".format(x, gpus[x*2], gpus[x*2+1])
                #reply += "\n    *GPU{}:*\n        Температура: {}ºC\n        Обороты кулера: {}%".format(x, gpus[x*2], gpus[x*2+1])
        else:
            reply += "\nНет соединения с ригом *{0[0]}*, проверьте валидность введенных *IP {0[1]}* и *порта {0[2]}* ".format(rig)
    bot.reply_to(message, reply,parse_mode="markdown")

@bot.message_handler(commands=['main'])
def send_main_hashrate(message):
    if not is_owner(message):
        return None
    reply=''
    for rig in rigs:
        reply += "\n\n*⛏" + rig[0] + "⛏*\n"
        answer = contact_miner("info",rig[1],rig[2])
        if answer != None:
            single = answer[3].split(';')
            reply += "*Хешрейт основной валюты по каждой GPU:\n*"
            for x, hashrate in enumerate(single):
                reply += "\t    *GPU{}:* {:0.3f} Mh/s".format(x,float(hashrate)/1000)
        else:
            reply += "\nНет соединения с ригом *{0[0]}*, проверьте валидность введенных *IP {0[1]}* и *порта {0[2]}* ".format(rig)
    bot.reply_to(message, reply,parse_mode="markdown")

@bot.message_handler(commands=['dual'])
def send_dual_hashrate(message):
    if not is_owner(message):
        return None
    reply=''
    for rig in rigs:
        reply += "\n\n*⛏" + rig[0] + "⛏*"
        answer = contact_miner("info",rig[1],rig[2])
        if answer != None:
            single = answer[5].split(';')
            for x, hashrate in enumerate(single):
                if hashrate != 'off':
                    reply += "\n    *GPU{}:* {:0.3f} Mh/s".format(x,float(hashrate)/1000)
                else:
                    reply += "\n    *GPU{}:* Дуал майнинг отключен".format(x)
        else:
            reply += "\nНет соединения с ригом *{0[0]}*, проверьте валидность введенных *IP {0[1]}* и *порта {0[2]}* ".format(rig)
    bot.reply_to(message, reply,parse_mode="markdown")

@bot.message_handler(commands=['info'])
def send_info(message):
    if not is_owner(message):
        return None
    reply=''
    for rig in rigs:
        reply += "\n\n*⛏" + rig[0] + "⛏*\n"
        answer = contact_miner("info",rig[1],rig[2])
        if answer != None:
            time=int(answer[1])
            reply += "*Версия:* {}\n*Аптайм:* {} Дней, {} Часов, {} Минут.".format(answer[0], time//60//24, time//60%24, time%60)
        else:
            reply += "\nНет соединения с ригом *{0[0]}*, проверьте валидность введенных *IP {0[1]}* и *порта {0[2]}* ".format(rig)
    bot.reply_to(message, reply,parse_mode="markdown")

@bot.message_handler(commands=['status'])
def status(message):
    if not is_owner(message):
        return None
    reply=''
    for rig in rigs:
        answer = contact_miner("info",rig[1],rig[2])
        if answer != None:
            status = 'Вкл. ✅'
        else:
            status = 'Выкл. 🔴'
        reply += "*{}* сейчас {}\n".format(rig[0], status)
    bot.reply_to(message, reply,parse_mode="markdown")


@bot.message_handler(commands=['restart'])
def restart(message):
    if not is_owner(message):
        return None
    choose = message.text[9:]
    reply = ''
    if choose != '':
        if choose == 'all':
            reply = 'Перезапуск майнеров на *ВСЕХ* ригах'
            for rig in rigs:
                contact_miner("restart_miner",rig[1],rig[2])
        else:
            for rig in rigs:
                if choose in rig:
                    contact_miner("restart_miner",rig[1],rig[2])
                    reply = "Перезапуск *{}*".format(rig[0])
    else:
        reply = "Вы должны ввести имя рига после /restart или *all* для перезапуска майнеров на всех ригах."
    if reply == "":
        reply = "Извините я не могу найти данный риг"
    bot.reply_to(message, reply, parse_mode="markdown")

@bot.message_handler(commands=['reboot'])
def restart(message):
    if not is_owner(message):
        return None
    choose = message.text[8:]
    reply = ''
    if choose != '':
        if choose == 'all':
            reply = 'Перезагрузка Всех ригов'
            for rig in rigs:
                contact_miner("reboot_rig",rig[1],rig[2])
        else:
            for rig in rigs:
                if choose in rig:
                    contact_miner("reboot_rig",rig[1],rig[2])
                    reply = "Перезагрузка *{}*".format(rig[0])
    else:
        reply = "Вы должны ввести имя рига после /reboot или *all* для перезапуска майнеров на всех ригах."
    if reply == "":
        reply = "Извините я не могу найти данный риг"
    bot.reply_to(message, reply, parse_mode="markdown")


alarm = Process(target=check_status)
alarm.start()

bot.polling()
