#!/usr/bin/env python

import json
import logging
import signal
import socket
import subprocess
import sys
import threading
import time
from functools import wraps

import telebot


#Token given by BotFather
token = ''

#IP of the rig (localhost if running bot in the rig)
miner_ip = 'localhost'

#Port where claymore's miner is listening (default 3333)
port = 3333

#Your telegram id (You can get it from https://telegram.me/my_id_bot)
my_id = 0


bot = telebot.TeleBot(token)

logger = telebot.logger
logger.setLevel(logging.DEBUG)


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


def smi():
    cmd = 'nvidia-smi --query-gpu=temperature.gpu,fan.speed,power.draw,clocks.sm,clocks.mem --format=csv,noheader'
    info = subprocess.getoutput(cmd)
    lines = info.split('\n') if info else []
    return [line.split(',') for line in lines]


def owner(handler):
    @wraps(handler)
    def inner(message):
        if message.from_user.id == my_id:
            return handler(message)
    return inner


def send_error(message):
    bot.send_message(
        message.chat.id, 
        'I am having problems contacting with the rig, please check that the *IP* and the *port* are correct.',
        parse_mode='markdown'
    )


@bot.message_handler(commands=['start','help'])
@owner
def help_handler(message):
    help_msg = [
        '/hashrate - Shows the mining hashrate.',
        '/main - Shows the main coin hashrate of each GPU.',
        '/dual - Shows the dual coin hashrate of each GPU.',
        '/gpu_info - Send the temperature and fan speed of the GPUs.',
        '/info - Send miner version and uptime.',
        '/restart - Restart Claymore\'s miner.',
        '/reboot - Reboot the rig (calls reboot script in miner folder).',
        '/help - Shows this message.',
    ]

    bot.send_message(message.chat.id, '\n'.join(help_msg))


@bot.message_handler(commands=['hashrate'])
@owner
def hashrate_handler(message):
    answer = contact_miner('info')

    if answer is not None:

        def hashrate_info(raw):
            hashrate_format = '\n'.join([
                '  Hashrate: {} Mh/s',
                '  Shares found: {}',
                '  Rejected Shares: {}',
            ])
            return(hashrate_format.format(
                int(raw[0])/1000,
                raw[1],
                raw[2],
            ))

        main_raw = answer[2].split(';')
        dual_raw = ''

        if len(answer[7].split(';')) == 2:
            dual_raw = answer[4].split(';')

        msg = '*Main coin*:\n' + hashrate_info(main_raw)
        if dual_raw:
            msg += '\n*Dual coin*:\n' + hashrate_info(dual_raw)

        bot.send_message(message.chat.id, msg, parse_mode='markdown')

    else: send_error(message)


@bot.message_handler(commands=['gpu_info'])
@owner
def gpu_info_handler(message):
    result = smi()
    if result:
        info_format = '\n'.join([
            '    Temp: {} ºC',
            '    Fan: {}',
            '    Power: {}',
            '    Core: {}',
            '    Mem: {}',
        ])

        info = smi()

        msg = '*GPU information:*\n'
        for n, line in enumerate(info):
           msg += 'GPU{}:\n{}\n'.format(n, info_format.format(*line))

        bot.send_message(message.chat.id, msg, parse_mode='markdown')
    else:
        send_error(message)


@bot.message_handler(commands=['main'])
@owner
def main_handler(message):
    answer = contact_miner('info')
    if answer is not None:
        single = answer[3].split(';')
        single_hashrate_main = '*Main coin hashrate of each GPU:*'
        for x, hashrate in enumerate(single):
            single_hashrate_main += '\n    *GPU%d:* %0.3f Mh/s' % (x, float(hashrate)/1000)
        bot.send_message(message.chat.id, single_hashrate_main, parse_mode='markdown')
    else: 
        send_error(message)


@bot.message_handler(commands=['dual'])
@owner
def dual_handler(message):
    answer = contact_miner('info')
    if answer != None:
        single = answer[5].split(';')
        single_hashrate_dual = '*Dual coin hashrate of each GPU:*'
        for x, hashrate in enumerate(single):
            try:
                hashrate = '%0.3f Mh/s' % float(hashrate) / 1000
            except ValueError:
                pass
            single_hashrate_dual += '\n    *GPU%d:* %s' % (x, hashrate)
        bot.send_message(message.chat.id, single_hashrate_dual, parse_mode='markdown')
    else:
        send_error(message)


@bot.message_handler(commands=['info'])
@owner
def info_handler(message):
    answer = contact_miner('info')
    if answer is not None:
        time = int(answer[1])
        general_info = \
            '*Version:* %s\n*Uptime:* %s Days, %s Hours, %s Minutes.' % \
            (answer[0], time//60//24, time//60%24, time%60)
        bot.send_message(message.chat.id, general_info, parse_mode='markdown')
    else:
        send_error(message)


@bot.message_handler(commands=['restart'])
@owner
def restart(message):
    contact_miner('restart_miner')
    bot.send_message(message.chat.id, 'Restarting miner.', parse_mode='markdown')


@bot.message_handler(commands=['reboot'])
@owner
def restart(message):
    contact_miner('reboot_rig')
    bot.send_message(message.chat.id, 'Rebooting ring.', parse_mode='markdown')


def healthcheck():
    logger.info('Miner healthcheck')

    request = b'{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        msg = ''

        try:
            s.connect((miner_ip, port))
        except Exception:
            msg = 'Can\'t connect to miner'
        else:
            s.sendall(request)
            data = s.recv(1024)
            if data != b'':
                resp = json.loads(data.decode('utf-8'))
                error = resp['error']
                if error:
                    msg = error
            else:
                msg = 'Can\'t get stat from miner'

        if msg:
            logger.error('Helthcheck failed: {}'.format(msg))
            bot.send_message(my_id, 'Miner got error: {}'.format(msg))
        else:
            logger.info('Helthcheck ok')

    global timer
    timer = threading.Timer(60, healthcheck)
    timer.start()


timer = threading.Timer(60, healthcheck)
timer.start()

def signal_handler(signal, frame):
    timer.cancel()
    timer.join()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as err:
        logger.exception(err)
        time.sleep(5)
 
