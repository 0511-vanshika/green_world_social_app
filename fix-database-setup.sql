-- Drop existing tables if they exist and recreate them
DROP TABLE IF EXISTS likes CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS follows CASCADE;
DROP TABLE IF EXISTS plant_analyses CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table with proper constraints
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  password_hash TEXT NOT NULL,
  avatar_url TEXT,
  bio TEXT,
  location VARCHAR(100),
  growing_zone VARCHAR(10),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create posts table
CREATE TABLE posts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255),
  content TEXT NOT NULL,
  image_url TEXT,
  tags TEXT[],
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create plant_analyses table with all health metrics
CREATE TABLE plant_analyses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  plant_name VARCHAR(255),
  dehydration_level VARCHAR(50) NOT NULL,
  dehydration_score DECIMAL(3,2),
  stress_level VARCHAR(50),
  stress_score DECIMAL(3,2),
  sunlight_exposure VARCHAR(50),
  sunlight_warning TEXT,
  overall_health_score DECIMAL(3,2),
  confidence_score DECIMAL(3,2),
  recommendations TEXT[],
  watering_schedule TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create follows table
CREATE TABLE follows (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  follower_id UUID REFERENCES users(id) ON DELETE CASCADE,
  following_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(follower_id, following_id)
);

-- Create likes table
CREATE TABLE likes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, post_id)
);

-- Create comments table
CREATE TABLE comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_plant_analyses_user_id ON plant_analyses(user_id);
CREATE INDEX idx_follows_follower_id ON follows(follower_id);
CREATE INDEX idx_follows_following_id ON follows(following_id);
CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_likes_post_id ON likes(post_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);

-- Insert some test users for demonstration
INSERT INTO users (email, username, first_name, last_name, password_hash, bio, location, growing_zone) VALUES
('test@example.com', 'testuser', 'Test', 'User', 'dGVzdA==', 'Test user for demonstration', 'Test City', '8b'),
('jane.doe@example.com', 'plantlover123', 'Jane', 'Doe', 'cGFzc3dvcmQ=', 'Urban gardener passionate about houseplants and sustainable gardening practices.', 'Portland, OR', '8b'),
('robert.green@example.com', 'robertgreen', 'Robert', 'Green', 'cGFzc3dvcmQ=', 'Expert gardener with 20+ years of experience in organic farming.', 'Seattle, WA', '9a'),
('sarah.lee@example.com', 'sarahlee', 'Sarah', 'Lee', 'cGFzc3dvcmQ=', 'Beginner gardener learning about indoor plants and herb gardens.', 'Austin, TX', '8b');

-- Insert sample posts
INSERT INTO posts (user_id, title, content, tags, likes_count, comments_count) VALUES
((SELECT id FROM users WHERE username = 'robertgreen'), 'Companion Planting Strategies', 'I have been experimenting with companion planting this season and have seen amazing results. Marigolds really do keep pests away from my tomatoes! What companion planting combinations have worked well for you?', ARRAY['OrganicGardening', 'CompanionPlanting'], 124, 32),
((SELECT id FROM users WHERE username = 'sarahlee'), 'Help Identify This Plant', 'Can anyone help identify this plant? Found it growing in my garden and I am not sure if it is a weed or something I should keep.', ARRAY['PlantID', 'Help'], 45, 18);
