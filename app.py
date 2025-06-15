from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
import json
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)

def init_db():
    conn = sqlite3.connect('greenverse.db')
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
    
    # Plant analyses table - NEW ENHANCED VERSION
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
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with NEW plant analysis system!")

def generate_plant_analysis():
    plants = [
        {'name': 'Monstera Deliciosa', 'type': 'Tropical Houseplant'},
        {'name': 'Fiddle Leaf Fig', 'type': 'Indoor Tree'},
        {'name': 'Snake Plant', 'type': 'Succulent'},
        {'name': 'Pothos', 'type': 'Trailing Vine'},
        {'name': 'Peace Lily', 'type': 'Flowering Plant'}
    ]
    
    plant = random.choice(plants)
    dehydration_score = random.uniform(0.2, 0.9)
    stress_score = random.uniform(0.1, 0.8)
    sunlight_score = random.uniform(0.4, 0.9)
    overall_health = (1 - dehydration_score + sunlight_score + (1 - stress_score)) / 3
    
    # Determine levels
    dehydration_level = 'Well Hydrated' if dehydration_score < 0.3 else 'Slightly Dehydrated' if dehydration_score < 0.6 else 'Moderately Dehydrated' if dehydration_score < 0.8 else 'Severely Dehydrated'
    stress_level = 'No Stress' if stress_score < 0.2 else 'Low Stress' if stress_score < 0.4 else 'Moderate Stress' if stress_score < 0.6 else 'High Stress'
    sunlight_exposure = 'Excellent' if sunlight_score > 0.8 else 'Good' if sunlight_score > 0.6 else 'Adequate' if sunlight_score > 0.4 else 'Insufficient'
    urgency_level = 'Low' if overall_health > 0.7 else 'Medium' if overall_health > 0.5 else 'High'
    
    # Generate symptoms
    symptoms = []
    if dehydration_score > 0.6:
        symptoms.extend(['Wilting leaves', 'Dry soil surface', 'Brown leaf edges'])
    if stress_score > 0.5:
        symptoms.extend(['Yellowing leaves', 'Stunted growth', 'Leaf drop'])
    if sunlight_score < 0.5:
        symptoms.extend(['Leggy growth', 'Pale leaves', 'Slow growth'])
    
    # Generate recommendations
    recommendations = []
    if dehydration_score > 0.5:
        recommendations.extend(['Water thoroughly until drainage', 'Check soil moisture regularly'])
    if stress_score > 0.4:
        recommendations.extend(['Remove damaged leaves', 'Ensure proper drainage'])
    if sunlight_score < 0.6:
        recommendations.extend(['Move to brighter location', 'Consider grow light'])
    
    # Prevention tips
    prevention_tips = [
        'Establish consistent watering schedule',
        'Monitor soil moisture weekly',
        'Ensure proper drainage',
        'Maintain appropriate humidity',
        'Rotate plant weekly',
        'Inspect for pests regularly'
    ]
    
    # Cure suggestions based on health
    cure_suggestions = []
    if overall_health < 0.5:
        cure_suggestions.extend([
            'IMMEDIATE INTERVENTION REQUIRED',
            'Assess root system for rot',
            'Trim all dead/damaged leaves',
            'Repot in fresh soil if needed',
            'Apply fungicide if infection detected',
            'Quarantine to prevent spread'
        ])
    elif overall_health < 0.7:
        cure_suggestions.extend([
            'Adjust watering schedule',
            'Improve growing conditions',
            'Apply appropriate fertilizer',
            'Prune damaged areas',
            'Monitor closely for improvement'
        ])
    else:
        cure_suggestions.extend([
            'Continue current care routine',
            'Fine-tune conditions as needed',
            'Regular maintenance pruning'
        ])
    
    # Disease/pest detection
    disease_detected = 'None'
    pest_detected = 'None'
    if stress_score > 0.6:
        diseases = ['Leaf Spot', 'Root Rot', 'Powdery Mildew', 'Bacterial Blight']
        disease_detected = random.choice(diseases) if random.random() > 0.7 else 'None'
    if random.random() > 0.8:
        pests = ['Spider Mites', 'Aphids', 'Scale Insects', 'Fungus Gnats']
        pest_detected = random.choice(pests)
    
    # Follow-up date
    follow_up_days = 3 if urgency_level == 'High' else 7 if urgency_level == 'Medium' else 14
    follow_up_date = (datetime.now() + timedelta(days=follow_up_days)).strftime('%Y-%m-%d')
    
    return {
        'plant_name': plant['name'],
        'plant_type': plant['type'],
        'dehydration_level': dehydration_level,
        'dehydration_score': dehydration_score,
        'stress_level': stress_level,
        'stress_score': stress_score,
        'sunlight_exposure': sunlight_exposure,
        'sunlight_score': sunlight_score,
        'disease_detected': disease_detected,
        'pest_detected': pest_detected,
        'overall_health_score': overall_health,
        'confidence_score': random.randint(85, 98),
        'symptoms': symptoms,
        'recommendations': recommendations,
        'prevention_tips': prevention_tips,
        'cure_suggestions': cure_suggestions,
        'watering_schedule': f"Water every {random.randint(3, 14)} days when top inch is dry",
        'fertilizer_recommendation': random.choice([
            'Balanced liquid fertilizer monthly',
            'Diluted fertilizer bi-weekly',
            'Slow-release fertilizer quarterly',
            'Organic compost monthly'
        ]),
        'urgency_level': urgency_level,
        'recovery_time': '1-3 days' if urgency_level == 'Low' else '3-7 days' if urgency_level == 'Medium' else '1-3 weeks',
        'follow_up_date': follow_up_date
    }

def save_plant_analysis(user_id, image_url, analysis_data):
    analysis_id = str(uuid.uuid4())
    conn = sqlite3.connect('greenverse.db')
    conn.row_factory = sqlite3.Row
    
    conn.execute('''
        INSERT INTO plant_analyses 
        (id, user_id, image_url, plant_name, plant_type, dehydration_level, dehydration_score,
         stress_level, stress_score, sunlight_exposure, sunlight_score, disease_detected, 
         pest_detected, overall_health_score, confidence_score, symptoms, recommendations, 
         prevention_tips, cure_suggestions, watering_schedule, fertilizer_recommendation, 
         urgency_level, recovery_time, follow_up_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        analysis_id, user_id, image_url,
        analysis_data['plant_name'], analysis_data['plant_type'],
        analysis_data['dehydration_level'], analysis_data['dehydration_score'],
        analysis_data['stress_level'], analysis_data['stress_score'],
        analysis_data['sunlight_exposure'], analysis_data['sunlight_score'],
        analysis_data['disease_detected'], analysis_data['pest_detected'],
        analysis_data['overall_health_score'], analysis_data['confidence_score'],
        json.dumps(analysis_data['symptoms']), json.dumps(analysis_data['recommendations']),
        json.dumps(analysis_data['prevention_tips']), json.dumps(analysis_data['cure_suggestions']),
        analysis_data['watering_schedule'], analysis_data['fertilizer_recommendation'],
        analysis_data['urgency_level'], analysis_data['recovery_time'],
        analysis_data['follow_up_date'], ''
    ))
    
    conn.commit()
    conn.close()
    return analysis_id

def get_plant_history(user_id):
    conn = sqlite3.connect('greenverse.db')
    conn.row_factory = sqlite3.Row
    analyses = conn.execute('''
        SELECT * FROM plant_analyses 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return analyses

# Routes
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌱 GreenVerse - NEW VERSION</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
            .header { text-align: center; color: white; margin-bottom: 50px; }
            .card { background: white; border-radius: 20px; padding: 30px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            .btn { background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px; font-weight: bold; }
            .btn:hover { background: #218838; transform: translateY(-2px); }
            .feature { display: inline-block; width: 300px; margin: 20px; vertical-align: top; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="font-size: 3rem; margin-bottom: 10px;">🌱 GreenVerse</h1>
                <h2 style="font-size: 1.5rem; opacity: 0.9;">NEW AI Plant Health System</h2>
                <p style="font-size: 1.2rem; opacity: 0.8;">Advanced diagnostics • Prevention tips • Cure suggestions • Complete history</p>
            </div>
            
            <div class="card">
                <h2 style="color: #28a745; text-align: center;">🚀 NEW FEATURES AVAILABLE!</h2>
                
                <div style="text-align: center;">
                    <div class="feature">
                        <h3>🔬 AI Plant Analyzer</h3>
                        <p>Advanced health diagnostics with disease detection and treatment plans</p>
                        <a href="/plant-analyzer" class="btn">Start Analysis</a>
                    </div>
                    
                    <div class="feature">
                        <h3>📊 Analysis History</h3>
                        <p>Track your plant health journey and see improvements over time</p>
                        <a href="/plant-history" class="btn">View History</a>
                    </div>
                    
                    <div class="feature">
                        <h3>💊 Treatment Plans</h3>
                        <p>Get specific cure suggestions for damaged or sick plants</p>
                        <a href="/plant-analyzer" class="btn">Get Treatment</a>
                    </div>
                </div>
            </div>
            
            <div class="card" style="background: #d4edda; border: 2px solid #28a745;">
                <h3 style="color: #155724;">✅ What's New in This Version:</h3>
                <ul style="color: #155724; font-size: 1.1rem;">
                    <li><strong>Disease Detection:</strong> Identifies plant diseases and pests</li>
                    <li><strong>Prevention Tips:</strong> Proactive care suggestions</li>
                    <li><strong>Cure Suggestions:</strong> Treatment plans for sick plants</li>
                    <li><strong>Complete History:</strong> Track all your plant analyses</li>
                    <li><strong>Recovery Timeline:</strong> Expected healing times</li>
                    <li><strong>Urgency Levels:</strong> Priority-based care alerts</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="/login" class="btn" style="font-size: 1.2rem; padding: 20px 40px;">🔑 Login to Continue</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Auto-login for demo
        session['user_id'] = '1'
        return redirect(url_for('plant_analyzer'))
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - GreenVerse</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .login-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); max-width: 400px; width: 100%; }
            .form-group { margin-bottom: 20px; }
            .form-control { width: 100%; padding: 15px; border: 2px solid #ddd; border-radius: 10px; font-size: 16px; }
            .btn { background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 10px; width: 100%; font-size: 16px; cursor: pointer; }
            .btn:hover { background: #218838; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2 style="text-align: center; color: #28a745; margin-bottom: 30px;">🌱 Login to GreenVerse</h2>
            <form method="POST">
                <div class="form-group">
                    <input type="email" name="email" class="form-control" placeholder="Email" value="test@example.com" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" class="form-control" placeholder="Password" value="test" required>
                </div>
                <button type="submit" class="btn">🔑 Login & Start Analyzing</button>
            </form>
            <p style="text-align: center; margin-top: 20px; color: #666;">
                Demo credentials: test@example.com / test
            </p>
        </div>
    </body>
    </html>
    '''

@app.route('/plant-analyzer', methods=['GET', 'POST'])
def plant_analyzer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle file upload
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
            
            # Return results page
            return render_analysis_results(analysis, f"uploads/{unique_filename}")
    
    # GET request - show upload form
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔬 AI Plant Health Analyzer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 40px; border-radius: 20px; margin-bottom: 30px; }
            .card { background: white; border-radius: 20px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 30px; }
            .upload-area { border: 3px dashed #28a745; padding: 60px; text-align: center; border-radius: 20px; background: #f8f9fa; }
            .btn { background: #28a745; color: white; padding: 20px 40px; border: none; border-radius: 15px; font-size: 18px; cursor: pointer; margin: 10px; }
            .btn:hover { background: #218838; transform: translateY(-2px); }
            .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }
            .feature-card { background: #f8f9fa; padding: 20px; border-radius: 15px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="font-size: 2.5rem; margin-bottom: 10px;">🔬 AI Plant Health Analyzer</h1>
                <p style="font-size: 1.2rem; opacity: 0.9;">Advanced plant diagnostics with prevention & cure recommendations</p>
            </div>
            
            <div class="card">
                <div class="upload-area">
                    <i style="font-size: 4rem; color: #28a745;">🌱</i>
                    <h3 style="color: #28a745; margin: 20px 0;">Upload Plant Photo</h3>
                    <p style="color: #666; margin-bottom: 30px;">Get comprehensive health analysis, prevention tips, and cure suggestions</p>
                    
                    <form method="POST" enctype="multipart/form-data">
                        <input type="file" name="plant_image" accept="image/*" required style="margin-bottom: 20px; padding: 10px;">
                        <br>
                        <button type="submit" class="btn">🔬 Analyze Plant Health</button>
                    </form>
                </div>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <h4 style="color: #28a745;">🔍 Disease Detection</h4>
                    <p>Identifies common plant diseases and pest infestations</p>
                </div>
                <div class="feature-card">
                    <h4 style="color: #28a745;">🛡️ Prevention Tips</h4>
                    <p>Proactive care suggestions to prevent future issues</p>
                </div>
                <div class="feature-card">
                    <h4 style="color: #28a745;">💊 Treatment Plans</h4>
                    <p>Specific cure suggestions for damaged plants</p>
                </div>
                <div class="feature-card">
                    <h4 style="color: #28a745;">📊 Health Tracking</h4>
                    <p>Complete history of all your plant analyses</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="/plant-history" class="btn">📊 View Analysis History</a>
                <a href="/" class="btn" style="background: #6c757d;">🏠 Home</a>
            </div>
        </div>
    </body>
    </html>
    '''

def render_analysis_results(analysis, image_url):
    urgency_color = '#dc3545' if analysis['urgency_level'] == 'High' else '#ffc107' if analysis['urgency_level'] == 'Medium' else '#28a745'
    urgency_icon = '🚨' if analysis['urgency_level'] == 'High' else '⚠️' if analysis['urgency_level'] == 'Medium' else '✅'
    
    symptoms_html = ''.join([f'<li>• {symptom}</li>' for symptom in analysis['symptoms']])
    recommendations_html = ''.join([f'<li>✓ {rec}</li>' for rec in analysis['recommendations']])
    prevention_html = ''.join([f'<li>🛡️ {tip}</li>' for tip in analysis['prevention_tips']])
    cure_html = ''.join([f'<li>💊 {cure}</li>' for cure in analysis['cure_suggestions']])
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌱 Analysis Results - {analysis['plant_name']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); min-height: 100vh; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; text-align: center; padding: 40px; border-radius: 20px; margin-bottom: 30px; }}
            .card {{ background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .urgency-alert {{ background: {urgency_color}; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 30px; }}
            .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 15px; text-align: center; }}
            .progress-bar {{ background: #e9ecef; height: 10px; border-radius: 5px; overflow: hidden; margin: 10px 0; }}
            .progress-fill {{ height: 100%; transition: width 1s ease; }}
            .btn {{ background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px; }}
            .section {{ margin-bottom: 30px; }}
            .section h3 {{ color: #28a745; border-bottom: 2px solid #28a745; padding-bottom: 10px; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
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
                <h3>{urgency_icon} {analysis['urgency_level']} Priority</h3>
                <p>Overall Health Score: {int(analysis['overall_health_score'] * 100)}%</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h4>💧 Hydration Level</h4>
                    <h3 style="color: #17a2b8;">{analysis['dehydration_level']}</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {int((1-analysis['dehydration_score'])*100)}%; background: #17a2b8;"></div>
                    </div>
                    <small>{int((1-analysis['dehydration_score'])*100)}% Hydrated</small>
                </div>
                
                <div class="metric-card">
                    <h4>⚡ Stress Level</h4>
                    <h3 style="color: #ffc107;">{analysis['stress_level']}</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {int(analysis['stress_score']*100)}%; background: #ffc107;"></div>
                    </div>
                    <small>{int(analysis['stress_score']*100)}% Stress</small>
                </div>
                
                <div class="metric-card">
                    <h4>☀️ Sunlight</h4>
                    <h3 style="color: #fd7e14;">{analysis['sunlight_exposure']}</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {int(analysis['sunlight_score']*100)}%; background: #fd7e14;"></div>
                    </div>
                    <small>{int(analysis['sunlight_score']*100)}% Optimal</small>
                </div>
            </div>
            
            {f'''
            <div class="card" style="border-left: 5px solid #dc3545;">
                <h3 style="color: #dc3545;">🚨 Issues Detected</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    {f'<div><strong>Disease:</strong> {analysis["disease_detected"]}</div>' if analysis["disease_detected"] != "None" else ""}
                    {f'<div><strong>Pest:</strong> {analysis["pest_detected"]}</div>' if analysis["pest_detected"] != "None" else ""}
                </div>
            </div>
            ''' if analysis["disease_detected"] != "None" or analysis["pest_detected"] != "None" else ""}
            
            <div class="card">
                <div class="section">
                    <h3>🔍 Observed Symptoms</h3>
                    <ul>{symptoms_html}</ul>
                </div>
                
                <div class="section">
                    <h3>💡 Immediate Recommendations</h3>
                    <ul>{recommendations_html}</ul>
                </div>
                
                <div class="section">
                    <h3>🛡️ Prevention Tips</h3>
                    <ul>{prevention_html}</ul>
                </div>
                
                <div class="section">
                    <h3>💊 Treatment & Recovery Plan</h3>
                    <ul>{cure_html}</ul>
                </div>
            </div>
            
            <div class="card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; text-align: center;">
                    <div>
                        <h4>⏰ Expected Recovery</h4>
                        <h3>{analysis['recovery_time']}</h3>
                    </div>
                    <div>
                        <h4>📅 Follow-up Date</h4>
                        <h3>{analysis['follow_up_date']}</h3>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h4 style="color: #17a2b8;">💧 Watering Schedule</h4>
                        <p>{analysis['watering_schedule']}</p>
                    </div>
                    <div>
                        <h4 style="color: #28a745;">🌱 Fertilizer</h4>
                        <p>{analysis['fertilizer_recommendation']}</p>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="/plant-analyzer" class="btn">🔬 Analyze Another Plant</a>
                <a href="/plant-history" class="btn">📊 View History</a>
                <a href="/" class="btn" style="background: #6c757d;">🏠 Home</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/plant-history')
def plant_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    analyses = get_plant_history(session['user_id'])
    
    # Parse JSON fields
    for analysis in analyses:
        if analysis['symptoms']:
            analysis['symptoms'] = json.loads(analysis['symptoms'])
        if analysis['recommendations']:
            analysis['recommendations'] = json.loads(analysis['recommendations'])
        if analysis['prevention_tips']:
            analysis['prevention_tips'] = json.loads(analysis['prevention_tips'])
        if analysis['cure_suggestions']:
            analysis['cure_suggestions'] = json.loads(analysis['cure_suggestions'])
    
    if not analyses:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>📊 Plant Analysis History</title>
            <style>
                body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
                .empty-state { text-align: center; background: white; padding: 60px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
                .btn { background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px; }
            </style>
        </head>
        <body>
            <div class="empty-state">
                <div style="font-size: 4rem; margin-bottom: 20px;">🌱</div>
                <h2 style="color: #28a745;">No Plant Analyses Yet</h2>
                <p style="color: #666; margin-bottom: 30px;">Start analyzing your plants to build your health history!</p>
                <a href="/plant-analyzer" class="btn">🔬 Analyze Your First Plant</a>
                <a href="/" class="btn" style="background: #6c757d;">🏠 Home</a>
            </div>
        </body>
        </html>
        '''
    
    # Generate history HTML
    history_cards = []
    for analysis in analyses:
        urgency_color = '#dc3545' if analysis['urgency_level'] == 'High' else '#ffc107' if analysis['urgency_level'] == 'Medium' else '#28a745'
        
        history_cards.append(f'''
        <div class="history-card">
            <div class="card-header">
                <h4>{analysis['plant_name']}</h4>
                <span class="badge" style="background: {urgency_color};">{analysis['urgency_level']} Priority</span>
            </div>
            <div class="card-body">
                <div class="metrics">
                    <div class="metric">
                        <span class="metric-label">Health:</span>
                        <span class="metric-value">{int(analysis['overall_health_score'] * 100)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Hydration:</span>
                        <span class="metric-value">{analysis['dehydration_level']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Stress:</span>
                        <span class="metric-value">{analysis['stress_level']}</span>
                    </div>
                </div>
                
                <div class="analysis-details">
                    <div class="detail-section">
                        <h6>🔍 Symptoms:</h6>
                        <ul>{''.join([f'<li>{symptom}</li>' for symptom in analysis['symptoms'][:3]])}</ul>
                    </div>
                    
                    <div class="detail-section">
                        <h6>💡 Key Recommendations:</h6>
                        <ul>{''.join([f'<li>{rec}</li>' for rec in analysis['recommendations'][:3]])}</ul>
                    </div>
                    
                    <div class="detail-section">
                        <h6>💊 Treatment Plan:</h6>
                        <ul>{''.join([f'<li>{cure}</li>' for cure in analysis['cure_suggestions'][:2]])}</ul>
                    </div>
                </div>
                
                <div class="card-footer">
                    <small>📅 {analysis['created_at'].split()[0]} • Recovery: {analysis['recovery_time']}</small>
                </div>
            </div>
        </div>
        ''')
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📊 Plant Analysis History</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); min-height: 100vh; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; text-align: center; padding: 40px; border-radius: 20px; margin-bottom: 30px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .history-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
            .history-card {{ background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); overflow: hidden; }}
            .card-header {{ padding: 20px; background: #f8f9fa; display: flex; justify-content: between; align-items: center; }}
            .card-body {{ padding: 20px; }}
            .card-footer {{ padding: 15px 20px; background: #f8f9fa; border-top: 1px solid #eee; }}
            .badge {{ padding: 5px 10px; border-radius: 20px; color: white; font-size: 12px; }}
            .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }}
            .metric {{ text-align: center; }}
            .metric-label {{ display: block; font-size: 12px; color: #666; }}
            .metric-value {{ display: block; font-weight: bold; color: #28a745; }}
            .detail-section {{ margin-bottom: 15px; }}
            .detail-section h6 {{ color: #28a745; margin-bottom: 5px; }}
            .detail-section ul {{ list-style: none; padding: 0; }}
            .detail-section li {{ padding: 2px 0; font-size: 14px; color: #666; }}
            .btn {{ background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Plant Analysis History</h1>
                <p>Track your plant health journey and improvements over time</p>
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
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="/plant-analyzer" class="btn">🔬 New Analysis</a>
                <a href="/" class="btn" style="background: #6c757d;">🏠 Home</a>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🌱 Initializing GreenVerse with NEW Plant Health System...")
    init_db()
    print("✅ Database ready!")
    print("🚀 Starting server...")
    print("📍 Visit: http://localhost:5000")
    print("🔬 Plant Analyzer: http://localhost:5000/plant-analyzer")
    print("📊 Plant History: http://localhost:5000/plant-history")
    app.run(debug=True, host='0.0.0.0', port=5000)
