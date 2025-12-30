import os
# TensorFlow warnings ko hide karne ke liye
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from issue_detector import detect_issue_with_ai

app = Flask(__name__)
app.secret_key = 'civiclens_restored_final_2025'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROFILE_FOLDER'] = 'static/profiles'

# Login persistence 30 days ke liye
app.permanent_session_lifetime = timedelta(days=30)

# Folders ensure karein
for folder in [app.config['UPLOAD_FOLDER'], app.config['PROFILE_FOLDER']]:
    if not os.path.exists(folder): os.makedirs(folder)

def get_db_connection():
    conn = sqlite3.connect('issues.db')
    conn.row_factory = sqlite3.Row
    return conn

# Database Initialization with Credits Column
def init_db():
    conn = get_db_connection()
    # Users Table (Added 'credits' field)
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, email TEXT UNIQUE, password TEXT, 
                  phone TEXT, bio TEXT, profile_pic TEXT DEFAULT 'default_user.png',
                  credits INTEGER DEFAULT 0)''') # User rewards track karne ke liye
    # Reports Table
    conn.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, image_path TEXT, 
                  issue_type TEXT, ai_description TEXT, lat TEXT, lon TEXT, address TEXT, 
                  status TEXT DEFAULT 'Pending', timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- ROUTES ---

@app.route('/')
def landing():
    user_data = None
    if session.get('logged_in') and session.get('role') == 'citizen':
        conn = get_db_connection()
        user_data = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        conn.close()
    return render_template('landing.html', user=user_data)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name, email, pw = request.form.get('name'), request.form.get('email'), request.form.get('password')
        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                         (name, email, generate_password_hash(pw)))
            conn.commit()
            conn.close()
            flash("Signup Successful! Please login.")
            return redirect(url_for('login'))
        except: flash("Email already registered!")
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email, pw = request.form.get('email'), request.form.get('password')
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], pw):
            session.update({'role': 'citizen', 'logged_in': True, 'user_id': user['id'], 'user_name': user['name']})
            return redirect(url_for('landing'))
        flash("Wrong Credentials!")
    return render_template('login.html', auth_mode=False)

@app.route('/auth_login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'POST':
        email, password = request.form.get('email'), request.form.get('password')
        if email == "admin@gov.in" and password == "admin123":
            session.update({'role': 'admin', 'logged_in': True, 'user_name': 'Authority'})
            return redirect(url_for('admin_dashboard'))
        flash("Invalid Credentials!")
    return render_template('login.html', auth_mode=True)

@app.route('/index')
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if request.method == 'POST':
        name, phone, bio = request.form.get('name'), request.form.get('phone'), request.form.get('bio')
        conn.execute("UPDATE users SET name=?, phone=?, bio=? WHERE id=?", (name, phone, bio, session['user_id']))
        conn.commit()
        conn.close()
        session['user_name'] = name
        return redirect(url_for('user_dashboard'))
    conn.close()
    return render_template('edit_profile.html', user=user)

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('logged_in'): return redirect(url_for('login'))
    file = request.files.get('file')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    address = request.form.get('address')
    
    if not lat or not lon:
        flash("Location access is mandatory for reporting issues.")
        return redirect(url_for('index'))
    
    if file:
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        issue_type, ai_desc = detect_issue_with_ai(filepath)
        
        if issue_type == "Invalid":
            session['last_img'] = filename 
            session['last_lat'] = lat
            session['last_lon'] = lon
            session['last_addr'] = address
            flash(f"AI Alert: {ai_desc}")
            return redirect(url_for('index'))

        conn = get_db_connection()
        conn.execute('''INSERT INTO reports 
                     (user_id, image_path, issue_type, ai_description, lat, lon, address, timestamp) 
                     VALUES (?,?,?,?,?,?,?,?)''',
                  (session['user_id'], filename, issue_type, ai_desc, lat, lon, address, 
                   datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()
        
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('index'))

@app.route('/manual_upload', methods=['POST'])
def manual_upload():
    if not session.get('logged_in'): return redirect(url_for('login'))
    filename = request.form.get('temp_filename')
    
    conn = get_db_connection()
    conn.execute('''INSERT INTO reports (user_id, image_path, issue_type, ai_description, lat, lon, address, timestamp) 
                 VALUES (?,?,?,?,?,?,?,?)''',
              (session['user_id'], filename, request.form.get('issue_type'), f"Manual: {request.form.get('user_desc')}", 
               request.form.get('lat'), request.form.get('lon'), request.form.get('address'), datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    flash("Manual submission successful!")
    return redirect(url_for('user_dashboard'))

@app.route('/user_dashboard')
def user_dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    # User info fetch credits ke liye
    user = conn.execute("SELECT credits FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    reports = conn.execute("SELECT * FROM reports WHERE user_id = ? ORDER BY id DESC", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('user_dashboard.html', reports=reports, user_credits=user['credits'])

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    conn = get_db_connection()
    reports = conn.execute('''SELECT r.*, u.name as user_name FROM reports r 
                            LEFT JOIN users u ON r.user_id = u.id ORDER BY r.id DESC''').fetchall()
    conn.close()
    return render_template('dashboard.html', reports=reports)

@app.route('/resolve_issue/<int:id>')
def resolve_issue(id):
    if session.get('role') == 'admin':
        conn = get_db_connection()
        
        # Report fetch karein user_id nikalne ke liye
        report = conn.execute("SELECT user_id, status FROM reports WHERE id = ?", (id,)).fetchone()
        
        if report and report['status'] != 'Resolved':
            # Issue Resolve karein
            conn.execute("UPDATE reports SET status = 'Resolved' WHERE id = ?", (id,))
            # User ko 50 Credits de
            conn.execute("UPDATE users SET credits = credits + 50 WHERE id = ?", (report['user_id'],))
            conn.commit()
            flash("Issue marked as resolved and 50 credits awarded!")
        
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)