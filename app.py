import json
import smtplib
import sqlite3
import re
import random
import secrets
from datetime import datetime, timedelta
from email.message import EmailMessage
from flask import Flask, render_template, request, flash, redirect, url_for, session
import os
from config import Config

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = Config.SECRET_KEY

# Load configuration
ALLOWED_EMAILS = Config.ALLOWED_EMAILS
SIGNATURE_PATHS = Config.SIGNATURE_PATHS
DATABASE_PATH = Config.DATABASE_PATH

# OTP storage (in-memory for simplicity, consider database storage for production)
otp_store = {}

def load_credentials():
    return Config.load_credentials()

credentials = load_credentials()

def load_signature(account):
    path = SIGNATURE_PATHS.get(account.lower())
    if path and os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return ""

def get_all_clients():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients

def get_all_templates():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, subject, body FROM templates")
    templates = cursor.fetchall()
    conn.close()
    return templates

def convert_clickable_links(text):
    pattern = r'\[([^\]]+)\]\{([^\}]+)\}'
    return re.sub(pattern, r'<a href="\2">\1</a>', text)

# Helper function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Helper function to send OTP email
def send_otp_email(email, otp):
    # Determine which account to use based on email domain
    account = "hsa" if "homeschool.asia" in email else "kfq"
    acc_info = credentials[account]
    
    print(f"Attempting to send OTP to {email} using {account} account: {acc_info['email']}")
    
    msg = EmailMessage()
    msg["Subject"] = "Your OTP for MST Email Automation"
    msg["From"] = f'{acc_info["display_name"]} <{acc_info["email"]}>'
    msg["To"] = email
    
    body_text = f"Your OTP for MST Email Automation is: {otp}\n\nThis code will expire in 10 minutes."
    
    body_html = f"""
    <html>
    <head>
        <style>
            body, div, p, td {{
                font-family: Arial, sans-serif;
                font-size: 16px;
                color: black;
            }}
        </style>
    </head>
    <body>
        <div>
            <h2>Your OTP for MST Email Automation</h2>
            <p>Your 6-digit verification code is:</p>
            <h1 style="font-size: 32px; letter-spacing: 5px; background-color: #f5f5f5; padding: 15px; text-align: center; border-radius: 8px;">{otp}</h1>
            <p>This code will expire in 10 minutes.</p>
            <p>If you did not request this code, please ignore this email.</p>
        </div>
    </body>
    </html>
    """
    
    msg.set_content(body_text)
    msg.add_alternative(body_html, subtype="html")
    
    try:
        print(f"Connecting to SMTP server: {acc_info['smtp_server']}:{acc_info['smtp_port']}")
        with smtplib.SMTP(acc_info["smtp_server"], acc_info["smtp_port"]) as server:
            print("Starting TLS")
            server.starttls()
            print(f"Logging in with email: {acc_info['email']}")
            server.login(acc_info["email"], acc_info["password"])
            print("Sending message")
            server.send_message(msg)
            print("Message sent successfully")
        return True
    except Exception as e:
        print(f"Failed to send OTP to {email}: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Account info used: {acc_info['email']} (password hidden)")
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash("Email is required.", "error")
            return redirect(url_for('login'))
        
        if email not in ALLOWED_EMAILS:
            flash("Invalid email address. Please use an authorized email.", "error")
            return redirect(url_for('login'))
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP with expiration time (10 minutes)
        otp_store[email] = {
            'otp': otp,
            'expires_at': datetime.now() + timedelta(minutes=10)
        }
        
        # Send OTP email
        if send_otp_email(email, otp):
            flash("OTP sent to your email.", "success")
            return redirect(url_for('verify_otp_page', email=email))
        else:
            flash("Failed to send OTP. Please try again.", "error")
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/verify-otp', methods=['GET'])
def verify_otp_page():
    email = request.args.get('email')
    if not email or email not in ALLOWED_EMAILS:
        flash("Invalid request. Please login again.", "error")
        return redirect(url_for('login'))
    
    return render_template('verify_otp.html', email=email)

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    email = request.form.get('email')
    otp = request.form.get('otp')
    
    if not email or not otp:
        flash("Email and OTP are required.", "error")
        return redirect(url_for('login'))
    
    if email not in otp_store:
        flash("OTP expired or invalid. Please request a new one.", "error")
        return redirect(url_for('login'))
    
    stored_otp = otp_store[email]
    
    # Check if OTP is expired
    if datetime.now() > stored_otp['expires_at']:
        del otp_store[email]
        flash("OTP has expired. Please request a new one.", "error")
        return redirect(url_for('login'))
    
    # Verify OTP
    if otp == stored_otp['otp']:
        # OTP verified, set session
        session['authenticated'] = True
        session['email'] = email
        
        # Remove OTP from store
        del otp_store[email]
        
        flash("Login successful!", "success")
        return redirect(url_for('index'))
    else:
        flash("Invalid OTP. Please try again.", "error")
        return redirect(url_for('verify_otp_page', email=email))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/')
def index():
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
    
    clients = get_all_clients()
    templates = get_all_templates()
    return render_template('send_email.html', clients=clients, templates=templates)

@app.route('/send', methods=['POST'])
def send_email():
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
        
    selected_emails = request.form.getlist('recipients')
    subject = request.form.get('subject')
    body = request.form.get('body')
    account = request.form.get('account').lower()
    send_type = request.form.get('send_type', 'to')

    if not selected_emails or not subject or not body or not account:
        flash("All fields are required.", "error")
        return redirect(url_for('index'))

    if account not in credentials:
        flash(f"No credentials found for account: {account}", "error")
        return redirect(url_for('index'))

    acc_info = credentials[account]
    signature_html = load_signature(account)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in selected_emails)
    cursor.execute(f"SELECT name, email FROM clients WHERE email IN ({placeholders})", selected_emails)
    client_data = cursor.fetchall()
    conn.close()

    sent_count = 0
    failed_count = 0

    for name, email in client_data:
        personalized_body = body.replace("{name}", name)
        converted_body = convert_clickable_links(personalized_body)
        body_html_content = converted_body.replace("\n", "<br>")

        body_html = f"""
        <html>
        <head>
            <style>
                body, div, p, td {{
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    color: black;
                }}
                a {{
                    color: #007BFF;
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div>
                <p>{body_html_content}</p>
                <div style="color: black;">{signature_html}</div>
            </div>
        </body>
        </html>
        """

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f'{acc_info["display_name"]} <{acc_info["email"]}>'

        if send_type == 'to':
            msg["To"] = email
        else:
            msg["To"] = acc_info["email"]
            msg["Bcc"] = email

        msg.set_content(personalized_body)
        msg.add_alternative(body_html, subtype="html")

        try:
            with smtplib.SMTP(acc_info["smtp_server"], acc_info["smtp_port"]) as server:
                server.starttls()
                server.login(acc_info["email"], acc_info["password"])
                server.send_message(msg)
            sent_count += 1
        except Exception as e:
            print(f"Failed to send to {email}: {e}")
            failed_count += 1

    flash(f"Emails sent: {sent_count}, Failed: {failed_count}", "success" if failed_count == 0 else "error")
    return redirect(url_for('index'))

@app.route('/clients')
def view_clients():
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
        
    clients = get_all_clients()
    return render_template('clients.html', clients=clients)

@app.route('/clients/add', methods=['POST'])
def add_client():
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
        
    name = request.form.get('name')
    email = request.form.get('email')
    if not name or not email:
        flash("Name and email are required.", "error")
    else:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clients (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            conn.close()
            flash("Client added successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
    return redirect(url_for('view_clients'))

@app.route('/clients/delete/<int:client_id>')
def delete_client(client_id):
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
    flash("Client deleted successfully.", "success")
    return redirect(url_for('view_clients'))

@app.route('/clients/edit/<int:client_id>', methods=['POST'])
def edit_client(client_id):
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
        
    name = request.form.get('name')
    email = request.form.get('email')
    if not name or not email:
        flash("Name and email are required.", "error")
    else:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE clients SET name = ?, email = ? WHERE id = ?", (name, email, client_id))
            conn.commit()
            conn.close()
            flash("Client updated successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
    return redirect(url_for('view_clients'))

@app.route('/email-templates')
def email_templates():
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
        
    templates = get_all_templates()
    return render_template('email_templates.html', templates=templates)

@app.route('/templates/add', methods=['POST'])
def add_template():
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
        
    name = request.form.get('name')
    subject = request.form.get('subject')
    body = request.form.get('body')
    if not name or not subject or not body:
        flash("All fields are required.", "error")
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO templates (name, subject, body) VALUES (?, ?, ?)", (name, subject, body))
        conn.commit()
        conn.close()
        flash("Template added successfully!", "success")
    return redirect(url_for('email_templates'))

@app.route('/templates/delete/<int:template_id>')
def delete_template(template_id):
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()
    flash("Template deleted successfully!", "success")
    return redirect(url_for('email_templates'))

@app.route('/templates/edit/<int:template_id>', methods=['POST'])
def edit_template(template_id):
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access this page.", "error")
        return redirect(url_for('login'))
        
    name = request.form.get('name')
    subject = request.form.get('subject')
    body = request.form.get('body')
    if not name or not subject or not body:
        flash("All fields are required.", "error")
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE templates SET name = ?, subject = ?, body = ? WHERE id = ?", (name, subject, body, template_id))
        conn.commit()
        conn.close()
        flash("Template updated successfully!", "success")
    return redirect(url_for('email_templates'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
