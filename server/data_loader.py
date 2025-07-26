#!/usr/bin/env python3
"""
Utility script to load country polygon data from various sources.
This script can be used to populate the database with real country boundary data.
"""

import json
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def connect_to_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5433",
            database="isincountry_db",
            user="isincountry_user",
            password="isincountry_password"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def load_sample_countries():
    """Load sample country data with simplified polygons"""
    countries_data = [
        {
            "country_code": "USA",
            "country_name": "United States",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [-125, 25], [-66, 25], [-66, 49], [-125, 49], [-125, 25]
                ]]
            }
        },
        {
            "country_code": "CAN",
            "country_name": "Canada",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [-140, 42], [-52, 42], [-52, 84], [-140, 84], [-140, 42]
                ]]
            }
        },
        {
            "country_code": "MEX",
            "country_name": "Mexico",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [-118, 14], [-86, 14], [-86, 33], [-118, 33], [-118, 14]
                ]]
            }
        },
        {
            "country_code": "GBR",
            "country_name": "United Kingdom",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [-8, 49], [2, 49], [2, 61], [-8, 61], [-8, 49]
                ]]
            }
        },
        {
            "country_code": "FRA",
            "country_name": "France",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [-5, 42], [8, 42], [8, 52], [-5, 52], [-5, 42]
                ]]
            }
        },
        {
            "country_code": "ISR",
            "country_name": "Israel",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [34.2, 29.5], [35.9, 29.5], [35.9, 33.4], [34.2, 33.4], [34.2, 29.5]
                ]]
            }
        },
        {
            "country_code": "DEU",
            "country_name": "Germany",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [5.8, 47.3], [15.0, 47.3], [15.0, 55.1], [5.8, 55.1], [5.8, 47.3]
                ]]
            }
        },
        {
            "country_code": "ITA",
            "country_name": "Italy",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [6.6, 35.5], [18.5, 35.5], [18.5, 47.1], [6.6, 47.1], [6.6, 35.5]
                ]]
            }
        },
        {
            "country_code": "ESP",
            "country_name": "Spain",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [-9.3, 35.9], [4.3, 35.9], [4.3, 43.8], [-9.3, 43.8], [-9.3, 35.9]
                ]]
            }
        },
        {
            "country_code": "JPN",
            "country_name": "Japan",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [123.0, 24.0], [146.0, 24.0], [146.0, 46.0], [123.0, 46.0], [123.0, 24.0]
                ]]
            }
        },
        {
            "country_code": "CHN",
            "country_name": "China",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [73.5, 18.2], [135.1, 18.2], [135.1, 53.6], [73.5, 53.6], [73.5, 18.2]
                ]]
            }
        },
        {
            "country_code": "IND",
            "country_name": "India",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [68.1, 6.8], [97.4, 6.8], [97.4, 37.1], [68.1, 37.1], [68.1, 6.8]
                ]]
            }
        },
        {
            "country_code": "AUS",
            "country_name": "Australia",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [113.3, -43.6], [153.6, -43.6], [153.6, -10.7], [113.3, -10.7], [113.3, -43.6]
                ]]
            }
        },
        {
            "country_code": "BRA",
            "country_name": "Brazil",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [-74.0, -33.8], [-34.8, -33.8], [-34.8, 5.3], [-74.0, 5.3], [-74.0, -33.8]
                ]]
            }
        },
        {
            "country_code": "RUS",
            "country_name": "Russia",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [19.6, 41.2], [180.0, 41.2], [180.0, 81.9], [19.6, 81.9], [19.6, 41.2]
                ]]
            }
        },
        {
            "country_code": "ZAF",
            "country_name": "South Africa",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [16.3, -35.0], [32.9, -35.0], [32.9, -22.1], [16.3, -22.1], [16.3, -35.0]
                ]]
            }
        },
        {
            "country_code": "EGY",
            "country_name": "Egypt",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [24.7, 22.0], [36.9, 22.0], [36.9, 31.7], [24.7, 31.7], [24.7, 22.0]
                ]]
            }
        },
        {
            "country_code": "TUR",
            "country_name": "Turkey",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [26.0, 35.8], [44.8, 35.8], [44.8, 42.1], [26.0, 42.1], [26.0, 35.8]
                ]]
            }
        },
        {
            "country_code": "ARG",
            "country_name": "Argentina",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [-73.6, -55.1], [-53.6, -55.1], [-53.6, -21.8], [-73.6, -21.8], [-73.6, -55.1]
                ]]
            }
        },
        {
            "country_code": "NLD",
            "country_name": "Netherlands",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [3.4, 50.8], [7.2, 50.8], [7.2, 53.6], [3.4, 53.6], [3.4, 50.8]
                ]]
            }
        },
        {
            "country_code": "CHE",
            "country_name": "Switzerland",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [6.0, 45.8], [10.5, 45.8], [10.5, 47.8], [6.0, 47.8], [6.0, 45.8]
                ]]
            }
        },
        {
            "country_code": "SWE",
            "country_name": "Sweden",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [11.1, 55.3], [24.2, 55.3], [24.2, 69.1], [11.1, 69.1], [11.1, 55.3]
                ]]
            }
        },
        {
            "country_code": "NOR",
            "country_name": "Norway",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [4.6, 58.0], [31.3, 58.0], [31.3, 71.2], [4.6, 71.2], [4.6, 58.0]
                ]]
            }
        },
        {
            "country_code": "DNK",
            "country_name": "Denmark",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [8.1, 54.6], [12.7, 54.6], [12.7, 57.8], [8.1, 57.8], [8.1, 54.6]
                ]]
            }
        },
        {
            "country_code": "POL",
            "country_name": "Poland",
            "polygon_data": {
                "type": "Polygon",
                "coordinates": [[
                    [14.1, 49.0], [24.1, 49.0], [24.1, 54.8], [14.1, 54.8], [14.1, 49.0]
                ]]
            }
        }
    ]

    conn = connect_to_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        for country in countries_data:
            # Check if country already exists
            cursor.execute(
                "SELECT id FROM countries WHERE country_code = %s",
                (country["country_code"],)
            )

            if cursor.fetchone():
                print(f"Country {country['country_code']} already exists, skipping...")
                continue

            # Insert new country
            cursor.execute("""
                INSERT INTO countries (country_code, country_name, polygon_data)
                VALUES (%s, %s, %s)
            """, (
                country["country_code"],
                country["country_name"],
                json.dumps(country["polygon_data"])
            ))

            print(f"Added country: {country['country_name']} ({country['country_code']})")

        conn.commit()
        print("Sample countries loaded successfully!")

    except Exception as e:
        print(f"Error loading countries: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def test_coordinate_check():
    """Test the coordinate checking functionality"""
    test_coordinates = [
        {"lat": 40.7128, "lon": -74.0060, "country": "USA", "expected": True},   # New York
        {"lat": 45.4215, "lon": -75.6972, "country": "CAN", "expected": True},   # Ottawa
        {"lat": 19.4326, "lon": -99.1332, "country": "MEX", "expected": True},   # Mexico City
        {"lat": 51.5074, "lon": -0.1278, "country": "GBR", "expected": True},    # London
        {"lat": 48.8566, "lon": 2.3522, "country": "FRA", "expected": True},     # Paris
        {"lat": 31.7683, "lon": 35.2137, "country": "ISR", "expected": True},    # Jerusalem, Israel
        {"lat": 52.5200, "lon": 13.4050, "country": "DEU", "expected": True},    # Berlin, Germany
        {"lat": 41.9028, "lon": 12.4964, "country": "ITA", "expected": True},    # Rome, Italy
        {"lat": 40.4168, "lon": -3.7038, "country": "ESP", "expected": True},    # Madrid, Spain
        {"lat": 35.6762, "lon": 139.6503, "country": "JPN", "expected": True},   # Tokyo, Japan
        {"lat": 39.9042, "lon": 116.4074, "country": "CHN", "expected": True},   # Beijing, China
        {"lat": 28.6139, "lon": 77.2090, "country": "IND", "expected": True},    # New Delhi, India
        {"lat": -33.8688, "lon": 151.2093, "country": "AUS", "expected": True},  # Sydney, Australia
        {"lat": -15.7939, "lon": -47.8828, "country": "BRA", "expected": True},  # Brasília, Brazil
        {"lat": 55.7558, "lon": 37.6173, "country": "RUS", "expected": True},    # Moscow, Russia
        {"lat": 40.7128, "lon": -74.0060, "country": "CAN", "expected": False},  # New York in Canada (should fail)
        {"lat": 31.7683, "lon": 35.2137, "country": "USA", "expected": False},   # Jerusalem in USA (should fail)
    ]

    print("\nTesting coordinate checks...")

    for test in test_coordinates:
        try:
            response = requests.post('http://localhost:5000/api/v1/check', json={
                'latitude': test['lat'],
                'longitude': test['lon'],
                'country_code': test['country']
            })

            if response.status_code == 200:
                result = response.json()
                is_inside = result['data']['is_inside_country']
                status = "✓" if is_inside == test['expected'] else "✗"
                print(f"{status} {test['lat']}, {test['lon']} in {test['country']}: {is_inside}")
            else:
                print(f"✗ Error testing {test['lat']}, {test['lon']}: {response.status_code}")

        except requests.RequestException as e:
            print(f"✗ Request error: {e}")

if __name__ == "__main__":
    print("IsInCountry Data Loader")
    print("=" * 50)

    # Load sample countries
    load_sample_countries()

    # Test API (make sure server is running)
    print("\nTo test the API, make sure the server is running and then run:")
    print("python data_loader.py test")

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_coordinate_check()
