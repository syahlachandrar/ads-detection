from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from instagrapi import Client
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import PassiveAggressiveRegressor

app = Flask(__name__)
Bootstrap(app)

# Membaca dataset untuk melatih model
data = pd.read_csv("data_instagram.csv", encoding='latin1')

# Ekstraksi fitur dan target dari dataset
x = np.array(data[['Likes', 'Saves', 'Comments', 'Shares', 'Profile Visits', 'Follows']])
y = np.array(data["Impressions"])

# Membagi dataset menjadi set pelatihan dan set pengujian
xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.25, random_state=42)

# Melatih model PassiveAggressiveRegressor
model = PassiveAggressiveRegressor()
model.fit(xtrain, ytrain)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hasil', methods=['POST'])
def hasil():
    url = request.form['url']
    scraped_data = scrape_instagram_post(url)
    predicted_reach = predict_reach(scraped_data)
    
    return render_template('hasil.html', result=scraped_data, predicted_reach=predicted_reach)

def scrape_instagram_post(url):
    # Inisialisasi client
    cl = Client()

    # Login menggunakan username dan password
    username = 'sxyl.ipynb'  # Ganti dengan username Anda
    password = 'syahlachandra123'  # Ganti dengan password Anda
    cl.login(username, password)

    # Mendapatkan Primary Key (PK) dari post berdasarkan URL
    media_pk = cl.media_pk_from_url(url)

    # Mendapatkan detail post
    media_info = cl.media_info(media_pk).dict()
    
    # Mendapatkan informasi pengguna
    user_info = cl.user_info(media_info['user']['pk']).dict()

    # Ekstraksi data yang diperlukan
    username = media_info['user']['username']
    like_count = media_info.get('like_count', 0)
    comment_count = media_info.get('comment_count', 0)
    following_count = user_info.get('following_count', 0)

    return {
        'username': username,
        'like_count': like_count,
        'comment_count': comment_count,
        'following_count': following_count
    }

def predict_reach(scraped_data):
    likes = scraped_data['like_count']
    comments = scraped_data['comment_count']
    following = scraped_data['following_count']
    
    # Menggunakan nilai 0 untuk Saves, Shares, dan Profile Visits
    features = np.array([[likes, 0, comments, 0, 0, following]])

    # Prediksi jangkauan (reach) dengan model yang dilatih
    predicted_reach = model.predict(features)
    
    return predicted_reach[0]

if __name__ == '__main__':
    app.run(debug=True)
