from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from instagrapi import Client

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hasil', methods=['POST'])
def hasil():
    url = request.form['url']
    result = scrape_instagram_post(url)
    
    return render_template('hasil.html', result=result)

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

    # Ekstraksi data yang diperlukan
    username = media_info['user']['username']
    caption = media_info['caption_text']
    like_count = media_info['like_count']
    comment_count = media_info['comment_count']
    view_count = media_info['view_count'] if 'view_count' in media_info else 0

    # Output hasil
    return {
        'username': username,
        'caption': caption,
        'like_count': like_count,
        'comment_count': comment_count,
        'view_count': view_count
    }

if __name__ == '__main__':
    app.run(debug=True)
