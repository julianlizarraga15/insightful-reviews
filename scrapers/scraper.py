import requests
import pandas as pd
import os
from urllib.parse import urlencode, quote, unquote
import time

def make_request_with_backoff(url, params, max_attempts=5):
    attempt = 0
    backoff_factor = 1  # Initial backoff factor, in seconds

    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; YourApplication)',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    while attempt < max_attempts:
        full_url = f"{url}?{urlencode(params, quote_via=quote)}"
        response = requests.get(full_url, headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            # Rate limit handling
            attempt += 1
            sleep_time = backoff_factor * (2 ** attempt)
            print(f"Rate limit hit, backing off for {sleep_time} seconds.")
            time.sleep(sleep_time)
        else:
            # Other error handling
            response.raise_for_status()

    raise Exception(f"Failed to fetch data after {max_attempts} attempts.")

def fetch_all_reviews(base_url, initial_params):
    print("Fetching all reviews from site...")
    start_time = time.time()
    all_reviews = []
    params = initial_params.copy()
    while True:
        response = make_request_with_backoff(base_url, params)
        data = response.json()
        all_reviews.extend(data['reviews'])

        # Check for the next page
        if 'nextUrl' in data and data['nextUrl']:
            next_params_str = data['nextUrl'].split('?')[1]
            # Unquote before parsing to avoid double-encoding
            next_params_str = unquote(next_params_str)
            params = dict(param.split('=') for param in next_params_str.split('&'))
        else:
            break  # No more pages
    end_time = time.time()
    print(f"Total reviews fetched: {len(all_reviews)}")
    print(f"Time taken to fetch reviews: {(end_time - start_time)/60:.2f} minutes")

    return all_reviews

def process_reviews_to_csv(base_url, initial_params, csv_path):

    review_data = fetch_all_reviews(base_url, initial_params)
    reviews_df = pd.json_normalize(review_data)
    reviews_df.to_csv(csv_path, index=False)


if __name__ == '__main__':
    
    # Configuration
    base_url = 'https://api.okendo.io/v1/stores/231fb74a-b56e-4485-8920-1e583252adf5/reviews'
    initial_params = {
        'limit': 5,
        'orderBy': 'has_media desc'
    }
    current_dir = os.path.dirname(__file__)
    relative_path = '../data/raw'
    csv_name = 'reviews_workfromhomedesk.csv'
    csv_path = os.path.join(current_dir, relative_path, csv_name)

    # Execution
    process_reviews_to_csv(base_url, initial_params, csv_path)
