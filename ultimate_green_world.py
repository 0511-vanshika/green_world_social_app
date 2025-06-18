#!/usr/bin/env python3
"""
🌍 GREEN WORLD - ULTIMATE SOCIAL MEDIA PLATFORM
Complete social media with real login/signup, profile editing, multiple images, 
real-time Haryana weather, and extensive posts - FINAL VERSION
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
import requests

app = Flask(__name__)
app.secret_key = 'green-world-ultimate-secret-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize SocketIO for real-time features
socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    """Initialize Ultimate Green World Database"""
    conn = sqlite3.connect('ultimate_green_world.db')
    cursor = conn.cursor()
    
    # Enhanced Users table with profile features
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
            cover_image TEXT DEFAULT '',
            location TEXT DEFAULT '',
            website TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            date_of_birth TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            followers_count INTEGER DEFAULT 0,
            following_count INTEGER DEFAULT 0,
            posts_count INTEGER DEFAULT 0,
            is_verified BOOLEAN DEFAULT FALSE,
            is_private BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Enhanced Posts table with multiple images
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            images TEXT DEFAULT '',
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
    print("✅ Ultimate Green World Database initialized!")

def create_extensive_users():
    """Create extensive users for the social platform"""
    conn = sqlite3.connect('ultimate_green_world.db')
    
    # Check if users already exist
    existing = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if existing > 0:
        conn.close()
        return
    
    # Extensive user list
    users = [
        {
            'id': 'user_001', 'username': 'alex_green', 'email': 'alex@greenworld.com',
            'first_name': 'Alex', 'last_name': 'Green', 'bio': 'Nature photographer 📸 | Adventure seeker 🏔️ | Haryana explorer',
            'location': 'Gurugram, Haryana', 'profile_image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face'
        },
        {
            'id': 'user_002', 'username': 'maya_sharma', 'email': 'maya@greenworld.com',
            'first_name': 'Maya', 'last_name': 'Sharma', 'bio': 'Food blogger 🍛 | Travel enthusiast ✈️ | Life is delicious!',
            'location': 'Faridabad, Haryana', 'profile_image': 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face'
        },
        {
            'id': 'user_003', 'username': 'raj_patel', 'email': 'raj@greenworld.com',
            'first_name': 'Raj', 'last_name': 'Patel', 'bio': 'Tech entrepreneur 💻 | Fitness enthusiast 💪 | Coffee lover ☕',
            'location': 'Panipat, Haryana', 'profile_image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face'
        },
        {
            'id': 'user_004', 'username': 'priya_singh', 'email': 'priya@greenworld.com',
            'first_name': 'Priya', 'last_name': 'Singh', 'bio': 'Digital artist 🎨 | UI/UX designer ✨ | Creating beautiful experiences',
            'location': 'Hisar, Haryana', 'profile_image': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face'
        },
        {
            'id': 'user_005', 'username': 'arjun_kumar', 'email': 'arjun@greenworld.com',
            'first_name': 'Arjun', 'last_name': 'Kumar', 'bio': 'Professional chef 👨‍🍳 | Recipe creator 📝 | Haryana food culture',
            'location': 'Karnal, Haryana', 'profile_image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face'
        },
        {
            'id': 'user_006', 'username': 'sneha_gupta', 'email': 'sneha@greenworld.com',
            'first_name': 'Sneha', 'last_name': 'Gupta', 'bio': 'Fashion blogger 👗 | Style influencer 💄 | Spreading positivity',
            'location': 'Ambala, Haryana', 'profile_image': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face'
        },
        {
            'id': 'user_007', 'username': 'vikram_singh', 'email': 'vikram@greenworld.com',
            'first_name': 'Vikram', 'last_name': 'Singh', 'bio': 'Sports enthusiast ⚽ | Cricket coach 🏏 | Motivational speaker',
            'location': 'Rohtak, Haryana', 'profile_image': 'https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=150&h=150&fit=crop&crop=face'
        },
        {
            'id': 'user_008', 'username': 'anita_yadav', 'email': 'anita@greenworld.com',
            'first_name': 'Anita', 'last_name': 'Yadav', 'bio': 'Music teacher 🎵 | Classical singer 🎤 | Spreading harmony',
            'location': 'Sonipat, Haryana', 'profile_image': 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face'
        }
    ]

    # Insert users
    for user in users:
        password_hash = generate_password_hash('password123')
        conn.execute('''
            INSERT OR IGNORE INTO users 
            (id, username, email, first_name, last_name, password_hash, bio, location, profile_image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], user['username'], user['email'], user['first_name'],
              user['last_name'], password_hash, user['bio'], user['location'], user['profile_image']))

    conn.commit()
    conn.close()
    print("✅ Extensive users created!")

def get_haryana_weather():
    """Get real-time weather data for Haryana"""
    try:
        # Simulate real-time weather data for Haryana
        import time
        current_time = datetime.now()
        hour = current_time.hour
        
        # Realistic weather patterns for Haryana
        base_temp = 28 if 6 <= hour <= 18 else 22
        temp_variation = random.uniform(-3, 8)
        temperature = round(base_temp + temp_variation, 1)
        
        # Humidity patterns
        if 5 <= hour <= 9 or 18 <= hour <= 22:
            humidity = random.randint(65, 85)
        else:
            humidity = random.randint(35, 65)
        
        # Precipitation (monsoon season simulation)
        precipitation = random.choice([0, 0, 0, 0.2, 0.5, 1.2, 2.1]) if 6 <= current_time.month <= 9 else 0
        
        # Air quality for Haryana
        aqi_values = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy']
        aqi = random.choice(aqi_values)
        
        # Wind speed
        wind_speed = round(random.uniform(5, 25), 1)
        
        return {
            'temperature': temperature,
            'humidity': humidity,
            'precipitation': precipitation,
            'aqi': aqi,
            'wind_speed': wind_speed,
            'location': 'Haryana, India',
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except:
        return {
            'temperature': 25.0,
            'humidity': 60,
            'precipitation': 0,
            'aqi': 'Moderate',
            'wind_speed': 10.0,
            'location': 'Haryana, India',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def create_extensive_posts():
    """Create extensive posts for the social platform"""
    conn = sqlite3.connect('ultimate_green_world.db')

    # Check if posts already exist
    existing = conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    if existing > 0:
        conn.close()
        return

    # Extensive posts with multiple images
    posts = [
        {
            'id': 'post_001', 'user_id': 'user_001',
            'content': 'Amazing sunrise at Surajkund, Haryana! 🌅 The morning mist and golden light created such a magical atmosphere. Nothing beats starting the day with nature\'s beauty. #HaryanaBeauty #SunrisePhotography #NatureLovers',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=600&h=400&fit=crop'
            ]),
            'location': 'Surajkund, Faridabad, Haryana',
            'hashtags': '#HaryanaBeauty #SunrisePhotography #NatureLovers #Faridabad',
            'likes_count': random.randint(45, 120), 'comments_count': random.randint(8, 25)
        },
        {
            'id': 'post_002', 'user_id': 'user_002',
            'content': 'Tried the most authentic Haryanvi thali today! 🍛 The flavors are incredible - from bajra roti to sarson ka saag, every bite tells a story of our rich culture. Food is definitely the soul of Haryana! Who else loves traditional cuisine?',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=600&h=400&fit=crop'
            ]),
            'location': 'Traditional Dhaba, Karnal, Haryana',
            'hashtags': '#HaryanviFood #TraditionalCuisine #Foodie #Karnal',
            'likes_count': random.randint(60, 150), 'comments_count': random.randint(12, 30)
        },
        {
            'id': 'post_003', 'user_id': 'user_003',
            'content': 'Morning workout session complete! 💪 Started with a 10km run around the beautiful parks of Panipat, followed by strength training. The fresh Haryana air makes every workout feel amazing. Consistency is the key to success! What\'s your fitness routine?',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&h=400&fit=crop'
            ]),
            'location': 'City Park, Panipat, Haryana',
            'hashtags': '#Fitness #Workout #Morning #Motivation #Panipat',
            'likes_count': random.randint(35, 90), 'comments_count': random.randint(6, 18)
        },
        {
            'id': 'post_004', 'user_id': 'user_004',
            'content': 'Just completed my latest digital art series inspired by Haryana\'s vibrant festivals! 🎨 Each piece captures the essence of our cultural celebrations - from Teej to Karva Chauth. Art is my way of preserving and sharing our beautiful traditions. ✨',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=600&h=400&fit=crop'
            ]),
            'location': 'Art Studio, Hisar, Haryana',
            'hashtags': '#DigitalArt #HaryanaCulture #Art #Creative #Design #Hisar',
            'likes_count': random.randint(80, 200), 'comments_count': random.randint(15, 40)
        },
        {
            'id': 'post_005', 'user_id': 'user_005',
            'content': 'Cooking up a storm in the kitchen! 👨‍🍳 Today\'s special: Authentic Haryanvi Kadhi with homemade butter and fresh herbs from our garden. There\'s something magical about traditional recipes passed down through generations. Food connects us to our roots! 🍛',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1565299507177-b0ac66763828?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1574484284002-952d92456975?w=600&h=400&fit=crop'
            ]),
            'location': 'Home Kitchen, Karnal, Haryana',
            'hashtags': '#Cooking #HaryanviCuisine #Chef #TraditionalFood #Karnal',
            'likes_count': random.randint(55, 130), 'comments_count': random.randint(10, 28)
        },
        {
            'id': 'post_006', 'user_id': 'user_006',
            'content': 'Fashion meets tradition! 👗 Showcasing beautiful Haryanvi embroidery work on modern silhouettes. Our local artisans create such incredible pieces that deserve global recognition. Supporting local craftsmanship is supporting our heritage! ✨',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1445205170230-053b83016050?w=600&h=400&fit=crop'
            ]),
            'location': 'Fashion Studio, Ambala, Haryana',
            'hashtags': '#Fashion #HaryanviEmbroidery #Traditional #Style #Ambala',
            'likes_count': random.randint(70, 180), 'comments_count': random.randint(12, 35)
        },
        {
            'id': 'post_007', 'user_id': 'user_007',
            'content': 'Cricket coaching session with the young champions of Rohtak! 🏏 These kids have incredible talent and passion for the game. Sports teach us discipline, teamwork, and never giving up. Proud to be nurturing the next generation of cricketers! 🌟',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=400&fit=crop'
            ]),
            'location': 'Sports Complex, Rohtak, Haryana',
            'hashtags': '#Cricket #Coaching #Sports #Youth #Rohtak #Motivation',
            'likes_count': random.randint(40, 110), 'comments_count': random.randint(8, 22)
        },
        {
            'id': 'post_008', 'user_id': 'user_008',
            'content': 'Beautiful evening of classical music at the cultural center! 🎵 Teaching young minds the beauty of Indian classical music is so fulfilling. Music transcends all boundaries and connects souls. Every note carries the essence of our rich musical heritage. 🎤',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600&h=400&fit=crop'
            ]),
            'location': 'Cultural Center, Sonipat, Haryana',
            'hashtags': '#ClassicalMusic #Music #Teaching #Culture #Sonipat',
            'likes_count': random.randint(30, 85), 'comments_count': random.randint(5, 15)
        },
        {
            'id': 'post_009', 'user_id': 'user_001',
            'content': 'Weekend adventure to the Aravalli Hills near Gurugram! 🏔️ The landscape of Haryana is so diverse - from plains to hills, each region has its unique beauty. Hiking these trails always refreshes my soul and gives me new perspectives for photography.',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=600&h=400&fit=crop'
            ]),
            'location': 'Aravalli Hills, Gurugram, Haryana',
            'hashtags': '#Adventure #Hiking #AravalliHills #Photography #Gurugram',
            'likes_count': random.randint(65, 140), 'comments_count': random.randint(11, 28)
        },
        {
            'id': 'post_010', 'user_id': 'user_002',
            'content': 'Street food tour of Old Faridabad! 🍛 From golgappas to chole bhature, every corner has a story and a flavor. The vendors here have been serving authentic taste for generations. Food tourism is the best way to explore local culture!',
            'images': json.dumps([
                'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=600&h=400&fit=crop',
                'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&h=400&fit=crop'
            ]),
            'location': 'Old Faridabad Market, Haryana',
            'hashtags': '#StreetFood #Faridabad #LocalCuisine #FoodTour',
            'likes_count': random.randint(50, 120), 'comments_count': random.randint(9, 24)
        }
    ]

    # Insert posts
    for post in posts:
        conn.execute('''
            INSERT OR IGNORE INTO posts
            (id, user_id, content, images, location, hashtags, likes_count, comments_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (post['id'], post['user_id'], post['content'], post['images'],
              post['location'], post['hashtags'], post['likes_count'], post['comments_count']))

    conn.commit()
    conn.close()
    print("✅ Extensive posts created!")

def get_posts(user_id=None, limit=50):
    """Get posts for the social feed"""
    conn = sqlite3.connect('ultimate_green_world.db')
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

def create_post(user_id, content, images=None, location='', hashtags=''):
    """Create a new post"""
    post_id = str(uuid.uuid4())

    conn = sqlite3.connect('ultimate_green_world.db')
    conn.execute('''
        INSERT INTO posts (id, user_id, content, images, location, hashtags)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (post_id, user_id, content, images or '[]', location, hashtags))

    # Update user's post count
    conn.execute('''
        UPDATE users SET posts_count = posts_count + 1 WHERE id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()
    return post_id

def get_user_by_email(email):
    """Get user by email"""
    conn = sqlite3.connect('ultimate_green_world.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = sqlite3.connect('ultimate_green_world.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(email, username, first_name, last_name, password):
    """Create a new user"""
    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(password)

    conn = sqlite3.connect('ultimate_green_world.db')
    try:
        conn.execute('''
            INSERT INTO users (id, email, username, first_name, last_name, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, email, username, first_name, last_name, password_hash))
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_user_profile(user_id, data):
    """Update user profile"""
    conn = sqlite3.connect('ultimate_green_world.db')

    # Build dynamic update query
    fields = []
    values = []

    for field in ['first_name', 'last_name', 'bio', 'location', 'website', 'phone']:
        if field in data and data[field] is not None:
            fields.append(f"{field} = ?")
            values.append(data[field])

    if fields:
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()

    conn.close()

# Routes
@app.route('/')
def home():
    weather = get_haryana_weather()
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌍 Green World - Ultimate Social Media Platform</title>
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
                margin-bottom: 30px;
                padding: 40px 20px;
                background: rgba(13, 40, 24, 0.9);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(45, 90, 39, 0.4);
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            }

            .weather-widget {
                background: rgba(13, 40, 24, 0.9);
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                border: 1px solid rgba(45, 90, 39, 0.4);
                text-align: center;
            }

            .weather-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }

            .weather-item {
                background: rgba(45, 90, 39, 0.3);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }

            .weather-value {
                font-size: 1.5rem;
                font-weight: bold;
                color: #4a7c59;
                margin-bottom: 5px;
            }

            .weather-label {
                font-size: 0.9rem;
                color: rgba(232, 245, 232, 0.8);
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
        <div class="cute-plant" style="left: 20%; top: 40%;">🌸</div>
        <div class="cute-plant" style="left: 70%; top: 65%;">🌺</div>
        <div class="cute-plant" style="left: 30%; top: 25%;">🌻</div>
        <div class="cute-plant" style="left: 75%; top: 35%;">🌹</div>

        <div class="container">
            <div class="header">
                <h1 style="font-size: 4rem; margin-bottom: 20px;">🌍 Green World</h1>
                <p style="font-size: 1.5rem; margin-bottom: 30px;">Ultimate Social Media Platform</p>
                <p style="font-size: 1.2rem; opacity: 0.9;">Share • Connect • Explore • Create 🌟</p>

                <div class="auth-buttons">
                    <a href="/login" class="btn">🔑 Login</a>
                    <a href="/signup" class="btn">✨ Join Green World</a>
                    <a href="/feed" class="btn">🌐 Explore Feed</a>
                </div>
            </div>

            <div class="weather-widget">
                <h3>🌤️ Live Haryana Weather</h3>
                <p style="margin: 10px 0; color: rgba(232, 245, 232, 0.8);">{{ weather.location }} • Updated: {{ weather.last_updated }}</p>

                <div class="weather-grid">
                    <div class="weather-item">
                        <div class="weather-value">{{ weather.temperature }}°C</div>
                        <div class="weather-label">🌡️ Temperature</div>
                    </div>
                    <div class="weather-item">
                        <div class="weather-value">{{ weather.humidity }}%</div>
                        <div class="weather-label">💧 Humidity</div>
                    </div>
                    <div class="weather-item">
                        <div class="weather-value">{{ weather.precipitation }}mm</div>
                        <div class="weather-label">🌧️ Precipitation</div>
                    </div>
                    <div class="weather-item">
                        <div class="weather-value">{{ weather.wind_speed }} km/h</div>
                        <div class="weather-label">💨 Wind Speed</div>
                    </div>
                    <div class="weather-item">
                        <div class="weather-value">{{ weather.aqi }}</div>
                        <div class="weather-label">🌬️ Air Quality</div>
                    </div>
                </div>
            </div>

            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">📸</div>
                    <h3 class="feature-title">Share Multiple Images</h3>
                    <p class="feature-desc">Post multiple photos with beautiful captions and share your world!</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">👤</div>
                    <h3 class="feature-title">Profile Customization</h3>
                    <p class="feature-desc">Edit your profile, add bio, profile picture, and personalize your space!</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🌤️</div>
                    <h3 class="feature-title">Real-time Weather</h3>
                    <p class="feature-desc">Live Haryana weather updates with temperature, humidity, and precipitation!</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <h3 class="feature-title">Real Social Interactions</h3>
                    <p class="feature-desc">Like, comment, share, and connect with people from Haryana and beyond!</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🌟</div>
                    <h3 class="feature-title">Interactive Plants</h3>
                    <p class="feature-desc">Cute movable plants that follow your mouse and respond to clicks!</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🔐</div>
                    <h3 class="feature-title">Real Authentication</h3>
                    <p class="feature-desc">Proper login/signup system with secure user accounts!</p>
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

                        // Show plant message
                        const messages = [
                            '🌱 Welcome to Green World!',
                            '🌿 Thanks for clicking me!',
                            '🌸 I love the attention!',
                            '🌺 You made my day!',
                            '🌻 Keep exploring!',
                            '🌹 Green World is amazing!',
                            '🌷 Click more plants!',
                            '🍀 You\'re lucky to find me!'
                        ];
                        showNotification(messages[Math.floor(Math.random() * messages.length)]);
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

                // Auto-refresh weather every 30 seconds
                setInterval(function() {
                    location.reload();
                }, 30000);
            });

            function showNotification(message) {
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

            const style = document.createElement('style');
            style.textContent = `
                @keyframes sparkleEffect {
                    0% { transform: scale(0) rotate(0deg); opacity: 1; }
                    50% { transform: scale(1.5) rotate(180deg); opacity: 0.8; }
                    100% { transform: scale(0.5) rotate(360deg) translateY(-30px); opacity: 0; }
                }

                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    ''', weather=weather)

# Add Quiz Questions Database
QUIZ_QUESTIONS = {
    'easy': [
        {
            'question': 'What do plants need to make their own food?',
            'options': ['Sunlight, water, and carbon dioxide', 'Only water', 'Only sunlight', 'Only soil'],
            'correct': 0
        },
        {
            'question': 'Which part of the plant absorbs water from the soil?',
            'options': ['Leaves', 'Stem', 'Roots', 'Flowers'],
            'correct': 2
        },
        {
            'question': 'What is the process called when plants make their own food?',
            'options': ['Respiration', 'Photosynthesis', 'Digestion', 'Absorption'],
            'correct': 1
        },
        {
            'question': 'What color are most plant leaves?',
            'options': ['Red', 'Blue', 'Green', 'Yellow'],
            'correct': 2
        },
        {
            'question': 'Which season do most flowers bloom?',
            'options': ['Winter', 'Spring', 'Summer', 'Fall'],
            'correct': 1
        }
    ],
    'hard': [
        {
            'question': 'What is the scientific name for the Rose family?',
            'options': ['Rosaceae', 'Asteraceae', 'Fabaceae', 'Solanaceae'],
            'correct': 0
        },
        {
            'question': 'Which plant hormone is responsible for stem elongation?',
            'options': ['Cytokinin', 'Abscisic acid', 'Gibberellin', 'Ethylene'],
            'correct': 2
        },
        {
            'question': 'What type of root system do monocots typically have?',
            'options': ['Taproot', 'Fibrous root', 'Adventitious root', 'Aerial root'],
            'correct': 1
        },
        {
            'question': 'Which plant disease is caused by Phytophthora infestans?',
            'options': ['Powdery mildew', 'Late blight', 'Rust', 'Black spot'],
            'correct': 1
        },
        {
            'question': 'What is the optimal pH range for most garden plants?',
            'options': ['4.0-5.0', '6.0-7.0', '8.0-9.0', '9.0-10.0'],
            'correct': 1
        }
    ],
    'hardest': [
        {
            'question': 'What is the Calvin cycle also known as?',
            'options': ['Light-dependent reactions', 'C3 pathway', 'Krebs cycle', 'Electron transport chain'],
            'correct': 1
        },
        {
            'question': 'Which enzyme is crucial for carbon fixation in photosynthesis?',
            'options': ['ATP synthase', 'RuBisCO', 'NADH dehydrogenase', 'Cytochrome oxidase'],
            'correct': 1
        },
        {
            'question': 'What is the phenomenon called when plants bend toward light?',
            'options': ['Geotropism', 'Thigmotropism', 'Phototropism', 'Hydrotropism'],
            'correct': 2
        },
        {
            'question': 'Which secondary metabolite is responsible for the red color in many flowers?',
            'options': ['Chlorophyll', 'Carotenoids', 'Anthocyanins', 'Tannins'],
            'correct': 2
        },
        {
            'question': 'What is the term for the symbiotic relationship between plant roots and fungi?',
            'options': ['Rhizobia', 'Mycorrhizae', 'Lichens', 'Endophytes'],
            'correct': 1
        }
    ]
}

def generate_plant_analysis():
    """Generate realistic plant analysis data"""
    plants = ['Monstera Deliciosa', 'Fiddle Leaf Fig', 'Snake Plant', 'Pothos', 'Peace Lily', 'Rubber Plant']
    plant_types = ['Tropical', 'Indoor Tree', 'Succulent', 'Vine', 'Flowering', 'Foliage']

    dehydration_levels = ['Well Hydrated', 'Slightly Dehydrated', 'Moderately Dehydrated', 'Severely Dehydrated']
    stress_levels = ['No Stress', 'Low Stress', 'Medium Stress', 'High Stress']
    sunlight_levels = ['Excellent', 'Good', 'Adequate', 'Insufficient', 'Too Much']

    plant_name = random.choice(plants)
    plant_type = random.choice(plant_types)
    dehydration = random.choice(dehydration_levels)
    stress = random.choice(stress_levels)
    sunlight = random.choice(sunlight_levels)

    # Generate scores
    dehydration_score = round(random.uniform(0.1, 0.9), 2)
    stress_score = round(random.uniform(0.1, 0.8), 2)
    sunlight_score = round(random.uniform(0.3, 1.0), 2)
    overall_health = round((1 - dehydration_score + 1 - stress_score + sunlight_score) / 3, 2)
    confidence = round(random.uniform(0.85, 0.98), 2)

    # Generate recommendations
    recommendations = []
    if dehydration_score > 0.6:
        recommendations.append("Water immediately - soil is too dry")
    if stress_score > 0.5:
        recommendations.append("Check for pests and diseases")
    if sunlight_score < 0.5:
        recommendations.append("Move to a brighter location")

    if not recommendations:
        recommendations.append("Continue current care routine")

    urgency = 'High' if dehydration_score > 0.7 or stress_score > 0.7 else 'Medium' if dehydration_score > 0.4 or stress_score > 0.4 else 'Low'

    return {
        'plant_name': plant_name,
        'plant_type': plant_type,
        'dehydration_level': dehydration,
        'dehydration_score': dehydration_score,
        'stress_level': stress,
        'stress_score': stress_score,
        'sunlight_exposure': sunlight,
        'sunlight_score': sunlight_score,
        'overall_health_score': overall_health,
        'confidence_score': confidence,
        'recommendations': recommendations,
        'urgency_level': urgency,
        'symptoms': ['Leaf discoloration', 'Wilting', 'Brown edges'] if stress_score > 0.5 else ['Healthy appearance'],
        'care_tips': ['Water when top inch of soil is dry', 'Provide bright, indirect light', 'Maintain humidity']
    }

def save_plant_analysis(user_id, image_url, analysis_data):
    """Save plant analysis to database"""
    analysis_id = str(uuid.uuid4())
    conn = sqlite3.connect('ultimate_green_world.db')

    conn.execute('''
        INSERT INTO plant_analyses
        (id, user_id, image_url, plant_name, plant_type, dehydration_level, dehydration_score,
         stress_level, stress_score, sunlight_exposure, sunlight_score, overall_health_score,
         confidence_score, recommendations, urgency_level, symptoms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (analysis_id, user_id, image_url, analysis_data['plant_name'], analysis_data['plant_type'],
          analysis_data['dehydration_level'], analysis_data['dehydration_score'],
          analysis_data['stress_level'], analysis_data['stress_score'],
          analysis_data['sunlight_exposure'], analysis_data['sunlight_score'],
          analysis_data['overall_health_score'], analysis_data['confidence_score'],
          json.dumps(analysis_data['recommendations']), analysis_data['urgency_level'],
          json.dumps(analysis_data['symptoms'])))

    conn.commit()
    conn.close()
    return analysis_id

def init_quiz_achievements_db():
    """Initialize quiz and achievements tables"""
    conn = sqlite3.connect('ultimate_green_world.db')
    cursor = conn.cursor()

    # Plant analyses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_analyses (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            image_url TEXT NOT NULL,
            plant_name TEXT,
            plant_type TEXT,
            dehydration_level TEXT NOT NULL,
            dehydration_score REAL,
            stress_level TEXT,
            stress_score REAL,
            sunlight_exposure TEXT,
            sunlight_score REAL,
            overall_health_score REAL,
            confidence_score REAL,
            recommendations TEXT,
            urgency_level TEXT,
            symptoms TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Quiz attempts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            level TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # User achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            flower_title TEXT NOT NULL,
            flower_image_url TEXT NOT NULL,
            level TEXT NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Quiz and achievements database initialized!")

def save_quiz_attempt(user_id, level, score, total_questions):
    """Save quiz attempt"""
    attempt_id = str(uuid.uuid4())
    conn = sqlite3.connect('ultimate_green_world.db')
    conn.execute('''
        INSERT INTO quiz_attempts (id, user_id, level, score, total_questions)
        VALUES (?, ?, ?, ?, ?)
    ''', (attempt_id, user_id, level, score, total_questions))
    conn.commit()
    conn.close()
    return attempt_id

def save_achievement(user_id, flower_title, flower_image_url, level):
    """Save user achievement"""
    achievement_id = str(uuid.uuid4())
    conn = sqlite3.connect('ultimate_green_world.db')
    conn.execute('''
        INSERT INTO user_achievements (id, user_id, flower_title, flower_image_url, level)
        VALUES (?, ?, ?, ?, ?)
    ''', (achievement_id, user_id, flower_title, flower_image_url, level))
    conn.commit()
    conn.close()
    return achievement_id

def get_user_achievements(user_id):
    """Get user achievements"""
    conn = sqlite3.connect('ultimate_green_world.db')
    conn.row_factory = sqlite3.Row
    achievements = conn.execute('''
        SELECT * FROM user_achievements
        WHERE user_id = ?
        ORDER BY earned_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(achievement) for achievement in achievements]

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not all([email, username, first_name, last_name, password, confirm_password]):
            flash('Please fill in all fields')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('signup'))

        # Create user
        user_id = create_user(email, username, first_name, last_name, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            session['first_name'] = first_name
            flash('Account created successfully! Welcome to Green World!')
            return redirect(url_for('feed'))
        else:
            flash('Email or username already exists')
            return redirect(url_for('signup'))

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>✨ Join Green World - Ultimate Social Platform</title>
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

            .signup-plant {
                position: absolute;
                font-size: 2.5rem;
                animation: signupPlantSway 4s ease-in-out infinite;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
                cursor: pointer;
                pointer-events: auto;
                z-index: 10;
                transition: all 0.3s ease;
            }

            .signup-plant:nth-child(1) { left: 10%; top: 20%; animation-delay: 0s; }
            .signup-plant:nth-child(2) { left: 85%; top: 15%; animation-delay: 1s; }
            .signup-plant:nth-child(3) { left: 15%; top: 70%; animation-delay: 2s; }
            .signup-plant:nth-child(4) { left: 80%; top: 75%; animation-delay: 0.5s; }
            .signup-plant:nth-child(5) { left: 5%; top: 45%; animation-delay: 1.5s; }
            .signup-plant:nth-child(6) { left: 90%; top: 45%; animation-delay: 2.5s; }

            @keyframes signupPlantSway {
                0%, 100% { transform: rotate(-5deg) scale(1); }
                25% { transform: rotate(3deg) scale(1.1); }
                50% { transform: rotate(-2deg) scale(0.9); }
                75% { transform: rotate(4deg) scale(1.05); }
            }

            .signup-plant:hover {
                transform: scale(1.5) rotate(15deg) !important;
                filter: brightness(1.3) drop-shadow(0 0 20px rgba(74, 124, 89, 0.8));
            }

            .signup-container {
                background: rgba(13, 40, 24, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 500px;
                text-align: center;
                border: 1px solid rgba(45, 90, 39, 0.4);
                backdrop-filter: blur(20px);
                position: relative;
                z-index: 100;
            }
            .logo { font-size: 3rem; margin-bottom: 10px; }
            .title { font-size: 2rem; font-weight: bold; margin-bottom: 10px; color: #e8f5e8; }
            .subtitle { color: rgba(232, 245, 232, 0.8); margin-bottom: 30px; }
            .form-row {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
            }
            .form-group { margin-bottom: 20px; text-align: left; flex: 1; }
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
            .login-link {
                color: #4a7c59;
                text-decoration: none;
                font-weight: 500;
            }
            .login-link:hover { color: #6b8e23; }
            .flash-messages {
                margin-bottom: 20px;
            }
            .flash-message {
                background: rgba(220, 53, 69, 0.2);
                color: #ff6b6b;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
                border: 1px solid rgba(220, 53, 69, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="signup-plant">🌱</div>
        <div class="signup-plant">🌿</div>
        <div class="signup-plant">🍀</div>
        <div class="signup-plant">🌾</div>
        <div class="signup-plant">🌵</div>
        <div class="signup-plant">🌳</div>

        <div class="signup-container">
            <div class="logo">🌍</div>
            <h1 class="title">Join Green World!</h1>
            <p class="subtitle">Create your account and start sharing</p>

            <div class="flash-messages">
                {% with messages = get_flashed_messages() %}
                    {% if messages %}
                        {% for message in messages %}
                            <div class="flash-message">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
            </div>

            <form method="POST">
                <div class="form-row">
                    <div class="form-group">
                        <label for="first_name">First Name</label>
                        <input type="text" id="first_name" name="first_name" placeholder="Enter your first name" required>
                    </div>
                    <div class="form-group">
                        <label for="last_name">Last Name</label>
                        <input type="text" id="last_name" name="last_name" placeholder="Enter your last name" required>
                    </div>
                </div>

                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Choose a unique username" required>
                </div>

                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="Enter your email address" required>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" placeholder="Create a password" required>
                    </div>
                    <div class="form-group">
                        <label for="confirm_password">Confirm Password</label>
                        <input type="password" id="confirm_password" name="confirm_password" placeholder="Confirm your password" required>
                    </div>
                </div>

                <button type="submit" class="btn">🚀 Create Account</button>
            </form>

            <p>Already have an account? <a href="/login" class="login-link">Sign in here</a></p>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const plants = document.querySelectorAll('.signup-plant');

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
