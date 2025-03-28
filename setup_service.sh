#!/bin/bash
# Setup script for LM Arena Monitor systemd service

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Virtual environment not found at $PROJECT_DIR/venv"
    echo "Please set up a virtual environment first:"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Create the service file content with proper paths
SERVICE_CONTENT="[Unit]
Description=LM Arena Monitor Telegram Bot
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/bot.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target"

# Determine if we should use user service or system service
if [ "$EUID" -ne 0 ]; then
    # User is not root, set up as user service
    echo "Setting up as user service (systemd user unit)"
    
    # Create user systemd directory if it doesn't exist
    mkdir -p ~/.config/systemd/user/
    
    # Write the service file
    echo "$SERVICE_CONTENT" > ~/.config/systemd/user/lmarena-bot.service
    
    # Enable and start the service
    systemctl --user daemon-reload
    systemctl --user enable lmarena-bot.service
    systemctl --user start lmarena-bot.service
    
    echo "Service installed as user service."
    echo "To check status: systemctl --user status lmarena-bot.service"
    echo "To view logs: journalctl --user -u lmarena-bot.service"
    echo "To stop: systemctl --user stop lmarena-bot.service"
    
    # Check if lingering is enabled for the user
    if ! loginctl show-user $(whoami) | grep -q "Linger=yes"; then
        echo ""
        echo "NOTE: To ensure the service runs even when you're not logged in,"
        echo "you may need to enable lingering for your user:"
        echo "sudo loginctl enable-linger $(whoami)"
    fi
else
    # User is root, set up as system service
    echo "Setting up as system service"
    
    # For root user, we'll use the fixed path /root/code/lmarena-monitor
    SERVICE_CONTENT="[Unit]
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
WantedBy=multi-user.target"
    
    # Write the service file
    echo "$SERVICE_CONTENT" > /etc/systemd/system/lmarena-bot.service
    
    # Enable and start the service
    systemctl daemon-reload
    systemctl enable lmarena-bot.service
    systemctl start lmarena-bot.service
    
    echo "Service installed as system service."
    echo "To check status: systemctl status lmarena-bot.service"
    echo "To view logs: journalctl -u lmarena-bot.service"
    echo "To stop: systemctl stop lmarena-bot.service"
fi

echo ""
echo "Setup complete!"
