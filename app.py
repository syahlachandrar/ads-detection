import os
import spacy
import traceback
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from auth.auth import auth
from instagrapi import Client
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import PassiveAggressiveRegressor
from controllers import add_user, edit_user, delete_user, add_hasil,  get_all_hasil
from scrape import scrape_instagram_post
from tf_idf import extract_top_keywords_tfidf, extract_top_keywords_rake
from headline_sub import extract_headline_subheadline, detect_price
import re

app = Flask(__name__)
Bootstrap(app)
mysql = MySQL(app)

# Secret key and MySQL configurations
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_project'
app.config['MYSQL_CHARSET'] = 'utf8mb4'


# Register the blueprint
app.register_blueprint(auth)

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


def clean_list(data):
    # Meratakan list dari list menjadi list tunggal
    flat_list = [item for sublist in data for item in sublist]  # Flatten the list
    return [re.sub(r'[^\x00-\x7F]+', '', str(item)) for item in flat_list]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hasil', methods=['POST'])
def hasil():
    # Ambil URL dari form
    url = request.form['url']
    
    # Scrape data dari URL Instagram
    scraped_data = scrape_instagram_post(url)
    
    # Ambil caption untuk dianalisis
    caption = scraped_data['caption']
    
    # Ekstraksi headline dan subheadline
    headline, subheadline = extract_headline_subheadline(caption)

    # Ekstraksi keywords dengan RAKE
    top_keywords_rake = extract_top_keywords_rake([caption])
    
    # Deteksi harga pada caption
    detected_price = detect_price(caption)

    # Prediksi jangkauan (reach)
    predicted_reach = predict_reach(scraped_data)

    # Ambil jumlah like dan komentar dari hasil scraping
    like_count = scraped_data['like_count']
    comment_count = scraped_data['comment_count']
    
    # Tambahkan hasil ke database
    add_hasil(
        mysql, 
        url, 
        headline, 
        subheadline, 
        detected_price, 
        predicted_reach, 
        top_keywords_rake,  # Menggunakan Rake keywords
        like_count,  # Menambahkan like_count
        comment_count  # Menambahkan comment_count
    )

    # Tampilkan hasil di halaman hasil.html
    return render_template(
        'hasil.html', 
        result=scraped_data, 
    )


@app.route('/hasil_analisis', methods=['GET'])
def hasil_analisis():
    # Ambil URL dari query string
    url = request.args.get('url')
    
    # Scrape data dari URL Instagram
    scraped_data = scrape_instagram_post(url)
    
    # Ambil caption untuk dianalisis
    caption = scraped_data['caption']
    
    # Ekstraksi headline dan subheadline
    headline, subheadline = extract_headline_subheadline(caption)

    # Ekstraksi keywords dengan RAKE
    rake_keywords = extract_top_keywords_rake([caption])
    
    # Deteksi harga pada caption
    detected_price = detect_price(caption)

    # Prediksi jangkauan (reach)
    predicted_reach = predict_reach(scraped_data)

    # Kirim data ke halaman hasil_analisis.html
    return render_template(
        'hasil_analis.html', 
        headline=headline, 
        subheadline=subheadline,
        detected_price=detected_price,
        rake_keywords=rake_keywords,
        predicted_reach=predicted_reach
    )


    # Tampilkan hasil di halaman hasil_analisis.html
    return render_template(
        'hasil_analis.html', 
        result=result
    )

@app.route('/riwayat_analisis')
def riwayat_analisis():
    # Ambil data riwayat analisis dari database
    hasil_data = get_all_hasil(mysql)
    
    # Kirim data ke template untuk ditampilkan dalam tabel
    return render_template('riwayat_analisis.html', hasil_data=hasil_data)

@app.route('/dashboardadmin', methods=['GET', 'POST'])
def dashboard_admin():
    if 'loggedin' in session and session['level'] == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT user_id, username, email FROM tb_users WHERE level = %s', ('admin',))
        users = cursor.fetchall()
        return render_template('dashboardadmin.html', users=users, title="Data Admin")
    else:
        flash('Akses ditolak. Halaman ini hanya untuk Admin.', 'danger')
        return redirect(url_for('home'))

@app.route('/dashboardpengguna', methods=['GET', 'POST'])
def dashboard_pengguna():
    if 'loggedin' in session and session['level'] == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT user_id, username, email FROM tb_users WHERE level = %s', ('pengunjung',))
        users = cursor.fetchall()
        return render_template('dashboardadmin.html', users=users, title="Data Pengguna")
    else:
        flash('Akses ditolak. Halaman ini hanya untuk Admin.', 'danger')
        return redirect(url_for('home'))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user_route():
    return add_user(mysql)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user_route(user_id):
    return edit_user(user_id, mysql)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user_route(user_id):
    print(f'Method: {request.method}, User ID: {user_id}')  # Tambahkan ini untuk debugging
    return delete_user(user_id, mysql)



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
