#!/bin/bash
# Setup script for LM Arena Monitor cron job

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
if [ -d "$PROJECT_DIR/venv" ]; then
    # Use the Python executable from the virtual environment
    PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
    echo "Using Python from virtual environment: $PYTHON_PATH"
else
    # Fall back to system Python if venv doesn't exist
    PYTHON_PATH="$(which python3)"
    echo "Virtual environment not found, using system Python: $PYTHON_PATH"
    echo "It's recommended to set up a virtual environment for this project."
    echo "Run: python3 -m venv venv"
fi

# Create the cron job line
CRON_LINE="0 * * * * cd $PROJECT_DIR && $PYTHON_PATH $PROJECT_DIR/monitor.py >> $PROJECT_DIR/data/cron.log 2>&1"

# Check if the cron job already exists
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "$PROJECT_DIR/monitor.py")

if [ -n "$EXISTING_CRON" ]; then
    echo "Cron job already exists. No changes made."
    echo "Current cron job: $EXISTING_CRON"
else
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "Cron job added successfully!"
    echo "The monitor will run every hour at minute 0."
    echo "Added: $CRON_LINE"
fi

# Make sure the script files are executable
chmod +x "$PROJECT_DIR/scraper.py" "$PROJECT_DIR/bot.py" "$PROJECT_DIR/monitor.py"

echo ""
echo "Setup complete!"
echo "To start the Telegram bot, run: python3 $PROJECT_DIR/bot.py"
echo "To manually run the monitor, run: python3 $PROJECT_DIR/monitor.py"
