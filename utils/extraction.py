def extract_headline_subheadline(caption):
    # Ekstraksi headline dan subheadline dari caption
    # Contoh: gunakan simple logic untuk menemukan headline/subheadline
    headline = caption.split('.')[0]
    subheadline = caption.split('.')[1] if len(caption.split('.')) > 1 else None
    return headline, subheadline

def detect_price(caption):
    # Deteksi harga dalam caption
    # Contoh sederhana: mencari angka yang menyerupai harga
    import re
    price = re.findall(r'\$\d+', caption)
    return price[0] if price else 'Tidak ada harga'

def detect_product_advantage(caption):
    # Deteksi kelebihan produk
    keywords = ["tahan lama", "terjangkau", "inovatif", "premium"]
    advantages = [word for word in keywords if word in caption.lower()]
    return advantages
