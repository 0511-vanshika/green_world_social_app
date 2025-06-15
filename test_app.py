from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = 'test-key'

@app.route('/')
def index():
    return '<h1>🌱 GreenVerse Test</h1><p><a href="/plant-analyzer">Go to Plant Analyzer</a></p>'

@app.route('/plant-analyzer')
def plant_analyzer():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Plant Analyzer - Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .header { text-align: center; color: #28a745; margin-bottom: 30px; }
            .upload-area { border: 3px dashed #28a745; padding: 40px; text-align: center; border-radius: 10px; }
            .btn { background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔬 AI Plant Health Analyzer</h1>
                <p>Advanced plant diagnostics with prevention & cure recommendations</p>
            </div>
            
            <div class="upload-area">
                <h3>🌱 Upload Plant Photo</h3>
                <p>Get comprehensive health analysis, prevention tips, and cure suggestions</p>
                <form method="POST" enctype="multipart/form-data">
                    <input type="file" name="plant_image" accept="image/*" required style="margin: 20px;">
                    <br>
                    <button type="submit" class="btn">🔬 Analyze Plant Health</button>
                </form>
            </div>
            
            <div style="margin-top: 30px; text-align: center;">
                <a href="/plant-history" style="color: #28a745;">📊 View Analysis History</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/plant-analyzer', methods=['POST'])
def plant_analyzer_post():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analysis Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .result { background: #d4edda; padding: 20px; border-radius: 10px; margin: 20px 0; }
            .btn { background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌱 Analysis Complete!</h1>
            
            <div class="result">
                <h3>Plant: Monstera Deliciosa</h3>
                <p><strong>Health Status:</strong> 85% Healthy</p>
                <p><strong>Hydration:</strong> Well Hydrated</p>
                <p><strong>Stress Level:</strong> Low Stress</p>
            </div>
            
            <div class="result">
                <h4>🔬 Recommendations:</h4>
                <ul>
                    <li>Continue current watering schedule</li>
                    <li>Ensure good drainage</li>
                    <li>Monitor for pests weekly</li>
                </ul>
            </div>
            
            <div class="result">
                <h4>🛡️ Prevention Tips:</h4>
                <ul>
                    <li>Water when top inch of soil is dry</li>
                    <li>Maintain humidity around 60%</li>
                    <li>Rotate plant weekly for even growth</li>
                </ul>
            </div>
            
            <div class="result">
                <h4>💊 Treatment Plan:</h4>
                <ul>
                    <li>No immediate treatment needed</li>
                    <li>Continue regular care routine</li>
                    <li>Next check-up in 2 weeks</li>
                </ul>
            </div>
            
            <p><a href="/plant-analyzer" class="btn">🔄 Analyze Another Plant</a></p>
            <p><a href="/plant-history" class="btn">📊 View History</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/plant-history')
def plant_history():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Plant History</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .history-item { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 5px solid #28a745; }
            .btn { background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌱 Plant Analysis History</h1>
            <p>Track your plant health journey and improvements over time</p>
            
            <div class="history-item">
                <h4>Monstera Deliciosa - Jan 15, 2024</h4>
                <p><strong>Health:</strong> 85% | <strong>Status:</strong> Healthy</p>
                <p><strong>Issues:</strong> None detected</p>
                <p><strong>Action:</strong> Continue current care</p>
            </div>
            
            <div class="history-item">
                <h4>Fiddle Leaf Fig - Jan 10, 2024</h4>
                <p><strong>Health:</strong> 65% | <strong>Status:</strong> Needs Attention</p>
                <p><strong>Issues:</strong> Slight dehydration, brown leaf tips</p>
                <p><strong>Action:</strong> Increase watering frequency</p>
            </div>
            
            <div class="history-item">
                <h4>Snake Plant - Jan 5, 2024</h4>
                <p><strong>Health:</strong> 92% | <strong>Status:</strong> Excellent</p>
                <p><strong>Issues:</strong> None</p>
                <p><strong>Action:</strong> Perfect care routine</p>
            </div>
            
            <p><a href="/plant-analyzer" class="btn">🔬 New Analysis</a></p>
            <p><a href="/" class="btn">🏠 Home</a></p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🌱 Starting GreenVerse Test Server...")
    print("📍 Visit: http://localhost:5000")
    print("🔬 Plant Analyzer: http://localhost:5000/plant-analyzer")
    print("📊 Plant History: http://localhost:5000/plant-history")
    app.run(debug=True, host='0.0.0.0', port=5000)
