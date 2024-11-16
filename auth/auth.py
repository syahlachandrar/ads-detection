from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
import re

# Create a blueprint
auth = Blueprint('auth', __name__)
mysql = MySQL()

# Registration route
import re

@auth.route('/registrasi', methods=('GET', 'POST'))
def registrasi():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['pass']

        # Pola regex untuk mendeteksi email admin (misal mengandung 'admin')
        admin_email_pattern = re.compile(r'.*admin.*@.*')

        # Tentukan level berdasarkan email
        if admin_email_pattern.match(email):
            level = 'Admin'
        else:
            level = 'Pengunjung'

        # Check if username or email exists
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM tb_users WHERE username=%s OR email=%s', (username, email,))
        akun = cursor.fetchone()
        if akun is None:
            cursor.execute('INSERT INTO tb_users VALUES (NULL, %s, %s, %s, %s)',
                           (username, email, generate_password_hash(password), level))
            mysql.connection.commit()
            flash('Registrasi Berhasil', 'success')
            return redirect(url_for('auth.login'))  # Redirect to login after registration
        else:
            flash('Username atau email sudah ada', 'danger')
    return render_template('daftar.html')


# Login route
@auth.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if email exists
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM tb_users WHERE email=%s', (email,))
        akun = cursor.fetchone()
        if akun is None:
            flash('Login Gagal, Cek Username Anda', 'danger')
        elif not check_password_hash(akun[3], password):
            flash('Login gagal, Cek Password Anda', 'danger')
        else:
            session['loggedin'] = True
            session['username'] = akun[1]
            session['level'] = akun[4]
            
            # Debugging: cek session level
            print(session)

            # Jika level pengguna adalah Admin, arahkan ke halaman dashboard-admin
            if session['level'] == 'admin':
                return redirect(url_for('dashboard_admin'))  # Arahkan admin ke dashboard admin
            else:
                return redirect(url_for('home'))  # Arahkan pengguna biasa ke halaman home
    return render_template('login.html')



# Logout route
@auth.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('level', None)
    return redirect(url_for('auth.login'))
