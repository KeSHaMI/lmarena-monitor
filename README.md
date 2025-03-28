# LM Arena Monitor Bot

A Telegram bot that monitors the [LM Arena](https://lmarena.ai) leaderboard and notifies users when the top 3 LLMs change.

## Features

- Scrapes the LM Arena website hourly using Selenium
- Handles website alerts automatically
- Notifies subscribed users when the top 3 LLMs change
- Provides commands to subscribe, unsubscribe, and check the current leaderboard

## Requirements

- Python 3.8 or higher
- Chrome or Chromium browser (for Selenium)
- ChromeDriver matching your Chrome version

## Installation

### Local Development Setup

1. Clone the repository or download the files:

```bash
git clone https://github.com/yourusername/lmarena-monitor.git
cd lmarena-monitor
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:

```bash
cp .env.example .env
```

5. Edit the `.env` file and add your Telegram bot token:

```
TELEGRAM_BOT_TOKEN=your_token_here
```

### Server Deployment

To deploy this bot on a server:

1. SSH into your server and clone the repository:

```bash
ssh user@your-server
git clone https://github.com/yourusername/lmarena-monitor.git /root/code/lmarena-monitor
cd /root/code/lmarena-monitor
```

> **Note:** In this documentation, we use `/root/code/lmarena-monitor` as the example project path. Replace this with your actual path if different.

2. Set up a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create and configure the `.env` file:

```bash
cp .env.example .env
nano .env  # Or use your preferred text editor
```

5. Install Chrome/Chromium and ChromeDriver (if not already installed):

```bash
# For Debian/Ubuntu
sudo apt update
sudo apt install -y chromium-browser chromium-driver

# For CentOS/RHEL
sudo yum install -y chromium chromedriver
```

6. Set up the systemd service for the bot (see below for details)

7. Set up the cron job for the monitor (see below for details)

## Telegram Bot Setup

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Send the `/newbot` command
3. Follow the instructions to create a new bot
4. Copy the API token provided
5. Add the token to your `.env` file

## Usage

### Running the Bot

To start the Telegram bot:

```bash
python bot.py
```

This will start the bot and allow users to interact with it using the following commands:

- `/start` - Introduction and help
- `/subscribe` - Subscribe to notifications
- `/unsubscribe` - Unsubscribe from notifications
- `/current` - Show the current top 3 LLMs

### Testing the Monitor

To manually test the monitor script:

```bash
python monitor.py
```

This will check the current leaderboard, compare it with the previous state, and send notifications if there are changes.

### Setting Up the Systemd Service

To keep the bot running continuously and ensure it starts automatically on system boot:

#### Automatic Setup (Recommended)

Use the provided setup script:

```bash
# Make the script executable
chmod +x setup_service.sh

# Run the setup script
./setup_service.sh
```

The script will:
- Verify that the virtual environment exists
- Create the appropriate systemd service file with correct paths
- Install it as a user service or system service (depending on whether you run it as root)
- Enable and start the service
- Provide instructions for checking status and logs

#### Manual Setup

If you prefer to set up the service manually:

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/lmarena-bot.service
```

2. Add the following content:

```ini
[Unit]
Description=LM Arena Monitor Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/code/lmarena-monitor
ExecStart=/root/code/lmarena-monitor/venv/bin/python /root/code/lmarena-monitor/bot.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable lmarena-bot.service
sudo systemctl start lmarena-bot.service
```

4. Check the service status:

```bash
sudo systemctl status lmarena-bot.service
```

#### User Service (Non-root Alternative)

If you don't have root access, you can set up a user service:

1. Create the service file in your user directory:

```bash
mkdir -p ~/.config/systemd/user/
nano ~/.config/systemd/user/lmarena-bot.service
```

2. Add the same content as above, but you can omit the `User=` line.

3. Enable and start the user service:

```bash
systemctl --user daemon-reload
systemctl --user enable lmarena-bot.service
systemctl --user start lmarena-bot.service
```

4. To ensure the service runs even when you're not logged in:

```bash
sudo loginctl enable-linger $USER
```

### Setting Up the Cron Job

To automatically check for changes every hour, set up a cron job using the virtual environment:

1. For manual setup, open your crontab:

```bash
crontab -e
```

2. Add the following line to run the script every hour:

```
0 * * * * cd /root/code/lmarena-monitor && /root/code/lmarena-monitor/venv/bin/python /root/code/lmarena-monitor/monitor.py >> /root/code/lmarena-monitor/data/cron.log 2>&1
```

3. Alternatively, use the provided setup script:

```bash
# Make the script executable
chmod +x setup_cron.sh

# Run the setup script
./setup_cron.sh
```

The setup script will automatically configure the cron job with the correct paths.

## Troubleshooting

### Selenium Issues

If you encounter issues with Selenium:

1. Make sure Chrome or Chromium is installed
2. Ensure ChromeDriver is installed and matches your Chrome version
3. Check the logs in `data/monitor.log` for specific errors

### Telegram Bot Issues

If the bot is not responding:

1. Verify your bot token in the `.env` file
2. Check if the bot is running (`python bot.py`)
3. Try restarting the bot

### Systemd Service Issues

If the systemd service is not working:

1. Check the service status:
   ```bash
   sudo systemctl status lmarena-bot.service
   ```

2. View the logs:
   ```bash
   sudo journalctl -u lmarena-bot.service
   ```

3. Common issues to check:
   - Incorrect paths in the service file
   - Permissions issues (the user running the service needs access to all files)
   - Virtual environment not properly set up
   - Missing dependencies

4. After fixing issues, reload and restart the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart lmarena-bot.service
   ```

### Cron Job Issues

If the cron job is not working:

1. Check the cron log: `data/cron.log`
2. Ensure the paths in the cron job are correct
3. Make sure the Python script has execute permissions: `chmod +x monitor.py`
4. Verify the virtual environment path is correct

## License

This project is licensed under the MIT License - see the LICENSE file for details.
