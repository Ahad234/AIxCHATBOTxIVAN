# Telegram Bot Deployment on VPS

This guide explains how to deploy your Telegram bot on a Virtual Private Server (VPS) using **Python**.

---

## 🚀 Requirements
- A VPS (Ubuntu/Debian recommended)
- Python 3.9+
- Git installed
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- Your bot source code

---

## 🔧 Setup Instructions

### 1. Connect to Your VPS
```bash
ssh username@your_server_ip

2. Update Your Server

sudo apt update && sudo apt upgrade -y

3. Install Dependencies

sudo apt install python3 python3-pip python3-venv git -y

4. Clone Your Repository

git clone https://github.com/username/your-bot-repo.git
cd your-bot-repo

5. Create a Virtual Environment

python3 -m venv venv
source venv/bin/activate


6. Install Python Packages

pip install -r requirements.txt

7. Set Environment Variables

* Create a .env file:

nano .env

8. Add:


TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

Now, use

python3 bot.py


 9. Run in Background with screen

sudo apt install screen
screen -S bot
source venv/bin/activate
python3 bot.py


Detach: Ctrl + A + D
Reattach: screen -r bot

10. (Optional) Setup Auto-Restart with systemd

sudo nano /etc/systemd/system/telegram-bot.service

paste:

[Unit]
Description=Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/your-bot-repo
ExecStart=/root/your-bot-repo/venv/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target

Reload, start, and enable:


sudo systemctl daemon-reload
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot

