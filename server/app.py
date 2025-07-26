from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import json
from shapely.geometry import Point, Polygon
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# Database Models
class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(3), unique=True, nullable=False)
    country_name = db.Column(db.String(100), nullable=False)
    polygon_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'country_code': self.country_code,
            'country_name': self.country_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Helper Functions
def is_point_in_polygon(lat, lon, polygon_data):
    """
    Check if a point (lat, lon) is inside a polygon.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        polygon_data (str): JSON string containing polygon coordinates

    Returns:
        bool: True if point is inside polygon, False otherwise
    """
    try:
        # Parse polygon data
        polygon_json = json.loads(polygon_data)

        # Create Shapely Point and Polygon objects
        point = Point(lon, lat)  # Note: Shapely uses (x, y) = (lon, lat)

        if polygon_json['type'] == 'Polygon':
            # Single polygon
            coordinates = polygon_json['coordinates'][0]  # Exterior ring
            polygon = Polygon(coordinates)
            return polygon.contains(point)
        elif polygon_json['type'] == 'MultiPolygon':
            # Multiple polygons
            for polygon_coords in polygon_json['coordinates']:
                polygon = Polygon(polygon_coords[0])  # Exterior ring of each polygon
                if polygon.contains(point):
                    return True
            return False
        else:
            return False

    except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
        print(f"Error processing polygon data: {e}")
        return False

# API Routes
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/v1/countries', methods=['GET'])
def get_countries():
    """Get list of all available countries"""
    try:
        countries = Country.query.all()
        return jsonify({
            'success': True,
            'data': [country.to_dict() for country in countries],
            'count': len(countries)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/countries/<country_code>', methods=['GET'])
def get_country(country_code):
    """Get specific country information"""
    try:
        country = Country.query.filter_by(country_code=country_code.upper()).first()
        if not country:
            return jsonify({
                'success': False,
                'error': f'Country with code {country_code} not found'
            }), 404

        return jsonify({
            'success': True,
            'data': country.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/check', methods=['POST'])
def check_coordinate():
    """
    Main endpoint to check if a coordinate is inside a country.

    Expected JSON payload:
    {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "country_code": "USA"
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        required_fields = ['latitude', 'longitude', 'country_code']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Extract and validate coordinates
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid latitude or longitude format'
            }), 400

        # Validate coordinate ranges
        if not (-90 <= latitude <= 90):
            return jsonify({
                'success': False,
                'error': 'Latitude must be between -90 and 90'
            }), 400

        if not (-180 <= longitude <= 180):
            return jsonify({
                'success': False,
                'error': 'Longitude must be between -180 and 180'
            }), 400

        country_code = data['country_code'].upper()

        # Find country in database
        country = Country.query.filter_by(country_code=country_code).first()
        if not country:
            return jsonify({
                'success': False,
                'error': f'Country with code {country_code} not found'
            }), 404

        # Check if point is inside country polygon
        is_inside = is_point_in_polygon(latitude, longitude, country.polygon_data)

        return jsonify({
            'success': True,
            'data': {
                'is_inside_country': is_inside,
                'latitude': latitude,
                'longitude': longitude,
                'country_code': country_code,
                'country_name': country.country_name,
                'checked_at': datetime.utcnow().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/v1/countries', methods=['POST'])
def add_country():
    """Add a new country with polygon data"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        required_fields = ['country_code', 'country_name', 'polygon_data']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Validate polygon data is valid JSON
        try:
            json.loads(data['polygon_data'])
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'Invalid polygon_data JSON format'
            }), 400

        # Check if country already exists
        existing_country = Country.query.filter_by(
            country_code=data['country_code'].upper()
        ).first()

        if existing_country:
            return jsonify({
                'success': False,
                'error': f'Country with code {data["country_code"]} already exists'
            }), 409

        # Create new country
        new_country = Country(
            country_code=data['country_code'].upper(),
            country_name=data['country_name'],
            polygon_data=data['polygon_data']
        )

        db.session.add(new_country)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': new_country.to_dict(),
            'message': 'Country added successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()

    # Run the application
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
