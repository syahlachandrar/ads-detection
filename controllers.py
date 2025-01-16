from flask import request, redirect, url_for, flash, render_template
from werkzeug.security import generate_password_hash
import re
import json


def clean_list(data):
    # Jika data adalah list of lists, ratakan terlebih dahulu
    if isinstance(data[0], list):
        data = [item for sublist in data for item in sublist]
    return [re.sub(r'[^\x00-\x7F]+', '', item) for item in data] 


def add_user(mysql):
    if request.method == 'POST':
        print(request.form)  # Tambahkan ini untuk melihat data yang diterima
        username = request.form.get('username')  # Gunakan .get untuk menghindari KeyError
        email = request.form.get('email')
        password = request.form.get('pass')
        level = request.form.get('level')  # Ubah ini untuk menggunakan .get
        
        # Validasi level
        if level not in ['1', '2']:
            flash('Level tidak valid!', 'danger')
            return redirect(url_for('add_user_route'))

        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO tb_users (username, email, pass, level) VALUES (%s, %s, %s, %s)', 
                       (username, email, hashed_password, level))
        mysql.connection.commit()
        cursor.close()

        flash('User berhasil ditambahkan!', 'success')
        if level == '1':
            return redirect(url_for('dashboard_admin'))  
        else:
            return redirect(url_for('dashboard_pengguna'))

    return render_template('tambah.html')

def edit_user(user_id, mysql):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE tb_users SET username = %s, email = %s WHERE user_id = %s', (username, email, user_id))
        mysql.connection.commit()
        flash('User berhasil diupdate!', 'success')
        return redirect(url_for('dashboard_admin'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    print(f"Editing user with ID: {user_id}")
    return render_template('edit_user.html', user=user)

def delete_user(user_id, mysql):
    cursor = mysql.connection.cursor()
    
    # Ambil level pengguna sebelum dihapus
    cursor.execute('SELECT level FROM tb_users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    
    if user:
        level = user[0]  # Ambil level pengguna
        print(f"Level pengguna yang akan dihapus: {level}")  # Debugging

        # Hapus pengguna
        cursor.execute('DELETE FROM tb_users WHERE user_id = %s', (user_id,))
        mysql.connection.commit()
        cursor.close()

        flash('User berhasil dihapus!', 'success')

        # Redirect berdasarkan level pengguna
        if level == '1':
            print("Mengalihkan ke dashboard admin")  # Debugging
            return redirect(url_for('dashboard_admin'))  # Jika admin yang dihapus, kembali ke dashboard admin
        elif level == '2':
            print("Mengalihkan ke dashboard pengguna")  # Debugging
            return redirect(url_for('dashboard_pengguna'))  # Jika pengunjung yang dihapus, kembali ke dashboard pengguna

    # Jika pengguna tidak ditemukan, kembali ke dashboard admin sebagai fallback
    return redirect(url_for('dashboard_admin'))

# tAbel hasill
def add_hasil(mysql, url, headline, subheadline, detected_price, predicted_reach, rake_keywords, like_count, comment_count,performance):
    # Pastikan rake_keywords dalam format string
    rake_keywords_cleaned = ', '.join([str(item) for item in rake_keywords]) if isinstance(rake_keywords, list) else str(rake_keywords)
    
    # Pastikan headline dan subheadline adalah string
    headline = str(headline) if headline else ""
    subheadline = str(subheadline) if subheadline else ""
    
    try:
        # Query untuk memasukkan data ke database
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO tb_hasil (url, headline, subheadline, detected_price, 
                          predicted_reach, rake_keywords, like_count, comment_count, performance, created_at) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())''', 
                       (url, headline, subheadline, detected_price, 
                        predicted_reach, rake_keywords_cleaned, like_count, comment_count, performance))

        mysql.connection.commit()  # Simpan perubahan ke database
        cursor.close()
        print("Data berhasil disimpan ke database.")
    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan ke database: {e}")


def get_all_hasil(mysql):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_hasil ORDER BY created_at DESC")
    results = cursor.fetchall()
    cursor.close()
    return results



