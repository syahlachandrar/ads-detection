from instagrapi import Client
import re
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.DEBUG)

def remove_invalid_characters(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)  # Hapus karakter non-ASCII

def scrape_instagram_post(url):
    try:
        cl = Client()
        cl.login('coba.2_3', 'coba123')  # Login dengan akun yang sudah disiapkan

        # Ekstraksi ID postingan dari URL
        media_id = cl.media_pk_from_url(url)
        logging.debug(f"Media ID: {media_id}")

        # Mendapatkan detail postingan
        media_info = cl.media_info(media_id).dict()
        logging.debug(f"Media Info: {media_info}")

        # Ambil data yang diperlukan dari 'media_info'
        scraped_data = {
            'username': media_info['user']['username'],
            'caption': remove_invalid_characters(media_info.get('caption_text', '')),
            'like_count': media_info.get('like_count', 0),
            'comment_count': media_info.get('comment_count', 0),
            'following_count': media_info['user'].get('following_count', 0),
            'follower_count': media_info['user'].get('follower_count', 0)
        }

        return scraped_data

    except Exception as e:
        logging.error(f"Error during Instagram scraping: {e}")
        raise
