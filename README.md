# Claymore miner bot
Telegram Bot for statistics and remote management of Claymore's GPU miner.

# Getting Started

This bot works with python3 so you need it and pip for installing the module needed.
```bash
sudo pacman -S python3 python-pip
sudo apt install python3 python3-pip
```

Then, you need the module pyTelegramBotAPI.
```bash
sudo pip3 install pyTelegramBotAPI
```
Now you need a `Token` from the [BotFather](https://telegram.me/BotFather).

Once you have the `Token` you can configure the bot.

Open miner_bot.py and edit the variables `token`, `miner_ip`, `port` and `my_id`.

Finally, to run the bot you just need to type: `./miner_bot.py`.

# Available Commands
```
/hashrate - Shows the mining hashrate.
/main - Shows the main coin hashrate of each GPU.
/dual - Shows the dual coin hashrate of each GPU.
/gpu_info - Send the temperature and fan speed of the GPUs.
/info - Send miner version and uptime.
/restart - Restart Claymore's miner.
/reboot - Reboot the rig(calls reboot.bat or reboot.sh).
/help - Shows this message.
```
# Screenshots
|   |   |
|:---:|:---:|
|<img src="https://user-images.githubusercontent.com/3170731/29235549-f9f570ba-7eff-11e7-95ac-353f0cbc5ac5.png" width="410">|<img src="https://user-images.githubusercontent.com/3170731/29235552-fde84a9e-7eff-11e7-9bae-470344647900.png" width="410">|
|start and hashrate|main and dual|
|<img src="https://user-images.githubusercontent.com/3170731/29235553-fefd3926-7eff-11e7-8ce8-7dd03285927a.png" width="410">|<img src="https://user-images.githubusercontent.com/3170731/29235554-ffffecec-7eff-11e7-96b4-ec131802d2a2.png" width="410">|
|gpu_info and info|restart|
