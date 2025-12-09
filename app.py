from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
from ml_model import train_crime_model, predict_crime, get_crime_insights
import folium
from geopy.geocoders import Nominatim
import json

app = Flask(__name__)

# Load datasets
df = pd.read_csv('data/crime_data.csv')

# Load district coordinates
district_coords_df = pd.read_csv('data/district_coordinates.csv')

# Crime types from dataset
CRIME_TYPES = ['Murder', 'Rape', 'Kidnapping', 'Dacoity', 'Burglary', 'Theft', 
              'Riots', 'Forgery', 'Counterfeiting', 'Arson', 'Acid attack', 
              'Dowry Deaths', 'Stalking']

STATES = sorted(df['States/UTs'].unique())
DISTRICTS = sorted(df['District'].unique())

@app.route('/')
def index():
    return render_template('index.html', crime_types=CRIME_TYPES, states=STATES)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html', 
                        crime_types=CRIME_TYPES,
                        states=STATES)

@app.route('/api/analysis')
def api_analysis():
    """API endpoint for analysis data"""
    try:
        state = request.args.get('state')
        print(state)
        crime_type = request.args.get('crime_type')
        print(crime_type)
        year = request.args.get('year')
        print(year)
        
        analysis_data = perform_analysis(state, crime_type, year)
        return jsonify(analysis_data)
    except Exception as e:
        print(f"Error in api_analysis: {e}")
        return jsonify({
            'top_districts': [],
            'yearly_trend': {},
            'total_crimes': 0,
            'avg_crimes': 0
        })

@app.route('/prediction')
def prediction():
    return render_template('prediction.html', crime_types=CRIME_TYPES, states=STATES)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        state = data['state']
        district = data['district']
        crime_type = data['crime_type']
        year = data.get('year', 2015)
        
        prediction_result = predict_crime(state, district, crime_type, year)
        return jsonify(prediction_result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/hotspots')
def hotspots():
    return render_template('hotspots.html', 
                        crime_types=CRIME_TYPES,
                        states=STATES)

@app.route('/api/hotspots')
def api_hotspots():
    """API endpoint for hotspots data"""
    try:
        state = request.args.get('state', 'All')
        crime_type = request.args.get('crime_type', 'Total_Crimes')
        
        hotspots_data = get_crime_hotspots(state, crime_type)
        return jsonify(hotspots_data)
    except Exception as e:
        print(f"Error in api_hotspots: {e}")
        return jsonify({})

@app.route('/api/hotspots/coordinates')
def api_hotspots_coordinates():
    """API endpoint to get coordinates for hotspots"""
    try:
        state = request.args.get('state', 'All')
        crime_type = request.args.get('crime_type', 'Total_Crimes')
        
        hotspots_data = get_crime_hotspots_with_coordinates(state, crime_type)
        return jsonify(hotspots_data)
    except Exception as e:
        print(f"Error in api_hotspots_coordinates: {e}")
        return jsonify({})

@app.route('/policies')
def policies():
    return render_template('policies.html', 
                        states=STATES)

@app.route('/api/policies')
def api_policies():
    """API endpoint for policies data with filters"""
    state = request.args.get('state', 'All')
    district = request.args.get('district', 'All')
    crime_type = request.args.get('crime_type', 'Total_Crimes')
    year = request.args.get('year', '2014')
    
    insights = get_crime_insights(state, district, crime_type, year)
    return jsonify(insights)

@app.route('/get_districts')
def get_districts():
    state = request.args.get('state')
    if not state:
        return jsonify([])
    
    districts = sorted(df[df['States/UTs'] == state]['District'].unique())
    return jsonify(districts)

@app.route('/get_coordinates')
def get_coordinates():
    """API endpoint to get coordinates for a specific district"""
    state = request.args.get('state')
    district = request.args.get('district')
    
    if not state or not district:
        return jsonify({'error': 'State and district required'})
    
    coordinates = get_coordinates_for_district(state, district)
    return jsonify({
        'state': state,
        'district': district,
        'latitude': coordinates[0],
        'longitude': coordinates[1]
    })

def perform_analysis(state, crime_type, year):
    """Perform crime data analysis"""
    try:
        year = int(year)
        
        # Filter data based on state and year
        if state == 'All':
            filtered_data = df[df['Year'] == year]
        else:
            filtered_data = df[(df['States/UTs'] == state) & (df['Year'] == year)]
        
        # Handle case where crime_type column might not exist
        if crime_type not in filtered_data.columns:
            crime_type = 'Total_Crimes'

        # For "All" states, we want state-level totals, not district-level
        if state == 'All':
            # Group by state and sum the crime_type for each state
            state_totals = filtered_data.groupby('States/UTs')[crime_type].sum().reset_index()
            state_totals = state_totals.rename(columns={'States/UTs': 'District'})
            
            top_districts_data = state_totals.nlargest(10, crime_type)
        else:
            # For specific state, show top districts
            top_districts_data = filtered_data[['District', crime_type]].copy()
            top_districts_data[crime_type] = top_districts_data[crime_type].fillna(0)
            top_districts = top_districts_data.nlargest(10, crime_type)
        
        # Yearly trend
        if state == 'All':
            yearly_data = df.groupby('Year')[crime_type].sum()
        else:
            state_data = df[df['States/UTs'] == state]
            yearly_data = state_data.groupby('Year')[crime_type].sum()
        
        # Calculate statistics
        total_crimes = filtered_data[crime_type].sum()
        avg_crimes = filtered_data[crime_type].mean()

        return {
            'top_districts': top_districts_data.to_dict('records'),
            'yearly_trend': yearly_data.astype(int).to_dict(),
            'total_crimes': int(total_crimes),
            'avg_crimes': float(avg_crimes)
        }
    except Exception as e:
        print(f"Error in perform_analysis: {e}")
        return {
            'top_districts': [],
            'yearly_trend': {},
            'total_crimes': 0,
            'avg_crimes': 0
        }
    

def get_crime_hotspots(state, crime_type):
    """Get crime hotspots for mapping"""
    try:
        print(f"Getting hotspots for state: {state}, crime_type: {crime_type}")
        
        # Handle case where crime_type column might not exist
        if crime_type not in df.columns:
            crime_type = 'Total_Crimes'
            print(f"Crime type not found, using: {crime_type}")
        
        if state == 'All':
            # Aggregate by state and district
            grouped_data = df.groupby(['States/UTs', 'District'])[crime_type].sum().reset_index()
            
            # Create location keys and sort by crime count
            hotspots_dict = {}
            for _, row in grouped_data.iterrows():
                location_key = f"{row['States/UTs']},{row['District']}"
                # Ensure we have a valid number
                crime_count = row[crime_type]
                if pd.isna(crime_count):
                    crime_count = 0
                hotspots_dict[location_key] = int(crime_count)
            
            # Get top 30 hotspots
            sorted_hotspots = dict(sorted(hotspots_dict.items(), 
                                        key=lambda x: x[1], reverse=True)[:30])
            print(f"Found {len(sorted_hotspots)} hotspots for all states")
            return sorted_hotspots
        else:
            # Filter by state and aggregate by district
            state_data = df[df['States/UTs'] == state]
            if state_data.empty:
                print(f"No data found for state: {state}")
                return {}
                
            district_data = state_data.groupby('District')[crime_type].sum()
            
            hotspots_dict = {}
            for district, crime_count in district_data.items():
                # Ensure we have a valid number
                if pd.isna(crime_count):
                    crime_count = 0
                location_key = f"{state},{district}"
                hotspots_dict[location_key] = int(crime_count)
            
            # Get top 20 hotspots
            sorted_hotspots = dict(sorted(hotspots_dict.items(), 
                                       key=lambda x: x[1], reverse=True)[:20])
            print(f"Found {len(sorted_hotspots)} hotspots for state: {state}")
            return sorted_hotspots
    except Exception as e:
        print(f"Error in get_crime_hotspots: {e}")
        return {}

def get_crime_hotspots_with_coordinates(state, crime_type):
    """Get crime hotspots with coordinates"""
    try:
        hotspots = get_crime_hotspots(state, crime_type)
        hotspots_with_coords = {}
        
        for location, crime_count in hotspots.items():
            state_name, district_name = location.split(',', 1)
            coordinates = get_coordinates_for_district(state_name.strip(), district_name.strip())
            
            hotspots_with_coords[location] = {
                'crime_count': crime_count,
                'latitude': coordinates[0],
                'longitude': coordinates[1],
                'state': state_name.strip(),
                'district': district_name.strip()
            }
        
        return hotspots_with_coords
    except Exception as e:
        print(f"Error in get_crime_hotspots_with_coordinates: {e}")
        return {}

# Load district coordinates
def load_district_coordinates():
    try:
        coords_df = pd.read_csv('data/district_coordinates.csv')
        coordinates = {}
        for _, row in coords_df.iterrows():
            coordinates[f"{row['State']},{row['District']}"] = [row['Latitude'], row['Longitude']]
        return coordinates
    except Exception as e:
        print(f"Error loading coordinates: {e}")
        return {}

# Load coordinates at startup
district_coordinates = load_district_coordinates()

def get_coordinates_for_district(state, district):
    key = f"{state},{district}"
    return district_coordinates.get(key, [20.5937, 78.9629])  # Default to India center

if __name__ == '__main__':
    # Train model on startup
    try:
        train_crime_model()
        print("Model trained successfully")
    except Exception as e:
        print(f"Model training failed: {e}")
    app.run(debug=True, port=5000)