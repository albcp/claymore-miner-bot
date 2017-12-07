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
    bot.reply_to(message, "/hashrate - Shows the mining hashrate.\n/main - Shows the main coin hashrate of each GPU.\n/dual - Shows the dual coin hashrate of each GPU.\n/gpu_info - Send the temperature and fan speed of the GPUs.\n/info - Send miner version and uptime.\n/restart - Restart Claymore's miner.\n/reboot - Reboot the rig (calls reboot script in miner folder).\n/status - Shows the rig list and their state (on/off).\n/help - Shows this message.")

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
            reply += '*Main coin*:\n    Hashrate: {:0.3f} Mh/s\n    Shares found: {}\n    Rejected Shares: {}'.format(int(main_raw[0])/1000, main_raw[1], main_raw[2])
            if len(answer[7].split(";"))==2:
                dual_raw=answer[4].split(';')
                reply += '\n*Dual coin*:\n    Hashrate: {:0.3f} Mh/s\n    Shares found: {}\n    Rejected Shares: {}'.format(int(dual_raw[0])/1000, dual_raw[1], dual_raw[2])
        else:
            reply += "I am having problems contacting with *{0[0]}*, please check that the *IP {0[1]}* and the *port {0[2]}* are correct.".format(rig)
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
            reply += "*GPU information:*"
            for x in range(0,len(gpus)//2):
                reply += "\n    *GPU{}:*\n        Temperature: {}ºC\n        Fan Speed: {}%".format(x, gpus[x*2], gpus[x*2+1])
                #reply += "\n    *GPU{}:* 🌡️{}ºC   🌬️{}%".format(x, gpus[x*2], gpus[x*2+1]) #With EMOJIS instead of text :D
        else:
            reply += "I am having problems contacting with *{0[0]}*, please check that the *IP {0[1]}* and the *port {0[2]}* are correct.".format(rig)
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
            reply += "*Main coin hashrate of each GPU:*"
            for x, hashrate in enumerate(single):
                reply += "\n    *GPU{}:* {:0.3f} Mh/s".format(x,float(hashrate)/1000)
        else:
            reply += "I am having problems contacting with *{0[0]}*, please check that the *IP {0[1]}* and the *port {0[2]}* are correct.".format(rig)
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
                    reply += "\n    *GPU{}:* dual mining is off".format(x)
        else:
            reply += "\nI am having problems contacting with *{0[0]}*, please check that the *IP {0[1]}* and the *port {0[2]}* are correct.".format(rig)
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
            reply += "*Version:* {}\n*Uptime:* {} Days, {} Hours, {} Minutes.".format(answer[0], time//60//24, time//60%24, time%60)
        else:
            reply += "I am having problems contacting with *{0[0]}*, please check that the *IP {0[1]}* and the *port {0[2]}* are correct.".format(rig)
    bot.reply_to(message, reply,parse_mode="markdown")

@bot.message_handler(commands=['status'])
def status(message):
    if not is_owner(message):
        return None
    reply=''
    for rig in rigs:
        answer = contact_miner("info",rig[1],rig[2])
        if answer != None:
            status = 'on ✅'
        else:
            status = 'off 🔴'
        reply += "*{}* is {}\n".format(rig[0], status)
    bot.reply_to(message, reply,parse_mode="markdown")


@bot.message_handler(commands=['restart'])
def restart(message):
    if not is_owner(message):
        return None
    choose = message.text[9:]
    reply = ''
    if choose != '':
        if choose == 'all':
            reply = 'Restarting all the miners'
            for rig in rigs:
                contact_miner("restart_miner",rig[1],rig[2])
        else:
            for rig in rigs:
                if choose in rig:
                    contact_miner("restart_miner",rig[1],rig[2])
                    reply = "Restarting *{}*".format(rig[0])
    else:
        reply = "You must enter the name of the rig after /restart or *all* to restart all the miners."
    if reply == "":
        reply = "Sorry, I am not able to find the rig"
    bot.reply_to(message, reply, parse_mode="markdown")

@bot.message_handler(commands=['reboot'])
def restart(message):
    if not is_owner(message):
        return None
    choose = message.text[8:]
    reply = ''
    if choose != '':
        if choose == 'all':
            reply = 'Rebooting all the rigs'
            for rig in rigs:
                contact_miner("reboot_rig",rig[1],rig[2])
        else:
            for rig in rigs:
                if choose in rig:
                    contact_miner("reboot_rig",rig[1],rig[2])
                    reply = "Rebooting *{}*".format(rig[0])
    else:
        reply = "You must enter the name of the rig after /reboot or *all* to reboot all the rigs."
    if reply == "":
        reply = "Sorry, I am not able to find the rig"
    bot.reply_to(message, reply, parse_mode="markdown")


alarm = Process(target=check_status)
alarm.start()

bot.polling()
