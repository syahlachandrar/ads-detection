from flask import request, redirect, url_for, flash, render_template
from werkzeug.security import generate_password_hash

from flask import request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash

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
