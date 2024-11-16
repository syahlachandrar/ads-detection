import pickle
import numpy as np

# Muat model dari file model.pkl
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

def predict_reach(scraped_data):
    # Ambil fitur dari data yang di-scrape
    likes = scraped_data['like_count']
    saves = scraped_data['saves']
    comments = scraped_data['comment_count']
    shares = scraped_data['shares']
    profile_visits = scraped_data['profile_visits']
    following = scraped_data['following_count']

    # Buat array fitur untuk prediksi
    features = np.array([[likes, saves, comments, shares, profile_visits, following]])

    # Prediksi reach menggunakan model yang sudah dilatih
    predicted_reach = model.predict(features)

    return predicted_reach[0]
