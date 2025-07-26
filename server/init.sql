-- Initialize the database with country polygons table
CREATE EXTENSION IF NOT EXISTS postgis;

-- Countries table to store country information and polygon boundaries
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(3) UNIQUE NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    polygon_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster country code lookups
CREATE INDEX IF NOT EXISTS idx_country_code ON countries(country_code);

-- Insert sample data for testing (simplified polygons)
INSERT INTO countries (country_code, country_name, polygon_data) VALUES
('USA', 'United States', '{"type":"Polygon","coordinates":[[[-125,25],[-66,25],[-66,49],[-125,49],[-125,25]]]}'),
('CAN', 'Canada', '{"type":"Polygon","coordinates":[[[-140,42],[-52,42],[-52,84],[-140,84],[-140,42]]]}'),
('MEX', 'Mexico', '{"type":"Polygon","coordinates":[[[-118,14],[-86,14],[-86,33],[-118,33],[-118,14]]]}')
ON CONFLICT (country_code) DO NOTHING;
