-- Add health and personal information fields to users table
-- Migration: 002_add_health_info

ALTER TABLE users ADD COLUMN height REAL;
ALTER TABLE users ADD COLUMN weight REAL;
ALTER TABLE users ADD COLUMN sex TEXT;
ALTER TABLE users ADD COLUMN body_type TEXT;
ALTER TABLE users ADD COLUMN bmi REAL;

