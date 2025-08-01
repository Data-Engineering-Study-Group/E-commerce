import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()

API_KEY = os.getenv("Key")
BASE_CURRENCY = "NGN"
TARGET_CURRENCIES = [
    'USD', 'EUR', 'GBP', 'CNY', 'JPY',
    'ZAR', 'CAD', 'AUD', 'GHS', 'XOF',
    'XAF', 'INR', 'CHF', 'RUB', 'AED'
]
START_DATE = datetime(2000, 1, 1)
END_DATE = datetime(2000, 1, 30)
WAIT_TIME = 2  # seconds between API calls


# Loop through dates
def generate_date_list(start, end):
    # Calculates days btw start and end (inclusive)
    days = (end - start).days + 1
    return [(start + timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range(days)]


# Fetch historical exchange rate with 1 Naira as base currency
def get_rates_for_date(date):
    url = f'https://api.currencyfreaks.com/v2.0/rates/historical'
    params = {
        'apikey': API_KEY,
        'date': date,
        'base': BASE_CURRENCY
    }

    r = requests.get(url, params=params)
    r.raise_for_status()  # Raise error if request fails
    return r.json()

# Save historical exchange rate in CSV

def main():
    date_list = generate_date_list(START_DATE, END_DATE)

    # CSV output
    filename = 'ngn2_historical_rates_2000.csv'
    fieldnames = ['date', 'base', 'target', 'rate']

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Loops through each date
        for date in date_list:
            print(f"Processing date: {date}")  # Tracks progress

            try:
                # Fetches all exchange rates for that day
                data = get_rates_for_date(date)
                rates = data.get('rates', {})
                base = data.get('base', BASE_CURRENCY)

                # Fetches exchange rates for specific currencies
                for target in TARGET_CURRENCIES:
                    rate = rates.get(target)

                    # If rate is not available in endpint, DO NOT include in
                    # CSV
                    if rate is not None:
                        writer.writerow({
                            'date': date,
                            'base': base,
                            'target': target,
                            'rate': float(rate)
                        })

                    else:
                        print(f"Rate for {target} not found on {date}.")

            # Error handling and rate limit
            except Exception as e:
                print(f"Error for {date}: {e}")
            time.sleep(WAIT_TIME)

    print(f"Done. Data saved to {filename}")


if __name__ == '__main__':
    main()

# This script fetches historical exchange rates for Naira (NGN) against various currencies
# from January 1, 2000 to January 30, 2000 and saves them in a CSV file.
# It uses the CurrencyFreaks API and handles rate limits by waiting between requests.
# The script also handles errors gracefully and skips missing rates.
# Make sure to set the API key in a .env file with the variable 'Key'.
# The output CSV file will contain the date, base currency, target currency, and exchange rate.
# The script is designed to be run in a Python environment with the required libraries installed.
