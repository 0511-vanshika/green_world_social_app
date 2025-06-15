-- Update plant_analyses table to include stress and sunlight data
ALTER TABLE plant_analyses 
ADD COLUMN IF NOT EXISTS stress_level VARCHAR(50),
ADD COLUMN IF NOT EXISTS stress_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS sunlight_exposure VARCHAR(50),
ADD COLUMN IF NOT EXISTS sunlight_warning TEXT,
ADD COLUMN IF NOT EXISTS overall_health_score DECIMAL(3,2);

-- Update existing records with sample data
UPDATE plant_analyses SET 
  stress_level = 'Low',
  stress_score = 0.25,
  sunlight_exposure = 'Adequate',
  sunlight_warning = NULL,
  overall_health_score = 0.85
WHERE stress_level IS NULL;
