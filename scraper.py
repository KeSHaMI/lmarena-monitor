#!/usr/bin/env python3
"""
LM Arena Scraper Module

This module handles scraping the LM Arena website to extract the top 3 LLMs
from the leaderboard.
"""

import json
import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logger
logger = logging.getLogger(__name__)

def save_leaderboard_data(data):
    """
    Save the current leaderboard data
    
    Args:
        data (dict): The leaderboard data to save
    """
    os.makedirs('data', exist_ok=True)
    with open('data/leaderboard.json', 'w') as f:
        json.dump(data, f)
    logger.info("Saved leaderboard data")

def scrape_leaderboard(headless=True, debug=False):
    """
    Scrape the top 3 LLMs from lmarena.ai
    
    Args:
        headless (bool): Whether to run the browser in headless mode
        debug (bool): Whether to enable debug mode (print HTML, wait longer)
    
    Returns:
        dict: A dictionary containing the top 3 LLMs with their ranks, names, and scores
              Format: {"top3": [{"rank": 1, "name": "LLM1", "score": 95.2}, ...]}
        None: If scraping fails
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
        # Add these options to better emulate a real browser in headless mode
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Common options for both headless and non-headless modes
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")  # Fix DevToolsActivePort error
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--disable-features=VizDisplayCompositor")  # Disable GPU compositing
    
    # Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    try:
        # Setup Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Navigate to LM Arena
        logger.info("Navigating to lmarena.ai")
        driver.get("https://lmarena.ai")
        
        # Execute JavaScript to hide the webdriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Wait for the page to load completely using dynamic wait
        logger.info("Waiting for page to load completely")
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Handle alert if present
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            logger.info("Alert found, accepting it")
            alert.accept()
        except (TimeoutException, NoAlertPresentException):
            logger.info("No alert found or alert timed out")
        
        # Additional wait after page load
        time.sleep(3)
        
        # Try multiple selectors to find and click the Leaderboard tab
        logger.info("Attempting to find and click the Leaderboard tab")
        tab_clicked = False
        selectors = [
            (By.ID, "component-176-button"),
            (By.CSS_SELECTOR, "button[role='tab'][aria-controls='component-176']"),
            (By.XPATH, "//button[contains(text(), 'Leaderboard')]"),
            (By.XPATH, "//button[contains(@class, 'tab') and contains(text(), 'Leaderboard')]"),
            (By.CSS_SELECTOR, "button.tab")  # Generic tab selector as last resort
        ]
        
        for selector_type, selector in selectors:
            try:
                logger.info(f"Trying to find leaderboard tab with selector: {selector_type} - {selector}")
                leaderboard_tab = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((selector_type, selector))
                )
                logger.info(f"Leaderboard tab found with selector: {selector}")
                leaderboard_tab.click()
                logger.info("Successfully clicked on Leaderboard tab")
                tab_clicked = True
                # Wait for the table to load after clicking
                time.sleep(3)
                break
            except Exception as e:
                logger.warning(f"Failed to find/click tab with selector {selector}: {e}")
        
        if not tab_clicked:
            logger.warning("Could not find Leaderboard tab with any selector, continuing anyway as it might be the default view")
        
        # Print HTML content if in debug mode
        if debug:
            logger.info("Printing HTML content")
            html_content = driver.page_source
            print("\n\n===== HTML CONTENT =====\n")
            print(html_content)
            print("\n===== END HTML CONTENT =====\n")
            
            # Save HTML to file for easier analysis
            with open("data/page_source.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info("Saved HTML content to data/page_source.html")
        
        # Try multiple approaches to find the leaderboard table
        logger.info("Looking for the leaderboard table")
        table = None
        table_selectors = [
            (By.CSS_SELECTOR, "table.table.svelte-82jkx"),
            (By.CSS_SELECTOR, "table.table"),
            (By.XPATH, "//table[contains(@class, 'table')]"),
            (By.TAG_NAME, "table")
        ]
        
        for selector_type, selector in table_selectors:
            try:
                logger.info(f"Trying to find table with selector: {selector_type} - {selector}")
                table = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((selector_type, selector))
                )
                logger.info(f"Found the leaderboard table with selector: {selector}")
                break
            except Exception as e:
                logger.warning(f"Failed to find table with selector {selector}: {e}")
        
        if table is None:
            # Last resort: try to find any table
            tables = driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"Found {len(tables)} tables on the page")
            if len(tables) > 0:
                table = tables[0]
                logger.info("Using the first table found as fallback")
            else:
                logger.error("No tables found on the page")
                
                # Save the page source for debugging
                html_content = driver.page_source
                with open("data/failed_page_source.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info("Saved failed page HTML to data/failed_page_source.html")
                
                return None

        
        # Extract the top 3 LLMs
        logger.info("Extracting top 3 LLMs")
        try:
            # Find all rows in the tbody
            leaderboard_rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            logger.info(f"Found {len(leaderboard_rows)} rows in the table")
            
            top3 = []
            for i, row in enumerate(leaderboard_rows[:3]):  # Get only top 3
                try:
                    # Get all cells in the row
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    # Extract data from cells
                    rank_ub = cells[0].text.strip()  # Rank (UB)
                    model_cell = cells[2]  # Model name is in the 3rd column
                    
                    # Extract model name - it might be inside a span with class "md"
                    model_spans = model_cell.find_elements(By.CSS_SELECTOR, "span.md")
                    if model_spans:
                        # Try to find the link inside the span
                        links = model_spans[0].find_elements(By.TAG_NAME, "a")
                        if links:
                            model_name = links[0].text.strip()
                        else:
                            model_name = model_spans[0].text.strip()
                    else:
                        model_name = model_cell.text.strip()
                    
                    # Extract score from the 4th column
                    score = float(cells[3].text.strip())
                    
                    top3.append({
                        "rank": int(rank_ub),
                        "name": model_name,
                        "score": score
                    })
                    logger.info(f"Extracted model: Rank {rank_ub}, Name: {model_name}, Score: {score}")
                except (IndexError, ValueError) as e:
                    logger.error(f"Error parsing row {i+1}: {e}")
        except Exception as e:
            logger.error(f"Error extracting data from table: {e}")
            return None
        
        logger.info(f"Successfully extracted {len(top3)} models")
        result = {"top3": top3}
        
        # Save the scraped data to leaderboard.json
        save_leaderboard_data(result)
        
        return result
    
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return None
    
    finally:
        # Close the browser (unless in debug mode)
        if not debug:
            try:
                driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
        else:
            logger.info("Debug mode: browser left open for inspection")
            input("Press Enter to close the browser...")
            try:
                driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")

def scrape_with_retry(max_retries=3, headless=True, debug=False):
    """
    Attempt to scrape the leaderboard with retries
    
    Args:
        max_retries (int): Maximum number of retry attempts
        headless (bool): Whether to run in headless mode
        debug (bool): Whether to enable debug mode
        
    Returns:
        dict: The scraped leaderboard data, or None if all attempts fail
    """
    for attempt in range(1, max_retries + 1):
        logger.info(f"Scraping attempt {attempt}/{max_retries}")
        result = scrape_leaderboard(headless=headless, debug=debug)
        if result:
            logger.info(f"Scraping successful on attempt {attempt}")
            return result
        else:
            logger.warning(f"Scraping attempt {attempt} failed, {'retrying' if attempt < max_retries else 'giving up'}")
            if attempt < max_retries:
                # Wait before retrying, with increasing delay
                time.sleep(attempt * 2)
    
    logger.error(f"All {max_retries} scraping attempts failed")
    return None

if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the scraper with debug mode and visible browser
    print("Running scraper in debug mode with visible browser")
    result = scrape_with_retry(max_retries=3, headless=True, debug=False)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Failed to scrape leaderboard after multiple attempts")
