from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'secretkey'
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'videos')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            uploaded_by TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    if 'user' in session:
        search_query = request.args.get('search', '')
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        if search_query:
            cursor.execute("SELECT filename, uploaded_by FROM videos WHERE filename LIKE ?", ('%' + search_query + '%',))
        else:
            cursor.execute("SELECT filename, uploaded_by FROM videos")
        videos = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM videos WHERE uploaded_by = ?", (session['user'],))
        video_count = cursor.fetchone()[0]
        conn.close()
        return render_template('home.html', user=session['user'], videos=videos, video_count=video_count, search_query=search_query)
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            flash('Signup successful! Please login.', 'success')
            return redirect('/login')
        except:
            flash('User already exists!', 'error')
            return redirect('/signup')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect('/')
        flash('Invalid credentials', 'error')
        return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect('/login')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        if 'video' not in request.files:
            flash("No video file found", "error")
            return redirect('/upload')

        file = request.files['video']
        if file.filename == '':
            flash("No selected file", "error")
            return redirect('/upload')

        if file:
            filename = secure_filename(file.filename)
            upload_dir = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO videos (filename, uploaded_by) VALUES (?, ?)', (filename, session['user']))
            conn.commit()
            conn.close()

            flash("Video uploaded successfully!", "success")
            return redirect('/')
        else:
            flash("Something went wrong", "error")
    return render_template('upload.html')

@app.route('/delete/<filename>', methods=['POST'])
def delete_video(filename):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM videos WHERE filename = ? AND uploaded_by = ?', (filename, session['user']))
    conn.commit()
    conn.close()

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    flash("Video deleted successfully.", "info")
    return redirect('/')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM videos WHERE uploaded_by = ?', (session['user'],))
    videos = cursor.fetchall()
    conn.close()

    return render_template('profile.html', user=session['user'], videos=videos)

if __name__== '__main__':
    init_db()
    app.run(debug=True)