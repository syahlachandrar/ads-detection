# headline_sub.py
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Memastikan nltk memiliki semua data yang dibutuhkan
import nltk
nltk.download('punkt')
nltk.download('stopwords')

def extract_headline_subheadline(caption):
    # Tokenisasi teks menjadi kalimat
    sentences = sent_tokenize(caption)
    
    if not sentences:
        return None, None

    # Menggunakan pendekatan sederhana:
    # Kalimat pertama sebagai headline
    headline = sentences[0]

    # Kalimat kedua sebagai subheadline jika ada
    subheadline = sentences[1] if len(sentences) > 1 else None

    return headline, subheadline

def detect_price(caption):
    # Daftar kata-kata yang menunjukkan angka bukan harga produk
    exclusion_keywords = [
        r'potongan', r'diskon', r'promo', r'gratis', r'hadiah', 
        r'voucher', r'cashback', r'bonus'
    ]
    
    # Pola regex untuk mendeteksi harga
    price_patterns = [
        r'(?<![\w])Rp\s?[\d.,]+(?![\w])',            # Format "Rp 1.000.000" atau "Rp1000000"
        r'(?<![\w])IDR\s?[\d.,]+(?![\w])',           # Format "IDR 1.000.000"
        r'(?<![\w])\$\s?[\d.,]+(?![\w])',            # Format "$1000" atau "$ 1,000.00"
        r'(?<![\w])[\d.]+(?:k|K|ribu)(?![\w])',      # Format "100k" atau "100 ribu"
        r'(?<![\w])[\d.]+(?:jt|juta)(?![\w])'        # Format "1jt" atau "1 juta"
    ]
    
    # Gabungkan semua pola ke dalam satu regex
    combined_pattern = '|'.join(price_patterns)
    
    # Cari apakah ada yang cocok dengan pola harga
    matches = re.finditer(combined_pattern, caption, re.IGNORECASE)
    
    for match in matches:
        detected_price = match.group(0)
        
        # Ambil kata-kata di sekitar harga yang terdeteksi
        context = caption[max(0, match.start() - 20): match.end() + 20].lower()
        
        # Periksa apakah konteks mengandung kata-kata yang mengecualikan
        if any(re.search(keyword, context) for keyword in exclusion_keywords):
            continue  # Lewati angka ini karena bukan harga produk
        
        return detected_price  # Harga valid ditemukan
    
    return None  # Tidak ada harga yang valid ditemukan