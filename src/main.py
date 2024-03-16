import os
import requests
import pandas as pd
from helpers import construct_csv_path
import time

class OpenAIAnalyzer:
    def __init__(self, model="gpt-3.5-turbo"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def send_request(self, prompt, context):
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response_json = response.json()
            if 'choices' in response_json and response_json['choices']:
                return response_json["choices"][0]["message"]["content"].strip()
            else:
                print("Unexpected response structure:", response_json)
                return None
        except Exception as e:
            print(f"Request error: {e}")
            return None

class ReviewProcessor:
    def __init__(self, analyzer, raw_filepath, processed_filepath):
        self.analyzer = analyzer
        self.raw_filepath = raw_filepath
        self.processed_filepath = processed_filepath
        self.df = pd.read_csv(self.raw_filepath)

        if 'openai_analysis' not in self.df.columns:
            self.df['openai_analysis'] = pd.NA  # Initialize with missing values
    
    def analyze_review(self, review):
        context = (
            "You will analyze a product review from the company Work From Home Desks. Identify the key aspects mentioned, "
            "categorize them as positive or negative, and classify them into one of the following categories: "
            "Assembly and Setup, Design and Appearance, Maintenance and Cleaning, Environmental and Health Impact, "
            "Functionality and Usability, Quality and Durability, Delivery and Customer Service, "
            "Value, Portability, Comfort and Ergonomics."
        )
        prompt = "This is the review:\n" + review
        return self.analyzer.send_request(prompt, context)
    
    def process_reviews(self):
        for i, row in self.df.iterrows():
            if pd.isna(row['openai_analysis']):
                review = row['body']
                result = self.analyze_review(review)
                if result is not None:
                    self.df.at[i, 'openai_analysis'] = result
                    print(f"Processed review {i+1}/{len(self.df)}")
                else:
                    print(f"Failed to process review {i+1}")
        self.save_results()

    def save_results(self):
        self.df.to_csv(self.processed_filepath, index=False)
        print("All changes saved to file.")


if __name__ == "__main__":
    
    analyzer = OpenAIAnalyzer()
    raw_csv_path = construct_csv_path('../data/raw', 'reviews_workfromhomedesk.csv')
    processed_csv_path = construct_csv_path('../data/processed', 'processed_reviews_workfromhomedesk.csv')
    review_processor = ReviewProcessor(analyzer, raw_csv_path, processed_csv_path)
    review_processor.process_reviews()
