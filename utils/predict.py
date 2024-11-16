import json
import numpy as np
import pandas as pd
from sklearn.linear_model import PassiveAggressiveRegressor
from sklearn.model_selection import train_test_split

class ReachPredictor:
    def __init__(self):
        self.model = None
        self.product_advantages_keywords = []

    def train_model(self):
        # Load dataset
        data = pd.read_csv("data_instagram.csv", encoding='latin1')

        # Feature and target extraction
        x = np.array(data[['Likes', 'Saves', 'Comments', 'Shares', 'Profile Visits', 'Follows']])
        y = np.array(data["Impressions"])

        # Train/test split
        xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.25, random_state=42)

        # Train the model
        self.model = PassiveAggressiveRegressor()
        self.model.fit(xtrain, ytrain)

    def predict_reach(self, scraped_data):
        if self.model is None:
            raise ValueError("Model is not trained yet.")
        
        likes = scraped_data['like_count']
        comments = scraped_data['comment_count']
        following = scraped_data['following_count']
        
        # Using 0 for Saves, Shares, and Profile Visits
        features = np.array([[likes, 0, comments, 0, 0, following]])
        
        # Predicting reach
        predicted_reach = self.model.predict(features)
        return predicted_reach[0]

    def load_keywords(self):
        with open('keywords.json', 'r') as file:
            data = json.load(file)
        self.product_advantages_keywords = data['product_advantages_keywords']
