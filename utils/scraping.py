from instagrapi import Client

def scrape_instagram_post(url):
    # Membuat instance client Instagram
    cl = Client()

    # Masukkan username dan password secara langsung
    username = 'your_username'  # Ganti dengan username Instagram kamu
    password = 'your_password'  # Ganti dengan password Instagram kamu

    # Validasi apakah username dan password telah terisi
    if not username or not password:
        raise Exception("Username dan password harus diisi.")

    # Mencoba login ke akun Instagram
    try:
        cl.login(username, password)
    except Exception as e:
        raise Exception(f"Login gagal: {str(e)}")

    # Mencoba mengambil data dari URL yang diberikan
    try:
        media_pk = cl.media_pk_from_url(url)
        media_info = cl.media_info(media_pk).dict()

        # Mengambil informasi dari postingan
        caption = media_info['caption_text']
        like_count = media_info.get('like_count', 0)
        comment_count = media_info.get('comment_count', 0)
        user_info = cl.user_info(media_info['user']['pk']).dict()
        following_count = user_info.get('following_count', 0)

        # Mengembalikan data hasil scraping
        return {
            'caption': caption,
            'like_count': like_count,
            'comment_count': comment_count,
            'following_count': following_count
        }
    except Exception as e:
        raise Exception(f"Gagal mengambil data dari Instagram: {str(e)}")
