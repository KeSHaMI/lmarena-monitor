#!/usr/bin/env python3
"""
LM Arena Monitor

This script checks for changes in the LM Arena leaderboard and sends notifications
when the top 3 LLMs change. It is designed to be run by a cron job.
"""

import json
import os
import logging
import asyncio
from scraper import scrape_with_retry, save_leaderboard_data
from bot import send_notifications

# Configure logger
logger = logging.getLogger(__name__)

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

# Using save_leaderboard_data from scraper.py

def leaderboards_differ(previous, current):
    """
    Check if the leaderboards differ in any way
    
    Args:
        previous (dict): Previous leaderboard data
        current (dict): Current leaderboard data
    
    Returns:
        bool: True if the leaderboards differ, False otherwise
    """
    # If either leaderboard is empty, consider them different
    if not previous['top3'] or not current['top3']:
        return True
    
    # If the number of models differs, they're different
    if len(previous['top3']) != len(current['top3']):
        return True
    
    # Check each model
    for prev_model, curr_model in zip(previous['top3'], current['top3']):
        # If the name or rank differs, they're different
        if prev_model['name'] != curr_model['name'] or prev_model['rank'] != curr_model['rank']:
            return True
    
    return False

async def detect_changes():
    """
    Check for changes in the top 3 LLMs
    
    Returns:
        bool: True if changes were detected, False otherwise
    """
    previous = load_previous_leaderboard()
    current = scrape_with_retry(max_retries=3, headless=True)
    
    if current is None:
        logger.error("Failed to scrape leaderboard after multiple attempts")
        return False
    
    if leaderboards_differ(previous, current):
        logger.info("Leaderboard changes detected")
        await send_notifications(previous, current)
        save_leaderboard_data(current)
        return True
    
    logger.info("No leaderboard changes detected")
    return False

async def main():
    """Main function"""
    logger.info("Starting LM Arena monitor")
    await detect_changes()
    logger.info("Monitor run completed")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/monitor.log'),
            logging.StreamHandler()
        ]
    )
    
    # Run the monitor
    asyncio.run(main())
