from instagrapi import Client

def scrape_instagram_post(url):
    cl = Client()
    cl.login('advert.ig', 'advert1')  # Login dengan akun yang sudah disiapkan

    # Ekstraksi ID postingan dari URL
    media_id = cl.media_pk_from_url(url)
    
    # Mendapatkan detail postingan
    media_info = cl.media_info(media_id).dict()
    
    # Mengambil data resolusi dari 'media_info'
    width = None
    height = None

    # Jika postingan adalah foto tunggal
    if media_info.get('media_type') == 1:
        width = media_info.get('dimensions', {}).get('width')
        height = media_info.get('dimensions', {}).get('height')
    
    # Jika postingan adalah carousel (beberapa foto)
    elif media_info.get('media_type') == 8:
        if media_info.get('resources'):
            # Mengambil resolusi dari foto pertama dalam carousel
            first_resource = media_info['resources'][0]
            width = first_resource.get('dimensions', {}).get('width')
            height = first_resource.get('dimensions', {}).get('height')

    # Ambil data yang diperlukan dari 'media_info'
    scraped_data = {
        'username': media_info['user']['username'],
        'caption': media_info.get('caption_text', ''),
        'like_count': media_info.get('like_count', 0),
        'comment_count': media_info.get('comment_count', 0),
        'following_count': media_info['user'].get('following_count', 0),
        'follower_count': media_info['user'].get('follower_count', 0),
        'width': width,
        'height': height
    }

    return scraped_data
