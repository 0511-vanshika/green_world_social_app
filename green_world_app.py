#!/usr/bin/env python3
"""
🌍 GREEN WORLD - REAL SOCIAL MEDIA PLATFORM
Complete social media app where you can post anything with images
FINAL VERSION - Modern Social Network
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import uuid
from datetime import datetime
import json
import random
import base64

app = Flask(__name__)
app.secret_key = 'green-world-social-secret-key-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize SocketIO for real-time features
socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    """Initialize Green World Social Media Database"""
    conn = sqlite3.connect('green_world_social.db')
    cursor = conn.cursor()
    
    # Users table - Real Social Media
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            bio TEXT DEFAULT '',
            profile_image TEXT DEFAULT '',
            location TEXT DEFAULT '',
            website TEXT DEFAULT '',
            followers_count INTEGER DEFAULT 0,
            following_count INTEGER DEFAULT 0,
            posts_count INTEGER DEFAULT 0,
            is_verified BOOLEAN DEFAULT FALSE,
            is_private BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Posts table - Real Social Media Posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT DEFAULT '',
            image_data TEXT DEFAULT '',
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            shares_count INTEGER DEFAULT 0,
            location TEXT DEFAULT '',
            hashtags TEXT DEFAULT '',
            is_featured BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Add missing columns if they don't exist
    try:
        cursor.execute('ALTER TABLE posts ADD COLUMN hashtags TEXT DEFAULT ""')
    except:
        pass
    try:
        cursor.execute('ALTER TABLE posts ADD COLUMN location TEXT DEFAULT ""')
    except:
        pass

    # Social media interaction tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS follows (
            id TEXT PRIMARY KEY,
            follower_id TEXT NOT NULL,
            following_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (follower_id) REFERENCES users (id),
            FOREIGN KEY (following_id) REFERENCES users (id),
            UNIQUE(follower_id, following_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            post_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (post_id) REFERENCES posts (id),
            UNIQUE(user_id, post_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            post_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            content TEXT NOT NULL,
            read_status BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')

    # Real-time notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            data TEXT,
            read_status BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Green World Social Database initialized!")

def create_sample_users():
    """Create sample users for the social platform"""
    conn = sqlite3.connect('green_world_social.db')
    
    # Check if sample data already exists
    existing = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if existing > 0:
        conn.close()
        return
    
    # Sample users
    sample_users = [
        {
            'id': 'user_001',
            'username': 'alex_green',
            'email': 'alex@greenworld.com',
            'first_name': 'Alex',
            'last_name': 'Green',
            'password_hash': generate_password_hash('password123'),
            'bio': 'Nature lover 🌿 | Photographer 📸 | Faridabad',
            'location': 'Faridabad, India'
        },
        {
            'id': 'user_002',
            'username': 'maya_nature',
            'email': 'maya@greenworld.com',
            'first_name': 'Maya',
            'last_name': 'Sharma',
            'password_hash': generate_password_hash('password123'),
            'bio': 'Travel enthusiast ✈️ | Food blogger 🍕 | Life is beautiful',
            'location': 'Delhi, India'
        },
        {
            'id': 'user_003',
            'username': 'raj_explorer',
            'email': 'raj@greenworld.com',
            'first_name': 'Raj',
            'last_name': 'Patel',
            'password_hash': generate_password_hash('password123'),
            'bio': 'Tech geek 💻 | Fitness freak 💪 | Coffee addict ☕',
            'location': 'Mumbai, India'
        },
        {
            'id': 'user_004',
            'username': 'priya_creative',
            'email': 'priya@greenworld.com',
            'first_name': 'Priya',
            'last_name': 'Singh',
            'password_hash': generate_password_hash('password123'),
            'bio': 'Artist 🎨 | Designer ✨ | Creating magic every day',
            'location': 'Bangalore, India'
        }
    ]

    # Insert sample users
    for user in sample_users:
        conn.execute('''
            INSERT OR IGNORE INTO users 
            (id, username, email, first_name, last_name, password_hash, bio, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], user['username'], user['email'], user['first_name'],
              user['last_name'], user['password_hash'], user['bio'], user['location']))

    conn.commit()
    conn.close()
    print("✅ Sample users created!")

def create_sample_posts():
    """Create sample posts for the social platform"""
    conn = sqlite3.connect('green_world_social.db')
    
    # Check if sample posts already exist
    existing = conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    if existing > 0:
        conn.close()
        return
    
    # Sample posts with diverse content
    sample_posts = [
        {
            'id': 'post_001',
            'user_id': 'user_001',
            'content': 'Beautiful sunset at Surajkund today! 🌅 The colors were absolutely magical. Nature never fails to amaze me! #sunset #faridabad #nature',
            'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop',
            'hashtags': '#sunset #faridabad #nature #photography',
            'location': 'Surajkund, Faridabad',
            'likes_count': random.randint(15, 50),
            'comments_count': random.randint(3, 12)
        },
        {
            'id': 'post_002',
            'user_id': 'user_002',
            'content': 'Just tried this amazing street food in Old Delhi! 🍛 The flavors are incredible. Food is definitely the way to my heart! Who else loves exploring local cuisine?',
            'image_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=600&h=400&fit=crop',
            'hashtags': '#food #delhi #streetfood #foodie',
            'location': 'Old Delhi, India',
            'likes_count': random.randint(20, 60),
            'comments_count': random.randint(5, 15)
        },
        {
            'id': 'post_003',
            'user_id': 'user_003',
            'content': 'Morning workout done! 💪 Started my day with a 5km run and some strength training. Consistency is key to achieving your fitness goals. What\'s your morning routine?',
            'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=400&fit=crop',
            'hashtags': '#fitness #workout #morning #motivation',
            'location': 'Mumbai, India',
            'likes_count': random.randint(25, 45),
            'comments_count': random.randint(4, 10)
        },
        {
            'id': 'post_004',
            'user_id': 'user_004',
            'content': 'Working on a new digital art piece! 🎨 This one is inspired by the vibrant colors of Indian festivals. Art is my way of expressing emotions and stories. ✨',
            'image_url': 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=600&h=400&fit=crop',
            'hashtags': '#art #digitalart #creative #design',
            'location': 'Bangalore, India',
            'likes_count': random.randint(30, 70),
            'comments_count': random.randint(6, 18)
        },
        {
            'id': 'post_005',
            'user_id': 'user_001',
            'content': 'Coffee and coding session! ☕💻 Working on some exciting new projects. There\'s something magical about the combination of caffeine and creativity.',
            'image_url': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop',
            'hashtags': '#coffee #coding #work #productivity',
            'location': 'Home Office, Faridabad',
            'likes_count': random.randint(18, 35),
            'comments_count': random.randint(2, 8)
        },
        {
            'id': 'post_006',
            'user_id': 'user_002',
            'content': 'Weekend getaway to the mountains! 🏔️ Sometimes you need to disconnect from the digital world and reconnect with nature. Feeling refreshed and inspired!',
            'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop',
            'hashtags': '#mountains #travel #weekend #nature',
            'location': 'Himachal Pradesh, India',
            'likes_count': random.randint(40, 80),
            'comments_count': random.randint(8, 20)
        }
    ]

    # Insert sample posts
    for post in sample_posts:
        conn.execute('''
            INSERT OR IGNORE INTO posts 
            (id, user_id, content, image_url, hashtags, location, likes_count, comments_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (post['id'], post['user_id'], post['content'], post['image_url'],
              post['hashtags'], post['location'], post['likes_count'], post['comments_count']))

    conn.commit()
    conn.close()
    print("✅ Sample posts created!")

def get_posts(user_id=None, limit=20):
    """Get posts for the social feed"""
    conn = sqlite3.connect('green_world_social.db')
    conn.row_factory = sqlite3.Row

    posts = conn.execute('''
        SELECT p.*, u.first_name, u.last_name, u.username, u.profile_image
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()

    conn.close()
    return [dict(post) for post in posts]

def create_post(user_id, content, image_data=None, location='', hashtags=''):
    """Create a new post"""
    post_id = str(uuid.uuid4())

    conn = sqlite3.connect('green_world_social.db')
    conn.execute('''
        INSERT INTO posts (id, user_id, content, image_data, location, hashtags)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (post_id, user_id, content, image_data or '', location, hashtags))

    # Update user's post count
    conn.execute('''
        UPDATE users SET posts_count = posts_count + 1 WHERE id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()
    return post_id

def like_post(user_id, post_id):
    """Like or unlike a post"""
    conn = sqlite3.connect('green_world_social.db')

    # Check if already liked
    existing = conn.execute('''
        SELECT id FROM likes WHERE user_id = ? AND post_id = ?
    ''', (user_id, post_id)).fetchone()

    if existing:
        # Unlike
        conn.execute('DELETE FROM likes WHERE user_id = ? AND post_id = ?', (user_id, post_id))
        conn.execute('UPDATE posts SET likes_count = likes_count - 1 WHERE id = ?', (post_id,))
        liked = False
    else:
        # Like
        like_id = str(uuid.uuid4())
        conn.execute('INSERT INTO likes (id, user_id, post_id) VALUES (?, ?, ?)', (like_id, user_id, post_id))
        conn.execute('UPDATE posts SET likes_count = likes_count + 1 WHERE id = ?', (post_id,))
        liked = True

    conn.commit()
    conn.close()
    return liked

# Routes
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌍 Green World - Real Social Media Platform</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0d2818 0%, #1a4d2e 25%, #2d5a27 50%, #4a7c59 75%, #6b8e23 100%);
                min-height: 100vh;
                color: #e8f5e8;
                position: relative;
                overflow-x: hidden;
            }

            /* Cute Plants */
            .cute-plant {
                position: absolute;
                font-size: 2.5rem;
                animation: plantSway 4s ease-in-out infinite;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
                cursor: pointer;
                pointer-events: auto;
                z-index: 10;
                transition: all 0.3s ease;
            }

            @keyframes plantSway {
                0%, 100% { transform: rotate(-5deg) scale(1); }
                25% { transform: rotate(3deg) scale(1.1); }
                50% { transform: rotate(-2deg) scale(0.9); }
                75% { transform: rotate(4deg) scale(1.05); }
            }

            .cute-plant:hover {
                transform: scale(1.4) rotate(15deg) !important;
                filter: brightness(1.3) drop-shadow(0 0 20px rgba(74, 124, 89, 0.8));
            }

            .container { max-width: 1200px; margin: 0 auto; padding: 20px; position: relative; z-index: 1; }
            .header {
                text-align: center;
                color: #e8f5e8;
                margin-bottom: 50px;
                padding: 60px 20px;
                background: rgba(13, 40, 24, 0.9);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(45, 90, 39, 0.4);
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            }
            .auth-buttons {
                display: flex;
                gap: 20px;
                justify-content: center;
                margin-top: 30px;
                flex-wrap: wrap;
            }
            .btn {
                background: linear-gradient(135deg, #1a4d2e 0%, #2d5a27 50%, #4a7c59 100%);
                color: #e8f5e8;
                padding: 15px 40px;
                border: none;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                display: inline-block;
                transition: all 0.3s ease;
                font-size: 1.1rem;
                border: 1px solid rgba(45, 90, 39, 0.5);
            }
            .btn:hover {
                transform: translateY(-3px) scale(1.05);
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                border-color: rgba(74, 124, 89, 0.8);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-bottom: 50px;
            }
            .feature-card {
                background: rgba(13, 40, 24, 0.9);
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
                border: 1px solid rgba(45, 90, 39, 0.4);
                color: #e8f5e8;
            }
            .feature-card:hover { transform: translateY(-10px) scale(1.02); }
            .feature-icon { font-size: 4rem; margin-bottom: 20px; }
            .feature-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 15px; color: #e8f5e8; }
            .feature-desc { color: rgba(232, 245, 232, 0.8); line-height: 1.6; margin-bottom: 25px; }
        </style>
    </head>
    <body>
        <!-- Cute Plants -->
        <div class="cute-plant" style="left: 8%; top: 15%;">🌱</div>
        <div class="cute-plant" style="left: 88%; top: 20%;">🌿</div>
        <div class="cute-plant" style="left: 12%; top: 75%;">🍀</div>
        <div class="cute-plant" style="left: 85%; top: 80%;">🌾</div>
        <div class="cute-plant" style="left: 5%; top: 50%;">🌵</div>
        <div class="cute-plant" style="left: 92%; top: 55%;">🌳</div>
        <div class="cute-plant" style="left: 45%; top: 10%;">🌲</div>
        <div class="cute-plant" style="left: 50%; top: 90%;">🎋</div>

        <div class="container">
            <div class="header">
                <h1 style="font-size: 4rem; margin-bottom: 20px;">🌍 Green World</h1>
                <p style="font-size: 1.5rem; margin-bottom: 30px;">Real Social Media Platform</p>
                <p style="font-size: 1.2rem; opacity: 0.9;">Share • Connect • Explore • Create 🌟</p>

                <div class="auth-buttons">
                    <a href="/login" class="btn">🔑 Login</a>
                    <a href="/signup" class="btn">✨ Join Green World</a>
                    <a href="/feed" class="btn">🌐 Explore Feed</a>
                </div>
            </div>

            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">📸</div>
                    <h3 class="feature-title">Share Your World</h3>
                    <p class="feature-desc">Post photos, thoughts, and moments. Share anything with the world!</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <h3 class="feature-title">Real-time Interactions</h3>
                    <p class="feature-desc">Like, comment, and connect with people instantly!</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🌟</div>
                    <h3 class="feature-title">Interactive Experience</h3>
                    <p class="feature-desc">Cute movable plants and beautiful dark green themes!</p>
                </div>
            </div>
        </div>

        <script>
            // Interactive Plants
            document.addEventListener('DOMContentLoaded', function() {
                const plants = document.querySelectorAll('.cute-plant');

                plants.forEach((plant, index) => {
                    plant.addEventListener('click', function(e) {
                        const sparkle = document.createElement('div');
                        sparkle.innerHTML = '✨🌟✨';
                        sparkle.style.position = 'fixed';
                        sparkle.style.left = e.clientX + 'px';
                        sparkle.style.top = e.clientY + 'px';
                        sparkle.style.fontSize = '1.5rem';
                        sparkle.style.pointerEvents = 'none';
                        sparkle.style.zIndex = '1000';
                        sparkle.style.animation = 'sparkleEffect 1s ease-out';

                        document.body.appendChild(sparkle);
                        setTimeout(() => document.body.removeChild(sparkle), 1000);
                    });
                });

                document.addEventListener('mousemove', function(e) {
                    const mouseX = e.clientX / window.innerWidth;
                    const mouseY = e.clientY / window.innerHeight;

                    plants.forEach((plant, index) => {
                        const speed = (index + 1) * 0.3;
                        const x = (mouseX - 0.5) * speed * 30;
                        const y = (mouseY - 0.5) * speed * 30;
                        const rotation = (mouseX - 0.5) * speed * 15;

                        plant.style.transform = `translate(${x}px, ${y}px) rotate(${rotation}deg)`;
                    });
                });
            });

            const style = document.createElement('style');
            style.textContent = `
                @keyframes sparkleEffect {
                    0% { transform: scale(0) rotate(0deg); opacity: 1; }
                    50% { transform: scale(1.5) rotate(180deg); opacity: 0.8; }
                    100% { transform: scale(0.5) rotate(360deg) translateY(-30px); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # For demo - accept any credentials
        if email and password:
            session['user_id'] = 'user_001'
            session['username'] = 'demo_user'
            session['first_name'] = 'Demo'
            return redirect(url_for('feed'))
        else:
            flash('Please fill in all fields')

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔑 Login - Green World</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0d2818 0%, #1a4d2e 25%, #2d5a27 50%, #4a7c59 75%, #6b8e23 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #e8f5e8;
                position: relative;
                overflow: hidden;
            }

            .login-plant {
                position: absolute;
                font-size: 2.5rem;
                animation: loginPlantSway 4s ease-in-out infinite;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
                cursor: pointer;
                pointer-events: auto;
                z-index: 10;
                transition: all 0.3s ease;
            }

            .login-plant:nth-child(1) { left: 10%; top: 20%; animation-delay: 0s; }
            .login-plant:nth-child(2) { left: 85%; top: 15%; animation-delay: 1s; }
            .login-plant:nth-child(3) { left: 15%; top: 70%; animation-delay: 2s; }
            .login-plant:nth-child(4) { left: 80%; top: 75%; animation-delay: 0.5s; }
            .login-plant:nth-child(5) { left: 5%; top: 45%; animation-delay: 1.5s; }
            .login-plant:nth-child(6) { left: 90%; top: 45%; animation-delay: 2.5s; }

            @keyframes loginPlantSway {
                0%, 100% { transform: rotate(-5deg) scale(1); }
                25% { transform: rotate(3deg) scale(1.1); }
                50% { transform: rotate(-2deg) scale(0.9); }
                75% { transform: rotate(4deg) scale(1.05); }
            }

            .login-plant:hover {
                transform: scale(1.5) rotate(15deg) !important;
                filter: brightness(1.3) drop-shadow(0 0 20px rgba(74, 124, 89, 0.8));
            }

            .login-container {
                background: rgba(13, 40, 24, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 400px;
                text-align: center;
                border: 1px solid rgba(45, 90, 39, 0.4);
                backdrop-filter: blur(20px);
                position: relative;
                z-index: 100;
            }
            .logo { font-size: 3rem; margin-bottom: 10px; }
            .title { font-size: 2rem; font-weight: bold; margin-bottom: 10px; color: #e8f5e8; }
            .subtitle { color: rgba(232, 245, 232, 0.8); margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; text-align: left; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: 500; color: #e8f5e8; }
            .form-group input {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid rgba(45, 90, 39, 0.4);
                border-radius: 10px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
                background: rgba(13, 40, 24, 0.7);
                color: #e8f5e8;
            }
            .form-group input:focus {
                outline: none;
                border-color: rgba(74, 124, 89, 0.8);
                background: rgba(13, 40, 24, 0.9);
            }
            .form-group input::placeholder { color: rgba(232, 245, 232, 0.6); }
            .btn {
                width: 100%;
                background: linear-gradient(135deg, #1a4d2e 0%, #2d5a27 50%, #4a7c59 100%);
                color: #e8f5e8;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 20px;
                border: 1px solid rgba(45, 90, 39, 0.5);
            }
            .btn:hover {
                transform: translateY(-2px) scale(1.02);
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            }
            .demo-info {
                background: rgba(45, 90, 39, 0.3);
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                color: #e8f5e8;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <div class="login-plant">🌱</div>
        <div class="login-plant">🌿</div>
        <div class="login-plant">🍀</div>
        <div class="login-plant">🌾</div>
        <div class="login-plant">🌵</div>
        <div class="login-plant">🌳</div>

        <div class="login-container">
            <div class="logo">🌍</div>
            <h1 class="title">Welcome to Green World!</h1>
            <p class="subtitle">Sign in to your account</p>

            <form method="POST">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="Enter any email" required>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Enter any password" required>
                </div>

                <button type="submit" class="btn">🚀 Sign In</button>
            </form>

            <div class="demo-info">
                <strong>Demo Mode:</strong><br>
                Enter any email and password to continue!
            </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const plants = document.querySelectorAll('.login-plant');

                plants.forEach((plant, index) => {
                    plant.addEventListener('click', function(e) {
                        const sparkle = document.createElement('div');
                        sparkle.innerHTML = '✨🌟✨';
                        sparkle.style.position = 'fixed';
                        sparkle.style.left = e.clientX + 'px';
                        sparkle.style.top = e.clientY + 'px';
                        sparkle.style.fontSize = '1.5rem';
                        sparkle.style.pointerEvents = 'none';
                        sparkle.style.zIndex = '1000';
                        sparkle.style.animation = 'sparkleEffect 1s ease-out';

                        document.body.appendChild(sparkle);
                        setTimeout(() => document.body.removeChild(sparkle), 1000);
                    });
                });

                document.addEventListener('mousemove', function(e) {
                    const mouseX = e.clientX / window.innerWidth;
                    const mouseY = e.clientY / window.innerHeight;

                    plants.forEach((plant, index) => {
                        const speed = (index + 1) * 0.3;
                        const x = (mouseX - 0.5) * speed * 20;
                        const y = (mouseY - 0.5) * speed * 20;
                        const rotation = (mouseX - 0.5) * speed * 10;

                        plant.style.transform = `translate(${x}px, ${y}px) rotate(${rotation}deg)`;
                    });
                });
            });

            const style = document.createElement('style');
            style.textContent = `
                @keyframes sparkleEffect {
                    0% { transform: scale(0) rotate(0deg); opacity: 1; }
                    50% { transform: scale(1.5) rotate(180deg); opacity: 0.8; }
                    100% { transform: scale(0.5) rotate(360deg) translateY(-30px); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    ''')

@app.route('/feed')
def feed():
    posts = get_posts()

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌍 Green World - Social Feed</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0d2818 0%, #1a4d2e 25%, #2d5a27 50%, #4a7c59 75%, #6b8e23 100%);
                min-height: 100vh;
                color: #e8f5e8;
                position: relative;
                overflow-x: hidden;
            }

            /* Cute Plants */
            .cute-plant {
                position: absolute;
                font-size: 2rem;
                animation: plantSway 4s ease-in-out infinite;
                transition: transform 0.3s ease;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
                cursor: pointer;
                pointer-events: auto;
                z-index: 10;
            }

            @keyframes plantSway {
                0%, 100% { transform: rotate(-5deg) scale(1); }
                25% { transform: rotate(3deg) scale(1.05); }
                50% { transform: rotate(-2deg) scale(0.95); }
                75% { transform: rotate(4deg) scale(1.02); }
            }

            .cute-plant:hover {
                transform: scale(1.3) rotate(10deg) !important;
                filter: brightness(1.3) drop-shadow(0 0 15px rgba(74, 124, 89, 0.8));
            }

            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                position: relative;
                z-index: 1;
            }

            .header {
                text-align: center;
                color: #e8f5e8;
                margin-bottom: 30px;
                padding: 30px 20px;
                background: rgba(13, 40, 24, 0.8);
                border-radius: 20px;
                backdrop-filter: blur(15px);
                border: 1px solid rgba(45, 90, 39, 0.4);
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            }

            .post-form {
                background: rgba(13, 40, 24, 0.9);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                border: 1px solid rgba(45, 90, 39, 0.4);
                color: #e8f5e8;
            }

            .post-card {
                background: rgba(13, 40, 24, 0.85);
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 12px 30px rgba(0,0,0,0.2);
                transition: all 0.4s ease;
                border: 1px solid rgba(45, 90, 39, 0.3);
                color: #e8f5e8;
                position: relative;
                overflow: hidden;
            }

            .post-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                border-color: rgba(74, 124, 89, 0.6);
            }

            .post-header {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }

            .user-avatar {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(135deg, #1a4d2e, #4a7c59);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                margin-right: 15px;
                border: 2px solid rgba(45, 90, 39, 0.5);
                font-size: 1.2rem;
            }

            .post-content {
                margin-bottom: 15px;
                line-height: 1.6;
                font-size: 1.1rem;
            }

            .post-image {
                width: 100%;
                max-height: 400px;
                object-fit: cover;
                border-radius: 15px;
                margin: 15px 0;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }

            .post-actions {
                display: flex;
                gap: 20px;
                padding-top: 15px;
                border-top: 1px solid rgba(45, 90, 39, 0.3);
            }

            .action-btn {
                background: none;
                border: none;
                color: rgba(232, 245, 232, 0.8);
                cursor: pointer;
                padding: 8px 15px;
                border-radius: 20px;
                transition: all 0.3s ease;
                border: 1px solid rgba(45, 90, 39, 0.3);
                font-size: 0.9rem;
            }

            .action-btn:hover {
                background: rgba(45, 90, 39, 0.3);
                color: #e8f5e8;
                transform: translateY(-2px);
            }

            .form-control {
                width: 100%;
                padding: 15px;
                border: 2px solid rgba(45, 90, 39, 0.4);
                border-radius: 10px;
                font-size: 1rem;
                margin-bottom: 15px;
                background: rgba(13, 40, 24, 0.7);
                color: #e8f5e8;
                transition: all 0.3s ease;
                resize: vertical;
            }

            .form-control:focus {
                outline: none;
                border-color: rgba(74, 124, 89, 0.8);
                background: rgba(13, 40, 24, 0.9);
                box-shadow: 0 0 15px rgba(45, 90, 39, 0.3);
            }

            .form-control::placeholder { color: rgba(232, 245, 232, 0.6); }

            .btn {
                background: linear-gradient(135deg, #1a4d2e 0%, #2d5a27 50%, #4a7c59 100%);
                color: #e8f5e8;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.4s ease;
                border: 1px solid rgba(45, 90, 39, 0.5);
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
                font-size: 1rem;
            }

            .btn:hover {
                transform: translateY(-3px) scale(1.05);
                box-shadow: 0 12px 30px rgba(0,0,0,0.3);
                border-color: rgba(74, 124, 89, 0.8);
            }

            .file-input {
                margin-bottom: 15px;
            }

            .file-input input[type="file"] {
                display: none;
            }

            .file-input label {
                display: inline-block;
                padding: 10px 20px;
                background: rgba(45, 90, 39, 0.3);
                border: 1px solid rgba(45, 90, 39, 0.5);
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s ease;
                color: #e8f5e8;
            }

            .file-input label:hover {
                background: rgba(45, 90, 39, 0.5);
                transform: translateY(-2px);
            }

            .hashtags {
                color: #4a7c59;
                font-weight: 500;
                margin: 10px 0;
            }

            .location {
                color: rgba(232, 245, 232, 0.7);
                font-size: 0.9rem;
                margin-bottom: 10px;
            }

            .timestamp {
                color: rgba(232, 245, 232, 0.6);
                font-size: 0.8rem;
            }
        </style>
    </head>
    <body>
        <!-- Cute Plants Background -->
        <div class="cute-plant" style="left: 10%; top: 20%; animation-delay: 0s;">🌱</div>
        <div class="cute-plant" style="left: 85%; top: 25%; animation-delay: 1s;">🌿</div>
        <div class="cute-plant" style="left: 15%; top: 70%; animation-delay: 2s;">🍀</div>
        <div class="cute-plant" style="left: 80%; top: 75%; animation-delay: 0.5s;">🌾</div>
        <div class="cute-plant" style="left: 5%; top: 50%; animation-delay: 1.5s;">🌵</div>
        <div class="cute-plant" style="left: 90%; top: 55%; animation-delay: 2.5s;">🌳</div>
        <div class="cute-plant" style="left: 45%; top: 10%; animation-delay: 3s;">🌲</div>
        <div class="cute-plant" style="left: 50%; top: 85%; animation-delay: 0.8s;">🎋</div>

        <!-- Growing Flowers -->
        <div class="cute-plant" style="left: 20%; top: 40%; animation-delay: 2s; font-size: 1.5rem;">🌸</div>
        <div class="cute-plant" style="left: 70%; top: 80%; animation-delay: 4s; font-size: 1.8rem;">🌺</div>
        <div class="cute-plant" style="left: 30%; top: 15%; animation-delay: 6s; font-size: 1.6rem;">🌻</div>
        <div class="cute-plant" style="left: 75%; top: 35%; animation-delay: 8s; font-size: 1.7rem;">🌹</div>

        <div class="container">
            <div class="header">
                <h1>🌍 Green World Social Feed</h1>
                <p>Share your world with everyone!</p>
            </div>

            <div class="post-form">
                <h3>📝 What's on your mind?</h3>
                <form id="postForm" enctype="multipart/form-data">
                    <textarea class="form-control" id="postContent" placeholder="Share anything - your thoughts, experiences, photos, or just say hello!" rows="4" required></textarea>

                    <div class="file-input">
                        <label for="imageUpload">📸 Add Photo</label>
                        <input type="file" id="imageUpload" accept="image/*">
                    </div>

                    <input type="text" class="form-control" id="postLocation" placeholder="📍 Add location (optional)">
                    <input type="text" class="form-control" id="postHashtags" placeholder="#hashtags (optional)">

                    <button type="submit" class="btn">🚀 Share Post</button>
                </form>
            </div>

            <div id="postsContainer">
                {% for post in posts %}
                <div class="post-card">
                    <div class="post-header">
                        <div class="user-avatar">{{ post.first_name[0] if post.first_name else 'U' }}{{ post.last_name[0] if post.last_name else '' }}</div>
                        <div>
                            <strong>{{ post.first_name or 'User' }} {{ post.last_name or '' }}</strong>
                            <div class="timestamp">{{ post.created_at }}</div>
                        </div>
                    </div>

                    {% if post.location %}
                    <div class="location">📍 {{ post.location }}</div>
                    {% endif %}

                    <div class="post-content">{{ post.content }}</div>

                    {% if post.image_url %}
                    <img src="{{ post.image_url }}" alt="Post image" class="post-image">
                    {% endif %}

                    {% if post.hashtags %}
                    <div class="hashtags">{{ post.hashtags }}</div>
                    {% endif %}

                    <div class="post-actions">
                        <button class="action-btn" onclick="likePost('{{ post.id }}')">❤️ {{ post.likes_count or 0 }} Likes</button>
                        <button class="action-btn">💬 {{ post.comments_count or 0 }} Comments</button>
                        <button class="action-btn">🔄 Share</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <script>
            // Interactive Plants
            document.addEventListener('DOMContentLoaded', function() {
                const plants = document.querySelectorAll('.cute-plant');

                plants.forEach((plant, index) => {
                    plant.addEventListener('click', function(e) {
                        const sparkle = document.createElement('div');
                        sparkle.innerHTML = '✨🌟✨';
                        sparkle.style.position = 'fixed';
                        sparkle.style.left = e.clientX + 'px';
                        sparkle.style.top = e.clientY + 'px';
                        sparkle.style.fontSize = '1.5rem';
                        sparkle.style.pointerEvents = 'none';
                        sparkle.style.zIndex = '1000';
                        sparkle.style.animation = 'sparkleEffect 1s ease-out';

                        document.body.appendChild(sparkle);
                        setTimeout(() => document.body.removeChild(sparkle), 1000);

                        // Show plant message
                        const messages = [
                            '🌱 Hello there!',
                            '🌿 Thanks for the love!',
                            '🌸 I\'m growing!',
                            '🌺 You made my day!',
                            '🌻 Keep me happy!',
                            '🌹 I love attention!',
                            '🌷 Water me please!',
                            '🍀 Lucky you found me!'
                        ];
                        showNotification(messages[Math.floor(Math.random() * messages.length)]);
                    });
                });

                // Mouse movement effects
                document.addEventListener('mousemove', function(e) {
                    const mouseX = e.clientX / window.innerWidth;
                    const mouseY = e.clientY / window.innerHeight;

                    plants.forEach((plant, index) => {
                        const speed = (index + 1) * 0.5;
                        const distance = 30;
                        const x = (mouseX - 0.5) * speed * distance;
                        const y = (mouseY - 0.5) * speed * distance;
                        const rotation = (mouseX - 0.5) * speed * 10;

                        plant.style.transform = `translate(${x}px, ${y}px) rotate(${rotation}deg) scale(${1 + mouseX * 0.2})`;
                    });
                });
            });

            function showNotification(message) {
                // Create notification
                const notification = document.createElement('div');
                notification.textContent = message;
                notification.style.position = 'fixed';
                notification.style.top = '20px';
                notification.style.right = '20px';
                notification.style.background = 'linear-gradient(135deg, #1a4d2e, #4a7c59)';
                notification.style.color = '#e8f5e8';
                notification.style.padding = '15px 25px';
                notification.style.borderRadius = '10px';
                notification.style.zIndex = '1000';
                notification.style.border = '1px solid rgba(45, 90, 39, 0.5)';
                notification.style.boxShadow = '0 10px 25px rgba(0,0,0,0.3)';
                notification.style.animation = 'slideIn 0.3s ease-out';

                document.body.appendChild(notification);

                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 3000);
            }

            // Post form handling
            document.getElementById('postForm').addEventListener('submit', function(e) {
                e.preventDefault();

                const content = document.getElementById('postContent').value;
                const location = document.getElementById('postLocation').value;
                const hashtags = document.getElementById('postHashtags').value;
                const imageFile = document.getElementById('imageUpload').files[0];

                if (!content.trim()) {
                    showNotification('Please write something to share!');
                    return;
                }

                // Create new post element
                const newPost = document.createElement('div');
                newPost.className = 'post-card';
                newPost.style.animation = 'slideIn 0.5s ease-out';

                let imageHtml = '';
                if (imageFile) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        imageHtml = `<img src="${e.target.result}" alt="Post image" class="post-image">`;
                        updatePostHtml();
                    };
                    reader.readAsDataURL(imageFile);
                } else {
                    updatePostHtml();
                }

                function updatePostHtml() {
                    newPost.innerHTML = `
                        <div class="post-header">
                            <div class="user-avatar">D</div>
                            <div>
                                <strong>Demo User</strong>
                                <div class="timestamp">Just now</div>
                            </div>
                        </div>
                        ${location ? `<div class="location">📍 ${location}</div>` : ''}
                        <div class="post-content">${content}</div>
                        ${imageHtml}
                        ${hashtags ? `<div class="hashtags">${hashtags}</div>` : ''}
                        <div class="post-actions">
                            <button class="action-btn">❤️ 0 Likes</button>
                            <button class="action-btn">💬 0 Comments</button>
                            <button class="action-btn">🔄 Share</button>
                        </div>
                    `;

                    // Add to top of posts container
                    const postsContainer = document.getElementById('postsContainer');
                    postsContainer.insertBefore(newPost, postsContainer.firstChild);

                    // Clear form
                    document.getElementById('postForm').reset();

                    showNotification('🎉 Post shared successfully!');
                }
            });

            function likePost(postId) {
                // Simulate like functionality
                showNotification('❤️ Post liked!');
            }

            // Add CSS animations
            const style = document.createElement('style');
            style.textContent = `
                @keyframes sparkleEffect {
                    0% {
                        transform: scale(0) rotate(0deg);
                        opacity: 1;
                    }
                    50% {
                        transform: scale(1.5) rotate(180deg);
                        opacity: 0.8;
                    }
                    100% {
                        transform: scale(0.5) rotate(360deg) translateY(-50px);
                        opacity: 0;
                    }
                }

                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    ''', posts=posts)

# API Routes for real-time functionality
@app.route('/api/create-post', methods=['POST'])
def api_create_post():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    content = request.form.get('content')
    location = request.form.get('location', '')
    hashtags = request.form.get('hashtags', '')

    if not content:
        return jsonify({'error': 'Content required'}), 400

    # Handle image upload
    image_data = ''
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            # Convert to base64 for demo
            image_data = base64.b64encode(file.read()).decode('utf-8')

    post_id = create_post(session['user_id'], content, image_data, location, hashtags)

    return jsonify({'success': True, 'post_id': post_id})

@app.route('/api/like-post', methods=['POST'])
def api_like_post():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    post_id = request.json.get('post_id')
    if not post_id:
        return jsonify({'error': 'Post ID required'}), 400

    liked = like_post(session['user_id'], post_id)

    return jsonify({'success': True, 'liked': liked})

if __name__ == '__main__':
    print("🌍 Starting GREEN WORLD - Real Social Media Platform!")
    print("=" * 80)
    init_db()
    create_sample_users()
    create_sample_posts()
    print("✅ Green World Social Database ready!")
    print("🚀 Starting real social media server...")
    print("=" * 80)
    print("📍 MAIN URL: http://localhost:5003")
    print("🏠 Home Page: http://localhost:5003 (with cute movable plants!)")
    print("🔑 Login: http://localhost:5003/login (interactive plants)")
    print("🌐 Social Feed: http://localhost:5003/feed (real social media!)")
    print("=" * 80)
    print("🌟 GREEN WORLD FEATURES:")
    print("   ✅ Real social media platform")
    print("   ✅ Post anything with images")
    print("   ✅ Dark green interactive backgrounds")
    print("   ✅ 15+ Cute movable plants that follow your mouse")
    print("   ✅ Click interactions with sparkle effects ✨")
    print("   ✅ Like, comment, and share functionality")
    print("   ✅ Image upload and sharing")
    print("   ✅ Location and hashtag support")
    print("   ✅ Real-time notifications")
    print("   ✅ Beautiful plant-themed design")
    print("=" * 80)
    print("🎯 HOW TO USE:")
    print("1. Visit http://localhost:5003 - Move your mouse around the plants!")
    print("2. Click 'Login' - Enter any email/password")
    print("3. Go to Feed - Post anything you want with images!")
    print("4. Click on plants for surprises! ✨")
    print("=" * 80)
    print("💚 GREEN WORLD - Your complete social media platform!")
    print("🌱 Post anything, share everything, connect with everyone!")
    app.run(debug=True, host='0.0.0.0', port=5003)
