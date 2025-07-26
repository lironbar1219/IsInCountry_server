#!/bin/bash

# IsInCountry Server Setup Script

echo "🚀 Setting up IsInCountry Server..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Start PostgreSQL with Docker Compose
echo "📦 Starting PostgreSQL database..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip3 install -r requirements.txt

# Load sample data
echo "📊 Loading sample country data..."
python3 data_loader.py

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Start the server: python3 app.py"
echo "2. Test the API: curl http://localhost:5000/api/v1/health"
echo "3. Access database admin: http://localhost:8080"
echo "   - System: PostgreSQL"
echo "   - Server: postgres"
echo "   - Username: isincountry_user"
echo "   - Password: isincountry_password"
echo "   - Database: isincountry_db"
