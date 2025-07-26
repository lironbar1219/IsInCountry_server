# IsInCountry API Service

A REST API service for checking if coordinates are within specific country boundaries. This server provides the backend for the IsInCountry SDK.

## 🚀 Quick Start

### 1. Local Development

```bash
# Start PostgreSQL database
cd server
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Load sample countries
python data_loader.py

# Start the server
python app.py
```

### 2. Deploy to Cloud

```bash
# Deploy to Railway (Recommended)
./deploy.sh

# Or see DEPLOYMENT.md for other options
```

## 📁 Project Structure

```
isincountry-api/
├── server/                 # Python Flask API
│   ├── app.py             # Main Flask application
│   ├── data_loader.py     # Load country data
│   ├── auto_loader.py     # Auto-fetch countries from APIs
│   ├── requirements.txt   # Python dependencies
│   ├── docker-compose.yml # PostgreSQL setup
│   └── .env              # Environment variables
├── docs/                  # API documentation
├── DEPLOYMENT.md         # Deployment guide
└── deployment files      # Cloud deployment configs
```

## 🌐 API Endpoints

### Health Check
```http
GET /api/v1/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-26T15:29:30.469402",
  "version": "1.0.0"
}
```

### Get All Countries
```http
GET /api/v1/countries
```
**Response:**
```json
{
  "success": true,
  "count": 25,
  "data": [
    {
      "id": 6,
      "country_code": "ISR",
      "country_name": "Israel",
      "created_at": null,
      "updated_at": null
    }
  ]
}
```

### Check Coordinates
```http
POST /api/v1/check
Content-Type: application/json

{
    "latitude": 31.7683,
    "longitude": 35.2137,
    "country_code": "ISR"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "is_inside_country": true,
    "latitude": 31.7683,
    "longitude": 35.2137,
    "country_code": "ISR",
    "country_name": "Israel",
    "checked_at": "2025-07-26T15:30:15.123456"
  }
}
```

### Add New Country
```http
POST /api/v1/countries
Content-Type: application/json

{
    "country_code": "NLD",
    "country_name": "Netherlands",
    "polygon_data": "{\"type\":\"Polygon\",\"coordinates\":[[[3.4,50.8],[7.2,50.8],[7.2,53.6],[3.4,53.6],[3.4,50.8]]]}"
}
```

## 🗄️ Database

The service includes **25+ countries** with their boundary polygons:
- 🇺🇸 USA, 🇨🇦 Canada, 🇲🇽 Mexico
- 🇮🇱 Israel, 🇩🇪 Germany, 🇫🇷 France, 🇬🇧 UK
- 🇯🇵 Japan, 🇨🇳 China, 🇮🇳 India
- 🇦🇺 Australia, 🇧🇷 Brazil, 🇷🇺 Russia
- And many more...

### Auto-Load More Countries
```bash
# Load countries automatically from external APIs
python server/auto_loader.py natural-earth    # ~250 countries
python server/auto_loader.py nominatim 50     # 50 countries from OpenStreetMap
```

## 🚀 Deployment Options

### Railway (Recommended)
```bash
./deploy.sh  # Choose option 1
```

### Manual Deployment
1. **Render**: Free PostgreSQL + Web Service
2. **Heroku**: Classic choice with add-ons
3. **Vercel**: Serverless (requires DB modifications)
4. **AWS/GCP**: Full control

See `DEPLOYMENT.md` for detailed instructions.

## 🧪 Testing

### Test API Locally
```bash
cd server
python data_loader.py test
```

### Manual API Testing
```bash
# Health check
curl http://localhost:5000/api/v1/health

# Get countries
curl http://localhost:5000/api/v1/countries

# Test Jerusalem, Israel
curl -X POST http://localhost:5000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"latitude": 31.7683, "longitude": 35.2137, "country_code": "ISR"}'

# Test New York, USA
curl -X POST http://localhost:5000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060, "country_code": "USA"}'
```

## 📊 Supported Countries

Currently includes 25+ countries with more available via auto-loader:

| Code | Country | Code | Country |
|------|---------|------|---------|
| USA | United States | ISR | Israel |
| CAN | Canada | DEU | Germany |
| MEX | Mexico | ITA | Italy |
| GBR | United Kingdom | ESP | Spain |
| FRA | France | JPN | Japan |
| CHN | China | IND | India |
| AUS | Australia | BRA | Brazil |
| RUS | Russia | ZAF | South Africa |
| EGY | Egypt | TUR | Turkey |
| ARG | Argentina | NLD | Netherlands |
| CHE | Switzerland | SWE | Sweden |
| NOR | Norway | DNK | Denmark |
| POL | Poland | ... | and more |

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
CORS_ORIGINS=* 
```

### Local Development (.env file)
```bash
DATABASE_URL=postgresql://isincountry_user:isincountry_password@localhost:5433/isincountry_db
SECRET_KEY=dev-secret-key
FLASK_ENV=development
FLASK_DEBUG=True
```

## 🏗️ Algorithm

The service uses **Shapely** library for geometric operations:

1. **Point-in-Polygon Algorithm**: Uses ray casting algorithm
2. **Polygon Support**: Handles both simple polygons and multi-polygons
3. **Coordinate System**: WGS84 (latitude/longitude)
4. **Performance**: Optimized for real-time queries

## 📚 Client SDKs

This API service can be consumed by various client libraries:

- **Android SDK**: `isincountry-android` (separate repository)
- **iOS SDK**: `isincountry-ios` (future)
- **JavaScript SDK**: `isincountry-js` (future)
- **Python Client**: Direct HTTP requests

### Example Android Usage
```java
// In your Android app
IsInCountrySDK sdk = new IsInCountrySDK(context, "https://your-api.railway.app/api/v1/");
sdk.isInCountry("ISR", callback);
```

## 📖 API Documentation

### Error Responses
```json
{
  "success": false,
  "error": "Country with code XYZ not found"
}
```

### Status Codes
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (country not found)
- `405` - Method Not Allowed
- `500` - Internal Server Error

## 🔗 Related Projects

- **Android SDK**: [isincountry-android](https://github.com/yourusername/isincountry-android)
- **Example Apps**: [isincountry-examples](https://github.com/yourusername/isincountry-examples)
- **Documentation**: [GitHub Pages](https://yourusername.github.io/isincountry-api)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit a pull request

---

**Ready to deploy?** Run `./deploy.sh` and choose your preferred cloud provider!

## 📁 Project Structure

```
isincountry-sdk/
├── server/                 # Python Flask API
│   ├── app.py             # Main Flask application
│   ├── data_loader.py     # Load country data
│   ├── auto_loader.py     # Auto-fetch countries from APIs
│   └── requirements.txt   # Python dependencies
├── android-library/       # Android library
│   └── src/main/java/com/isincountry/sdk/
├── android-example/       # Example Android app
├── docs/                  # Documentation
└── deployment files       # Cloud deployment configs
```

## 🌐 API Endpoints

Once deployed, your API provides:

### Health Check
```http
GET /api/v1/health
```

### Get All Countries
```http
GET /api/v1/countries
```

### Check Coordinates
```http
POST /api/v1/check
Content-Type: application/json

{
    "latitude": 31.7683,
    "longitude": 35.2137,
    "country_code": "ISR"
}
```

## �️ Database

The service includes **25+ countries** with their boundary polygons:
- 🇺🇸 USA, 🇨🇦 Canada, 🇲🇽 Mexico
- 🇮🇱 Israel, 🇩🇪 Germany, 🇫🇷 France, 🇬🇧 UK
- 🇯🇵 Japan, 🇨🇳 China, 🇮🇳 India
- 🇦🇺 Australia, 🇧🇷 Brazil, 🇷🇺 Russia
- And many more...

### Auto-Load More Countries
```bash
# Load countries automatically from external APIs
python server/auto_loader.py natural-earth    # ~250 countries
python server/auto_loader.py nominatim 50     # 50 countries from OpenStreetMap
```

## 🚀 Deployment Options

### Railway (Recommended)
```bash
./deploy.sh  # Choose option 1
```

### Manual Deployment
1. **Render**: Free PostgreSQL + Web Service
2. **Heroku**: Classic choice with add-ons
3. **Vercel**: Serverless (requires DB modifications)
4. **AWS/GCP**: Full control

See `DEPLOYMENT.md` for detailed instructions.

## 📱 Android Integration

### Basic Usage
```java
IsInCountrySDK sdk = new IsInCountrySDK(context);

// Check current country (based on device locale)
sdk.isInCurrentCountry(callback);

// Check specific country
sdk.isInCountry("USA", callback);

// Check specific coordinates
sdk.checkCoordinatesInCountry(40.7128, -74.0060, "USA", callback);
```

### Advanced Usage
```java
// Get all available countries
sdk.getAvailableCountries(new CountriesCallback() {
    @Override
    public void onResult(List<Country> countries) {
        // Display countries list
    }
});
```

## 🧪 Testing

### Test API Locally
```bash
cd server
python data_loader.py test
```

### Test Coordinates
```bash
# Test Jerusalem, Israel
curl -X POST http://localhost:5000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"latitude": 31.7683, "longitude": 35.2137, "country_code": "ISR"}'
```

## 📊 Supported Countries

Currently includes 25+ countries with more available via auto-loader:

| Code | Country | Code | Country |
|------|---------|------|---------|
| USA | United States | ISR | Israel |
| CAN | Canada | DEU | Germany |
| MEX | Mexico | ITA | Italy |
| GBR | United Kingdom | ESP | Spain |
| FRA | France | JPN | Japan |
| CHN | China | IND | India |
| AUS | Australia | BRA | Brazil |
| RUS | Russia | ... | and more |

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key
FLASK_ENV=production
PORT=5000
```

### Android Permissions
```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.INTERNET" />
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md)
- [API Documentation](docs/api.md)
- [Android Library Guide](docs/android.md)
- [Contributing](CONTRIBUTING.md)

## 🔗 Links

- **API Service**: Deploy to cloud provider
- **Android Library**: Publish to JitPack
- **Example App**: Demo application
- **Documentation**: GitHub Pages

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit a pull request

---

**Ready to deploy?** Run `./deploy.sh` and choose your preferred cloud provider!