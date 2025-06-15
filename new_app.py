from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
import json
import random
import requests
from threading import Thread
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize SocketIO for real-time features
socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    conn = sqlite3.connect('new_greenverse.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Posts table for social media features
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            image_url TEXT,
            video_url TEXT,
            tags TEXT,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            shares_count INTEGER DEFAULT 0,
            post_type TEXT DEFAULT 'general',
            is_featured BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Enhanced plant analyses table
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
            sunlight_warning TEXT,
            disease_detected TEXT,
            pest_detected TEXT,
            overall_health_score REAL,
            confidence_score REAL,
            symptoms TEXT,
            recommendations TEXT,
            prevention_tips TEXT,
            cure_suggestions TEXT,
            watering_schedule TEXT,
            fertilizer_recommendation TEXT,
            urgency_level TEXT,
            recovery_time TEXT,
            follow_up_date TEXT,
            notes TEXT,
            analysis_status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Social media tables
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
    
    # Create demo user
    cursor.execute('''
        INSERT OR IGNORE INTO users 
        (id, email, username, first_name, last_name, password_hash)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('1', 'test@example.com', 'testuser', 'Plant', 'Expert', generate_password_hash('test')))
    
    # Insert demo analyses
    demo_analyses = [
        ('demo1', '1', 'demo1.jpg', 'Monstera Deliciosa', 'Tropical', 'Moderately Dehydrated', 0.65, 'Low Stress', 0.25, 'Adequate', 0.75, 'None', 'None', 0.72, 88, 
         '["Slight wilting", "Dry soil", "Brown edges"]', 
         '["Water thoroughly", "Check moisture weekly"]',
         '["Consistent watering", "Monitor humidity"]',
         '["Adjust watering schedule", "Improve drainage"]',
         'Water every 7-10 days', 'Monthly liquid fertilizer', 'Medium', '3-5 days', '2024-01-20', 'Responding well'),
        
        ('demo2', '1', 'demo2.jpg', 'Fiddle Leaf Fig', 'Indoor Tree', 'Severely Dehydrated', 0.85, 'High Stress', 0.80, 'Insufficient', 0.45, 'Leaf Spot', 'None', 0.45, 92,
         '["Brown leaf edges", "Dropping leaves", "Dry soil"]',
         '["Immediate watering", "Relocate to brighter spot"]',
         '["Consistent schedule", "Proper drainage"]',
         '["IMMEDIATE INTERVENTION", "Assess root system", "Apply fungicide"]',
         'Water every 5-7 days', 'Diluted fertilizer bi-weekly', 'High', '1-2 weeks', '2024-01-25', 'Critical condition'),
         
        ('demo3', '1', 'demo3.jpg', 'Snake Plant', 'Succulent', 'Well Hydrated', 0.30, 'No Stress', 0.10, 'Good', 0.85, 'None', 'None', 0.92, 95,
         '["Healthy green leaves", "Firm texture"]',
         '["Continue current routine"]',
         '["Avoid overwatering", "Good drainage"]',
         '["Maintain current care", "Regular pruning"]',
         'Water every 2-3 weeks', 'Fertilize quarterly', 'Low', 'Healthy', '2024-02-01', 'Excellent condition')
    ]
    
    for analysis in demo_analyses:
        cursor.execute('''
            INSERT OR IGNORE INTO plant_analyses 
            (id, user_id, image_url, plant_name, plant_type, dehydration_level, dehydration_score, stress_level, stress_score, sunlight_exposure, sunlight_score, disease_detected, pest_detected, overall_health_score, confidence_score, symptoms, recommendations, prevention_tips, cure_suggestions, watering_schedule, fertilizer_recommendation, urgency_level, recovery_time, follow_up_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', analysis)
    
    conn.commit()
    conn.close()
    print("✅ NEW Database initialized with enhanced plant analysis system!")

def init_quiz_db():
    conn = sqlite3.connect('new_greenverse.db')
    cursor = conn.cursor()
    
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

# Quiz questions database
QUIZ_QUESTIONS = {
    'simple': [
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
        },
        {
            'question': 'What do we call baby plants?',
            'options': ['Seedlings', 'Saplings', 'Sprouts', 'All of the above'],
            'correct': 3
        },
        {
            'question': 'Which part of the plant produces seeds?',
            'options': ['Roots', 'Stem', 'Leaves', 'Flowers'],
            'correct': 3
        },
        {
            'question': 'What do plants release into the air during photosynthesis?',
            'options': ['Carbon dioxide', 'Oxygen', 'Nitrogen', 'Water vapor'],
            'correct': 1
        },
        {
            'question': 'How often should most houseplants be watered?',
            'options': ['Every day', 'When soil is dry', 'Once a month', 'Never'],
            'correct': 1
        },
        {
            'question': 'What is the green substance in leaves called?',
            'options': ['Chlorophyll', 'Cellulose', 'Glucose', 'Starch'],
            'correct': 0
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
        },
        {
            'question': 'Which nutrient deficiency causes yellowing of leaves (chlorosis)?',
            'options': ['Phosphorus', 'Potassium', 'Nitrogen', 'Calcium'],
            'correct': 2
        },
        {
            'question': 'What is the term for plants that complete their life cycle in two years?',
            'options': ['Annual', 'Biennial', 'Perennial', 'Ephemeral'],
            'correct': 1
        },
        {
            'question': 'Which type of pollination occurs within the same flower?',
            'options': ['Cross-pollination', 'Self-pollination', 'Wind pollination', 'Water pollination'],
            'correct': 1
        },
        {
            'question': 'What is the waxy coating on leaves called?',
            'options': ['Epidermis', 'Cuticle', 'Mesophyll', 'Stomata'],
            'correct': 1
        },
        {
            'question': 'Which plant family does the tomato belong to?',
            'options': ['Rosaceae', 'Solanaceae', 'Brassicaceae', 'Cucurbitaceae'],
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
        },
        {
            'question': 'Which plant hormone inhibits seed germination and promotes dormancy?',
            'options': ['Auxin', 'Gibberellin', 'Abscisic acid', 'Cytokinin'],
            'correct': 2
        },
        {
            'question': 'What is the C4 pathway an adaptation for?',
            'options': ['Cold tolerance', 'Drought resistance', 'High light intensity', 'Low CO2 concentration'],
            'correct': 3
        },
        {
            'question': 'Which structure in chloroplasts contains the photosynthetic pigments?',
            'options': ['Stroma', 'Thylakoids', 'Granum', 'Intermembrane space'],
            'correct': 1
        },
        {
            'question': 'What is allelopathy in plants?',
            'options': ['Self-fertilization', 'Chemical inhibition of other plants', 'Rapid growth response', 'Seasonal flowering'],
            'correct': 1
        },
        {
            'question': 'Which type of plant tissue is responsible for secondary growth?',
            'options': ['Parenchyma', 'Collenchyma', 'Cambium', 'Sclerenchyma'],
            'correct': 2
        }
    ]
}

# Flower titles and their corresponding API search terms
FLOWER_TITLES = [
    {'title': 'Rose Guardian', 'flower': 'red rose'},
    {'title': 'Sunflower Champion', 'flower': 'sunflower'},
    {'title': 'Lily Master', 'flower': 'white lily'},
    {'title': 'Orchid Specialist', 'flower': 'purple orchid'},
    {'title': 'Tulip Expert', 'flower': 'colorful tulips'},
    {'title': 'Daisy Keeper', 'flower': 'white daisy'},
    {'title': 'Lavender Sage', 'flower': 'lavender field'},
    {'title': 'Cherry Blossom Sensei', 'flower': 'cherry blossom'},
    {'title': 'Iris Virtuoso', 'flower': 'blue iris'},
    {'title': 'Peony Prodigy', 'flower': 'pink peony'},
    {'title': 'Hibiscus Hero', 'flower': 'red hibiscus'},
    {'title': 'Jasmine Genius', 'flower': 'white jasmine'},
    {'title': 'Magnolia Maestro', 'flower': 'magnolia flower'},
    {'title': 'Daffodil Devotee', 'flower': 'yellow daffodil'},
    {'title': 'Carnation Connoisseur', 'flower': 'pink carnation'}
]

def get_flower_image(flower_name):
    # Using Unsplash API for beautiful flower images
    # In production, you'd want to use a real API key
    return f"https://source.unsplash.com/800x600/?{flower_name.replace(' ', '+')}"

def save_quiz_attempt(user_id, level, score, total_questions):
    attempt_id = str(uuid.uuid4())
    conn = sqlite3.connect('new_greenverse.db')
    conn.execute('''
        INSERT INTO quiz_attempts (id, user_id, level, score, total_questions)
        VALUES (?, ?, ?, ?, ?)
    ''', (attempt_id, user_id, level, score, total_questions))
    conn.commit()
    conn.close()
    return attempt_id

def save_achievement(user_id, flower_title, flower_image_url, level):
    achievement_id = str(uuid.uuid4())
    conn = sqlite3.connect('new_greenverse.db')
    conn.execute('''
        INSERT INTO user_achievements (id, user_id, flower_title, flower_image_url, level)
        VALUES (?, ?, ?, ?, ?)
    ''', (achievement_id, user_id, flower_title, flower_image_url, level))
    conn.commit()
    conn.close()
    return achievement_id

def get_user_achievements(user_id):
    conn = sqlite3.connect('new_greenverse.db')
    conn.row_factory = sqlite3.Row
    achievements = conn.execute('''
        SELECT * FROM user_achievements
        WHERE user_id = ?
        ORDER BY earned_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return achievements

# Enhanced Plant Analysis Functions
def generate_plant_analysis():
    """Generate comprehensive plant health analysis with enhanced dehydration detection"""

    # Simulated plant database
    plants = [
        {'name': 'Monstera Deliciosa', 'type': 'Tropical'},
        {'name': 'Fiddle Leaf Fig', 'type': 'Indoor Tree'},
        {'name': 'Snake Plant', 'type': 'Succulent'},
        {'name': 'Pothos', 'type': 'Vine'},
        {'name': 'Peace Lily', 'type': 'Flowering'},
        {'name': 'Rubber Plant', 'type': 'Tree'},
        {'name': 'ZZ Plant', 'type': 'Succulent'},
        {'name': 'Philodendron', 'type': 'Tropical'}
    ]

    plant = random.choice(plants)

    # Enhanced dehydration analysis
    dehydration_score = random.uniform(0.1, 0.9)
    if dehydration_score < 0.3:
        dehydration_level = 'Well Hydrated'
    elif dehydration_score < 0.6:
        dehydration_level = 'Moderately Dehydrated'
    else:
        dehydration_level = 'Severely Dehydrated'

    # Stress analysis
    stress_score = random.uniform(0.1, 0.8)
    if stress_score < 0.3:
        stress_level = 'No Stress'
    elif stress_score < 0.6:
        stress_level = 'Low Stress'
    else:
        stress_level = 'High Stress'

    # Sunlight analysis with warnings
    sunlight_score = random.uniform(0.2, 0.9)
    if sunlight_score < 0.4:
        sunlight_exposure = 'Insufficient'
        sunlight_warning = '⚠️ WARNING: Plant needs more sunlight. Consider relocating to a brighter spot.'
    elif sunlight_score > 0.8:
        sunlight_exposure = 'Excessive'
        sunlight_warning = '🔥 WARNING: Too much direct sunlight may cause leaf burn. Provide some shade.'
    else:
        sunlight_exposure = 'Adequate'
        sunlight_warning = '✅ Sunlight levels are optimal for this plant.'

    # Overall health calculation
    overall_health = (1 - dehydration_score) * 0.4 + (1 - stress_score) * 0.3 + (sunlight_score if sunlight_score <= 0.8 else (1 - sunlight_score)) * 0.3

    # Symptoms based on analysis
    symptoms = []
    if dehydration_score > 0.6:
        symptoms.extend(['Wilting leaves', 'Dry soil', 'Brown leaf edges'])
    if stress_score > 0.6:
        symptoms.extend(['Yellowing leaves', 'Dropping leaves', 'Stunted growth'])
    if sunlight_score < 0.4:
        symptoms.extend(['Leggy growth', 'Pale leaves', 'Slow growth'])
    elif sunlight_score > 0.8:
        symptoms.extend(['Leaf burn', 'Crispy edges', 'Fading colors'])

    if not symptoms:
        symptoms = ['Healthy appearance', 'Good color', 'Strong growth']

    # Recommendations
    recommendations = []
    if dehydration_score > 0.6:
        recommendations.extend(['Water immediately', 'Check soil moisture daily', 'Improve drainage'])
    if stress_score > 0.6:
        recommendations.extend(['Reduce environmental stress', 'Check for pests', 'Adjust care routine'])
    if sunlight_score < 0.4:
        recommendations.append('Move to brighter location')
    elif sunlight_score > 0.8:
        recommendations.append('Provide shade during peak hours')

    # Cure suggestions
    cure_suggestions = []
    if dehydration_score > 0.7:
        cure_suggestions.extend(['IMMEDIATE WATERING REQUIRED', 'Soak soil thoroughly', 'Monitor for 24-48 hours'])
    if stress_score > 0.7:
        cure_suggestions.extend(['Isolate plant', 'Apply appropriate treatment', 'Consult plant expert'])

    # Urgency level
    if dehydration_score > 0.7 or stress_score > 0.7:
        urgency_level = 'High'
    elif dehydration_score > 0.5 or stress_score > 0.5:
        urgency_level = 'Medium'
    else:
        urgency_level = 'Low'

    return {
        'plant_name': plant['name'],
        'plant_type': plant['type'],
        'dehydration_level': dehydration_level,
        'dehydration_score': dehydration_score,
        'stress_level': stress_level,
        'stress_score': stress_score,
        'sunlight_exposure': sunlight_exposure,
        'sunlight_score': sunlight_score,
        'sunlight_warning': sunlight_warning,
        'overall_health_score': overall_health,
        'confidence_score': random.randint(85, 98),
        'symptoms': symptoms,
        'recommendations': recommendations,
        'cure_suggestions': cure_suggestions,
        'urgency_level': urgency_level,
        'watering_schedule': f"Water every {random.randint(3, 14)} days when top inch is dry",
        'fertilizer_recommendation': random.choice([
            'Balanced liquid fertilizer monthly',
            'Slow-release granules quarterly',
            'Organic compost bi-monthly'
        ])
    }

def save_plant_analysis(user_id, image_url, analysis_data):
    """Save plant analysis to database"""
    analysis_id = str(uuid.uuid4())
    conn = sqlite3.connect('new_greenverse.db')

    conn.execute('''
        INSERT INTO plant_analyses
        (id, user_id, image_url, plant_name, plant_type, dehydration_level, dehydration_score,
         stress_level, stress_score, sunlight_exposure, sunlight_score, sunlight_warning,
         overall_health_score, confidence_score, symptoms, recommendations,
         cure_suggestions, watering_schedule, fertilizer_recommendation, urgency_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        analysis_id, user_id, image_url,
        analysis_data['plant_name'], analysis_data['plant_type'],
        analysis_data['dehydration_level'], analysis_data['dehydration_score'],
        analysis_data['stress_level'], analysis_data['stress_score'],
        analysis_data['sunlight_exposure'], analysis_data['sunlight_score'],
        analysis_data['sunlight_warning'],
        analysis_data['overall_health_score'], analysis_data['confidence_score'],
        json.dumps(analysis_data['symptoms']), json.dumps(analysis_data['recommendations']),
        json.dumps(analysis_data['cure_suggestions']),
        analysis_data['watering_schedule'], analysis_data['fertilizer_recommendation'],
        analysis_data['urgency_level']
    ))

    conn.commit()
    conn.close()
    return analysis_id

def get_plant_history(user_id):
    """Get plant analysis history for user"""
    conn = sqlite3.connect('new_greenverse.db')
    conn.row_factory = sqlite3.Row
    analyses = conn.execute('''
        SELECT * FROM plant_analyses
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return analyses

# Social Media Functions
def create_post(user_id, title, content, image_url=None, video_url=None, tags=None, post_type='general'):
    """Create a new social media post"""
    post_id = str(uuid.uuid4())
    conn = sqlite3.connect('new_greenverse.db')

    conn.execute('''
        INSERT INTO posts
        (id, user_id, title, content, image_url, video_url, tags, post_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (post_id, user_id, title, content, image_url, video_url, tags, post_type))

    conn.commit()
    conn.close()

    # Emit real-time update
    socketio.emit('new_post', {
        'post_id': post_id,
        'user_id': user_id,
        'title': title,
        'content': content,
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

    return post_id

def get_social_feed(user_id=None, limit=20):
    """Get social media feed posts"""
    conn = sqlite3.connect('new_greenverse.db')
    conn.row_factory = sqlite3.Row

    if user_id:
        # Get posts from followed users and own posts
        posts = conn.execute('''
            SELECT p.*, u.username, u.first_name, u.last_name, u.avatar_url
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id = ? OR p.user_id IN (
                SELECT following_id FROM follows WHERE follower_id = ?
            )
            ORDER BY p.created_at DESC
            LIMIT ?
        ''', (user_id, user_id, limit)).fetchall()
    else:
        # Get all posts for public feed
        posts = conn.execute('''
            SELECT p.*, u.username, u.first_name, u.last_name, u.avatar_url
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT ?
        ''', (limit,)).fetchall()

    conn.close()
    return posts

def like_post(user_id, post_id):
    """Like or unlike a post"""
    conn = sqlite3.connect('new_greenverse.db')

    # Check if already liked
    existing = conn.execute('''
        SELECT id FROM likes WHERE user_id = ? AND post_id = ?
    ''', (user_id, post_id)).fetchone()

    if existing:
        # Unlike
        conn.execute('DELETE FROM likes WHERE user_id = ? AND post_id = ?', (user_id, post_id))
        conn.execute('UPDATE posts SET likes_count = likes_count - 1 WHERE id = ?', (post_id,))
        action = 'unliked'
    else:
        # Like
        like_id = str(uuid.uuid4())
        conn.execute('INSERT INTO likes (id, user_id, post_id) VALUES (?, ?, ?)', (like_id, user_id, post_id))
        conn.execute('UPDATE posts SET likes_count = likes_count + 1 WHERE id = ?', (post_id,))
        action = 'liked'

    conn.commit()

    # Get updated like count
    likes_count = conn.execute('SELECT likes_count FROM posts WHERE id = ?', (post_id,)).fetchone()[0]
    conn.close()

    # Emit real-time update
    socketio.emit('post_liked', {
        'post_id': post_id,
        'user_id': user_id,
        'action': action,
        'likes_count': likes_count
    }, broadcast=True)

    return {'action': action, 'likes_count': likes_count}

def add_comment(user_id, post_id, content):
    """Add a comment to a post"""
    comment_id = str(uuid.uuid4())
    conn = sqlite3.connect('new_greenverse.db')

    conn.execute('''
        INSERT INTO comments (id, user_id, post_id, content)
        VALUES (?, ?, ?, ?)
    ''', (comment_id, user_id, post_id, content))

    conn.execute('UPDATE posts SET comments_count = comments_count + 1 WHERE id = ?', (post_id,))
    conn.commit()

    # Get user info for real-time update
    user = conn.execute('SELECT username, first_name, last_name FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    # Emit real-time update
    socketio.emit('new_comment', {
        'comment_id': comment_id,
        'post_id': post_id,
        'user_id': user_id,
        'username': user['username'],
        'user_name': f"{user['first_name']} {user['last_name']}",
        'content': content,
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

    return comment_id

def create_notification(user_id, notification_type, title, message, data=None):
    """Create a notification for a user"""
    notification_id = str(uuid.uuid4())
    conn = sqlite3.connect('new_greenverse.db')

    conn.execute('''
        INSERT INTO notifications (id, user_id, type, title, message, data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (notification_id, user_id, notification_type, title, message, json.dumps(data) if data else None))

    conn.commit()
    conn.close()

    # Emit real-time notification
    socketio.emit('new_notification', {
        'notification_id': notification_id,
        'type': notification_type,
        'title': title,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }, room=f'user_{user_id}')

    return notification_id

# WebSocket Event Handlers for Real-time Features
@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        join_room(f'user_{session["user_id"]}')
        print(f'User {session["user_id"]} connected to real-time updates')

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        leave_room(f'user_{session["user_id"]}')
        print(f'User {session["user_id"]} disconnected from real-time updates')

@socketio.on('join_feed')
def handle_join_feed():
    join_room('social_feed')
    emit('joined_feed', {'status': 'success'})

@socketio.on('leave_feed')
def handle_leave_feed():
    leave_room('social_feed')
    emit('left_feed', {'status': 'success'})

# NEW INTERFACE TEMPLATES
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🌱 GreenVerse - Plant Health & Knowledge System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            text-align: center; 
            color: white; 
            margin-bottom: 50px; 
            padding: 60px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 25px;
            backdrop-filter: blur(10px);
        }
        .header h1 { 
            font-size: 4rem; 
            margin-bottom: 20px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle { 
            font-size: 1.8rem; 
            margin-bottom: 15px; 
            opacity: 0.95;
        }
        .features-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 30px; 
            margin-bottom: 50px; 
        }
        .feature-card { 
            background: white; 
            border-radius: 25px; 
            padding: 40px; 
            text-align: center; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.1); 
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .feature-card:hover { 
            transform: translateY(-10px); 
            box-shadow: 0 25px 50px rgba(0,0,0,0.2); 
        }
        .feature-icon { 
            font-size: 4rem; 
            margin-bottom: 20px; 
            display: block;
        }
        .feature-title { 
            font-size: 1.8rem; 
            color: #28a745; 
            margin-bottom: 15px; 
            font-weight: bold;
        }
        .feature-description { 
            color: #666; 
            margin-bottom: 25px; 
            line-height: 1.6;
            font-size: 1.1rem;
        }
        .btn { 
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
            color: white; 
            padding: 18px 35px; 
            text-decoration: none; 
            border-radius: 50px; 
            display: inline-block; 
            margin: 10px; 
            font-weight: bold; 
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
        }
        .btn:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 10px 25px rgba(40, 167, 69, 0.4);
        }
        .btn-quiz {
            background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);
            box-shadow: 0 5px 15px rgba(111, 66, 193, 0.3);
        }
        .btn-quiz:hover {
            box-shadow: 0 10px 25px rgba(111, 66, 193, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 GreenVerse</h1>
            <div class="subtitle">Plant Health & Knowledge System</div>
        </div>
        
        <div class="features-grid">
            <div class="feature-card">
                <span class="feature-icon">🔬</span>
                <h3 class="feature-title">AI Plant Analyzer</h3>
                <p class="feature-description">
                    Advanced health diagnostics with disease detection and treatment recommendations
                </p>
                <a href="/plant-analyzer" class="btn">Start Analysis</a>
            </div>
            
            <div class="feature-card">
                <span class="feature-icon">🧠</span>
                <h3 class="feature-title">Plant Knowledge Quiz</h3>
                <p class="feature-description">
                    Test your plant knowledge, earn flower titles, and unlock beautiful rewards
                </p>
                <a href="/quiz" class="btn btn-quiz">Take Quiz</a>
            </div>
            
            <div class="feature-card">
                <span class="feature-icon">📊</span>
                <h3 class="feature-title">Health History</h3>
                <p class="feature-description">
                    Track your plant health journey and monitor improvements over time
                </p>
                <a href="/plant-history" class="btn">View History</a>
            </div>
            
            <div class="feature-card">
                <span class="feature-icon">🏆</span>
                <h3 class="feature-title">My Achievements</h3>
                <p class="feature-description">
                    View your earned flower titles, quiz scores, and beautiful flower collection
                </p>
                <a href="/achievements" class="btn">View Achievements</a>
            </div>
        </div>
    </div>
</body>
</html>
'''

ANALYZER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔬 AI Plant Health Analyzer - Enhanced Diagnostics</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); 
            min-height: 100vh; 
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
            color: white; 
            text-align: center; 
            padding: 50px; 
            border-radius: 25px; 
            margin-bottom: 40px;
            box-shadow: 0 15px 35px rgba(40, 167, 69, 0.3);
        }
        .header h1 { 
            font-size: 3rem; 
            margin-bottom: 15px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .header p { 
            font-size: 1.3rem; 
            opacity: 0.95; 
        }
        .upload-card { 
            background: white; 
            border-radius: 25px; 
            padding: 50px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.1); 
            margin-bottom: 40px;
        }
        .upload-area { 
            border: 4px dashed #28a745; 
            padding: 80px; 
            text-align: center; 
            border-radius: 25px; 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            border-color: #20c997;
            background: linear-gradient(135deg, #e9ecef 0%, #f8f9fa 100%);
            transform: translateY(-5px);
        }
        .upload-icon { 
            font-size: 5rem; 
            color: #28a745; 
            margin-bottom: 25px; 
            display: block;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        .upload-title { 
            color: #28a745; 
            margin: 25px 0; 
            font-size: 2rem;
            font-weight: bold;
        }
        .upload-description { 
            color: #666; 
            margin-bottom: 35px; 
            font-size: 1.2rem;
            line-height: 1.6;
        }
        .file-input { 
            margin-bottom: 25px; 
            padding: 15px; 
            border: 2px solid #ddd; 
            border-radius: 15px; 
            font-size: 16px;
            width: 100%;
            max-width: 400px;
        }
        .btn { 
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
            color: white; 
            padding: 20px 40px; 
            border: none; 
            border-radius: 50px; 
            font-size: 1.2rem; 
            cursor: pointer; 
            margin: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 8px 20px rgba(40, 167, 69, 0.3);
        }
        .btn:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 12px 30px rgba(40, 167, 69, 0.4);
        }
        .btn-secondary {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            box-shadow: 0 8px 20px rgba(108, 117, 125, 0.3);
        }
        .features-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 25px; 
            margin-top: 40px; 
        }
        .feature-card { 
            background: white; 
            padding: 30px; 
            border-radius: 20px; 
            text-align: center; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .feature-card h4 { 
            color: #28a745; 
            margin-bottom: 15px; 
            font-size: 1.3rem;
        }
        .feature-card p { 
            color: #666; 
            line-height: 1.6;
        }
        .nav-section {
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 AI Plant Health Analyzer</h1>
            <p>Advanced plant diagnostics with disease detection, prevention tips, and treatment plans</p>
        </div>
        
        <div class="upload-card">
            <div class="upload-area">
                <span class="upload-icon">🌱</span>
                <h3 class="upload-title">Upload Plant Photo</h3>
                <p class="upload-description">
                    Get comprehensive health analysis including disease detection, stress assessment, and personalized treatment recommendations
                </p>
                
                <form method="POST" enctype="multipart/form-data">
                    <input type="file" name="plant_image" accept="image/*" required class="file-input">
                    <br>
                    <button type="submit" class="btn">🔬 Analyze Plant Health</button>
                </form>
            </div>
        </div>
        
        <div class="features-grid">
            <div class="feature-card">
                <h4>🔍 Disease Detection</h4>
                <p>Advanced AI identifies common plant diseases, fungal infections, and pest infestations with high accuracy</p>
            </div>
            <div class="feature-card">
                <h4>🛡️ Prevention System</h4>
                <p>Proactive care suggestions and prevention tips to keep your plants healthy and thriving</p>
            </div>
            <div class="feature-card">
                <h4>💊 Treatment Plans</h4>
                <p>Specific cure suggestions and step-by-step recovery plans for damaged or sick plants</p>
            </div>
            <div class="feature-card">
                <h4>📊 Health Tracking</h4>
                <p>Complete history of all analyses with progress tracking and improvement monitoring</p>
            </div>
            <div class="feature-card">
                <h4>⚡ Instant Results</h4>
                <p>Get comprehensive analysis results in seconds with detailed recommendations and care plans</p>
            </div>
            <div class="feature-card">
                <h4>🎯 Precision Care</h4>
                <p>Tailored recommendations based on plant type, condition, and environmental factors</p>
            </div>
        </div>
        
        <div class="nav-section">
            <h3 style="color: #28a745; margin-bottom: 20px;">Explore More Features</h3>
            <a href="/plant-history" class="btn">📊 View Analysis History</a>
            <a href="/" class="btn btn-secondary">🏠 Home</a>
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    return render_template_string(HOME_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user_id'] = '1'
        return redirect(url_for('plant_analyzer'))
    
    login_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔑 Login - GreenVerse Enhanced</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
            }
            .login-card { 
                background: white; 
                padding: 50px; 
                border-radius: 25px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.2); 
                max-width: 450px; 
                width: 100%; 
            }
            .login-header {
                text-align: center;
                margin-bottom: 40px;
            }
            .login-header h2 {
                color: #28a745;
                font-size: 2.5rem;
                margin-bottom: 10px;
            }
            .login-header p {
                color: #666;
                font-size: 1.1rem;
            }
            .form-group { margin-bottom: 25px; }
            .form-control { 
                width: 100%; 
                padding: 18px; 
                border: 2px solid #ddd; 
                border-radius: 15px; 
                font-size: 16px; 
                transition: border-color 0.3s ease;
            }
            .form-control:focus {
                border-color: #28a745;
                outline: none;
            }
            .btn { 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; 
                padding: 18px 30px; 
                border: none; 
                border-radius: 15px; 
                width: 100%; 
                font-size: 18px; 
                cursor: pointer; 
                transition: transform 0.3s ease;
            }
            .btn:hover { 
                transform: translateY(-2px); 
            }
            .demo-info {
                text-align: center;
                margin-top: 25px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 15px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="login-card">
            <div class="login-header">
                <h2>🌱 GreenVerse</h2>
                <p>Enhanced Plant Health System</p>
            </div>
            <form method="POST">
                <div class="form-group">
                    <input type="email" name="email" class="form-control" placeholder="Email Address" value="test@example.com" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" class="form-control" placeholder="Password" value="test" required>
                </div>
                <button type="submit" class="btn">🔑 Login & Start Analyzing</button>
            </form>
            <div class="demo-info">
                <strong>Demo Credentials:</strong><br>
                Email: test@example.com<br>
                Password: test
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(login_template)

@app.route('/plant-analyzer', methods=['GET', 'POST'])
def plant_analyzer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'plant_image' not in request.files:
            return redirect(request.url)
        
        file = request.files['plant_image']
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Generate analysis
            analysis = generate_plant_analysis()
            
            # Save to database
            analysis_id = save_plant_analysis(session['user_id'], f"uploads/{unique_filename}", analysis)
            
            # Return results
            return render_analysis_results(analysis, f"uploads/{unique_filename}")
    
    return render_template_string(ANALYZER_TEMPLATE)

def render_analysis_results(analysis, image_url):
    urgency_color = '#dc3545' if analysis['urgency_level'] == 'High' else '#ffc107' if analysis['urgency_level'] == 'Medium' else '#28a745'
    urgency_icon = '🚨' if analysis['urgency_level'] == 'High' else '⚠️' if analysis['urgency_level'] == 'Medium' else '✅'
    
    symptoms_html = ''.join([f'<li><span class="symptom-bullet">•</span> {symptom}</li>' for symptom in analysis['symptoms']])
    recommendations_html = ''.join([f'<li><span class="rec-bullet">✓</span> {rec}</li>' for rec in analysis['recommendations']])
    prevention_html = ''.join([f'<li><span class="prev-bullet">🛡️</span> {tip}</li>' for tip in analysis['prevention_tips']])
    cure_html = ''.join([f'<li><span class="cure-bullet">💊</span> {cure}</li>' for cure in analysis['cure_suggestions']])
    
    results_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌱 Analysis Results - {analysis['plant_name']}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); 
                min-height: 100vh; 
                color: #333;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; 
                text-align: center; 
                padding: 50px; 
                border-radius: 25px; 
                margin-bottom: 40px;
                box-shadow: 0 15px 35px rgba(40, 167, 69, 0.3);
            }}
            .header h1 {{ 
                font-size: 3rem; 
                margin-bottom: 15px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }}
            .header h2 {{ 
                font-size: 2.2rem; 
                margin-bottom: 10px; 
                opacity: 0.95;
            }}
            .header p {{ 
                font-size: 1.2rem; 
                opacity: 0.9; 
            }}
            .urgency-alert {{ 
                background: {urgency_color}; 
                color: white; 
                padding: 30px; 
                border-radius: 20px; 
                text-align: center; 
                margin-bottom: 40px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }}
            .urgency-alert h3 {{ 
                font-size: 2rem; 
                margin-bottom: 15px; 
            }}
            .urgency-alert p {{ 
                font-size: 1.3rem; 
            }}
            .metrics-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 25px; 
                margin-bottom: 40px; 
            }}
            .metric-card {{ 
                background: white; 
                padding: 30px; 
                border-radius: 20px; 
                text-align: center; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .metric-card:hover {{
                transform: translateY(-5px);
            }}
            .metric-card h4 {{ 
                font-size: 1.3rem; 
                margin-bottom: 15px; 
            }}
            .metric-card h3 {{ 
                font-size: 1.8rem; 
                margin-bottom: 15px; 
            }}
            .progress-bar {{ 
                background: #e9ecef; 
                height: 12px; 
                border-radius: 6px; 
                overflow: hidden; 
                margin: 15px 0; 
            }}
            .progress-fill {{ 
                height: 100%; 
                transition: width 1.5s ease; 
                border-radius: 6px;
            }}
            .card {{ 
                background: white; 
                border-radius: 20px; 
                padding: 35px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
                margin-bottom: 25px; 
            }}
            .section {{ 
                margin-bottom: 35px; 
            }}
            .section h3 {{ 
                color: #28a745; 
                border-bottom: 3px solid #28a745; 
                padding-bottom: 15px; 
                margin-bottom: 25px;
                font-size: 1.8rem;
            }}
            .section ul {{ 
                list-style: none; 
                padding: 0; 
            }}
            .section li {{ 
                padding: 12px 0; 
                border-bottom: 1px solid #eee; 
                display: flex;
                align-items: flex-start;
                font-size: 1.1rem;
                line-height: 1.6;
            }}
            .section li:last-child {{
                border-bottom: none;
            }}
            .symptom-bullet, .rec-bullet, .prev-bullet, .cure-bullet {{
                margin-right: 12px;
                font-weight: bold;
                flex-shrink: 0;
            }}
            .symptom-bullet {{ color: #dc3545; }}
            .rec-bullet {{ color: #28a745; }}
            .prev-bullet {{ color: #17a2b8; }}
            .cure-bullet {{ color: #6f42c1; }}
            .issues-card {{
                border-left: 5px solid #dc3545;
                background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
            }}
            .recovery-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .recovery-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 40px;
                text-align: center;
            }}
            .recovery-item h4 {{
                font-size: 1.3rem;
                margin-bottom: 10px;
                opacity: 0.9;
            }}
            .recovery-item h3 {{
                font-size: 2rem;
            }}
            .care-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
            }}
            .care-item h4 {{
                margin-bottom: 15px;
                font-size: 1.3rem;
            }}
            .care-item p {{
                font-size: 1.1rem;
                line-height: 1.6;
                color: #555;
            }}
            .btn {{ 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; 
                padding: 18px 35px; 
                text-decoration: none; 
                border-radius: 50px; 
                display: inline-block; 
                margin: 15px; 
                font-weight: bold;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                box-shadow: 0 8px 20px rgba(40, 167, 69, 0.3);
            }}
            .btn:hover {{ 
                transform: translateY(-3px); 
                box-shadow: 0 12px 30px rgba(40, 167, 69, 0.4);
            }}
            .btn-secondary {{
                background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
                box-shadow: 0 8px 20px rgba(108, 117, 125, 0.3);
            }}
            .nav-section {{
                text-align: center;
                margin-top: 50px;
                padding: 40px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }}
            .nav-section h3 {{
                color: #28a745;
                margin-bottom: 25px;
                font-size: 2rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌱 Analysis Complete!</h1>
                <h2>{analysis['plant_name']}</h2>
                <p>{analysis['plant_type']} • AI Confidence: {analysis['confidence_score']}%</p>
            </div>
            
            <div class="urgency-alert">
                <h3>{urgency_icon} {analysis['urgency_level']} Priority Action Required</h3>
                <p>Overall Health Score: {int(analysis['overall_health_score'] * 100)}% • Recovery Time: {analysis['recovery_time']}</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h4>💧 Hydration Level</h4>
                    <h3 style="color: #17a2b8;">{analysis['dehydration_level']}</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {int((1-analysis['dehydration_score'])*100)}%; background: linear-gradient(90deg, #17a2b8, #20c997);"></div>
                    </div>
                    <small style="font-size: 1rem; color: #666;">{int((1-analysis['dehydration_score'])*100)}% Hydrated</small>
                </div>
                
                <div class="metric-card">
                    <h4>⚡ Stress Level</h4>
                    <h3 style="color: #ffc107;">{analysis['stress_level']}</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {int(analysis['stress_score']*100)}%; background: linear-gradient(90deg, #ffc107, #fd7e14);"></div>
                    </div>
                    <small style="font-size: 1rem; color: #666;">{int(analysis['stress_score']*100)}% Stress Level</small>
                </div>
                
                <div class="metric-card">
                    <h4>☀️ Sunlight Exposure</h4>
                    <h3 style="color: #fd7e14;">{analysis['sunlight_exposure']}</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {int(analysis['sunlight_score']*100)}%; background: linear-gradient(90deg, #fd7e14, #ffc107);"></div>
                    </div>
                    <small style="font-size: 1rem; color: #666;">{int(analysis['sunlight_score']*100)}% Optimal</small>
                </div>
            </div>
            
            {f'''
            <div class="card issues-card">
                <h3 style="color: #dc3545;">🚨 Health Issues Detected</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-top: 20px;">
                    {f'<div style="padding: 20px; background: rgba(220, 53, 69, 0.1); border-radius: 15px;"><strong style="color: #dc3545;">Disease Detected:</strong><br><span style="font-size: 1.2rem; color: #721c24;">{analysis["disease_detected"]}</span></div>' if analysis["disease_detected"] != "None" else ""}
                    {f'<div style="padding: 20px; background: rgba(220, 53, 69, 0.1); border-radius: 15px;"><strong style="color: #dc3545;">Pest Detected:</strong><br><span style="font-size: 1.2rem; color: #721c24;">{analysis["pest_detected"]}</span></div>' if analysis["pest_detected"] != "None" else ""}
                </div>
            </div>
            ''' if analysis["disease_detected"] != "None" or analysis["pest_detected"] != "None" else ""}
            
            <div class="card">
                <div class="section">
                    <h3>🔍 Observed Symptoms</h3>
                    <ul>{symptoms_html}</ul>
                </div>
                
                <div class="section">
                    <h3>💡 Immediate Action Plan</h3>
                    <ul>{recommendations_html}</ul>
                </div>
                
                <div class="section">
                    <h3>🛡️ Prevention Strategy</h3>
                    <ul>{prevention_html}</ul>
                </div>
                
                <div class="section">
                    <h3>💊 Treatment & Recovery Plan</h3>
                    <ul>{cure_html}</ul>
                </div>
            </div>
            
            <div class="card recovery-card">
                <div class="recovery-grid">
                    <div class="recovery-item">
                        <h4>⏰ Expected Recovery</h4>
                        <h3>{analysis['recovery_time']}</h3>
                    </div>
                    <div class="recovery-item">
                        <h4>📅 Follow-up Date</h4>
                        <h3>{analysis['follow_up_date']}</h3>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3 style="color: #28a745; text-align: center; margin-bottom: 30px;">🌱 Ongoing Care Schedule</h3>
                <div class="care-grid">
                    <div class="care-item">
                        <h4 style="color: #17a2b8;">💧 Watering Schedule</h4>
                        <p>{analysis['watering_schedule']}</p>
                    </div>
                    <div class="care-item">
                        <h4 style="color: #28a745;">🌱 Fertilizer Plan</h4>
                        <p>{analysis['fertilizer_recommendation']}</p>
                    </div>
                </div>
            </div>
            
            <div class="nav-section">
                <h3>Continue Your Plant Health Journey</h3>
                <a href="/plant-analyzer" class="btn">🔬 Analyze Another Plant</a>
                <a href="/plant-history" class="btn">📊 View Complete History</a>
                <a href="/" class="btn btn-secondary">🏠 Home</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(results_template)

@app.route('/plant-history')
def plant_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    analyses = get_plant_history(session['user_id'])
    
    # Parse JSON fields
    for analysis in analyses:
        try:
            if analysis['symptoms']:
                analysis['symptoms'] = json.loads(analysis['symptoms'])
            if analysis['recommendations']:
                analysis['recommendations'] = json.loads(analysis['recommendations'])
            if analysis['prevention_tips']:
                analysis['prevention_tips'] = json.loads(analysis['prevention_tips'])
            if analysis['cure_suggestions']:
                analysis['cure_suggestions'] = json.loads(analysis['cure_suggestions'])
        except:
            pass
    
    if not analyses:
        empty_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>📊 Plant Analysis History</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); 
                    min-height: 100vh; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                }
                .empty-state { 
                    text-align: center; 
                    background: white; 
                    padding: 80px; 
                    border-radius: 25px; 
                    box-shadow: 0 15px 35px rgba(0,0,0,0.1); 
                    max-width: 600px;
                }
                .empty-icon {
                    font-size: 5rem;
                    margin-bottom: 30px;
                    display: block;
                    animation: float 3s ease-in-out infinite;
                }
                @keyframes float {
                    0%, 100% { transform: translateY(0px); }
                    50% { transform: translateY(-10px); }
                }
                .empty-state h2 {
                    color: #28a745;
                    font-size: 2.5rem;
                    margin-bottom: 20px;
                }
                .empty-state p {
                    color: #666;
                    font-size: 1.3rem;
                    margin-bottom: 40px;
                    line-height: 1.6;
                }
                .btn { 
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                    color: white; 
                    padding: 20px 40px; 
                    text-decoration: none; 
                    border-radius: 50px; 
                    display: inline-block; 
                    margin: 15px; 
                    font-size: 1.2rem;
                    font-weight: bold;
                    transition: all 0.3s ease;
                    box-shadow: 0 8px 20px rgba(40, 167, 69, 0.3);
                }
                .btn:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 12px 30px rgba(40, 167, 69, 0.4);
                }
                .btn-secondary {
                    background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
                    box-shadow: 0 8px 20px rgba(108, 117, 125, 0.3);
                }
            </style>
        </head>
        <body>
            <div class="empty-state">
                <span class="empty-icon">🌱</span>
                <h2>No Plant Analyses Yet</h2>
                <p>Start analyzing your plants to build your comprehensive health history and track their progress over time!</p>
                <a href="/plant-analyzer" class="btn">🔬 Analyze Your First Plant</a>
                <a href="/" class="btn btn-secondary">🏠 Home</a>
            </div>
        </body>
        </html>
        '''
        return render_template_string(empty_template)
    
    # Generate history cards
    history_cards = []
    for analysis in analyses:
        urgency_color = '#dc3545' if analysis['urgency_level'] == 'High' else '#ffc107' if analysis['urgency_level'] == 'Medium' else '#28a745'
        
        # Safely get symptoms and recommendations
        symptoms = analysis.get('symptoms', [])
        recommendations = analysis.get('recommendations', [])
        cure_suggestions = analysis.get('cure_suggestions', [])
        
        if isinstance(symptoms, str):
            try:
                symptoms = json.loads(symptoms)
            except:
                symptoms = [symptoms]
        
        if isinstance(recommendations, str):
            try:
                recommendations = json.loads(recommendations)
            except:
                recommendations = [recommendations]
                
        if isinstance(cure_suggestions, str):
            try:
                cure_suggestions = json.loads(cure_suggestions)
            except:
                cure_suggestions = [cure_suggestions]
        
        history_cards.append(f'''
        <div class="history-card">
            <div class="card-header">
                <div class="plant-info">
                    <h4>{analysis['plant_name']}</h4>
                    <span class="plant-type">{analysis['plant_type']}</span>
                </div>
                <span class="badge" style="background: {urgency_color};">{analysis['urgency_level']} Priority</span>
            </div>
            <div class="card-body">
                <div class="metrics">
                    <div class="metric">
                        <span class="metric-label">Health Score</span>
                        <span class="metric-value" style="color: {urgency_color};">{int(analysis['overall_health_score'] * 100)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Hydration</span>
                        <span class="metric-value">{analysis['dehydration_level']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Stress</span>
                        <span class="metric-value">{analysis['stress_level']}</span>
                    </div>
                </div>
                
                <div class="analysis-details">
                    <div class="detail-section">
                        <h6>🔍 Key Symptoms:</h6>
                        <ul>{''.join([f'<li>{symptom}</li>' for symptom in symptoms[:3]])}</ul>
                    </div>
                    
                    <div class="detail-section">
                        <h6>💡 Recommendations:</h6>
                        <ul>{''.join([f'<li>{rec}</li>' for rec in recommendations[:3]])}</ul>
                    </div>
                    
                    <div class="detail-section">
                        <h6>💊 Treatment Plan:</h6>
                        <ul>{''.join([f'<li>{cure}</li>' for cure in cure_suggestions[:2]])}</ul>
                    </div>
                </div>
                
                <div class="card-footer">
                    <div class="footer-info">
                        <span>📅 {analysis['created_at'].split()[0]}</span>
                        <span>⏰ Recovery: {analysis['recovery_time']}</span>
                        <span>🎯 Confidence: {analysis['confidence_score']}%</span>
                    </div>
                </div>
            </div>
        </div>
        ''')
    
    history_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📊 Plant Analysis History - Enhanced Tracking</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); 
                min-height: 100vh; 
                color: #333;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; 
                text-align: center; 
                padding: 50px; 
                border-radius: 25px; 
                margin-bottom: 40px;
                box-shadow: 0 15px 35px rgba(40, 167, 69, 0.3);
            }}
            .header h1 {{ 
                font-size: 3rem; 
                margin-bottom: 15px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }}
            .header p {{ 
                font-size: 1.3rem; 
                opacity: 0.95; 
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 25px; 
                margin-bottom: 40px; 
            }}
            .stat-card {{ 
                background: white; 
                padding: 30px; 
                border-radius: 20px; 
                text-align: center; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            .stat-card h3 {{ 
                font-size: 2.5rem; 
                margin-bottom: 10px; 
            }}
            .stat-card p {{ 
                color: #666; 
                font-size: 1.1rem;
            }}
            .history-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); 
                gap: 25px; 
            }}
            .history-card {{ 
                background: white; 
                border-radius: 20px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
                overflow: hidden;
                transition: transform 0.3s ease;
            }}
            .history-card:hover {{
                transform: translateY(-5px);
            }}
            .card-header {{ 
                padding: 25px; 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
            }}
            .plant-info h4 {{
                font-size: 1.4rem;
                color: #28a745;
                margin-bottom: 5px;
            }}
            .plant-type {{
                color: #666;
                font-size: 0.9rem;
            }}
            .card-body {{ 
                padding: 25px; 
            }}
            .card-footer {{ 
                padding: 20px 25px; 
                background: #f8f9fa; 
                border-top: 1px solid #eee; 
            }}
            .badge {{ 
                padding: 8px 15px; 
                border-radius: 20px; 
                color: white; 
                font-size: 0.85rem; 
                font-weight: bold;
            }}
            .metrics {{ 
                display: grid; 
                grid-template-columns: repeat(3, 1fr); 
                gap: 20px; 
                margin-bottom: 25px; 
            }}
            .metric {{ 
                text-align: center; 
                padding: 15px;
                background: #f8f9fa;
                border-radius: 15px;
            }}
            .metric-label {{ 
                display: block; 
                font-size: 0.85rem; 
                color: #666; 
                margin-bottom: 5px;
            }}
            .metric-value {{ 
                display: block; 
                font-weight: bold; 
                font-size: 1.1rem;
            }}
            .detail-section {{ 
                margin-bottom: 20px; 
            }}
            .detail-section h6 {{ 
                color: #28a745; 
                margin-bottom: 10px; 
                font-size: 1rem;
            }}
            .detail-section ul {{ 
                list-style: none; 
                padding: 0; 
            }}
            .detail-section li {{ 
                padding: 5px 0; 
                font-size: 0.9rem; 
                color: #666;
                border-bottom: 1px solid #f0f0f0;
            }}
            .detail-section li:last-child {{
                border-bottom: none;
            }}
            .footer-info {{
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 15px;
            }}
            .footer-info span {{
                font-size: 0.85rem;
                color: #666;
                background: white;
                padding: 5px 10px;
                border-radius: 10px;
            }}
            .btn {{ 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; 
                padding: 18px 35px; 
                text-decoration: none; 
                border-radius: 50px; 
                display: inline-block; 
                margin: 15px; 
                font-weight: bold;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                box-shadow: 0 8px 20px rgba(40, 167, 69, 0.3);
            }}
            .btn:hover {{ 
                transform: translateY(-3px); 
                box-shadow: 0 12px 30px rgba(40, 167, 69, 0.4);
            }}
            .btn-secondary {{
                background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
                box-shadow: 0 8px 20px rgba(108, 117, 125, 0.3);
            }}
            .nav-section {{
                text-align: center;
                margin-top: 50px;
                padding: 40px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }}
            .nav-section h3 {{
                color: #28a745;
                margin-bottom: 25px;
                font-size: 2rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Plant Analysis History</h1>
                <p>Track your plant health journey and monitor improvements over time</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3 style="color: #28a745;">{len(analyses)}</h3>
                    <p>Total Analyses</p>
                </div>
                <div class="stat-card">
                    <h3 style="color: #28a745;">{len([a for a in analyses if a['urgency_level'] == 'Low'])}</h3>
                    <p>Healthy Plants</p>
                </div>
                <div class="stat-card">
                    <h3 style="color: #ffc107;">{len([a for a in analyses if a['urgency_level'] == 'Medium'])}</h3>
                    <p>Need Attention</p>
                </div>
                <div class="stat-card">
                    <h3 style="color: #dc3545;">{len([a for a in analyses if a['urgency_level'] == 'High'])}</h3>
                    <p>Critical Care</p>
                </div>
            </div>
            
            <div class="history-grid">
                {''.join(history_cards)}
            </div>
            
            <div class="nav-section">
                <h3>Continue Your Plant Health Journey</h3>
                <a href="/plant-analyzer" class="btn">🔬 New Analysis</a>
                <a href="/" class="btn btn-secondary">🏠 Home</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(history_template)

@app.route('/quiz')
def quiz_home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    quiz_home_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Plant Knowledge Quiz - Choose Your Level</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); 
                min-height: 100vh; 
                color: #333;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { 
                text-align: center; 
                color: white; 
                margin-bottom: 50px; 
                padding: 60px 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 25px;
                backdrop-filter: blur(10px);
            }
            .header h1 { 
                font-size: 3.5rem; 
                margin-bottom: 20px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p { 
                font-size: 1.3rem; 
                opacity: 0.9; 
                max-width: 600px;
                margin: 0 auto;
            }
            .levels-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
                gap: 30px; 
                margin-bottom: 50px; 
            }
            .level-card { 
                background: white; 
                border-radius: 25px; 
                padding: 40px; 
                text-align: center; 
                box-shadow: 0 15px 35px rgba(0,0,0,0.2); 
                transition: transform 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            .level-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 5px;
                background: var(--level-color);
            }
            .level-card:hover { 
                transform: translateY(-10px); 
            }
            .level-icon { 
                font-size: 4rem; 
                margin-bottom: 20px; 
                display: block;
            }
            .level-title { 
                font-size: 2rem; 
                margin-bottom: 15px; 
                font-weight: bold;
                color: var(--level-color);
            }
            .level-description { 
                color: #666; 
                margin-bottom: 20px; 
                line-height: 1.6;
                font-size: 1.1rem;
            }
            .level-details {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 25px;
            }
            .level-details h4 {
                color: var(--level-color);
                margin-bottom: 10px;
            }
            .level-details ul {
                list-style: none;
                padding: 0;
            }
            .level-details li {
                padding: 5px 0;
                color: #666;
            }
            .btn { 
                background: linear-gradient(135deg, var(--level-color), var(--level-color-dark)); 
                color: white; 
                padding: 18px 35px; 
                text-decoration: none; 
                border-radius: 50px; 
                display: inline-block; 
                font-weight: bold; 
                font-size: 1.1rem;
                transition: all 0.3s ease;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            }
            .btn:hover { 
                transform: translateY(-3px); 
                box-shadow: 0 12px 30px rgba(0,0,0,0.4);
            }
            .simple { --level-color: #28a745; --level-color-dark: #20c997; }
            .hard { --level-color: #ffc107; --level-color-dark: #fd7e14; }
            .hardest { --level-color: #dc3545; --level-color-dark: #c82333; }
            .nav-section {
                text-align: center;
                margin-top: 40px;
            }
            .btn-secondary {
                background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
                box-shadow: 0 8px 20px rgba(108, 117, 125, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Plant Knowledge Quiz</h1>
                <p>Test your plant expertise, earn beautiful flower titles, and unlock stunning rewards!</p>
            </div>
            
            <div class="levels-grid">
                <div class="level-card simple">
                    <span class="level-icon">🌱</span>
                    <h3 class="level-title">Simple Level</h3>
                    <p class="level-description">Perfect for beginners and plant enthusiasts starting their journey</p>
                    <div class="level-details">
                        <h4>What to Expect:</h4>
                        <ul>
                            <li>• Basic plant biology questions</li>
                            <li>• Common houseplant care</li>
                            <li>• Simple gardening concepts</li>
                            <li>• 10 questions per round</li>
                        </ul>
                    </div>
                    <a href="/quiz/simple" class="btn">🌱 Start Simple Quiz</a>
                </div>
                
                <div class="level-card hard">
                    <span class="level-icon">🌿</span>
                    <h3 class="level-title">Hard Level</h3>
                    <p class="level-description">For experienced gardeners and plant science students</p>
                    <div class="level-details">
                        <h4>What to Expect:</h4>
                        <ul>
                            <li>• Plant taxonomy and families</li>
                            <li>• Disease identification</li>
                            <li>• Advanced care techniques</li>
                            <li>• Botanical terminology</li>
                        </ul>
                    </div>
                    <a href="/quiz/hard" class="btn">🌿 Start Hard Quiz</a>
                </div>
                
                <div class="level-card hardest">
                    <span class="level-icon">🌳</span>
                    <h3 class="level-title">Hardest Level</h3>
                    <p class="level-description">Ultimate challenge for botanists and plant experts</p>
                    <div class="level-details">
                        <h4>What to Expect:</h4>
                        <ul>
                            <li>• Advanced plant physiology</li>
                            <li>• Molecular biology concepts</li>
                            <li>• Research-level questions</li>
                            <li>• Expert botanical knowledge</li>
                        </ul>
                    </div>
                    <a href="/quiz/hardest" class="btn">🌳 Start Hardest Quiz</a>
                </div>
            </div>
            
            <div class="nav-section">
                <a href="/achievements" class="btn btn-secondary">🏆 View My Achievements</a>
                <a href="/" class="btn btn-secondary">🏠 Home</a>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(quiz_home_template)

@app.route('/quiz/<level>')
def quiz_level(level):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if level not in QUIZ_QUESTIONS:
        return redirect(url_for('quiz_home'))
    
    questions = random.sample(QUIZ_QUESTIONS[level], 10)
    session['quiz_questions'] = questions
    session['quiz_level'] = level
    session['quiz_score'] = 0
    session['current_question'] = 0
    
    return redirect(url_for('quiz_question'))

@app.route('/quiz-question')
def quiz_question():
    if 'user_id' not in session or 'quiz_questions' not in session:
        return redirect(url_for('quiz_home'))
    
    current_q = session.get('current_question', 0)
    questions = session['quiz_questions']
    level = session['quiz_level']
    
    if current_q >= len(questions):
        return redirect(url_for('quiz_results'))
    
    question = questions[current_q]
    
    level_colors = {
        'simple': {'primary': '#28a745', 'secondary': '#20c997'},
        'hard': {'primary': '#ffc107', 'secondary': '#fd7e14'},
        'hardest': {'primary': '#dc3545', 'secondary': '#c82333'}
    }
    
    colors = level_colors[level]
    
    quiz_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Quiz Question {current_q + 1}/10</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%); 
                min-height: 100vh; 
                color: #333;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .quiz-container {{ 
                max-width: 800px; 
                width: 100%;
                margin: 20px;
                background: white; 
                border-radius: 25px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.2); 
                overflow: hidden;
            }}
            .quiz-header {{ 
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%); 
                color: white; 
                padding: 30px; 
                text-align: center; 
            }}
            .quiz-header h1 {{ 
                font-size: 2rem; 
                margin-bottom: 10px; 
            }}
            .progress-bar {{ 
                background: rgba(255,255,255,0.3); 
                height: 8px; 
                border-radius: 4px; 
                overflow: hidden; 
                margin-top: 20px;
            }}
            .progress-fill {{ 
                background: white; 
                height: 100%; 
                width: {(current_q + 1) * 10}%; 
                transition: width 0.3s ease;
            }}
            .quiz-body {{ 
                padding: 50px; 
            }}
            .question {{ 
                font-size: 1.5rem; 
                margin-bottom: 40px; 
                line-height: 1.6;
                color: #333;
                text-align: center;
            }}
            .options {{ 
                display: grid; 
                gap: 20px; 
            }}
            .option {{ 
                background: #f8f9fa; 
                border: 3px solid #e9ecef; 
                border-radius: 15px; 
                padding: 20px; 
                cursor: pointer; 
                transition: all 0.3s ease;
                font-size: 1.1rem;
                text-align: left;
            }}
            .option:hover {{ 
                border-color: {colors['primary']}; 
                background: #f0f8ff;
                transform: translateY(-2px);
            }}
            .option.selected {{ 
                border-color: {colors['primary']}; 
                background: linear-gradient(135deg, {colors['primary']}20, {colors['secondary']}20);
            }}
            .quiz-footer {{ 
                padding: 30px 50px; 
                background: #f8f9fa; 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
            }}
            .btn {{ 
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%); 
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 50px; 
                font-size: 1.1rem; 
                cursor: pointer; 
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            .btn:hover {{ 
                transform: translateY(-2px); 
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            }}
            .btn:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }}
            .score-display {{
                font-size: 1.1rem;
                color: #666;
            }}
        </style>
        <script>
            let selectedOption = null;
            
            function selectOption(index) {{
                // Remove previous selection
                document.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
                
                // Add selection to clicked option
                document.querySelectorAll('.option')[index].classList.add('selected');
                selectedOption = index;
                
                // Enable submit button
                document.getElementById('submitBtn').disabled = false;
            }}
            
            function submitAnswer() {{
                if (selectedOption !== null) {{
                    document.getElementById('answerForm').submit();
                }}
            }}
        </script>
    </head>
    <body>
        <div class="quiz-container">
            <div class="quiz-header">
                <h1>🧠 {level.title()} Level Quiz</h1>
                <p>Question {current_q + 1} of 10</p>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
            
            <div class="quiz-body">
                <div class="question">{question['question']}</div>
                
                <form id="answerForm" method="POST" action="/quiz-answer">
                    <div class="options">
                        {chr(10).join([f'<div class="option" onclick="selectOption({i})"><strong>{chr(65 + i)}.</strong> {option}</div>' for i, option in enumerate(question['options'])])}
                    </div>
                    <input type="hidden" name="selected_option" id="selectedOption">
                    <input type="hidden" name="correct_answer" value="{question['correct']}">
                </form>
            </div>
            
            <div class="quiz-footer">
                <div class="score-display">
                    Score: {session.get('quiz_score', 0)}/10
                </div>
                <button id="submitBtn" class="btn" onclick="submitAnswer()" disabled>
                    {('Next Question' if current_q < 9 else 'Finish Quiz')} →
                </button>
            </div>
        </div>
        
        <script>
            function selectOption(index) {{
                document.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
                document.querySelectorAll('.option')[index].classList.add('selected');
                document.getElementById('selectedOption').value = index;
                document.getElementById('submitBtn').disabled = false;
            }}
        </script>
    </body>
    </html>
    '''
    
    return render_template_string(quiz_template)

@app.route('/quiz-answer', methods=['POST'])
def quiz_answer():
    if 'user_id' not in session or 'quiz_questions' not in session:
        return redirect(url_for('quiz_home'))
    
    selected = int(request.form.get('selected_option', -1))
    correct = int(request.form.get('correct_answer', -1))
    
    if selected == correct:
        session['quiz_score'] = session.get('quiz_score', 0) + 1
    
    session['current_question'] = session.get('current_question', 0) + 1
    
    return redirect(url_for('quiz_question'))

@app.route('/quiz-results')
def quiz_results():
    if 'user_id' not in session or 'quiz_level' not in session:
        return redirect(url_for('quiz_home'))
    
    score = session.get('quiz_score', 0)
    level = session['quiz_level']
    user_id = session['user_id']
    
    # Save quiz attempt
    save_quiz_attempt(user_id, level, score, 10)
    
    # Check if user earned a reward (perfect score)
    reward_earned = False
    flower_title = ""
    flower_image = ""
    
    if score == 10:
        reward_earned = True
        flower_data = random.choice(FLOWER_TITLES)
        flower_title = flower_data['title']
        flower_image = get_flower_image(flower_data['flower'])
        
        # Save achievement
        save_achievement(user_id, flower_title, flower_image, level)
    
    level_colors = {
        'simple': {'primary': '#28a745', 'secondary': '#20c997'},
        'hard': {'primary': '#ffc107', 'secondary': '#fd7e14'},
        'hardest': {'primary': '#dc3545', 'secondary': '#c82333'}
    }
    
    colors = level_colors[level]
    
    results_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏆 Quiz Results - {score}/10</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%); 
                min-height: 100vh; 
                color: #333;
            }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
            .results-card {{ 
                background: white; 
                border-radius: 25px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.2); 
                overflow: hidden;
                margin-bottom: 30px;
            }}
            .results-header {{ 
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%); 
                color: white; 
                padding: 50px; 
                text-align: center; 
            }}
            .results-header h1 {{ 
                font-size: 3rem; 
                margin-bottom: 20px; 
            }}
            .score-display {{ 
                font-size: 4rem; 
                font-weight: bold; 
                margin: 20px 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .results-body {{ 
                padding: 50px; 
                text-align: center; 
            }}
            .performance-message {{ 
                font-size: 1.5rem; 
                margin-bottom: 30px; 
                color: #333;
            }}
            .reward-section {{ 
                background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); 
                border-radius: 20px; 
                padding: 40px; 
                margin: 30px 0;
                border: 3px solid #f39c12;
            }}
            .reward-section h2 {{ 
                color: #d35400; 
                font-size: 2.5rem; 
                margin-bottom: 20px;
                animation: bounce 2s infinite;
            }}
            @keyframes bounce {{
                0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
                40% {{ transform: translateY(-10px); }}
                60% {{ transform: translateY(-5px); }}
            }}
            .flower-image {{ 
                width: 300px; 
                height: 300px; 
                border-radius: 20px; 
                object-fit: cover; 
                margin: 20px 0;
                box-shadow: 0 15px 30px rgba(0,0,0,0.3);
            }}
            .flower-title {{ 
                font-size: 2rem; 
                color: #d35400; 
                font-weight: bold; 
                margin-top: 20px;
            }}
            .btn {{ 
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%); 
                color: white; 
                padding: 18px 35px; 
                text-decoration: none; 
                border-radius: 50px; 
                display: inline-block; 
                margin: 15px; 
                font-weight: bold;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            }}
            .btn:hover {{ 
                transform: translateY(-3px); 
                box-shadow: 0 12px 30px rgba(0,0,0,0.4);
            }}
            .btn-secondary {{
                background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            }}
            .btn-gold {{
                background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
                color: #d35400;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="results-card">
                <div class="results-header">
                    <h1>🏆 Quiz Complete!</h1>
                    <div class="score-display">{score}/10</div>
                    <p>{level.title()} Level</p>
                </div>
                
                <div class="results-body">
                    <div class="performance-message">
                        {f"🎉 Perfect Score! Outstanding knowledge!" if score == 10 else 
                         f"🌟 Excellent work! Great plant knowledge!" if score >= 8 else
                         f"👍 Good job! Keep learning about plants!" if score >= 6 else
                         f"📚 Keep studying! You're on the right track!" if score >= 4 else
                         f"🌱 Don't give up! Every expert was once a beginner!"}
                    </div>
                    
                    {f'''
                    <div class="reward-section">
                        <h2>🎊 CONGRATULATIONS! 🎊</h2>
                        <p style="font-size: 1.3rem; color: #d35400; margin-bottom: 20px;">
                            You've earned a new flower title!
                        </p>
                        <img src="{flower_image}" alt="{flower_title}" class="flower-image">
                        <div class="flower-title">🌸 {flower_title} 🌸</div>
                        <p style="margin-top: 20px; font-size: 1.1rem; color: #d35400;">
                            This beautiful title has been added to your achievements!
                        </p>
                    </div>
                    ''' if reward_earned else f'''
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 15px; margin: 20px 0;">
                        <h3 style="color: {colors['primary']}; margin-bottom: 15px;">💡 Want to earn a flower title?</h3>
                        <p style="font-size: 1.1rem; color: #666;">
                            Get a perfect score (10/10) to unlock a beautiful flower title and image!
                        </p>
                    </div>
                    '''}
                    
                    <div style="margin-top: 40px;">
                        <a href="/quiz/{level}" class="btn">🔄 Try Again</a>
                        <a href="/quiz" class="btn btn-secondary">📚 Choose Different Level</a>
                        <a href="/achievements" class="btn btn-gold">🏆 View Achievements</a>
                        <a href="/" class="btn btn-secondary">🏠 Home</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    
    # Clear quiz session data
    for key in ['quiz_questions', 'quiz_level', 'quiz_score', 'current_question']:
        session.pop(key, None)
    
    return render_template_string(results_template)

@app.route('/achievements')
def achievements():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_achievements = get_user_achievements(session['user_id'])
    
    # Get quiz statistics
    conn = sqlite3.connect('new_greenverse.db')
    conn.row_factory = sqlite3.Row
    quiz_stats = conn.execute('''
        SELECT level, COUNT(*) as attempts, AVG(score) as avg_score, MAX(score) as best_score
        FROM quiz_attempts 
        WHERE user_id = ? 
        GROUP BY level
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    if not user_achievements and not quiz_stats:
        empty_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>🏆 My Achievements</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); 
                    min-height: 100vh; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                }
                .empty-state { 
                    text-align: center; 
                    background: white; 
                    padding: 80px; 
                    border-radius: 25px; 
                    box-shadow: 0 15px 35px rgba(0,0,0,0.2); 
                    max-width: 600px;
                }
                .empty-icon {
                    font-size: 5rem;
                    margin-bottom: 30px;
                    display: block;
                }
                .empty-state h2 {
                    color: #6f42c1;
                    font-size: 2.5rem;
                    margin-bottom: 20px;
                }
                .empty-state p {
                    color: #666;
                    font-size: 1.3rem;
                    margin-bottom: 40px;
                    line-height: 1.6;
                }
                .btn { 
                    background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); 
                    color: white; 
                    padding: 20px 40px; 
                    text-decoration: none; 
                    border-radius: 50px; 
                    display: inline-block; 
                    margin: 15px; 
                    font-size: 1.2rem;
                    font-weight: bold;
                    transition: all 0.3s ease;
                }
                .btn:hover {
                    transform: translateY(-3px);
                }
            </style>
        </head>
        <body>
            <div class="empty-state">
                <span class="empty-icon">🏆</span>
                <h2>No Achievements Yet</h2>
                <p>Take quizzes and get perfect scores to earn beautiful flower titles and unlock stunning images!</p>
                <a href="/quiz" class="btn">🧠 Take Your First Quiz</a>
                <a href="/" class="btn" style="background: linear-gradient(135deg, #6c757d 0%, #495057 100%);">🏠 Home</a>
            </div>
        </body>
        </html>
        '''
        return render_template_string(empty_template)
    
    # Generate achievement cards
    achievement_cards = []
    for achievement in user_achievements:
        achievement_cards.append(f'''
        <div class="achievement-card">
            <div class="achievement-image">
                <img src="{achievement['flower_image_url']}" alt="{achievement['flower_title']}">
            </div>
            <div class="achievement-content">
                <h3 class="achievement-title">🌸 {achievement['flower_title']} 🌸</h3>
                <p class="achievement-level">Earned from {achievement['level'].title()} Level Quiz</p>
                <p class="achievement-date">📅 {achievement['earned_at'].split()[0]}</p>
            </div>
        </div>
        ''')
    
    # Generate stats cards
    stats_cards = []
    for stat in quiz_stats:
        level_colors = {
            'simple': '#28a745',
            'hard': '#ffc107', 
            'hardest': '#dc3545'
        }
        color = level_colors.get(stat['level'], '#6c757d')
        
        stats_cards.append(f'''
        <div class="stat-card" style="border-left: 5px solid {color};">
            <h4 style="color: {color};">{stat['level'].title()} Level</h4>
            <div class="stat-grid">
                <div class="stat-item">
                    <span class="stat-number">{stat['attempts']}</span>
                    <span class="stat-label">Attempts</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{int(stat['avg_score'])}</span>
                    <span class="stat-label">Avg Score</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{stat['best_score']}</span>
                    <span class="stat-label">Best Score</span>
                </div>
            </div>
        </div>
        ''')
    
    achievements_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏆 My Achievements - Flower Collection</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); 
                min-height: 100vh; 
                color: #333;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                text-align: center; 
                color: white; 
                margin-bottom: 50px; 
                padding: 60px 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 25px;
                backdrop-filter: blur(10px);
            }}
            .header h1 {{ 
                font-size: 3.5rem; 
                margin-bottom: 20px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .header p {{ 
                font-size: 1.3rem; 
                opacity: 0.9; 
            }}
            .section {{ 
                margin-bottom: 50px; 
            }}
            .section h2 {{ 
                color: white; 
                font-size: 2.5rem; 
                margin-bottom: 30px; 
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .achievements-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
                gap: 30px; 
            }}
            .achievement-card {{ 
                background: white; 
                border-radius: 25px; 
                overflow: hidden; 
                box-shadow: 0 15px 35px rgba(0,0,0,0.2); 
                transition: transform 0.3s ease;
            }}
            .achievement-card:hover {{ 
                transform: translateY(-10px); 
            }}
            .achievement-image {{ 
                height: 250px; 
                overflow: hidden; 
            }}
            .achievement-image img {{ 
                width: 100%; 
                height: 100%; 
                object-fit: cover; 
            }}
            .achievement-content {{ 
                padding: 30px; 
                text-align: center; 
            }}
            .achievement-title {{ 
                font-size: 1.8rem; 
                color: #6f42c1; 
                margin-bottom: 15px; 
                font-weight: bold;
            }}
            .achievement-level {{ 
                color: #666; 
                margin-bottom: 10px; 
                font-size: 1.1rem;
            }}
            .achievement-date {{ 
                color: #999; 
                font-size: 0.9rem; 
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 25px; 
            }}
            .stat-card {{ 
                background: white; 
                border-radius: 20px; 
                padding: 30px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            .stat-card h4 {{ 
                font-size: 1.5rem; 
                margin-bottom: 20px; 
            }}
            .stat-grid {{ 
                display: grid; 
                grid-template-columns: repeat(3, 1fr); 
                gap: 20px; 
            }}
            .stat-item {{ 
                text-align: center; 
            }}
            .stat-number {{ 
                display: block; 
                font-size: 2rem; 
                font-weight: bold; 
                color: #333;
            }}
            .stat-label {{ 
                display: block; 
                font-size: 0.9rem; 
                color: #666; 
                margin-top: 5px;
            }}
            .btn {{ 
                background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); 
                color: white; 
                padding: 18px 35px; 
                text-decoration: none; 
                border-radius: 50px; 
                display: inline-block; 
                margin: 15px; 
                font-weight: bold;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            }}
            .btn:hover {{ 
                transform: translateY(-3px); 
                box-shadow: 0 12px 30px rgba(0,0,0,0.4);
            }}
            .btn-secondary {{
                background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            }}
            .nav-section {{
                text-align: center;
                margin-top: 50px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏆 My Achievements</h1>
                <p>Your beautiful flower collection and quiz statistics</p>
            </div>
            
            {f'''
            <div class="section">
                <h2>🌸 Flower Titles Collection</h2>
                <div class="achievements-grid">
                    {''.join(achievement_cards)}
                </div>
            </div>
            ''' if achievement_cards else ''}
            
            {f'''
            <div class="section">
                <h2>📊 Quiz Statistics</h2>
                <div class="stats-grid">
                    {''.join(stats_cards)}
                </div>
            </div>
            ''' if stats_cards else ''}
            
            <div class="nav-section">
                <a href="/quiz" class="btn">🧠 Take More Quizzes</a>
                <a href="/" class="btn btn-secondary">🏠 Home</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(achievements_template)

# Social Media Routes
@app.route('/social-feed')
def social_feed():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    posts = get_social_feed(session['user_id'])

    social_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌱 GreenVerse Social Feed</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
                padding: 40px 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            .post-form {
                background: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }
            .post-card {
                background: white;
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .post-card:hover { transform: translateY(-5px); }
            .post-header {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }
            .user-avatar {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: #28a745;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                margin-right: 15px;
            }
            .post-content { margin-bottom: 15px; line-height: 1.6; }
            .post-actions {
                display: flex;
                gap: 20px;
                padding-top: 15px;
                border-top: 1px solid #eee;
            }
            .action-btn {
                background: none;
                border: none;
                color: #666;
                cursor: pointer;
                padding: 8px 15px;
                border-radius: 20px;
                transition: all 0.3s ease;
            }
            .action-btn:hover { background: #f8f9fa; color: #28a745; }
            .action-btn.liked { color: #e74c3c; }
            .form-control {
                width: 100%;
                padding: 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 1rem;
                margin-bottom: 15px;
            }
            .btn {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn:hover { transform: translateY(-2px); }
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
            }
        </style>
    </head>
    <body>
        <div class="notification" id="notification"></div>

        <div class="container">
            <div class="header">
                <h1>🌱 Social Feed</h1>
                <p>Share your plant journey with the community</p>
            </div>

            <div class="post-form">
                <h3>Share Something</h3>
                <form id="postForm">
                    <input type="text" class="form-control" id="postTitle" placeholder="Post title (optional)">
                    <textarea class="form-control" id="postContent" placeholder="What's growing in your garden?" rows="4" required></textarea>
                    <input type="text" class="form-control" id="postTags" placeholder="Tags (e.g., #succulents #indoor)">
                    <button type="submit" class="btn">📝 Share Post</button>
                </form>
            </div>

            <div id="postsContainer">
                <!-- Posts will be loaded here -->
            </div>
        </div>

        <script>
            const socket = io();

            // Join social feed room
            socket.emit('join_feed');

            // Handle new posts
            socket.on('new_post', function(data) {
                showNotification('New post from ' + data.user_id);
                loadPosts();
            });

            // Handle post likes
            socket.on('post_liked', function(data) {
                updateLikeCount(data.post_id, data.likes_count);
            });

            // Handle new comments
            socket.on('new_comment', function(data) {
                addCommentToPost(data.post_id, data);
            });

            // Submit new post
            document.getElementById('postForm').addEventListener('submit', function(e) {
                e.preventDefault();

                const title = document.getElementById('postTitle').value;
                const content = document.getElementById('postContent').value;
                const tags = document.getElementById('postTags').value;

                fetch('/api/create-post', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: title,
                        content: content,
                        tags: tags
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('postForm').reset();
                        showNotification('Post shared successfully!');
                    }
                });
            });

            function showNotification(message) {
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.style.display = 'block';
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 3000);
            }

            function loadPosts() {
                // Reload posts (simplified for demo)
                location.reload();
            }

            function updateLikeCount(postId, count) {
                const likeBtn = document.querySelector(`[data-post-id="${postId}"] .like-count`);
                if (likeBtn) {
                    likeBtn.textContent = count;
                }
            }

            function addCommentToPost(postId, comment) {
                // Add comment to post (simplified for demo)
                console.log('New comment:', comment);
            }
        </script>
    </body>
    </html>
    '''

    return render_template_string(social_template)

@app.route('/api/create-post', methods=['POST'])
def api_create_post():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})

    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    tags = data.get('tags', '')

    if not content:
        return jsonify({'success': False, 'error': 'Content is required'})

    post_id = create_post(session['user_id'], title, content, tags=tags)
    return jsonify({'success': True, 'post_id': post_id})

@app.route('/api/like-post', methods=['POST'])
def api_like_post():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})

    data = request.get_json()
    post_id = data.get('post_id')

    if not post_id:
        return jsonify({'success': False, 'error': 'Post ID is required'})

    result = like_post(session['user_id'], post_id)
    return jsonify({'success': True, **result})

@app.route('/api/add-comment', methods=['POST'])
def api_add_comment():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})

    data = request.get_json()
    post_id = data.get('post_id')
    content = data.get('content')

    if not post_id or not content:
        return jsonify({'success': False, 'error': 'Post ID and content are required'})

    comment_id = add_comment(session['user_id'], post_id, content)
    return jsonify({'success': True, 'comment_id': comment_id})

# Quiz API Routes
@app.route('/api/quiz/start', methods=['POST'])
def api_start_quiz():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})

    data = request.get_json()
    difficulty = data.get('difficulty', 'simple')

    if difficulty not in QUIZ_QUESTIONS:
        return jsonify({'success': False, 'error': 'Invalid difficulty level'})

    # Get random questions for the difficulty level
    questions = random.sample(QUIZ_QUESTIONS[difficulty], min(5, len(QUIZ_QUESTIONS[difficulty])))

    # Remove correct answers from response
    quiz_questions = []
    for i, q in enumerate(questions):
        quiz_questions.append({
            'id': i,
            'question': q['question'],
            'options': q['options']
        })

    # Store correct answers in session for verification
    session[f'quiz_answers_{difficulty}'] = [q['correct'] for q in questions]
    session[f'quiz_start_time_{difficulty}'] = time.time()

    return jsonify({
        'success': True,
        'questions': quiz_questions,
        'difficulty': difficulty,
        'total_questions': len(quiz_questions)
    })

@app.route('/api/quiz/submit', methods=['POST'])
def api_submit_quiz():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})

    data = request.get_json()
    difficulty = data.get('difficulty')
    user_answers = data.get('answers', [])

    if not difficulty or f'quiz_answers_{difficulty}' not in session:
        return jsonify({'success': False, 'error': 'Invalid quiz session'})

    correct_answers = session[f'quiz_answers_{difficulty}']
    start_time = session.get(f'quiz_start_time_{difficulty}', time.time())
    time_taken = int(time.time() - start_time)

    # Calculate score
    score = sum(1 for i, answer in enumerate(user_answers) if i < len(correct_answers) and answer == correct_answers[i])
    total_questions = len(correct_answers)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0

    # Save quiz attempt
    attempt_id = save_quiz_attempt(session['user_id'], difficulty, score, total_questions)

    # Check for perfect score reward
    flower_reward = None
    if percentage == 100:
        flower_data = random.choice(FLOWER_TITLES)
        flower_image = get_flower_image(flower_data['flower'])

        # Save achievement
        achievement_id = save_achievement(session['user_id'], flower_data['title'], flower_image, difficulty)

        flower_reward = {
            'title': flower_data['title'],
            'image': flower_image,
            'achievement_id': achievement_id
        }

        # Create notification
        create_notification(
            session['user_id'],
            'achievement',
            'Perfect Score! 🌸',
            f'You earned the "{flower_data["title"]}" title for a perfect score!',
            {'flower_title': flower_data['title'], 'flower_image': flower_image}
        )

    # Clean up session
    session.pop(f'quiz_answers_{difficulty}', None)
    session.pop(f'quiz_start_time_{difficulty}', None)

    return jsonify({
        'success': True,
        'score': score,
        'total_questions': total_questions,
        'percentage': percentage,
        'time_taken': time_taken,
        'flower_reward': flower_reward,
        'attempt_id': attempt_id
    })

@app.route('/api/quiz/leaderboard')
def api_quiz_leaderboard():
    conn = sqlite3.connect('new_greenverse.db')
    conn.row_factory = sqlite3.Row

    leaderboard = conn.execute('''
        SELECT u.username, u.first_name, u.last_name,
               qa.level, qa.score, qa.total_questions,
               (qa.score * 100.0 / qa.total_questions) as percentage,
               qa.completed_at
        FROM quiz_attempts qa
        JOIN users u ON qa.user_id = u.id
        ORDER BY percentage DESC, qa.completed_at DESC
        LIMIT 50
    ''').fetchall()

    conn.close()

    return jsonify({
        'success': True,
        'leaderboard': [dict(row) for row in leaderboard]
    })

# Enhanced Plant Analysis API
@app.route('/api/plant/analyze', methods=['POST'])
def api_analyze_plant():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})

    # For demo purposes, we'll simulate the analysis
    # In production, this would process the uploaded image
    analysis_data = generate_plant_analysis()

    # Save analysis to database
    analysis_id = save_plant_analysis(session['user_id'], 'demo_image.jpg', analysis_data)

    # Create notification for urgent cases
    if analysis_data['urgency_level'] == 'High':
        create_notification(
            session['user_id'],
            'plant_alert',
            '🚨 Plant Needs Attention!',
            f'Your {analysis_data["plant_name"]} requires immediate care.',
            {'analysis_id': analysis_id, 'urgency': 'high'}
        )

    return jsonify({
        'success': True,
        'analysis': analysis_data,
        'analysis_id': analysis_id
    })

# Authentication Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌱 GreenVerse Social - Welcome</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 50px;
                padding: 60px 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            .auth-buttons {
                display: flex;
                gap: 20px;
                justify-content: center;
                margin-top: 30px;
                flex-wrap: wrap;
            }
            .btn {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                display: inline-block;
                transition: all 0.3s ease;
                font-size: 1.1rem;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
            .btn.signup { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-bottom: 50px;
            }
            .feature-card {
                background: white;
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .feature-card:hover { transform: translateY(-10px); }
            .feature-icon { font-size: 4rem; margin-bottom: 20px; }
            .feature-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 15px; color: #333; }
            .feature-desc { color: #666; line-height: 1.6; margin-bottom: 25px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="font-size: 3.5rem; margin-bottom: 20px;">🌱 GreenVerse Social</h1>
                <p style="font-size: 1.3rem; margin-bottom: 30px;">The Ultimate Social Platform for Plant Enthusiasts</p>
                <p style="font-size: 1.1rem; opacity: 0.9;">Connect • Share • Learn • Grow Together 🌿</p>

                <div class="auth-buttons">
                    <a href="/login" class="btn">🔑 Login</a>
                    <a href="/signup" class="btn signup">✨ Sign Up Free</a>
                </div>
            </div>

            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">🌐</div>
                    <h3 class="feature-title">Real-time Social Feed</h3>
                    <p class="feature-desc">Share your plant journey, connect with fellow enthusiasts, get live updates, and join discussions!</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <h3 class="feature-title">Interactive Quiz System</h3>
                    <p class="feature-desc">Challenge yourself with 3 difficulty levels and earn beautiful flower titles as rewards!</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🔬</div>
                    <h3 class="feature-title">AI Plant Analysis</h3>
                    <p class="feature-desc">Upload plant photos for instant analysis: dehydration levels, stress rate, sunlight warnings & care tips!</p>
                </div>
            </div>
        </div>
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

        conn = sqlite3.connect('new_greenverse.db')
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user[4], password):  # password_hash is at index 4
            session['user_id'] = user[0]
            session['username'] = user[2]
            session['first_name'] = user[5]
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #333;
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
            .logo {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            .title {
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #333;
            }
            .form-group input {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            .form-group input:focus {
                outline: none;
                border-color: #28a745;
            }
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
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .signup-link {
                color: #666;
            }
            .signup-link a {
                color: #28a745;
                text-decoration: none;
                font-weight: bold;
            }
            .signup-link a:hover {
                text-decoration: underline;
            }
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

            <p class="signup-link">
                Don't have an account? <a href="/signup">Sign up here</a>
            </p>

            <p class="signup-link" style="margin-top: 15px;">
                <a href="/">← Back to Home</a>
            </p>
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

        conn = sqlite3.connect('new_greenverse.db')

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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #333;
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
            .logo {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            .title {
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #333;
            }
            .form-group input {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            .form-group input:focus {
                outline: none;
                border-color: #28a745;
            }
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
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .login-link {
                color: #666;
            }
            .login-link a {
                color: #28a745;
                text-decoration: none;
                font-weight: bold;
            }
            .login-link a:hover {
                text-decoration: underline;
            }
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

            <p class="login-link">
                Already have an account? <a href="/login">Sign in here</a>
            </p>

            <p class="login-link" style="margin-top: 15px;">
                <a href="/">← Back to Home</a>
            </p>
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

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌱 GreenVerse Social Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
                min-height: 100vh;
                color: #333;
            }
            .navbar {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 15px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .nav-container {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 20px;
            }
            .logo {
                font-size: 1.5rem;
                font-weight: bold;
            }
            .nav-links {
                display: flex;
                gap: 20px;
                align-items: center;
            }
            .nav-links a {
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 20px;
                transition: background 0.3s ease;
            }
            .nav-links a:hover {
                background: rgba(255,255,255,0.2);
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                display: grid;
                grid-template-columns: 1fr 2fr 1fr;
                gap: 20px;
            }
            .card {
                background: white;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .post-form {
                background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
                border: 2px dashed #28a745;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-group textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                resize: none;
                font-family: inherit;
                font-size: 1rem;
            }
            .form-group textarea:focus {
                outline: none;
                border-color: #28a745;
            }
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
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .btn.quiz { background: linear-gradient(135deg, #a55eea 0%, #8e44ad 100%); }
            .btn.analyze { background: linear-gradient(135deg, #26de81 0%, #20bf6b 100%); }
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
            .action-btn:hover {
                background: #f8f9fa;
                color: #28a745;
            }
            .online-indicator {
                width: 10px;
                height: 10px;
                background: #00ff00;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
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
                    <div class="online-indicator"></div>
                    <span>Welcome, {{ session.first_name }}!</span>
                    <a href="/quiz">🧠 Quiz</a>
                    <a href="/plant-analyzer">🔬 Analyze</a>
                    <a href="/achievements">🏆 Achievements</a>
                    <a href="/logout">🚪 Logout</a>
                </div>
            </div>
        </nav>

        <div class="container">
            <!-- Left Sidebar -->
            <div class="sidebar">
                <div class="card">
                    <h3>🎯 Quick Actions</h3>
                    <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 15px;">
                        <a href="/quiz" class="btn quiz">🧠 Take Quiz</a>
                        <a href="/plant-analyzer" class="btn analyze">🔬 Analyze Plant</a>
                        <a href="/achievements" class="btn">🏆 View Achievements</a>
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
                    <!-- Sample posts -->
                    <div class="post">
                        <div class="post-header">
                            <div class="avatar">SG</div>
                            <div>
                                <strong>Sarah Green</strong>
                                <div style="font-size: 0.9rem; color: #666;">2 minutes ago</div>
                            </div>
                        </div>
                        <p>Just got my Monstera deliciosa analyzed and it's thriving! 🌱 The AI detected perfect hydration levels. So happy with my plant care routine!</p>
                        <div class="post-actions">
                            <button class="action-btn">❤️ 12 Likes</button>
                            <button class="action-btn">💬 3 Comments</button>
                            <button class="action-btn">🔄 Share</button>
                        </div>
                    </div>

                    <div class="post">
                        <div class="post-header">
                            <div class="avatar">MJ</div>
                            <div>
                                <strong>Mike Johnson</strong>
                                <div style="font-size: 0.9rem; color: #666;">5 minutes ago</div>
                            </div>
                        </div>
                        <p>Just earned the "Rose Guardian" title in the quiz! 🌹 The hardest level was challenging but so worth it. Who else is taking the quiz?</p>
                        <div class="post-actions">
                            <button class="action-btn">❤️ 8 Likes</button>
                            <button class="action-btn">💬 5 Comments</button>
                            <button class="action-btn">🔄 Share</button>
                        </div>
                    </div>
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
                    </div>
                </div>

                <div class="card">
                    <h3>👥 Online Users</h3>
                    <div style="margin-top: 15px;">
                        <p>🟢 <span id="online-count">127</span> gardeners online</p>
                        <p style="margin-top: 10px; font-size: 0.9rem; color: #666;">Join the conversation!</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Initialize Socket.IO
            const socket = io();

            // Join user room for notifications
            socket.emit('join_room', '{{ session.user_id }}');

            // Handle real-time posts
            socket.on('new_post', function(data) {
                showNotification('🌱 New post from ' + data.username);
                addPostToFeed(data);
            });

            // Handle notifications
            socket.on('notification', function(data) {
                showNotification(data.message);
            });

            // Post form submission
            document.getElementById('postForm').addEventListener('submit', function(e) {
                e.preventDefault();

                const content = document.getElementById('postContent').value;
                if (!content.trim()) return;

                fetch('/api/create-post', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        content: content
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('postContent').value = '';
                        showNotification('✅ Post shared successfully!');
                    }
                });
            });

            function showNotification(message) {
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.style.display = 'block';
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 4000);
            }

            function addPostToFeed(postData) {
                const postsContainer = document.getElementById('postsContainer');
                const postElement = document.createElement('div');
                postElement.className = 'post';
                postElement.innerHTML = `
                    <div class="post-header">
                        <div class="avatar">${postData.username.substring(0, 2).toUpperCase()}</div>
                        <div>
                            <strong>${postData.first_name} ${postData.last_name}</strong>
                            <div style="font-size: 0.9rem; color: #666;">Just now</div>
                        </div>
                    </div>
                    <p>${postData.content}</p>
                    <div class="post-actions">
                        <button class="action-btn">❤️ 0 Likes</button>
                        <button class="action-btn">💬 0 Comments</button>
                        <button class="action-btn">🔄 Share</button>
                    </div>
                `;
                postsContainer.insertBefore(postElement, postsContainer.firstChild);
            }

            // Simulate online user count updates
            let onlineCount = 127;
            setInterval(() => {
                onlineCount += Math.floor(Math.random() * 10) - 5;
                onlineCount = Math.max(50, Math.min(200, onlineCount));
                document.getElementById('online-count').textContent = onlineCount;
            }, 5000);

            // Welcome notification
            setTimeout(() => {
                showNotification('🌱 Welcome to GreenVerse Social! Start sharing your plant journey!');
            }, 2000);
        </script>
    </body>
    </html>
    ''', session=session)

if __name__ == '__main__':
    print("🌱 Initializing GreenVerse ENHANCED Social Plant Health System...")
    init_db()
    init_quiz_db()
    print("✅ Database ready with enhanced features!")
    print("🚀 Starting enhanced server with real-time features...")
    print("📍 Visit: http://localhost:5001")
    print("🔬 Enhanced Plant Analyzer: http://localhost:5001/plant-analyzer")
    print("🧠 Plant Knowledge Quiz: http://localhost:5001/quiz")
    print("🏆 Achievements: http://localhost:5001/achievements")
    print("📊 Complete Plant History: http://localhost:5001/plant-history")
    print("🌐 Social Feed: http://localhost:5001/social-feed")
    print("💬 Real-time features enabled!")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
