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

### Setting Up the Cron Job

To automatically check for changes every hour, set up a cron job:

1. Open your crontab:

```bash
crontab -e
```

2. Add the following line to run the script every hour:

```
0 * * * * cd /path/to/lmarena-monitor && /path/to/venv/bin/python monitor.py >> data/cron.log 2>&1
```

Replace `/path/to/lmarena-monitor` with the absolute path to your project directory, and `/path/to/venv/bin/python` with the absolute path to the Python executable in your virtual environment.

To find the absolute path to your Python executable in the virtual environment, you can run:

```bash
which python  # When your virtual environment is activated
```

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

### Cron Job Issues

If the cron job is not working:

1. Check the cron log: `data/cron.log`
2. Ensure the paths in the cron job are correct
3. Make sure the Python script has execute permissions: `chmod +x monitor.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
