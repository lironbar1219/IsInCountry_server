# Deployment Guide - IsInCountry SDK

## Cloud Deployment Options

### Option 1: Railway (Recommended)
Railway is perfect for Flask + PostgreSQL applications with easy deployment.

#### Steps:
1. Create account at [railway.app](https://railway.app)
2. Install Railway CLI or use GitHub integration
3. Deploy using the files below

#### Benefits:
- Free PostgreSQL database
- Easy environment management
- Automatic HTTPS
- GitHub integration

### Option 2: Render
Free tier with PostgreSQL, good for production.

### Option 3: Vercel
Great for serverless deployment, requires some modifications for PostgreSQL.

---

## Railway Deployment (Recommended)

### 1. Create Railway Project Files

The files below are already created for Railway deployment.

### 2. Environment Variables on Railway

Set these environment variables in your Railway project:

```
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

### 3. Deploy Steps

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 4. Database Setup

Railway will provide PostgreSQL automatically. Run the data loader after deployment:

```bash
# After deployment, run this to load countries
railway run python data_loader.py
```

---

## API Endpoints (Production)

Once deployed, your API will be available at:
- `https://your-app.railway.app/api/v1/health`
- `https://your-app.railway.app/api/v1/countries`
- `https://your-app.railway.app/api/v1/check` (POST)

---

## Android Integration

Use these endpoints in your Android library:

```java
public class IsInCountryAPI {
    private static final String BASE_URL = "https://your-app.railway.app/api/v1/";
    
    // Implementation details in android-library/
}
```
