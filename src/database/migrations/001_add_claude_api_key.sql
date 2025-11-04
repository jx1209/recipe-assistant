-- Migration: Add Claude API key storage to users table
-- Date: 2025-11-04

-- Add encrypted API key field to users table
ALTER TABLE users ADD COLUMN claude_api_key_encrypted TEXT DEFAULT NULL;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_has_api_key ON users(claude_api_key_encrypted) 
WHERE claude_api_key_encrypted IS NOT NULL;

