# GreenVerse - Plant Social Network (Python Flask)

A complete social media platform for plant enthusiasts built with Python Flask.

## 🌟 Features

### Social Media Features
- **User Authentication** - Register, login, logout with secure password hashing
- **User Profiles** - Customizable profiles with bio, location, and growing zone
- **Post Creation** - Share text posts with optional images and tags
- **Social Interactions** - Like posts, comment, follow/unfollow users
- **Real-time Messaging** - Direct messages between users
- **Community Feed** - See posts from followed users and discover new content

### Plant-Specific Features
- **Plant Health Analyzer** - Upload plant photos for AI-powered health analysis
- **Dehydration Detection** - Get detailed reports on plant hydration levels
- **Care Recommendations** - Personalized watering schedules and plant care tips
- **Marketplace** - Browse and shop for gardening supplies
- **Crop Recommendations** - Location-based growing advice

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Run the application:**
   \`\`\`bash
   python app.py
   \`\`\`

4. **Open your browser:**
   Navigate to `http://localhost:5000`

### Demo Credentials
- **Email:** `test@example.com`
- **Password:** `test`

## 🛠️ Running in VS Code

### Setup Steps:
1. **Open VS Code**
2. **Open project folder** (File → Open Folder)
3. **Install Python extension** (if not already installed)
4. **Open integrated terminal** (`Ctrl + ` ` or Terminal → New Terminal)
5. **Install dependencies:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
6. **Run the app:**
   \`\`\`bash
   python app.py
   \`\`\`

### VS Code Features:
- **Debugging:** Press `F5` to start debugging
- **IntelliSense:** Auto-completion for Python code
- **Integrated Terminal:** Run commands without leaving VS Code
- **File Explorer:** Easy navigation through project files

## 📁 Project Structure

\`\`\`
greenverse-python/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── greenverse.db            # SQLite database (auto-created)
├── static/
│   └── uploads/             # User uploaded images
└── templates/               # HTML templates
    ├── base.html           # Base template with navigation
    ├── landing.html        # Homepage
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── dashboard.html      # User dashboard
    ├── community.html      # Community feed
    ├── messages.html       # Messages inbox
    ├── chat.html           # Individual chat
    ├── profile.html        # User profiles
    ├── dehydration_detector.html  # Plant analyzer
    ├── marketplace.html    # Shopping
    └── crop_recommendations.html  # Growing tips
\`\`\`

## 🎯 Key Features Explained

### Social Media Functionality
- **Posts:** Create text posts with optional titles, images, and hashtags
- **Interactions:** Like posts, add comments, share content
- **Following System:** Follow other users to see their posts in your feed
- **Messaging:** Send direct messages to other users
- **Profiles:** View user profiles with post history and stats

### Plant Care Tools
- **Health Analysis:** Upload plant photos for automated health assessment
- **Detailed Reports:** Get scores for hydration, stress levels, and sunlight exposure
- **Care Instructions:** Receive personalized watering schedules and care tips
- **Progress Tracking:** Monitor plant health over time

### Database Schema
The app uses SQLite with the following main tables:
- `users` - User accounts and profiles
- `posts` - User posts and content
- `follows` - User following relationships
- `likes` - Post likes
- `comments` - Post comments
- `messages` - Direct messages
- `plant_analyses` - Plant health analysis results

## 🔧 Customization

### Adding New Features
1. **Database:** Add new tables in the `init_db()` function
2. **Routes:** Add new Flask routes in `app.py`
3. **Templates:** Create new HTML templates in the `templates/` folder
4. **Styling:** Modify the CSS in `templates/base.html`

### Configuration
- **Secret Key:** Change `app.secret_key` for production
- **Upload Folder:** Modify `app.config['UPLOAD_FOLDER']` for different image storage
- **Database:** Replace SQLite with PostgreSQL/MySQL for production

## 🌱 Demo Data

The app includes demo users and posts:
- **Test User:** test@example.com / test
- **Jane Doe:** jane.doe@example.com / password
- **Robert Green:** robert.green@example.com / password
- **Sarah Lee:** sarah.lee@example.com / password
- **Emma Johnson:** emma.johnson@example.com / password

## 🚀 Production Deployment

For production deployment:
1. Change the secret key
2. Use a production database (PostgreSQL/MySQL)
3. Set up proper file storage (AWS S3, etc.)
4. Configure environment variables
5. Use a production WSGI server (Gunicorn, uWSGI)

## 📝 License

This project is open source and available under the MIT License.
