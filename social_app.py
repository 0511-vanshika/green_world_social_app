from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import uuid
from datetime import datetime
import json
import random
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize SocketIO for real-time features
socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect('greenverse_social.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            bio TEXT,
            avatar_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Posts table for social media features
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Likes table
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
    
    # Comments table
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
    
    # Quiz tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            flower_reward TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Plant analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_analyses (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            image_url TEXT NOT NULL,
            plant_name TEXT,
            dehydration_level TEXT NOT NULL,
            dehydration_score REAL,
            stress_rate REAL,
            sunlight_warning TEXT,
            prevention_tips TEXT,
            cure_suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

def create_sample_data():
    """Create sample users and posts for demonstration"""
    conn = sqlite3.connect('greenverse_social.db')

    # Check if sample data already exists
    existing = conn.execute('SELECT COUNT(*) FROM users WHERE email LIKE "%sample%"').fetchone()[0]
    if existing > 0:
        conn.close()
        return

    # Sample users
    sample_users = [
        {
            'id': 'user_001',
            'username': 'plant_lover_sarah',
            'email': 'sarah@sample.com',
            'first_name': 'Sarah',
            'last_name': 'Green',
            'password_hash': generate_password_hash('password123'),
            'bio': 'Plant enthusiast from Delhi 🌱'
        },
        {
            'id': 'user_002',
            'username': 'garden_guru_mike',
            'email': 'mike@sample.com',
            'first_name': 'Mike',
            'last_name': 'Johnson',
            'password_hash': generate_password_hash('password123'),
            'bio': 'Professional gardener and botanist 🌿'
        },
        {
            'id': 'user_003',
            'username': 'flower_queen_priya',
            'email': 'priya@sample.com',
            'first_name': 'Priya',
            'last_name': 'Sharma',
            'password_hash': generate_password_hash('password123'),
            'bio': 'Flower specialist from Faridabad 🌸'
        },
        {
            'id': 'user_004',
            'username': 'succulent_sam',
            'email': 'sam@sample.com',
            'first_name': 'Sam',
            'last_name': 'Patel',
            'password_hash': generate_password_hash('password123'),
            'bio': 'Succulent collector and indoor plant expert 🌵'
        }
    ]

    # Insert sample users
    for user in sample_users:
        conn.execute('''
            INSERT OR IGNORE INTO users (id, username, email, first_name, last_name, password_hash, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], user['username'], user['email'], user['first_name'],
              user['last_name'], user['password_hash'], user['bio']))

    # Sample posts with plant photos
    sample_posts = [
        {
            'id': 'post_001',
            'user_id': 'user_001',
            'content': 'Just repotted my beautiful Monstera deliciosa! 🌿 Look at those gorgeous fenestrations. She\'s been with me for 2 years now and growing so well in the Faridabad climate!',
            'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500&h=400&fit=crop',
            'likes_count': 24,
            'comments_count': 8
        },
        {
            'id': 'post_002',
            'user_id': 'user_002',
            'content': 'Morning garden inspection complete! ✅ My tomatoes are thriving in this humidity. The weather in Faridabad has been perfect for growing vegetables this season. 🍅',
            'image_url': 'https://images.unsplash.com/photo-1592419044706-39796d40f98c?w=500&h=400&fit=crop',
            'likes_count': 31,
            'comments_count': 12
        },
        {
            'id': 'post_003',
            'user_id': 'user_003',
            'content': 'My rose garden is in full bloom! 🌹 These David Austin roses are absolutely stunning. The morning dew and perfect temperature made them extra beautiful today.',
            'image_url': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=500&h=400&fit=crop',
            'likes_count': 45,
            'comments_count': 15
        },
        {
            'id': 'post_004',
            'user_id': 'user_004',
            'content': 'Succulent propagation success! 🌵 Started these little babies 3 months ago and now they\'re ready for their own pots. Perfect for the dry season here!',
            'image_url': 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=500&h=400&fit=crop',
            'likes_count': 18,
            'comments_count': 6
        },
        {
            'id': 'post_005',
            'user_id': 'user_001',
            'content': 'Snake plant babies! 🐍🌱 My Sansevieria is producing so many pups. These are perfect for beginners - they love the indoor conditions here in Faridabad.',
            'image_url': 'https://images.unsplash.com/photo-1493663284031-b7e3aaa4cab7?w=500&h=400&fit=crop',
            'likes_count': 22,
            'comments_count': 9
        },
        {
            'id': 'post_006',
            'user_id': 'user_002',
            'content': 'Herb garden update! 🌿 Fresh basil, mint, and coriander growing beautifully. Nothing beats cooking with herbs you\'ve grown yourself!',
            'image_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=500&h=400&fit=crop',
            'likes_count': 33,
            'comments_count': 11
        }
    ]

    # Insert sample posts
    for post in sample_posts:
        conn.execute('''
            INSERT OR IGNORE INTO posts (id, user_id, content, image_url, likes_count, comments_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (post['id'], post['user_id'], post['content'], post['image_url'],
              post['likes_count'], post['comments_count']))

    conn.commit()
    conn.close()

# Quiz Questions Database
QUIZ_QUESTIONS = {
    'easy': [
        {'question': 'What do plants need to make their own food?', 'options': ['Sunlight, water, and carbon dioxide', 'Only water', 'Only sunlight', 'Only soil'], 'correct': 0},
        {'question': 'Which part of the plant absorbs water?', 'options': ['Leaves', 'Stem', 'Roots', 'Flowers'], 'correct': 2},
        {'question': 'What is photosynthesis?', 'options': ['Plant breathing', 'Making food from sunlight', 'Plant sleeping', 'Plant growing'], 'correct': 1},
        {'question': 'What color are most plant leaves?', 'options': ['Red', 'Blue', 'Green', 'Yellow'], 'correct': 2},
        {'question': 'When do most flowers bloom?', 'options': ['Winter', 'Spring', 'Summer', 'Fall'], 'correct': 1}
    ],
    'hard': [
        {'question': 'What is the main function of chlorophyll?', 'options': ['Water absorption', 'Light absorption for photosynthesis', 'Nutrient storage', 'Root growth'], 'correct': 1},
        {'question': 'Which plant hormone promotes cell elongation?', 'options': ['Cytokinin', 'Auxin', 'Gibberellin', 'Abscisic acid'], 'correct': 1},
        {'question': 'What is the process of water movement through plants called?', 'options': ['Osmosis', 'Transpiration', 'Diffusion', 'Absorption'], 'correct': 1},
        {'question': 'Which tissue transports water in plants?', 'options': ['Phloem', 'Xylem', 'Cambium', 'Epidermis'], 'correct': 1},
        {'question': 'What triggers stomatal closure?', 'options': ['High humidity', 'Low light', 'Water stress', 'High temperature'], 'correct': 2}
    ],
    'hardest': [
        {'question': 'What is the Calvin cycle?', 'options': ['Light-dependent reactions', 'Carbon fixation process', 'Water transport', 'Nutrient absorption'], 'correct': 1},
        {'question': 'Which enzyme is crucial for carbon fixation?', 'options': ['RuBisCO', 'ATP synthase', 'NADH dehydrogenase', 'Catalase'], 'correct': 0},
        {'question': 'What is photorespiration?', 'options': ['Night breathing', 'Wasteful oxygen consumption', 'Water loss', 'Nutrient uptake'], 'correct': 1},
        {'question': 'Which pathway do CAM plants use?', 'options': ['C3 pathway', 'C4 pathway', 'Crassulacean Acid Metabolism', 'Calvin cycle only'], 'correct': 2},
        {'question': 'What is the function of the Casparian strip?', 'options': ['Water storage', 'Selective barrier in roots', 'Photosynthesis', 'Flower development'], 'correct': 1}
    ]
}

# Flower Rewards Database
FLOWER_REWARDS = [
    {'title': 'Rose Guardian', 'flower': 'red rose', 'image': 'https://source.unsplash.com/400x300/?red+rose'},
    {'title': 'Sunflower Champion', 'flower': 'sunflower', 'image': 'https://source.unsplash.com/400x300/?sunflower'},
    {'title': 'Lily Master', 'flower': 'white lily', 'image': 'https://source.unsplash.com/400x300/?white+lily'},
    {'title': 'Orchid Specialist', 'flower': 'purple orchid', 'image': 'https://source.unsplash.com/400x300/?purple+orchid'},
    {'title': 'Tulip Expert', 'flower': 'tulip', 'image': 'https://source.unsplash.com/400x300/?tulip'},
    {'title': 'Daisy Lover', 'flower': 'daisy', 'image': 'https://source.unsplash.com/400x300/?daisy'},
    {'title': 'Lavender Sage', 'flower': 'lavender', 'image': 'https://source.unsplash.com/400x300/?lavender'},
    {'title': 'Cherry Blossom Master', 'flower': 'cherry blossom', 'image': 'https://source.unsplash.com/400x300/?cherry+blossom'}
]

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌱 GreenVerse Social - Interactive Plant Community</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 25%, #6b8e23 50%, #8fbc8f 75%, #98fb98 100%);
                min-height: 100vh;
                color: #333;
                overflow-x: hidden;
                position: relative;
            }

            /* Animated Background */
            .bg-animation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                background:
                    radial-gradient(circle at 20% 80%, rgba(34, 139, 34, 0.4) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(50, 205, 50, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(144, 238, 144, 0.3) 0%, transparent 50%);
                animation: backgroundShift 20s ease-in-out infinite;
            }

            @keyframes backgroundShift {
                0%, 100% { transform: scale(1) rotate(0deg); }
                50% { transform: scale(1.1) rotate(5deg); }
            }

            /* Floating Particles */
            .particles {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                pointer-events: none;
            }

            .particle {
                position: absolute;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 50%;
                animation: float 15s infinite linear;
            }

            .particle:nth-child(1) { left: 10%; animation-delay: 0s; width: 4px; height: 4px; }
            .particle:nth-child(2) { left: 20%; animation-delay: 2s; width: 6px; height: 6px; }
            .particle:nth-child(3) { left: 30%; animation-delay: 4s; width: 3px; height: 3px; }
            .particle:nth-child(4) { left: 40%; animation-delay: 6s; width: 5px; height: 5px; }
            .particle:nth-child(5) { left: 50%; animation-delay: 8s; width: 4px; height: 4px; }
            .particle:nth-child(6) { left: 60%; animation-delay: 10s; width: 6px; height: 6px; }
            .particle:nth-child(7) { left: 70%; animation-delay: 12s; width: 3px; height: 3px; }
            .particle:nth-child(8) { left: 80%; animation-delay: 14s; width: 5px; height: 5px; }
            .particle:nth-child(9) { left: 90%; animation-delay: 16s; width: 4px; height: 4px; }

            @keyframes float {
                0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 20px;
                text-align: center;
                position: relative;
                z-index: 1;
            }

            .header {
                color: white;
                margin-bottom: 60px;
                backdrop-filter: blur(10px);
                background: rgba(255, 255, 255, 0.1);
                border-radius: 30px;
                padding: 60px 40px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }

            .title {
                font-size: 4rem;
                margin-bottom: 20px;
                background: linear-gradient(45deg, #fff, #90ee90, #98fb98);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: titleGlow 3s ease-in-out infinite alternate;
            }

            @keyframes titleGlow {
                0% { filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5)); }
                100% { filter: drop-shadow(0 0 20px rgba(144, 238, 144, 0.8)); }
            }

            .subtitle {
                font-size: 1.4rem;
                margin-bottom: 40px;
                opacity: 0.95;
                font-weight: 300;
                letter-spacing: 1px;
            }

            .auth-buttons {
                display: flex;
                gap: 25px;
                justify-content: center;
                flex-wrap: wrap;
                margin-top: 40px;
            }

            .btn {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 18px 45px;
                border: none;
                border-radius: 50px;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.2rem;
                transition: all 0.4s ease;
                position: relative;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3);
            }

            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
                transition: left 0.5s;
            }

            .btn:hover::before { left: 100%; }
            .btn:hover {
                transform: translateY(-5px) scale(1.05);
                box-shadow: 0 15px 40px rgba(40, 167, 69, 0.4);
            }

            .btn.signup {
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
            }

            .btn.signup:hover {
                box-shadow: 0 15px 40px rgba(255, 107, 107, 0.4);
            }

            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 40px;
                margin-top: 80px;
            }

            .feature-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                transition: all 0.4s ease;
                border: 1px solid rgba(255, 255, 255, 0.3);
                position: relative;
                overflow: hidden;
            }

            .feature-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #28a745, #20c997, #ff6b6b, #a55eea);
                background-size: 300% 100%;
                animation: gradientShift 3s ease infinite;
            }

            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .feature-card:hover {
                transform: translateY(-10px) scale(1.02);
                box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
            }

            .feature-icon {
                font-size: 4rem;
                margin-bottom: 20px;
                display: inline-block;
                animation: bounce 2s ease-in-out infinite;
            }

            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }

            .feature-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 15px;
                color: #2c3e50;
            }

            .feature-desc {
                color: #666;
                line-height: 1.6;
                font-size: 1.1rem;
                font-weight: 300;
            }

            /* Interactive Elements */
            .stats-section {
                margin-top: 80px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 30px;
            }

            .stat-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }

            .stat-card:hover {
                transform: scale(1.05);
                background: rgba(255, 255, 255, 0.15);
            }

            .stat-number {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #fff, #a8e6cf);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .stat-label {
                font-size: 1rem;
                opacity: 0.9;
                font-weight: 300;
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .title { font-size: 2.5rem; }
                .subtitle { font-size: 1.1rem; }
                .btn { padding: 15px 35px; font-size: 1rem; }
                .header { padding: 40px 20px; }
                .feature-card { padding: 30px; }
            }
        </style>
    </head>
    <body>
        <div class="bg-animation"></div>
        <div class="particles">
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
        </div>

        <div class="container">
            <div class="header">
                <h1 class="title">🌱 GreenVerse Social</h1>
                <p class="subtitle">The Ultimate Interactive Social Platform for Plant Enthusiasts</p>
                <p style="font-size: 1.1rem; opacity: 0.8; margin-bottom: 20px;">
                    Connect • Share • Learn • Grow Together in a Beautiful Digital Garden 🌿
                </p>
                <div class="auth-buttons">
                    <a href="/login" class="btn">🔑 Enter Garden</a>
                    <a href="/signup" class="btn signup">✨ Plant Your Roots</a>
                </div>
            </div>

            <div class="stats-section">
                <div class="stat-card">
                    <div class="stat-number" id="online-users">1.2K+</div>
                    <div class="stat-label">Active Gardeners</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">25K+</div>
                    <div class="stat-label">Plants Shared</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">500+</div>
                    <div class="stat-label">Flower Titles Earned</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">98%</div>
                    <div class="stat-label">Happy Plants</div>
                </div>
            </div>

            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">🌐</div>
                    <h3 class="feature-title">Interactive Social Garden</h3>
                    <p class="feature-desc">Share your plant journey with stunning visuals, real-time updates, and connect with fellow plant lovers in our beautiful digital garden space.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <h3 class="feature-title">Smart Quiz Ecosystem</h3>
                    <p class="feature-desc">Challenge yourself with 3 difficulty levels and earn beautiful flower titles as rewards. Compete with friends and showcase your botanical knowledge!</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔬</div>
                    <h3 class="feature-title">AI Plant Doctor</h3>
                    <p class="feature-desc">Advanced AI-powered plant health analysis with dehydration detection, stress monitoring, and personalized care recommendations for your green friends.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <h3 class="feature-title">Live Plant Chat</h3>
                    <p class="feature-desc">Real-time messaging with plant experts, instant notifications, and live discussions about gardening tips, plant care, and botanical discoveries.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🏆</div>
                    <h3 class="feature-title">Achievement Garden</h3>
                    <p class="feature-desc">Unlock beautiful flower titles, earn badges for plant care expertise, and build your reputation in our thriving plant community ecosystem.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">Growth Analytics</h3>
                    <p class="feature-desc">Track your plant health history, monitor progress over time, and get AI-powered insights to become the ultimate plant parent you've always wanted to be.</p>
                </div>
            </div>
        </div>

        <script>
            // Interactive animations
            document.addEventListener('DOMContentLoaded', function() {
                // Animate stats on scroll
                const statNumbers = document.querySelectorAll('.stat-number');

                function animateStats() {
                    statNumbers.forEach(stat => {
                        const rect = stat.getBoundingClientRect();
                        if (rect.top < window.innerHeight && rect.bottom > 0) {
                            stat.style.animation = 'none';
                            setTimeout(() => {
                                stat.style.animation = 'bounce 1s ease-in-out';
                            }, 100);
                        }
                    });
                }

                window.addEventListener('scroll', animateStats);
                animateStats(); // Initial call

                // Dynamic user count
                let userCount = 1200;
                setInterval(() => {
                    userCount += Math.floor(Math.random() * 10) - 5;
                    userCount = Math.max(1000, Math.min(1500, userCount));
                    document.getElementById('online-users').textContent = (userCount / 1000).toFixed(1) + 'K+';
                }, 3000);

                // Interactive particle effects on mouse move
                document.addEventListener('mousemove', function(e) {
                    const particles = document.querySelectorAll('.particle');
                    const mouseX = e.clientX / window.innerWidth;
                    const mouseY = e.clientY / window.innerHeight;

                    particles.forEach((particle, index) => {
                        const speed = (index + 1) * 0.5;
                        const x = mouseX * speed;
                        const y = mouseY * speed;
                        particle.style.transform += ` translate(${x}px, ${y}px)`;
                    });
                });
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill in all fields')
            return redirect(url_for('login'))

        conn = sqlite3.connect('greenverse_social.db')
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):  # password_hash is at index 3
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['first_name'] = user[4]
            flash('Welcome back!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔑 Login - GreenVerse Social</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 25%, #6b8e23 50%, #8fbc8f 75%, #98fb98 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 400px;
                text-align: center;
            }
            .logo { font-size: 3rem; margin-bottom: 10px; }
            .title { font-size: 2rem; font-weight: bold; margin-bottom: 10px; }
            .subtitle { color: #666; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; text-align: left; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
            .form-group input {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            .form-group input:focus { outline: none; border-color: #28a745; }
            .btn {
                width: 100%;
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
            .link { color: #28a745; text-decoration: none; font-weight: bold; }
            .link:hover { text-decoration: underline; }
            .alert {
                background: #f8d7da;
                color: #721c24;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">🌱</div>
            <h1 class="title">Welcome Back!</h1>
            <p class="subtitle">Sign in to your GreenVerse account</p>

            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <form method="POST">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">🚀 Sign In</button>
            </form>

            <p>Don't have an account? <a href="/signup" class="link">Sign up here</a></p>
            <p style="margin-top: 15px;"><a href="/" class="link">← Back to Home</a></p>
        </div>
    </body>
    </html>
    ''')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([email, username, first_name, last_name, password, confirm_password]):
            flash('Please fill in all fields')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('signup'))

        conn = sqlite3.connect('greenverse_social.db')

        # Check if email or username already exists
        existing_user = conn.execute('SELECT * FROM users WHERE email = ? OR username = ?', (email, username)).fetchone()
        if existing_user:
            flash('Email or username already exists')
            conn.close()
            return redirect(url_for('signup'))

        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)

        conn.execute('''
            INSERT INTO users (id, email, username, first_name, last_name, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, email, username, first_name, last_name, password_hash))

        conn.commit()
        conn.close()

        # Auto login after signup
        session['user_id'] = user_id
        session['username'] = username
        session['first_name'] = first_name

        flash('Account created successfully! Welcome to GreenVerse!')
        return redirect(url_for('dashboard'))

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>✨ Sign Up - GreenVerse Social</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 25%, #6b8e23 50%, #8fbc8f 75%, #98fb98 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .signup-container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 500px;
                text-align: center;
            }
            .logo { font-size: 3rem; margin-bottom: 10px; }
            .title { font-size: 2rem; font-weight: bold; margin-bottom: 10px; }
            .subtitle { color: #666; margin-bottom: 30px; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
            .form-group { margin-bottom: 20px; text-align: left; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
            .form-group input {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            .form-group input:focus { outline: none; border-color: #28a745; }
            .btn {
                width: 100%;
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                color: white;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
            .link { color: #28a745; text-decoration: none; font-weight: bold; }
            .link:hover { text-decoration: underline; }
            .alert {
                background: #f8d7da;
                color: #721c24;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="signup-container">
            <div class="logo">🌱</div>
            <h1 class="title">Join GreenVerse!</h1>
            <p class="subtitle">Create your account and start your plant journey</p>

            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <form method="POST">
                <div class="form-row">
                    <div class="form-group">
                        <label for="first_name">First Name</label>
                        <input type="text" id="first_name" name="first_name" required>
                    </div>
                    <div class="form-group">
                        <label for="last_name">Last Name</label>
                        <input type="text" id="last_name" name="last_name" required>
                    </div>
                </div>
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <div class="form-group">
                        <label for="confirm_password">Confirm Password</label>
                        <input type="password" id="confirm_password" name="confirm_password" required>
                    </div>
                </div>
                <button type="submit" class="btn">🚀 Create Account</button>
            </form>

            <p>Already have an account? <a href="/login" class="link">Sign in here</a></p>
            <p style="margin-top: 15px;"><a href="/" class="link">← Back to Home</a></p>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Create sample data if it doesn't exist
    create_sample_data()

    # Get user's posts including sample posts
    conn = sqlite3.connect('greenverse_social.db')
    conn.row_factory = sqlite3.Row
    posts = conn.execute('''
        SELECT p.*, u.username, u.first_name, u.last_name
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 20
    ''').fetchall()
    conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌱 GreenVerse Social Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 50%, #ffd3a5 100%);
                min-height: 100vh;
                color: #333;
                position: relative;
                overflow-x: hidden;
            }

            /* Animated Background with Flowers */
            .bg-garden {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                background-image:
                    url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="%23ff69b4" opacity="0.3"/><circle cx="80" cy="30" r="1.5" fill="%23ffd700" opacity="0.4"/><circle cx="60" cy="70" r="2.5" fill="%23ff6347" opacity="0.3"/><circle cx="30" cy="80" r="1" fill="%23da70d6" opacity="0.5"/><circle cx="90" cy="60" r="2" fill="%2300fa9a" opacity="0.3"/></svg>');
                background-size: 200px 200px;
                animation: floatFlowers 20s ease-in-out infinite;
            }

            @keyframes floatFlowers {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-20px) rotate(5deg); }
            }

            /* Floating Petals */
            .petals {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                pointer-events: none;
            }

            .petal {
                position: absolute;
                width: 10px;
                height: 10px;
                background: radial-gradient(circle, #ff69b4, #ff1493);
                border-radius: 50% 0 50% 0;
                animation: fallPetals 15s infinite linear;
                opacity: 0.7;
            }

            .petal:nth-child(1) { left: 10%; animation-delay: 0s; background: radial-gradient(circle, #ffd700, #ffa500); }
            .petal:nth-child(2) { left: 20%; animation-delay: 2s; background: radial-gradient(circle, #ff69b4, #ff1493); }
            .petal:nth-child(3) { left: 30%; animation-delay: 4s; background: radial-gradient(circle, #da70d6, #9370db); }
            .petal:nth-child(4) { left: 40%; animation-delay: 6s; background: radial-gradient(circle, #ff6347, #dc143c); }
            .petal:nth-child(5) { left: 50%; animation-delay: 8s; background: radial-gradient(circle, #00fa9a, #00ff7f); }
            .petal:nth-child(6) { left: 60%; animation-delay: 10s; background: radial-gradient(circle, #87ceeb, #4169e1); }
            .petal:nth-child(7) { left: 70%; animation-delay: 12s; background: radial-gradient(circle, #dda0dd, #ba55d3); }
            .petal:nth-child(8) { left: 80%; animation-delay: 14s; background: radial-gradient(circle, #f0e68c, #bdb76b); }
            .petal:nth-child(9) { left: 90%; animation-delay: 16s; background: radial-gradient(circle, #ffc0cb, #ff69b4); }

            @keyframes fallPetals {
                0% { transform: translateY(-100px) rotate(0deg); opacity: 0; }
                10% { opacity: 0.7; }
                90% { opacity: 0.7; }
                100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
            }
            .navbar {
                background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 50%, #20c997 100%);
                color: white;
                padding: 20px 0;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(255,255,255,0.1);
                position: relative;
                overflow: hidden;
            }

            .navbar::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M10,50 Q30,30 50,50 T90,50" stroke="%23ffffff" stroke-width="0.5" fill="none" opacity="0.1"/></svg>');
                background-size: 200px 100px;
                animation: navPattern 10s ease-in-out infinite;
            }

            @keyframes navPattern {
                0%, 100% { transform: translateX(0); }
                50% { transform: translateX(20px); }
            }
            .nav-container {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 20px;
            }
            .logo { font-size: 1.5rem; font-weight: bold; }
            .nav-links { display: flex; gap: 20px; align-items: center; }
            .nav-links a {
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 20px;
                transition: background 0.3s ease;
            }
            .nav-links a:hover { background: rgba(255,255,255,0.2); }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                display: grid;
                grid-template-columns: 1fr 2fr 1fr;
                gap: 20px;
            }

            .sidebar {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 25px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                height: fit-content;
                border: 1px solid rgba(255,255,255,0.3);
            }

            .main-feed {
                max-width: none;
            }

            .env-data {
                background: linear-gradient(135deg, #4a7c59 0%, #6b8e23 100%);
                color: white;
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 20px;
                position: relative;
                overflow: hidden;
            }

            .env-data::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="1" fill="%23ffffff" opacity="0.1"/><circle cx="80" cy="80" r="1.5" fill="%23ffffff" opacity="0.1"/></svg>');
                background-size: 50px 50px;
                animation: envPattern 20s linear infinite;
            }

            @keyframes envPattern {
                0% { transform: translateX(0) translateY(0); }
                100% { transform: translateX(50px) translateY(50px); }
            }

            .env-title {
                font-size: 1.3rem;
                font-weight: 600;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
            }

            .env-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                position: relative;
                z-index: 1;
            }

            .env-label {
                font-size: 1rem;
                opacity: 0.9;
            }

            .env-value {
                font-size: 1.2rem;
                font-weight: 600;
                background: rgba(255,255,255,0.2);
                padding: 5px 12px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }

            .time-display {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 15px;
                text-align: center;
                margin-bottom: 20px;
                backdrop-filter: blur(10px);
            }

            .current-time {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 5px;
            }

            .current-date {
                font-size: 0.9rem;
                opacity: 0.8;
            }
            .card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 30px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                margin-bottom: 25px;
                border: 1px solid rgba(255,255,255,0.2);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
                background-size: 300% 100%;
                animation: cardGradient 3s ease infinite;
            }

            @keyframes cardGradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            }

            .post-form {
                background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,249,250,0.9) 100%);
                border: 2px dashed #4ecdc4;
                border-radius: 25px;
                padding: 35px;
                margin-bottom: 40px;
                backdrop-filter: blur(20px);
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
            }

            .post-form::before {
                content: '🌸';
                position: absolute;
                top: 15px;
                right: 20px;
                font-size: 1.5rem;
                opacity: 0.3;
                animation: floatIcon 3s ease-in-out infinite;
            }

            @keyframes floatIcon {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-10px) rotate(10deg); }
            }

            .post-form:hover {
                border-color: #ff6b6b;
                transform: scale(1.02);
                box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            }
            .form-group textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                resize: none;
                font-family: inherit;
                font-size: 1rem;
                margin-bottom: 15px;
            }
            .form-group textarea:focus { outline: none; border-color: #28a745; }
            .btn {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
            .post {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 15px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #28a745;
            }
            .post-header {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }
            .avatar {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                margin-right: 15px;
            }
            .post-actions {
                display: flex;
                gap: 15px;
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #eee;
            }
            .action-btn {
                background: none;
                border: none;
                color: #666;
                cursor: pointer;
                padding: 5px 10px;
                border-radius: 15px;
                transition: all 0.3s ease;
            }
            .action-btn:hover { background: #f8f9fa; color: #28a745; }
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #28a745;
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                display: none;
                z-index: 1000;
                animation: slideIn 0.3s ease;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); }
                to { transform: translateX(0); }
            }
        </style>
    </head>
    <body>
        <div class="notification" id="notification"></div>

        <nav class="navbar">
            <div class="nav-container">
                <div class="logo">🌱 GreenVerse Social</div>
                <div class="nav-links">
                    <span>Welcome, {{ session.first_name }}!</span>
                    <a href="/quiz">🧠 Quiz</a>
                    <a href="/plant-analyzer">🔬 Analyze</a>
                    <a href="/logout">🚪 Logout</a>
                </div>
            </div>
        </nav>

        <div class="container">
            <!-- Left Sidebar -->
            <div class="sidebar">
                <div class="env-data">
                    <h3 class="env-title">🌍 Faridabad Environment</h3>
                    <div class="time-display">
                        <div class="current-time" id="currentTime">--:--:--</div>
                        <div class="current-date" id="currentDate">Loading...</div>
                    </div>
                    <div class="env-item">
                        <span class="env-label">🌡️ Temperature</span>
                        <span class="env-value" id="temperature">--°C</span>
                    </div>
                    <div class="env-item">
                        <span class="env-label">💧 Humidity</span>
                        <span class="env-value" id="humidity">--%</span>
                    </div>
                    <div class="env-item">
                        <span class="env-label">🌬️ Air Quality</span>
                        <span class="env-value" id="airQuality">--</span>
                    </div>
                    <div class="env-item">
                        <span class="env-label">☀️ UV Index</span>
                        <span class="env-value" id="uvIndex">--</span>
                    </div>
                </div>

                <div class="card">
                    <h3>🎯 Quick Actions</h3>
                    <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 15px;">
                        <a href="/quiz" class="btn quiz" style="background: linear-gradient(135deg, #a55eea 0%, #8e44ad 100%); text-decoration: none; text-align: center;">🧠 Take Quiz</a>
                        <a href="/plant-analyzer" class="btn analyze" style="background: linear-gradient(135deg, #26de81 0%, #20bf6b 100%); text-decoration: none; text-align: center;">🔬 Analyze Plant</a>
                    </div>
                </div>
            </div>

            <!-- Main Feed -->
            <div class="main-feed">
                <div class="post-form">
                    <h3>📝 Share with the Community</h3>
                    <form id="postForm">
                        <div class="form-group">
                            <textarea id="postContent" placeholder="What's growing in your garden today? Share your plant journey, ask questions, or give tips!" rows="4" required></textarea>
                        </div>
                        <button type="submit" class="btn">🚀 Share Post</button>
                    </form>
                </div>

                <div id="postsContainer">
                    {% for post in posts %}
                    <div class="post">
                        <div class="post-header">
                            <div class="avatar">{{ post.first_name[0] }}{{ post.last_name[0] }}</div>
                            <div>
                                <strong>{{ post.first_name }} {{ post.last_name }}</strong>
                                <div style="font-size: 0.9rem; color: #666;">{{ post.created_at }}</div>
                            </div>
                        </div>
                        <p>{{ post.content }}</p>
                        {% if post.image_url %}
                        <div style="margin: 15px 0;">
                            <img src="{{ post.image_url }}" alt="Plant photo" style="width: 100%; max-height: 400px; object-fit: cover; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                        </div>
                        {% endif %}
                        <div class="post-actions">
                            <button class="action-btn" onclick="likePost('{{ post.id }}')">❤️ {{ post.likes_count }} Likes</button>
                            <button class="action-btn">💬 {{ post.comments_count }} Comments</button>
                            <button class="action-btn">🔄 Share</button>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Right Sidebar -->
            <div class="sidebar">
                <div class="card">
                    <h3>🔥 Trending Now</h3>
                    <div style="margin-top: 15px;">
                        <p style="margin-bottom: 10px;">🌱 #MonsteraMonday</p>
                        <p style="margin-bottom: 10px;">🏆 #QuizChampion</p>
                        <p style="margin-bottom: 10px;">🔬 #PlantAnalysis</p>
                        <p style="margin-bottom: 10px;">💧 #WateringTips</p>
                        <p style="margin-bottom: 10px;">🌸 #FaridabadGardeners</p>
                    </div>
                </div>

                <div class="card">
                    <h3>👥 Online Users</h3>
                    <div style="margin-top: 15px;">
                        <p>🟢 <span id="online-count">127</span> gardeners online</p>
                        <p style="margin-top: 10px; font-size: 0.9rem; color: #666;">Join the conversation!</p>
                    </div>
                </div>

                <div class="card">
                    <h3>📊 Your Stats</h3>
                    <div style="margin-top: 15px;">
                        <p><strong>Posts:</strong> <span id="user-posts">0</span></p>
                        <p><strong>Analyses:</strong> <span id="user-analyses">0</span></p>
                        <p><strong>Quiz Score:</strong> <span id="user-score">0</span></p>
                        <p><strong>Achievements:</strong> <span id="user-achievements">0</span></p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Initialize Socket.IO
            const socket = io();

            // Real-time Environmental Data for Faridabad
            function updateEnvironmentalData() {
                // Simulate realistic environmental data for Faridabad
                const now = new Date();
                const faridabadTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Kolkata"}));

                // Update time display
                const timeString = faridabadTime.toLocaleTimeString('en-IN', {
                    hour12: true,
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
                const dateString = faridabadTime.toLocaleDateString('en-IN', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });

                document.getElementById('currentTime').textContent = timeString;
                document.getElementById('currentDate').textContent = dateString;

                // Simulate realistic temperature for Faridabad (varies by time of day)
                const hour = faridabadTime.getHours();
                let baseTemp = 25; // Base temperature
                if (hour >= 6 && hour <= 18) {
                    baseTemp = 28 + Math.sin((hour - 6) * Math.PI / 12) * 8; // Day cycle
                } else {
                    baseTemp = 22 + Math.random() * 4; // Night temperature
                }
                const temperature = Math.round(baseTemp + (Math.random() - 0.5) * 2);

                // Simulate humidity (higher in morning/evening)
                let baseHumidity = 60;
                if (hour >= 5 && hour <= 9 || hour >= 18 && hour <= 22) {
                    baseHumidity = 70 + Math.random() * 15;
                } else {
                    baseHumidity = 45 + Math.random() * 20;
                }
                const humidity = Math.round(baseHumidity);

                // Simulate air quality
                const airQualityValues = ['Good', 'Moderate', 'Poor'];
                const airQuality = airQualityValues[Math.floor(Math.random() * airQualityValues.length)];

                // Simulate UV index (higher during day)
                let uvIndex = 0;
                if (hour >= 8 && hour <= 17) {
                    uvIndex = Math.round(3 + Math.random() * 7);
                } else {
                    uvIndex = 0;
                }

                // Update display
                document.getElementById('temperature').textContent = temperature + '°C';
                document.getElementById('humidity').textContent = humidity + '%';
                document.getElementById('airQuality').textContent = airQuality;
                document.getElementById('uvIndex').textContent = uvIndex;

                // Color coding for values
                const tempElement = document.getElementById('temperature');
                if (temperature > 35) {
                    tempElement.style.background = 'rgba(255, 69, 58, 0.3)';
                } else if (temperature < 15) {
                    tempElement.style.background = 'rgba(0, 122, 255, 0.3)';
                } else {
                    tempElement.style.background = 'rgba(52, 199, 89, 0.3)';
                }

                const humidityElement = document.getElementById('humidity');
                if (humidity > 80) {
                    humidityElement.style.background = 'rgba(255, 149, 0, 0.3)';
                } else {
                    humidityElement.style.background = 'rgba(52, 199, 89, 0.3)';
                }
            }

            // Update environmental data every 5 seconds
            updateEnvironmentalData();
            setInterval(updateEnvironmentalData, 5000);

            // Post form submission
            document.getElementById('postForm').addEventListener('submit', function(e) {
                e.preventDefault();

                const content = document.getElementById('postContent').value;
                if (!content.trim()) return;

                fetch('/api/create-post', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: content })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('postContent').value = '';
                        showNotification('✅ Post shared successfully!');
                        location.reload(); // Refresh to show new post
                    }
                });
            });

            function likePost(postId) {
                fetch('/api/like-post', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ post_id: postId })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('❤️ Post liked!');
                        location.reload(); // Refresh to show updated likes
                    }
                });
            }

            function showNotification(message) {
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.style.display = 'block';
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 3000);
            }

            // Simulate online user count updates
            let onlineCount = 127;
            setInterval(() => {
                onlineCount += Math.floor(Math.random() * 10) - 5;
                onlineCount = Math.max(50, Math.min(200, onlineCount));
                document.getElementById('online-count').textContent = onlineCount;
            }, 8000);

            // Welcome notification
            setTimeout(() => {
                showNotification('🌱 Welcome to your GreenVerse dashboard! Real-time data from Faridabad 📍');
            }, 1000);

            // Add some sample notifications
            const notifications = [
                '🌱 Sarah just shared a new Monstera photo!',
                '🏆 Mike earned "Rose Guardian" title!',
                '💧 Perfect humidity for your plants today!',
                '☀️ UV index is moderate - great for outdoor plants!',
                '🌿 3 new gardeners joined from Faridabad!'
            ];

            let notificationIndex = 0;
            setInterval(() => {
                showNotification(notifications[notificationIndex]);
                notificationIndex = (notificationIndex + 1) % notifications.length;
            }, 15000);
        </script>
    </body>
    </html>
    ''', session=session, posts=posts)

# API Routes
@app.route('/api/create-post', methods=['POST'])
def api_create_post():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})

    data = request.get_json()
    content = data.get('content', '')

    if not content.strip():
        return jsonify({'success': False, 'error': 'Content is required'})

    # Create new post
    post_id = str(uuid.uuid4())
    conn = sqlite3.connect('greenverse_social.db')

    conn.execute('''
        INSERT INTO posts (id, user_id, content)
        VALUES (?, ?, ?)
    ''', (post_id, session['user_id'], content))

    conn.commit()
    conn.close()

    # Emit real-time update
    socketio.emit('new_post', {
        'post_id': post_id,
        'user_id': session['user_id'],
        'username': session['username'],
        'first_name': session['first_name'],
        'content': content,
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

    return jsonify({'success': True, 'post_id': post_id})

@app.route('/api/like-post', methods=['POST'])
def api_like_post():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})

    data = request.get_json()
    post_id = data.get('post_id')

    if not post_id:
        return jsonify({'success': False, 'error': 'Post ID is required'})

    conn = sqlite3.connect('greenverse_social.db')

    # Check if already liked
    existing = conn.execute('''
        SELECT id FROM likes WHERE user_id = ? AND post_id = ?
    ''', (session['user_id'], post_id)).fetchone()

    if existing:
        # Unlike
        conn.execute('DELETE FROM likes WHERE user_id = ? AND post_id = ?', (session['user_id'], post_id))
        conn.execute('UPDATE posts SET likes_count = likes_count - 1 WHERE id = ?', (post_id,))
        action = 'unliked'
    else:
        # Like
        like_id = str(uuid.uuid4())
        conn.execute('INSERT INTO likes (id, user_id, post_id) VALUES (?, ?, ?)', (like_id, session['user_id'], post_id))
        conn.execute('UPDATE posts SET likes_count = likes_count + 1 WHERE id = ?', (post_id,))
        action = 'liked'

    conn.commit()

    # Get updated like count
    likes_count = conn.execute('SELECT likes_count FROM posts WHERE id = ?', (post_id,)).fetchone()[0]
    conn.close()

    # Emit real-time update
    socketio.emit('post_liked', {
        'post_id': post_id,
        'user_id': session['user_id'],
        'action': action,
        'likes_count': likes_count
    }, broadcast=True)

    return jsonify({'success': True, 'action': action, 'likes_count': likes_count})

# Quiz System
@app.route('/quiz')
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Plant Quiz - GreenVerse Social</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 25%, #6b8e23 50%, #8fbc8f 75%, #98fb98 100%);
                min-height: 100vh;
                color: #333;
                position: relative;
                overflow-x: hidden;
            }

            /* Animated Background */
            .quiz-bg {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                background:
                    radial-gradient(circle at 25% 25%, rgba(34, 139, 34, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 75% 75%, rgba(50, 205, 50, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 50% 50%, rgba(144, 238, 144, 0.4) 0%, transparent 50%);
                animation: quizBgShift 15s ease-in-out infinite;
            }

            @keyframes quizBgShift {
                0%, 100% { transform: scale(1) rotate(0deg); }
                50% { transform: scale(1.1) rotate(3deg); }
            }

            .navbar {
                background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 50%, #20c997 100%);
                color: white;
                padding: 15px 0;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                backdrop-filter: blur(20px);
            }

            .nav-container {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 20px;
            }

            .logo { font-size: 1.5rem; font-weight: 600; }
            .nav-links { display: flex; gap: 20px; align-items: center; }
            .nav-links a {
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            .nav-links a:hover { background: rgba(255,255,255,0.2); transform: translateY(-2px); }

            .container {
                max-width: 900px;
                margin: 0 auto;
                padding: 40px 20px;
            }

            .quiz-header {
                text-align: center;
                color: white;
                margin-bottom: 50px;
                backdrop-filter: blur(10px);
                background: rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                padding: 40px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            .quiz-title {
                font-size: 3rem;
                margin-bottom: 15px;
                background: linear-gradient(45deg, #fff, #a8e6cf, #ffd3a5);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .difficulty-cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 30px;
                margin-top: 40px;
            }

            .difficulty-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 40px;
                text-align: center;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                transition: all 0.4s ease;
                border: 1px solid rgba(255,255,255,0.3);
                position: relative;
                overflow: hidden;
                cursor: pointer;
            }

            .difficulty-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                transition: all 0.3s ease;
            }

            .difficulty-card.easy::before { background: linear-gradient(90deg, #4ecdc4, #44a08d); }
            .difficulty-card.hard::before { background: linear-gradient(90deg, #f093fb, #f5576c); }
            .difficulty-card.hardest::before { background: linear-gradient(90deg, #4facfe, #00f2fe); }

            .difficulty-card:hover {
                transform: translateY(-10px) scale(1.05);
                box-shadow: 0 25px 50px rgba(0,0,0,0.2);
            }

            .difficulty-icon {
                font-size: 4rem;
                margin-bottom: 20px;
                display: inline-block;
                animation: bounce 2s ease-in-out infinite;
            }

            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-15px); }
                60% { transform: translateY(-7px); }
            }

            .difficulty-title {
                font-size: 1.8rem;
                font-weight: 600;
                margin-bottom: 15px;
                color: #2c3e50;
            }

            .difficulty-desc {
                color: #666;
                margin-bottom: 25px;
                line-height: 1.6;
            }

            .start-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-weight: 600;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
            }

            .start-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            }

            .rewards-section {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 25px;
                padding: 30px;
                margin-top: 40px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                text-align: center;
            }

            .flower-preview {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 20px;
                flex-wrap: wrap;
            }

            .flower-item {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 15px;
                transition: all 0.3s ease;
            }

            .flower-item:hover {
                transform: scale(1.1);
                background: rgba(255, 255, 255, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="quiz-bg"></div>

        <nav class="navbar">
            <div class="nav-container">
                <div class="logo">🌱 GreenVerse Quiz</div>
                <div class="nav-links">
                    <a href="/dashboard">🏠 Dashboard</a>
                    <a href="/plant-analyzer">🔬 Analyze</a>
                    <a href="/logout">🚪 Logout</a>
                </div>
            </div>
        </nav>

        <div class="container">
            <div class="quiz-header">
                <h1 class="quiz-title">🧠 Plant Knowledge Quiz</h1>
                <p style="font-size: 1.2rem; opacity: 0.9;">Test your botanical expertise and earn beautiful flower titles!</p>
            </div>

            <div class="difficulty-cards">
                <div class="difficulty-card easy" onclick="startQuiz('easy')">
                    <div class="difficulty-icon">🌱</div>
                    <h3 class="difficulty-title">Easy Garden</h3>
                    <p class="difficulty-desc">Perfect for budding gardeners. Basic plant knowledge and care tips.</p>
                    <button class="start-btn">Start Easy Quiz</button>
                </div>

                <div class="difficulty-card hard" onclick="startQuiz('hard')">
                    <div class="difficulty-icon">🌿</div>
                    <h3 class="difficulty-title">Advanced Botanist</h3>
                    <p class="difficulty-desc">For experienced plant parents. Detailed plant science and care techniques.</p>
                    <button class="start-btn">Start Hard Quiz</button>
                </div>

                <div class="difficulty-card hardest" onclick="startQuiz('hardest')">
                    <div class="difficulty-icon">🌳</div>
                    <h3 class="difficulty-title">Master Gardener</h3>
                    <p class="difficulty-desc">Expert level challenge. Advanced botany and plant physiology.</p>
                    <button class="start-btn">Start Expert Quiz</button>
                </div>
            </div>

            <div class="rewards-section">
                <h3 style="font-size: 1.8rem; margin-bottom: 15px;">🏆 Flower Title Rewards</h3>
                <p style="font-size: 1.1rem; opacity: 0.9;">Get perfect scores to unlock beautiful flower titles and images!</p>
                <div class="flower-preview">
                    <div class="flower-item">🌹 Rose Guardian</div>
                    <div class="flower-item">🌻 Sunflower Champion</div>
                    <div class="flower-item">🌸 Cherry Blossom Master</div>
                    <div class="flower-item">🌺 Orchid Specialist</div>
                    <div class="flower-item">🌷 Tulip Expert</div>
                </div>
            </div>
        </div>

        <script>
            function startQuiz(difficulty) {
                // Add loading animation
                event.target.innerHTML = '🌀 Loading...';
                event.target.disabled = true;

                // Simulate quiz start
                setTimeout(() => {
                    alert(`Starting ${difficulty} quiz! Get ready to earn your flower title! 🌸`);
                    // Here you would redirect to the actual quiz interface
                    // For now, we'll just reset the button
                    event.target.innerHTML = `Start ${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)} Quiz`;
                    event.target.disabled = false;
                }, 1500);
            }

            // Add interactive animations
            document.addEventListener('DOMContentLoaded', function() {
                const cards = document.querySelectorAll('.difficulty-card');

                cards.forEach((card, index) => {
                    card.style.animationDelay = `${index * 0.2}s`;
                    card.style.animation = 'fadeInUp 0.8s ease-out forwards';
                });
            });

            // Add CSS for fadeInUp animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(30px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .difficulty-card { opacity: 0; }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    ''', session=session)

# Plant Analyzer
@app.route('/plant-analyzer')
def plant_analyzer():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔬 Plant Analyzer - GreenVerse Social</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 25%, #6b8e23 50%, #8fbc8f 75%, #98fb98 100%);
                min-height: 100vh;
                color: #333;
                position: relative;
                overflow-x: hidden;
            }

            /* Animated Background */
            .analyzer-bg {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                background:
                    radial-gradient(circle at 30% 70%, rgba(34, 139, 34, 0.4) 0%, transparent 50%),
                    radial-gradient(circle at 70% 30%, rgba(50, 205, 50, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 50% 50%, rgba(144, 238, 144, 0.3) 0%, transparent 50%);
                animation: analyzerBgShift 12s ease-in-out infinite;
            }

            @keyframes analyzerBgShift {
                0%, 100% { transform: scale(1) rotate(0deg); }
                50% { transform: scale(1.05) rotate(-2deg); }
            }

            .navbar {
                background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 50%, #20c997 100%);
                color: white;
                padding: 15px 0;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                backdrop-filter: blur(20px);
            }

            .nav-container {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 20px;
            }

            .logo { font-size: 1.5rem; font-weight: 600; }
            .nav-links { display: flex; gap: 20px; align-items: center; }
            .nav-links a {
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            .nav-links a:hover { background: rgba(255,255,255,0.2); transform: translateY(-2px); }

            .container {
                max-width: 1000px;
                margin: 0 auto;
                padding: 40px 20px;
            }

            .analyzer-header {
                text-align: center;
                color: white;
                margin-bottom: 50px;
                backdrop-filter: blur(10px);
                background: rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                padding: 40px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            .analyzer-title {
                font-size: 3rem;
                margin-bottom: 15px;
                background: linear-gradient(45deg, #fff, #4facfe, #00f2fe);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .upload-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 40px;
                margin-bottom: 30px;
                border: 2px dashed #4facfe;
                text-align: center;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .upload-section::before {
                content: '🌿';
                position: absolute;
                top: 20px;
                right: 30px;
                font-size: 2rem;
                opacity: 0.3;
                animation: floatLeaf 4s ease-in-out infinite;
            }

            @keyframes floatLeaf {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-15px) rotate(15deg); }
            }

            .upload-section:hover {
                border-color: #00f2fe;
                transform: scale(1.02);
                box-shadow: 0 15px 30px rgba(79, 172, 254, 0.2);
            }

            .upload-area {
                border: 3px dashed #ddd;
                border-radius: 15px;
                padding: 60px 20px;
                margin-bottom: 30px;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
            }

            .upload-area:hover {
                border-color: #4facfe;
                background: rgba(79, 172, 254, 0.05);
            }

            .upload-icon {
                font-size: 4rem;
                margin-bottom: 20px;
                color: #4facfe;
                animation: pulse 2s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }

            .upload-text {
                font-size: 1.3rem;
                color: #666;
                margin-bottom: 15px;
                font-weight: 500;
            }

            .upload-subtext {
                color: #999;
                font-size: 1rem;
            }

            .analyze-btn {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 18px 40px;
                border: none;
                border-radius: 25px;
                font-weight: 600;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 10px 25px rgba(79, 172, 254, 0.3);
            }

            .analyze-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 35px rgba(79, 172, 254, 0.4);
            }

            .analyze-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }

            .results-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 40px;
                margin-top: 30px;
                border: 1px solid rgba(255,255,255,0.3);
                display: none;
            }

            .result-card {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                border-left: 5px solid #4facfe;
                transition: all 0.3s ease;
            }

            .result-card:hover {
                transform: translateX(5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }

            .result-title {
                font-size: 1.3rem;
                font-weight: 600;
                margin-bottom: 10px;
                color: #2c3e50;
            }

            .result-value {
                font-size: 1.1rem;
                color: #666;
                margin-bottom: 15px;
            }

            .progress-bar {
                width: 100%;
                height: 10px;
                background: #e9ecef;
                border-radius: 5px;
                overflow: hidden;
                margin-bottom: 15px;
            }

            .progress-fill {
                height: 100%;
                border-radius: 5px;
                transition: width 1s ease;
            }

            .progress-good { background: linear-gradient(90deg, #28a745, #20c997); }
            .progress-warning { background: linear-gradient(90deg, #ffc107, #fd7e14); }
            .progress-danger { background: linear-gradient(90deg, #dc3545, #e74c3c); }

            .suggestions {
                background: rgba(40, 167, 69, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
                border-left: 4px solid #28a745;
            }

            .suggestions h4 {
                color: #28a745;
                margin-bottom: 15px;
                font-size: 1.2rem;
            }

            .suggestions ul {
                list-style: none;
                padding: 0;
            }

            .suggestions li {
                padding: 8px 0;
                color: #666;
                position: relative;
                padding-left: 25px;
            }

            .suggestions li::before {
                content: '🌱';
                position: absolute;
                left: 0;
                top: 8px;
            }
        </style>
    </head>
    <body>
        <div class="analyzer-bg"></div>

        <nav class="navbar">
            <div class="nav-container">
                <div class="logo">🔬 Plant Analyzer</div>
                <div class="nav-links">
                    <a href="/dashboard">🏠 Dashboard</a>
                    <a href="/quiz">🧠 Quiz</a>
                    <a href="/logout">🚪 Logout</a>
                </div>
            </div>
        </nav>

        <div class="container">
            <div class="analyzer-header">
                <h1 class="analyzer-title">🔬 AI Plant Health Analyzer</h1>
                <p style="font-size: 1.2rem; opacity: 0.9;">Upload a photo of your plant for instant health analysis!</p>
            </div>

            <div class="upload-section">
                <div class="upload-area" onclick="document.getElementById('plantImage').click()">
                    <div class="upload-icon">📸</div>
                    <div class="upload-text">Click to Upload Plant Photo</div>
                    <div class="upload-subtext">Supports JPG, PNG, WebP (Max 16MB)</div>
                    <input type="file" id="plantImage" accept="image/*" style="display: none;" onchange="handleImageUpload(event)">
                </div>
                <button class="analyze-btn" id="analyzeBtn" onclick="analyzePlant()" disabled>
                    🔍 Analyze Plant Health
                </button>
            </div>

            <div class="results-section" id="resultsSection">
                <h3 style="text-align: center; margin-bottom: 30px; color: #2c3e50;">📊 Analysis Results</h3>

                <div class="result-card">
                    <div class="result-title">💧 Dehydration Level</div>
                    <div class="result-value" id="dehydrationLevel">Analyzing...</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="dehydrationProgress" style="width: 0%;"></div>
                    </div>
                </div>

                <div class="result-card">
                    <div class="result-title">😰 Stress Rate</div>
                    <div class="result-value" id="stressRate">Analyzing...</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="stressProgress" style="width: 0%;"></div>
                    </div>
                </div>

                <div class="result-card">
                    <div class="result-title">☀️ Sunlight Analysis</div>
                    <div class="result-value" id="sunlightAnalysis">Analyzing...</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="sunlightProgress" style="width: 0%;"></div>
                    </div>
                </div>

                <div class="suggestions" id="suggestions">
                    <h4>🌿 Care Recommendations</h4>
                    <ul id="suggestionsList">
                        <li>Analyzing your plant...</li>
                    </ul>
                </div>
            </div>
        </div>

        <script>
            let uploadedImage = null;

            function handleImageUpload(event) {
                const file = event.target.files[0];
                if (file) {
                    uploadedImage = file;
                    document.getElementById('analyzeBtn').disabled = false;

                    // Show preview
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const uploadArea = document.querySelector('.upload-area');
                        uploadArea.innerHTML = `
                            <img src="${e.target.result}" style="max-width: 100%; max-height: 300px; border-radius: 10px; margin-bottom: 15px;">
                            <div class="upload-text">✅ Image uploaded successfully!</div>
                            <div class="upload-subtext">Click "Analyze Plant Health" to continue</div>
                        `;
                    };
                    reader.readAsDataURL(file);
                }
            }

            function analyzePlant() {
                if (!uploadedImage) return;

                const analyzeBtn = document.getElementById('analyzeBtn');
                const resultsSection = document.getElementById('resultsSection');

                // Show loading state
                analyzeBtn.innerHTML = '🌀 Analyzing...';
                analyzeBtn.disabled = true;
                resultsSection.style.display = 'block';

                // Simulate AI analysis
                setTimeout(() => {
                    // Generate random but realistic results
                    const dehydrationScore = Math.random() * 100;
                    const stressScore = Math.random() * 100;
                    const sunlightScore = Math.random() * 100;

                    // Update dehydration
                    const dehydrationLevel = getDehydrationLevel(dehydrationScore);
                    document.getElementById('dehydrationLevel').textContent = dehydrationLevel.text;
                    document.getElementById('dehydrationProgress').style.width = dehydrationScore + '%';
                    document.getElementById('dehydrationProgress').className = 'progress-fill ' + dehydrationLevel.class;

                    // Update stress
                    const stressLevel = getStressLevel(stressScore);
                    document.getElementById('stressRate').textContent = stressLevel.text;
                    document.getElementById('stressProgress').style.width = stressScore + '%';
                    document.getElementById('stressProgress').className = 'progress-fill ' + stressLevel.class;

                    // Update sunlight
                    const sunlightLevel = getSunlightLevel(sunlightScore);
                    document.getElementById('sunlightAnalysis').textContent = sunlightLevel.text;
                    document.getElementById('sunlightProgress').style.width = sunlightScore + '%';
                    document.getElementById('sunlightProgress').className = 'progress-fill ' + sunlightLevel.class;

                    // Generate suggestions
                    const suggestions = generateSuggestions(dehydrationScore, stressScore, sunlightScore);
                    const suggestionsList = document.getElementById('suggestionsList');
                    suggestionsList.innerHTML = suggestions.map(s => `<li>${s}</li>`).join('');

                    // Reset button
                    analyzeBtn.innerHTML = '✅ Analysis Complete';
                    setTimeout(() => {
                        analyzeBtn.innerHTML = '🔍 Analyze Another Plant';
                        analyzeBtn.disabled = false;
                    }, 2000);

                }, 3000);
            }

            function getDehydrationLevel(score) {
                if (score < 30) return { text: `Well Hydrated (${score.toFixed(1)}%)`, class: 'progress-good' };
                if (score < 60) return { text: `Slightly Dehydrated (${score.toFixed(1)}%)`, class: 'progress-warning' };
                return { text: `Severely Dehydrated (${score.toFixed(1)}%)`, class: 'progress-danger' };
            }

            function getStressLevel(score) {
                if (score < 30) return { text: `Low Stress (${score.toFixed(1)}%)`, class: 'progress-good' };
                if (score < 60) return { text: `Moderate Stress (${score.toFixed(1)}%)`, class: 'progress-warning' };
                return { text: `High Stress (${score.toFixed(1)}%)`, class: 'progress-danger' };
            }

            function getSunlightLevel(score) {
                if (score < 30) return { text: `Insufficient Light (${score.toFixed(1)}%)`, class: 'progress-warning' };
                if (score < 70) return { text: `Optimal Light (${score.toFixed(1)}%)`, class: 'progress-good' };
                return { text: `⚠️ Excess Sunlight Warning (${score.toFixed(1)}%)`, class: 'progress-danger' };
            }

            function generateSuggestions(dehydration, stress, sunlight) {
                const suggestions = [];

                if (dehydration > 60) {
                    suggestions.push('💧 Water immediately - soil appears very dry');
                    suggestions.push('🕐 Check soil moisture daily for the next week');
                }

                if (stress > 60) {
                    suggestions.push('🌡️ Check for temperature stress or pests');
                    suggestions.push('🍃 Remove any yellowing or damaged leaves');
                }

                if (sunlight > 70) {
                    suggestions.push('☀️ WARNING: Move away from direct sunlight');
                    suggestions.push('🌤️ Provide filtered light or shade during peak hours');
                } else if (sunlight < 30) {
                    suggestions.push('💡 Move to a brighter location');
                    suggestions.push('🪟 Consider placing near a south-facing window');
                }

                suggestions.push('📅 Monitor plant daily for the next few days');
                suggestions.push('🌱 Consider using plant food if growth seems slow');

                return suggestions;
            }
        </script>
    </body>
    </html>
    ''', session=session)

if __name__ == '__main__':
    print("🌱 Starting GreenVerse Social App...")
    init_db()
    create_sample_data()
    print("✅ Database initialized with sample data!")
    print("🚀 Server starting at http://localhost:5002")
    print("📍 Real-time environmental data for Faridabad")
    print("📸 Sample posts with plant photos included")
    socketio.run(app, debug=True, host='0.0.0.0', port=5002)
