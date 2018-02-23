# Claymore miner bot
Telegram Bot for statistics and remote management of Claymore's GPU miner.

# News
Added the possibility to control multiple rigs and on/off alerts.

# Getting Started

This bot works with python3 so you need it and pip for installing the module needed.

For arch based distributions
```bash
sudo pacman -S python3 python-pip
```
For debian based distributions
```bash
sudo apt install python3 python3-pip
```
Then, you need the module pyTelegramBotAPI.
```bash
sudo pip3 install pyTelegramBotAPI
```
Now you need a `Token` from the [BotFather](https://telegram.me/BotFather).

Once you have the `Token` you can configure the bot.

Open config.py and modify the `token`, `my_id` and `rigs`.

Finally, to run the bot you just need to type: `python3 miner_bot.py`.

# Available Commands
```
/hashrate - Shows the mining hashrate.
/main - Shows the main coin hashrate of each GPU.
/dual - Shows the dual coin hashrate of each GPU.
/gpu_info - Send the temperature and fan speed of the GPUs.
/info - Send miner version and uptime.
/restart - Restart Claymore's miner.
/reboot - Reboot the rig(calls reboot.bat or reboot.sh).
/status - Shows the rig list and their state (on/off).
/help - Shows this message.
```
# Screenshots
|   |   |
|:---:|:---:|
|<img src="https://user-images.githubusercontent.com/3170731/29235549-f9f570ba-7eff-11e7-95ac-353f0cbc5ac5.png" width="410">|<img src="https://user-images.githubusercontent.com/3170731/29235552-fde84a9e-7eff-11e7-9bae-470344647900.png" width="410">|
|start and hashrate|main and dual|
|<img src="https://user-images.githubusercontent.com/3170731/29235553-fefd3926-7eff-11e7-8ce8-7dd03285927a.png" width="410">|<img src="https://user-images.githubusercontent.com/3170731/29235554-ffffecec-7eff-11e7-96b4-ec131802d2a2.png" width="410">|
|gpu_info and info|restart|

{RUS}
# Claymore miner bot
Telegram Bot для отображения статистики и удаленного управления Claymore Gpu Miner.

# Новости
Added the possibility to control multiple rigs and on/off alerts.
Добавлен русский перевод
# Установка

Этот бот работает на python3 так же вам нужен пакетный менеджер pip.

Для дистрибутивов на arch:
```bash
sudo pacman -S python3 python-pip
```
для дебианподобных дистрибутивов:
```bash
sudo apt install python3 python3-pip
```
так-же нужно установить модуль pyTelegramBotAPI.
```bash
sudo pip3 install pyTelegramBotAPI
```
теперь нужен `Token` от [BotFather](https://telegram.me/BotFather).

теперь когда у вас есть `Token` вы можете настроить бота.

откройте config.py и измените переменные `token`, `my_id` и `rigs`.

В конце нам нужно запустить бот командой: `python3 miner_bot.py`.

# Доступные команды
```
/hashrate - Отображает хешрейт.
/main - Отображает хешрейт основной валюты по каждой GPU.
/dual - Отображает хешрейт вторичной валюты по каждой GPU..
/gpu_info - Отображает Температуру и обороты кулеров GPU.
/info - Отображает версию майнера и текущее время работы.
/restart - Перезапуск майнера Claymore
/reboot - Перезапуск Рига (Вызывает Reboot.bat(sh) из каталога майнера).
/status - Отображает список и статус ригов(ВКЛ/ВЫКЛ).
/help - Отображает это сообщение.
```
# Screenshots
|   |   |
|:---:|:---:|
|<img src="https://github.com/naeternitas/claymore-miner-bot/raw/master/%D0%91%D0%B5%D0%B7%D1%8B%D0%BC%D1%8F%D0%BD%D0%BD%D1%8B%D0%B9.jpg">


