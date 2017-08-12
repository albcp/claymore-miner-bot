#!/usr/bin/python3

import socket
import json
import telebot

token = "" #Token given by BotFather
miner_ip = "" #IP of the rig (localhost if running bot in the rig)
port =  #Port where claymore's miner is listening (default 3333)
my_id =  #Your telegram id (You can get it from https://telegram.me/my_id_bot)


bot = telebot.TeleBot(token)

def contact_miner(r):
    if r == "info":
        request = b'{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'
    elif r == "restart_miner":
        request = b'{"id":0,"jsonrpc":"2.0","method":"miner_restart"}'
    elif r == "reboot_rig":
        request = b'{"id":0,"jsonrpc":"2.0","method":"miner_reboot"}'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((miner_ip, port))
        except Exception:
            return None
        s.sendall(request)
        data = s.recv(1024)
        if data != b'':
            return(json.loads(data.decode('utf-8'))['result'])

def is_owner(message):
    if message.from_user.id == my_id:
        return True

def report_error(message):
    bot.reply_to(message, "I am having problems contacting with the rig, please check that the *IP* and the *port* are correct.",parse_mode="markdown")

@bot.message_handler(commands=['start','help'])
def send_commands(message):
    if not is_owner(message):
        return None
    bot.reply_to(message, "/hashrate - Shows the mining hashrate.\n/main - Shows the main coin hashrate of each GPU.\n/dual - Shows the dual coin hashrate of each GPU.\n/gpu_info - Send the temperature and fan speed of the GPUs.\n/info - Send miner version and uptime.\n/restart - Restart Claymore's miner.\n/reboot - Reboot the rig (calls reboot script in miner folder).\n/help - Shows this message.")

@bot.message_handler(commands=['hashrate'])
def send_total(message):
    if not is_owner(message):
        return None
    answer = contact_miner("info")
    if answer != None:
        main_raw=answer[2].split(';')
        hashrate = '*Main coin*:\n    Hashrate: %0.3f Mh/s\n    Shares found: %s\n    Rejected Shares: %s'  %(int(main_raw[0])/1000, main_raw[1], main_raw[2])
        if len(answer[7].split(";"))==2:
            dual_raw=answer[4].split(';')
            hashrate += '\n*Dual coin*:\n    Hashrate: %0.3f Mh/s\n    Shares found: %s\n    Rejected Shares: %s'  %(int(dual_raw[0])/1000, dual_raw[1], dual_raw[2])
        bot.reply_to(message, hashrate,parse_mode="markdown")
    else: report_error(message)

@bot.message_handler(commands=['gpu_info'])
def send_gpu_info(message):
    if not is_owner(message):
        return None
    answer = contact_miner("info")
    if answer != None:
        gpus = answer[6].split(';')
        gpu_info = "\n*GPU information:*"
        for x in range(0,len(gpus)//2):
            gpu_info += "\n    *GPU%d:*\n        Temperature: %sºC\n        Fan Speed: %s%%" % (x, gpus[x*2], gpus[x*2+1])
            #gpu_info += "\n    *GPU%d:* 🌡️%sºC   🌬️%s%%" % (x, gpus[x*2], gpus[x*2+1]) #With EMOJIS instead of text :D
        bot.reply_to(message, gpu_info,parse_mode="markdown")
    else: report_error(message)

@bot.message_handler(commands=['main'])
def send_main_hashrate(message):
    if not is_owner(message):
        return None
    answer = contact_miner("info")
    if answer != None:
        single = answer[3].split(';')
        single_hashrate_main = "*Main coin hashrate of each GPU:*"
        for x, hashrate in enumerate(single):
            single_hashrate_main += "\n    *GPU%d:* %0.3f Mh/s" % (x,float(hashrate)/1000)
        bot.reply_to(message, single_hashrate_main,parse_mode="markdown")
    else: report_error(message)

@bot.message_handler(commands=['dual'])
def send_dual_hashrate(message):
    if not is_owner(message):
        return None
    answer = contact_miner("info")
    if answer != None:
        single = answer[5].split(';')
        single_hashrate_dual = "*Dual coin hashrate of each GPU:*"
        for x, hashrate in enumerate(single):
            single_hashrate_dual += "\n    *GPU%d:* %0.3f Mh/s" % (x,float(hashrate)/1000)
        bot.reply_to(message, single_hashrate_dual,parse_mode="markdown")
    else: report_error(message)

@bot.message_handler(commands=['info'])
def send_info(message):
    if not is_owner(message):
        return None
    answer = contact_miner("info")
    if answer != None:
        time=int(answer[1])
        general_info = "*Version:* %s\n*Uptime:* %s Days, %s Hours, %s Minutes." % (answer[0], time//60//24, time//60%24, time%60)
        bot.reply_to(message, general_info,parse_mode="markdown")
    else: report_error(message)

@bot.message_handler(commands=['restart'])
def restart(message):
    if not is_owner(message):
        return None
    contact_miner("restart_miner")
    bot.reply_to(message, "Restarting miner.",parse_mode="markdown")

@bot.message_handler(commands=['reboot'])
def restart(message):
    if not is_owner(message):
        return None
    contact_miner("reboot_rig")
    bot.reply_to(message, "Rebooting ring.",parse_mode="markdown")

bot.polling()
