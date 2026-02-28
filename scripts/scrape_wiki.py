import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

def scrape_wikipedia_events(year, month):
    """
    Scrapes Wikipedia Current Events Portal for a given month.
    URL format: https://en.wikipedia.org/wiki/Portal:Current_events/Month_Year
    """
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    month_str = months[month - 1]
    url = f"https://en.wikipedia.org/wiki/Portal:Current_events/{month_str}_{year}"
    
    headers = {
        'User-Agent': 'WhatWouldTrumpSay-ResearchBot/1.0 (Contact: your-email@example.com) base on python-requests'
    }
    
    print(f"Scraping {url}...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url} - Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    events = []
    
    # Wikipedia structure for Current Events is usually day-based containers
    # We look for div with class 'vevent' or similar, but it often changes.
    # A more robust way is looking for the date headers.
    
    days = soup.find_all('div', class_='vevent')
    for day_div in days:
        # Extract date from summary or anchor
        date_span = day_div.find('span', class_='summary')
        if not date_span:
            continue
            
        date_str = date_span.get_text() # e.g., "January 1, 2018 (Monday)"
        try:
            # Simple parsing of date_str
            clean_date_str = date_str.split('(')[0].strip()
            date_obj = datetime.strptime(clean_date_str, "%B %d, %Y").date()
        except Exception as e:
            print(f"Error parsing date {date_str}: {e}")
            continue

        # Extract bullet points
        content_div = day_div.find('div', class_='description')
        if content_div:
            # Flatten the nested lists into text
            summary = content_div.get_text(separator="\n").strip()
            events.append({
                "date": date_obj.isoformat(),
                "summary": summary
            })
            
    return events

if __name__ == "__main__":
    # Example: Scrape January 2018
    all_2018_events = []
    for m in range(1, 13):
        month_events = scrape_wikipedia_events(2018, m)
        all_2018_events.extend(month_events)
        time.sleep(1) # Be nice to Wiki
        
    df = pd.DataFrame(all_2018_events)
    df.to_csv("data/wikipedia_2018_events.csv", index=False)
    print(f"Saved {len(df)} days of events to data/wikipedia_2018_events.csv")
