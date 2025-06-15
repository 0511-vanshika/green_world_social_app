-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  avatar_url TEXT,
  bio TEXT,
  location VARCHAR(100),
  growing_zone VARCHAR(10),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create posts table
CREATE TABLE IF NOT EXISTS posts (
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

-- Create plant_analyses table for dehydration detection
CREATE TABLE IF NOT EXISTS plant_analyses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  plant_name VARCHAR(255),
  dehydration_level VARCHAR(50) NOT NULL,
  confidence_score DECIMAL(3,2),
  recommendations TEXT[],
  watering_schedule TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create follows table
CREATE TABLE IF NOT EXISTS follows (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  follower_id UUID REFERENCES users(id) ON DELETE CASCADE,
  following_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(follower_id, following_id)
);

-- Create likes table
CREATE TABLE IF NOT EXISTS likes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, post_id)
);

-- Create comments table
CREATE TABLE IF NOT EXISTS comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert sample data
INSERT INTO users (email, username, first_name, last_name, password_hash, bio, location, growing_zone) VALUES
('jane.doe@example.com', 'plantlover123', 'Jane', 'Doe', '$2b$10$example_hash', 'Urban gardener passionate about houseplants and sustainable gardening practices.', 'Portland, OR', '8b'),
('robert.green@example.com', 'robertgreen', 'Robert', 'Green', '$2b$10$example_hash', 'Expert gardener with 20+ years of experience in organic farming.', 'Seattle, WA', '9a'),
('sarah.lee@example.com', 'sarahlee', 'Sarah', 'Lee', '$2b$10$example_hash', 'Beginner gardener learning about indoor plants and herb gardens.', 'Austin, TX', '8b'),
('michael.park@example.com', 'michaelpark', 'Michael', 'Park', '$2b$10$example_hash', 'Hydroponic enthusiast and urban farming advocate.', 'Chicago, IL', '6a'),
('emma.johnson@example.com', 'emmajohnson', 'Emma', 'Johnson', '$2b$10$example_hash', 'Sustainable gardening consultant and permaculture designer.', 'Denver, CO', '7a');

-- Insert sample posts
INSERT INTO posts (user_id, title, content, tags, likes_count, comments_count) VALUES
((SELECT id FROM users WHERE username = 'robertgreen'), 'Companion Planting Strategies', 'I''ve been experimenting with companion planting this season and have seen amazing results. Marigolds really do keep pests away from my tomatoes! What companion planting combinations have worked well for you?', ARRAY['OrganicGardening', 'CompanionPlanting'], 124, 32),
((SELECT id FROM users WHERE username = 'emmajohnson'), 'Sustainable Watering Practices', 'With drought conditions becoming more common, I''ve been implementing water-saving techniques in my garden. Rain barrels and drip irrigation have made a huge difference! What methods are you using to conserve water?', ARRAY['WaterConservation', 'Sustainability'], 87, 19),
((SELECT id FROM users WHERE username = 'sarahlee'), 'Help Identify This Plant', 'Can anyone help identify this plant? Found it growing in my garden and I''m not sure if it''s a weed or something I should keep.', ARRAY['PlantID', 'Help'], 45, 18);
