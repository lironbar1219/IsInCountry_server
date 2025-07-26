#!/usr/bin/env python3
"""
Auto-loader for country boundary data from external sources.
This script fetches real country polygon data from public APIs and datasets.
"""

import json
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import time
from urllib.parse import quote

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

def fetch_countries_from_rest_api():
    """Fetch list of countries from REST Countries API"""
    try:
        print("📡 Fetching countries from REST Countries API...")
        response = requests.get("https://restcountries.com/v3.1/all?fields=name,cca3,cca2", timeout=30)
        response.raise_for_status()
        
        countries = response.json()
        print(f"✅ Found {len(countries)} countries")
        return countries
    except requests.RequestException as e:
        print(f"❌ Error fetching countries: {e}")
        return []

def fetch_country_geometry_from_nominatim(country_name, country_code):
    """Fetch country boundary from Nominatim (OpenStreetMap)"""
    try:
        # URL encode the country name
        encoded_name = quote(country_name)
        
        # Query Nominatim for country boundary
        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            'q': encoded_name,
            'format': 'geojson',
            'polygon_geojson': '1',
            'addressdetails': '1',
            'limit': '1',
            'countrycodes': country_code.lower() if len(country_code) == 2 else None
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        print(f"🔍 Fetching geometry for {country_name} ({country_code})...")
        
        response = requests.get(url, params=params, timeout=30, headers={
            'User-Agent': 'IsInCountrySDK/1.0 (https://github.com/yourusername/isincountry-sdk)'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('features') and len(data['features']) > 0:
                feature = data['features'][0]
                geometry = feature.get('geometry')
                
                if geometry and geometry.get('type') in ['Polygon', 'MultiPolygon']:
                    return geometry
                else:
                    print(f"⚠️  No suitable geometry found for {country_name}")
            else:
                print(f"⚠️  No results found for {country_name}")
        else:
            print(f"❌ HTTP {response.status_code} for {country_name}")
            
    except requests.RequestException as e:
        print(f"❌ Error fetching geometry for {country_name}: {e}")
    except Exception as e:
        print(f"❌ Unexpected error for {country_name}: {e}")
    
    return None

def simplify_geometry(geometry, tolerance=0.1):
    """Simplify geometry to reduce complexity (basic implementation)"""
    # This is a basic simplification - in production you might want to use
    # more sophisticated algorithms like Douglas-Peucker
    if geometry['type'] == 'Polygon':
        coords = geometry['coordinates'][0]  # Take exterior ring
        if len(coords) > 20:  # If too many points, take every nth point
            step = max(1, len(coords) // 15)
            simplified = coords[::step]
            # Ensure the polygon is closed
            if simplified[0] != simplified[-1]:
                simplified.append(simplified[0])
            return {
                'type': 'Polygon',
                'coordinates': [simplified]
            }
    elif geometry['type'] == 'MultiPolygon':
        # For multipolygon, take the largest polygon
        largest_polygon = max(geometry['coordinates'], key=lambda x: len(x[0]))
        coords = largest_polygon[0]  # Take exterior ring of largest polygon
        if len(coords) > 20:
            step = max(1, len(coords) // 15)
            simplified = coords[::step]
            if simplified[0] != simplified[-1]:
                simplified.append(simplified[0])
            return {
                'type': 'Polygon',
                'coordinates': [simplified]
            }
    
    return geometry

def load_countries_automatically(limit=50):
    """Automatically load countries from external APIs"""
    print("🌍 Auto-loading country boundary data...")
    print("=" * 60)
    
    # Fetch list of countries
    countries = fetch_countries_from_rest_api()
    if not countries:
        print("❌ Could not fetch country list")
        return
    
    # Connect to database
    conn = connect_to_db()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    cursor = conn.cursor()
    loaded_count = 0
    skipped_count = 0
    failed_count = 0
    
    try:
        for i, country in enumerate(countries[:limit]):
            if loaded_count >= limit:
                break
                
            # Get country info
            country_name = country['name']['common']
            country_code = country.get('cca3', '')  # Use 3-letter code
            
            if not country_code or len(country_code) != 3:
                print(f"⚠️  Skipping {country_name} - invalid country code")
                skipped_count += 1
                continue
            
            # Check if country already exists
            cursor.execute(
                "SELECT id FROM countries WHERE country_code = %s", 
                (country_code,)
            )
            
            if cursor.fetchone():
                print(f"⏭️  {country_name} ({country_code}) already exists, skipping...")
                skipped_count += 1
                continue
            
            # Fetch geometry
            cca2_code = country.get('cca2', '')
            geometry = fetch_country_geometry_from_nominatim(country_name, cca2_code)
            
            if geometry:
                # Simplify geometry to reduce size
                simplified_geometry = simplify_geometry(geometry)
                
                # Insert into database
                cursor.execute("""
                    INSERT INTO countries (country_code, country_name, polygon_data)
                    VALUES (%s, %s, %s)
                """, (
                    country_code,
                    country_name,
                    json.dumps(simplified_geometry)
                ))
                
                print(f"✅ Added {country_name} ({country_code})")
                loaded_count += 1
                
                # Rate limiting - be nice to the API
                time.sleep(1)
            else:
                print(f"❌ Failed to get geometry for {country_name}")
                failed_count += 1
            
            # Progress update
            if (i + 1) % 10 == 0:
                print(f"📊 Progress: {i + 1}/{min(len(countries), limit)} countries processed")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"🎉 Auto-loading completed!")
        print(f"✅ Successfully loaded: {loaded_count} countries")
        print(f"⏭️  Skipped (already exist): {skipped_count} countries")
        print(f"❌ Failed to load: {failed_count} countries")
        print(f"📊 Total in database: {loaded_count + skipped_count} countries")
        
    except Exception as e:
        print(f"❌ Error during auto-loading: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def fetch_from_natural_earth():
    """Fetch country data from Natural Earth (alternative method)"""
    print("🌍 Fetching from Natural Earth...")
    
    # Natural Earth provides different resolution datasets
    urls = {
        'low': 'https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson',
        'medium': 'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson'
    }
    
    try:
        response = requests.get(urls['medium'], timeout=60)
        response.raise_for_status()
        
        geojson_data = response.json()
        print(f"✅ Fetched {len(geojson_data['features'])} countries from Natural Earth")
        
        return geojson_data['features']
    except requests.RequestException as e:
        print(f"❌ Error fetching from Natural Earth: {e}")
        return []

def load_from_natural_earth():
    """Load countries from Natural Earth dataset"""
    print("🌍 Loading countries from Natural Earth dataset...")
    print("=" * 60)
    
    features = fetch_from_natural_earth()
    if not features:
        print("❌ Could not fetch Natural Earth data")
        return
    
    conn = connect_to_db()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    cursor = conn.cursor()
    loaded_count = 0
    skipped_count = 0
    
    try:
        for feature in features:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry')
            
            # Get country info from properties
            country_code = properties.get('ISO_A3') or properties.get('ADM0_A3')
            country_name = properties.get('NAME') or properties.get('ADMIN')
            
            if not country_code or not country_name or len(country_code) != 3:
                continue
            
            # Check if country already exists
            cursor.execute(
                "SELECT id FROM countries WHERE country_code = %s", 
                (country_code,)
            )
            
            if cursor.fetchone():
                print(f"⏭️  {country_name} ({country_code}) already exists, skipping...")
                skipped_count += 1
                continue
            
            if geometry and geometry.get('type') in ['Polygon', 'MultiPolygon']:
                # Simplify geometry
                simplified_geometry = simplify_geometry(geometry)
                
                # Insert into database
                cursor.execute("""
                    INSERT INTO countries (country_code, country_name, polygon_data)
                    VALUES (%s, %s, %s)
                """, (
                    country_code,
                    country_name,
                    json.dumps(simplified_geometry)
                ))
                
                print(f"✅ Added {country_name} ({country_code})")
                loaded_count += 1
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"🎉 Natural Earth loading completed!")
        print(f"✅ Successfully loaded: {loaded_count} countries")
        print(f"⏭️  Skipped (already exist): {skipped_count} countries")
        
    except Exception as e:
        print(f"❌ Error during Natural Earth loading: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import sys
    
    print("🌍 IsInCountry Auto-Loader")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "nominatim":
            # Load from Nominatim/OpenStreetMap
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            load_countries_automatically(limit)
        elif sys.argv[1] == "natural-earth":
            # Load from Natural Earth
            load_from_natural_earth()
        else:
            print("Usage:")
            print("  python auto_loader.py nominatim [limit]     # Load from Nominatim (default: 50)")
            print("  python auto_loader.py natural-earth        # Load from Natural Earth")
    else:
        print("Available loading methods:")
        print("1. Nominatim (OpenStreetMap) - More accurate but slower")
        print("2. Natural Earth - Faster but lower resolution")
        print("")
        print("Usage:")
        print("  python auto_loader.py nominatim [limit]     # Load from Nominatim (default: 50)")
        print("  python auto_loader.py natural-earth        # Load from Natural Earth")
        print("")
        print("Examples:")
        print("  python auto_loader.py natural-earth        # Fast way to load ~250 countries")
        print("  python auto_loader.py nominatim 20         # Load 20 countries from Nominatim")
