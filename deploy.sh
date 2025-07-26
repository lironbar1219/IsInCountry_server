#!/bin/bash

echo "🚀 IsInCountry SDK Deployment Script"
echo "====================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo "📋 Deployment Options:"
echo "1. Railway (Recommended)"
echo "2. Render"
echo "3. Heroku"
echo "4. Manual deployment guide"

read -p "Choose deployment option (1-4): " option

case $option in
    1)
        echo "🚄 Deploying to Railway..."
        echo ""
        echo "📝 Steps:"
        echo "1. Login to Railway"
        echo "2. Create new project"
        echo "3. Add PostgreSQL service"
        echo "4. Deploy the application"
        echo ""

        # Login to Railway
        echo "🔐 Logging in to Railway..."
        railway login

        # Initialize project
        echo "📦 Initializing Railway project..."
        railway init

        # Add PostgreSQL
        echo "🗄️  Adding PostgreSQL database..."
        railway add postgresql

        # Deploy
        echo "🚀 Deploying application..."
        railway up

        echo ""
        echo "✅ Deployment complete!"
        echo "🔗 Your API will be available at the Railway URL"
        echo "📊 Load sample data with: railway run python server/data_loader.py"
        ;;
    2)
        echo "🎨 Deploying to Render..."
        echo ""
        echo "📝 Manual steps for Render:"
        echo "1. Go to https://render.com"
        echo "2. Create new Web Service"
        echo "3. Connect your GitHub repo"
        echo "4. Use these settings:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn --bind 0.0.0.0:\$PORT server.app:app"
        echo "5. Add PostgreSQL database"
        echo "6. Set environment variables"
        ;;
    3)
        echo "🟣 Deploying to Heroku..."
        echo ""
        echo "📝 Manual steps for Heroku:"
        echo "1. Install Heroku CLI"
        echo "2. heroku create your-app-name"
        echo "3. heroku addons:create heroku-postgresql:hobby-dev"
        echo "4. git push heroku main"
        ;;
    4)
        echo "📖 Opening deployment guide..."
        echo ""
        echo "Check DEPLOYMENT.md for detailed instructions"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "🔧 Don't forget to:"
echo "1. Set environment variables in your cloud service"
echo "2. Load sample country data"
echo "3. Test the API endpoints"
echo "4. Update the Android library with the new API URL"
