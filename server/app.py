from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from dotenv import load_dotenv
import os
import json
import bcrypt
try:
    from shapely.geometry import Point, Polygon
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("Warning: Shapely not available. Some geometry operations will be disabled.")
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Database Models - Define before create_app to avoid circular imports
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

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

def create_app():
    print("Creating Flask application...")
    app = Flask(__name__)

    # Configure logging first
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Configuring application...")

    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.logger.info("Database URL configured")

        # Initialize database extension only if URL is provided
        try:
            db.init_app(app)
            app.logger.info("Database extension initialized")
        except Exception as e:
            app.logger.error(f"Database initialization failed: {e}")
    else:
        app.logger.info("No database URL provided, skipping database setup")

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    try:
        CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))
        app.logger.info("CORS initialized")
    except Exception as e:
        app.logger.error(f"CORS initialization failed: {e}")

    # Routes
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint"""
        return jsonify({
            'message': 'Country API Service',
            'status': 'running',
            'version': '1.0.0',
            'endpoints': {
                'status': '/api/v1/status',
                'countries': '/api/v1/countries',
                'check': '/api/v1/check',
                'init-db': '/api/v1/init-db (POST)'
            }
        })

    @app.route('/api/v1/status', methods=['GET'])
    def status_check():
        """Simple status check endpoint without database dependency"""
        return jsonify({
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'service': 'Country API'
        })

    @app.route('/api/v1/init-db', methods=['POST'])
    def initialize_database():
        """Initialize database with tables and sample data"""
        try:
            # Create tables
            db.create_all()

            # Sample countries data
            sample_countries = [
                {
                    "country_code": "USA",
                    "country_name": "United States",
                    "polygon_data": '{"type": "Polygon", "coordinates": [[[-125, 25], [-66, 25], [-66, 49], [-125, 49], [-125, 25]]]}'
                },
                {
                    "country_code": "ISR",
                    "country_name": "Israel",
                    "polygon_data": '{"type": "Polygon", "coordinates": [[[34.2, 29.5], [35.9, 29.5], [35.9, 33.4], [34.2, 33.4], [34.2, 29.5]]]}'
                },
                {
                    "country_code": "FRA",
                    "country_name": "France",
                    "polygon_data": '{"type": "Polygon", "coordinates": [[[-5, 42], [8, 42], [8, 52], [-5, 52], [-5, 42]]]}'
                },
                {
                    "country_code": "DEU",
                    "country_name": "Germany",
                    "polygon_data": '{"type": "Polygon", "coordinates": [[[5.8, 47.3], [15.0, 47.3], [15.0, 55.1], [5.8, 55.1], [5.8, 47.3]]]}'
                },
                {
                    "country_code": "GBR",
                    "country_name": "United Kingdom",
                    "polygon_data": '{"type": "Polygon", "coordinates": [[[-8, 49], [2, 49], [2, 61], [-8, 61], [-8, 49]]]}'
                }
            ]

            # Add sample countries
            added_countries = []
            for country_data in sample_countries:
                existing = Country.query.filter_by(country_code=country_data["country_code"]).first()
                if not existing:
                    country = Country(
                        country_code=country_data["country_code"],
                        country_name=country_data["country_name"],
                        polygon_data=country_data["polygon_data"]
                    )
                    db.session.add(country)
                    added_countries.append(country_data["country_code"])

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Database initialized successfully',
                'tables_created': True,
                'countries_added': added_countries,
                'total_countries': len(added_countries)
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Database initialization failed: {str(e)}'
            }), 500

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

    # Admin Routes
    @app.route('/admin')
    def admin_redirect():
        """Redirect /admin to login page"""
        return redirect(url_for('admin_login'))

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Admin login page"""
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard'))

        form = LoginForm()
        if form.validate_on_submit():
            admin = Admin.query.filter_by(username=form.username.data).first()
            if admin and admin.check_password(form.password.data):
                login_user(admin)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password.', 'error')

        return render_template('login.html', form=form)

    @app.route('/admin/logout')
    @login_required
    def admin_logout():
        """Admin logout"""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('admin_login'))

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        """Admin dashboard"""
        return render_template('dashboard.html')

    @app.route('/admin/init-admins', methods=['POST'])
    def init_admins():
        """Initialize admin table with default admin - no auth required for initial setup"""
        try:
            # Create admin table if it doesn't exist
            db.create_all()

            # Check if any admin exists
            admin_count = Admin.query.count()
            if admin_count == 0:
                # Create default admin with your credentials
                default_admin = Admin(
                    username='liron1219',
                    email='liron@example.com'
                )
                default_admin.set_password('123456')
                db.session.add(default_admin)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': 'Admin table initialized successfully',
                    'default_admin': {
                        'username': 'liron1219',
                        'password': '123456'
                    }
                })
            else:
                return jsonify({
                    'success': True,
                    'message': f'Admin table already exists with {admin_count} admins'
                })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Failed to initialize admin table: {str(e)}'
            }), 500

    @app.route('/admin/init-admins-protected', methods=['POST'])
    @login_required
    def init_admins_protected():
        """Initialize admin table with default admin - requires authentication"""
        try:
            # Create admin table if it doesn't exist
            db.create_all()

            # Check if any admin exists
            admin_count = Admin.query.count()
            if admin_count == 0:
                # Create default admin
                default_admin = Admin(
                    username='admin',
                    email='admin@example.com'
                )
                default_admin.set_password('admin123')
                db.session.add(default_admin)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': 'Admin table initialized successfully',
                    'default_admin': {
                        'username': 'admin',
                        'password': 'admin123'
                    }
                })
            else:
                return jsonify({
                    'success': True,
                    'message': f'Admin table already exists with {admin_count} admins'
                })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Failed to initialize admin table: {str(e)}'
            }), 500

    @app.route('/admin/add-admin', methods=['POST'])
    @login_required
    def add_admin():
        """Add new admin"""
        try:
            data = request.get_json()

            if not data or not data.get('username') or not data.get('password'):
                return jsonify({
                    'success': False,
                    'error': 'Username and password are required'
                }), 400

            # Check if username already exists
            existing_admin = Admin.query.filter_by(username=data['username']).first()
            if existing_admin:
                return jsonify({
                    'success': False,
                    'error': 'Username already exists'
                }), 400

            # Create new admin
            new_admin = Admin(
                username=data['username'],
                email=data.get('email', '')
            )
            new_admin.set_password(data['password'])

            db.session.add(new_admin)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'Admin {data["username"]} created successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Failed to create admin: {str(e)}'
            }), 500

    @app.route('/admin/clean-db', methods=['POST'])
    @login_required
    def clean_database():
        """Clean all countries from database"""
        try:
            deleted_count = Country.query.count()
            Country.query.delete()
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'Database cleaned successfully. Removed {deleted_count} countries.'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Failed to clean database: {str(e)}'
            }), 500

    @app.route('/admin/add-country', methods=['POST'])
    @login_required
    def add_country():
        """Add new country"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400

            required_fields = ['country_code', 'country_name', 'polygon_data']
            missing_fields = [field for field in required_fields if not data.get(field)]

            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400

            # Validate JSON format of polygon data
            try:
                json.loads(data['polygon_data'])
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON format for polygon data'
                }), 400

            # Check if country already exists
            existing_country = Country.query.filter_by(country_code=data['country_code'].upper()).first()
            if existing_country:
                return jsonify({
                    'success': False,
                    'error': f'Country with code {data["country_code"]} already exists'
                }), 400

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
                'message': f'Country {data["country_code"]} added successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Failed to add country: {str(e)}'
            }), 500

    @app.route('/admin/remove-country', methods=['POST'])
    @login_required
    def remove_country():
        """Remove country"""
        try:
            data = request.get_json()

            if not data or not data.get('country_code'):
                return jsonify({
                    'success': False,
                    'error': 'Country code is required'
                }), 400

            country = Country.query.filter_by(country_code=data['country_code'].upper()).first()
            if not country:
                return jsonify({
                    'success': False,
                    'error': f'Country with code {data["country_code"]} not found'
                }), 404

            db.session.delete(country)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'Country {data["country_code"]} removed successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Failed to remove country: {str(e)}'
            }), 500

    @app.route('/admin/remove-admin', methods=['POST'])
    @login_required
    def remove_admin():
        """Remove admin user"""
        try:
            data = request.get_json()

            if not data or not data.get('username'):
                return jsonify({
                    'success': False,
                    'error': 'Username is required'
                }), 400

            # Prevent removing yourself
            if data['username'] == current_user.username:
                return jsonify({
                    'success': False,
                    'error': 'Cannot remove yourself'
                }), 400

            # Find admin to remove
            admin_to_remove = Admin.query.filter_by(username=data['username']).first()
            if not admin_to_remove:
                return jsonify({
                    'success': False,
                    'error': f'Admin with username {data["username"]} not found'
                }), 404

            # Check if this is the last admin
            admin_count = Admin.query.count()
            if admin_count <= 1:
                return jsonify({
                    'success': False,
                    'error': 'Cannot remove the last admin user'
                }), 400

            db.session.delete(admin_to_remove)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'Admin {data["username"]} removed successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Failed to remove admin: {str(e)}'
            }), 500

    @app.route('/admin/admins', methods=['GET'])
    @login_required
    def get_admins():
        """Get list of all admin users"""
        try:
            admins = Admin.query.all()
            return jsonify({
                'success': True,
                'data': [admin.to_dict() for admin in admins],
                'count': len(admins)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get admins: {str(e)}'
            }), 500

    @app.route('/admin/stats')
    @login_required
    def admin_stats():
        """Get admin statistics"""
        try:
            countries_count = Country.query.count()
            admins_count = Admin.query.count()

            return jsonify({
                'success': True,
                'data': {
                    'countries_count': countries_count,
                    'admins_count': admins_count
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get statistics: {str(e)}'
            }), 500

    app.logger.info("Application startup completed")
    return app

def init_db(app):
    """Initialize database tables - called separately to avoid blocking startup"""
    if not os.getenv('DATABASE_URL'):
        app.logger.info("No database URL provided, skipping table creation")
        return

    try:
        with app.app_context():
            db.create_all()
            app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {e}")

print("Starting Country API Service...")

# Create the app instance
try:
    app = create_app()
    print("Flask app created successfully")
except Exception as e:
    print(f"Failed to create Flask app: {e}")
    raise

# Initialize database in a separate call
try:
    init_db(app)
except Exception as e:
    print(f"Database initialization failed, but continuing: {e}")

# Helper Functions
def is_point_in_polygon(lat, lon, polygon_data):
    """Check if a point (lat, lon) is inside a polygon."""
    if not SHAPELY_AVAILABLE:
        print("Warning: Cannot perform point-in-polygon check without Shapely library")
        return False

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

if __name__ == '__main__':
    # Run the application in development mode
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
