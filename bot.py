#!/usr/bin/env python3
"""
LM Arena Monitor Telegram Bot

This module implements a Telegram bot that notifies users when the top 3 LLMs
on LM Arena change.
"""

import json
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not found in .env file")
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")


def load_previous_leaderboard():
    """
    Load the previously saved leaderboard data
    
    Returns:
        dict: The previously saved leaderboard data
    """
    try:
        with open('data/leaderboard.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info("leaderboard.json not found, creating empty leaderboard")
        return {"top3": []}
    
    
def load_users():
    """
    Load the list of subscribed users
    
    Returns:
        list: List of user IDs
    """
    try:
        with open('data/users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info("users.json not found, creating empty list")
        return []

def save_users(users):
    """
    Save the list of subscribed users
    
    Args:
        users (list): List of user IDs
    """
    os.makedirs('data', exist_ok=True)
    with open('data/users.json', 'w') as f:
        json.dump(users, f)
    logger.info(f"Saved {len(users)} users to users.json")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command
    
    Args:
        update: Telegram update object
        context: Telegram context object
    """
    logger.info(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text(
        "Welcome to LM Arena Monitor Bot!\n\n"
        "I'll notify you when the top 3 LLMs on lmarena.ai change.\n\n"
        "Commands:\n"
        "/subscribe - Get notifications\n"
        "/unsubscribe - Stop notifications\n"
        "/current - Show current top 3 LLMs"
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /subscribe command
    
    Args:
        update: Telegram update object
        context: Telegram context object
    """
    user_id = update.effective_user.id
    users = load_users()
    
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        logger.info(f"User {user_id} subscribed")
        await update.message.reply_text("You've been subscribed to LM Arena updates!")
    else:
        logger.info(f"User {user_id} already subscribed")
        await update.message.reply_text("You're already subscribed!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /unsubscribe command
    
    Args:
        update: Telegram update object
        context: Telegram context object
    """
    user_id = update.effective_user.id
    users = load_users()
    
    if user_id in users:
        users.remove(user_id)
        save_users(users)
        logger.info(f"User {user_id} unsubscribed")
        await update.message.reply_text("You've been unsubscribed from LM Arena updates.")
    else:
        logger.info(f"User {user_id} tried to unsubscribe but wasn't subscribed")
        await update.message.reply_text("You're not subscribed.")

async def current(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /current command
    
    Args:
        update: Telegram update object
        context: Telegram context object
    """
    logger.info(f"User {update.effective_user.id} requested current leaderboard")
    await update.message.reply_text("Fetching current leaderboard...")
    
    # Use the already scraped data instead of re-scraping
    leaderboard = load_previous_leaderboard()
    
    if leaderboard and leaderboard['top3']:
        message = "Current Top 3 LLMs on LM Arena:\n\n"
        for model in leaderboard['top3']:
            message += f"{model['rank']}. {model['name']} - Score: {model['score']}\n"
        logger.info("Sent current leaderboard")
        await update.message.reply_text(message)
    else:
        logger.error("No leaderboard data available")
        await update.message.reply_text("Sorry, no leaderboard data is available. Try again later.")

async def send_notification_to_user(bot, user_id, message):
    """
    Send a notification to a single user
    
    Args:
        bot: Telegram bot instance
        user_id: User ID to send notification to
        message: Message to send
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        await bot.send_message(chat_id=user_id, text=message)
        logger.info(f"Notification sent to user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {e}")
        return False

async def send_notifications(previous, current):
    """
    Send notifications to all subscribed users
    
    Args:
        previous (dict): Previous leaderboard data
        current (dict): Current leaderboard data
    """
    users = load_users()
    if not users:
        logger.info("No users to notify")
        return
    
    # Create notification message
    message = "🔄 LM Arena Leaderboard Update! 🔄\n\n"
    message += "New Top 3:\n"
    for model in current['top3']:
        message += f"{model['rank']}. {model['name']} - Score: {model['score']}\n"
    
    message += "\nPrevious Top 3:\n"
    for model in previous['top3']:
        message += f"{model['rank']}. {model['name']} - Score: {model['score']}\n"
    
    # Initialize bot and send messages
    application = Application.builder().token(TOKEN).build()
    bot = application.bot
    
    # Send notifications to all users
    logger.info(f"Sending notifications to {len(users)} users")
    tasks = [send_notification_to_user(bot, user_id, message) for user_id in users]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(1 for result in results if result)
    logger.info(f"Successfully sent {success_count} out of {len(users)} notifications")

def main():
    """Run the bot"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    # Create the Application
    logger.info("Starting bot")
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("current", current))
    
    # Start the bot
    logger.info("Bot started")
    application.run_polling()

if __name__ == "__main__":
    main()
