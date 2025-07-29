# Country API Service

A REST API service for checking if coordinates are within specific country boundaries us## Local Developmentng precise polygon geometry. Features include a comprehensive admin portal for database management and country administration.

## Features

- **Point-in-Polygon Validation**: Check if coordinates fall within country boundaries
- **Admin Portal**: Web-based interface for managing countries and admin users
- **Database Management**: Initialize, clean, and manage country data
- **Authentication System**: Secure admin access with session management
- **RESTful API**: Clean endpoints for integration
- **Production Ready**: Deployed on Railway with PostgreSQL

## API Endpoints

### Public API

**Base URL**: `https://poetic-elegance-production-2172.up.railway.app`

#### Check Coordinate
```http
POST /api/v1/check
Content-Type: application/json

{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "country_code": "USA"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "is_inside_country": true,
    "latitude": 40.7128,
    "longitude": -74.0060,
    "country_code": "USA",
    "country_name": "United States",
    "checked_at": "2025-07-29T18:15:30.123456"
  }
}
```

#### Get Countries
```http
GET /api/v1/countries
```

#### Service Status
```http
GET /api/v1/status
```

#### Initialize Database
```http
POST /api/v1/init-db
```

## Admin Portal

Access the admin portal at `/admin` to manage your country database.

### Admin Features

- **Dashboard**: Overview with statistics and quick actions
- **Country Management**: Add, remove, and view countries with polygon data
- **Admin Management**: Add and remove admin users
- **Database Tools**: Initialize and clean database
- **Secure Authentication**: Login system with session management

### Admin Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/admin` | GET | Admin portal dashboard |
| `/admin/login` | GET/POST | Admin login page |
| `/admin/logout` | GET | Logout and redirect |
| `/admin/add-country` | POST | Add new country with polygon |
| `/admin/remove-country` | POST | Remove country by code |
| `/admin/add-admin` | POST | Create new admin user |
| `/admin/remove-admin` | POST | Remove admin user |
| `/admin/admins` | GET | List all admin users |
| `/admin/clean-db` | POST | Clear all country data |
| `/admin/init-admins` | POST | Initialize admin table |
| `/admin/stats` | GET | Get database statistics |

### Admin Setup

1. **Initialize Admin Table** (first time only):
   ```bash
   curl -X POST https://poetic-elegance-production-2172.up.railway.app/admin/init-admins
   ```

2. **Login**: Go to `/admin` and use the default credentials
3. **Manage**: Use the web interface to add countries and manage users

## Country Data Format

Countries are stored with GeoJSON polygon data:

```json
{
  "country_code": "USA",
  "country_name": "United States",
  "polygon_data": "{\"type\": \"Polygon\", \"coordinates\": [[[-125, 25], [-66, 25], [-66, 49], [-125, 49], [-125, 25]]]}"
}
```

## �️ Local Development

### Prerequisites
- Python 3.9+
- PostgreSQL
- Git

### Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/lironbar1219/IsInCountry_server.git
   cd IsInCountry_server
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and secret key
   ```

4. **Run Server**
   ```bash
   cd server
   python app.py
   ```

5. **Initialize Database**
   ```bash
   # Add sample countries
   curl -X POST http://localhost:5000/api/v1/init-db

   # Setup admin access
   curl -X POST http://localhost:5000/admin/init-admins
   ```

## Deployment

### Railway (Recommended)

1. **Connect Repository**: Link your GitHub repo to Railway
2. **Environment Variables**: Set `DATABASE_URL` and `SECRET_KEY`
3. **Deploy**: Railway automatically deploys from your main branch

The service includes:
- `Procfile` for Railway deployment
- `requirements.txt` for Python dependencies
- `Dockerfile` for containerization
- Health checks and monitoring

## Database Schema

### Countries Table
```sql
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(3) UNIQUE NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    polygon_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Admins Table
```sql
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **Session Management**: Flask-Login for admin authentication
- **Input Validation**: Comprehensive validation for all endpoints
- **CORS Configuration**: Configurable cross-origin resource sharing
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection attacks

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "error": "Error description"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (admin routes)
- `404`: Not Found
- `500`: Server Error

## Integration Example

```python
import requests

# Check if coordinates are in a country
response = requests.post('https://poetic-elegance-production-2172.up.railway.app/api/v1/check', json={
    "latitude": 40.7128,
    "longitude": -74.0060,
    "country_code": "USA"
})

result = response.json()
if result['success']:
    print(f"Is inside {result['data']['country_name']}: {result['data']['is_inside_country']}")
```

## Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key
FLASK_ENV=production
PORT=5000
```

### Local Development (.env file)
```bash
DATABASE_URL=postgresql://isincountry_user:isincountry_password@localhost:5433/isincountry_db
SECRET_KEY=dev-secret-key
FLASK_ENV=development
FLASK_DEBUG=True
```

## Testing

### API Testing Examples
```bash
# Health check
curl http://localhost:5000/api/v1/health

# Get all countries
curl http://localhost:5000/api/v1/countries

# Test Jerusalem, Israel coordinates
curl -X POST http://localhost:5000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"latitude": 31.7683, "longitude": 35.2137, "country_code": "ISR"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes and test thoroughly
4. Submit a pull request

---
