import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class CrimePredictor:
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.features = ['States/UTs', 'District', 'Year']
        
    def prepare_data(self, crime_type='Total_Crimes'):
        """Prepare data for training"""
        df = pd.read_csv('data/crime_data.csv')
        
        # Filter relevant columns
        crime_data = df[['States/UTs', 'District', 'Year', crime_type]].copy()
        
        # Handle missing values
        crime_data = crime_data.dropna()
        
        # Encode categorical variables
        for col in ['States/UTs', 'District']:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
            crime_data[col] = self.encoders[col].fit_transform(crime_data[col])
        
        X = crime_data[['States/UTs', 'District', 'Year']]
        y = crime_data[crime_type]
        
        return X, y
    
    def train_model(self, crime_type='Total_Crimes'):
        """Train model for specific crime type"""
        X, y = self.prepare_data(crime_type)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        self.models[crime_type] = model
        
        return {'mae': mae, 'r2': r2, 'model': model}
    
    def predict(self, state, district, crime_type='Total_Crimes', year=2015):
        """Predict crime for given parameters"""
        if crime_type not in self.models:
            self.train_model(crime_type)
        
        # Encode state and district
        state_encoded = self.encoders['States/UTs'].transform([state])[0]
        district_encoded = self.encoders['District'].transform([district])[0]
        
        # Prepare input
        input_data = np.array([[state_encoded, district_encoded, year]])
        
        # Predict
        prediction = self.models[crime_type].predict(input_data)[0]
        
        return max(0, prediction)  # Ensure non-negative prediction

def train_crime_model():
    """Train the crime prediction model"""
    predictor = CrimePredictor()
    
    # Train for total crimes
    results = predictor.train_model('Total_Crimes')
    print(f"Model trained - MAE: {results['mae']:.2f}, R2: {results['r2']:.2f}")
    
    # Save model
    joblib.dump(predictor, 'models/crime_model.pkl')
    
    return predictor

def predict_crime(state, district, crime_type='Total_Crimes', year=2015):
    """Predict crime rate"""
    try:
        predictor = joblib.load('models/crime_model.pkl')
        prediction = predictor.predict(state, district, crime_type, year)
        
        return {
            'state': state,
            'district': district,
            'crime_type': crime_type,
            'year': year,
            'predicted_crimes': round(prediction, 2),
            'confidence': 'high' if prediction > 0 else 'low'
        }
    except:
        # Fallback prediction
        return {
            'state': state,
            'district': district,
            'crime_type': crime_type,
            'year': year,
            'predicted_crimes': 100,  # Default fallback
            'confidence': 'medium'
        }
def get_crime_insights(state='All', district='All', crime_type='Total_Crimes', year=2014):
    """Generate crime insights and policy recommendations based on specific parameters"""
    try:
        df = pd.read_csv('data/crime_data.csv')
        
        # Filter data based on parameters
        filtered_df = df.copy()
        
        if state != 'All':
            filtered_df = filtered_df[filtered_df['States/UTs'] == state]
        
        if district != 'All':
            filtered_df = filtered_df[filtered_df['District'] == district]
        
        if year != 'All':
            filtered_df = filtered_df[filtered_df['Year'] == int(year)]
        
        insights = {
            'top_crimes': {},
            'trends': {},
            'recommendations': [],
            'crime_analysis': {},
            'area_info': {
                'state': state,
                'district': district,
                'crime_type': crime_type,
                'year': year
            }
        }
        
        if filtered_df.empty:
            insights['recommendations'] = [
                "No specific data available for the selected filters",
                "Consider broader analysis with 'All' states or districts",
                "Check data availability for different years"
            ]
            return insights
        
        # Analyze specific crime type
        if crime_type in filtered_df.columns:
            crime_data = filtered_df[crime_type]
            total_crimes = crime_data.sum()
            avg_crimes = crime_data.mean()
            max_crimes = crime_data.max()
            
            insights['crime_analysis'] = {
                'total': int(total_crimes),
                'average': float(avg_crimes),
                'maximum': int(max_crimes),
                'trend': 'increasing' if total_crimes > avg_crimes else 'decreasing'
            }
        
        # Generate specific recommendations based on crime type and severity
        recommendations = generate_specific_recommendations(filtered_df, crime_type, state, district)
        insights['recommendations'] = recommendations
        
        # Get top 3 crimes for the area
        crime_columns = ['Murder', 'Rape', 'Kidnapping', 'Theft', 'Burglary', 'Dacoity', 'Riots', 
                       'Forgery', 'Counterfeiting', 'Arson', 'Acid attack', 'Dowry Deaths', 'Stalking']
        
        available_crimes = [col for col in crime_columns if col in filtered_df.columns]
        if available_crimes:
            total_crimes_by_type = filtered_df[available_crimes].sum()
            top_3_crimes = total_crimes_by_type.nlargest(3)
            insights['top_crimes'] = top_3_crimes.to_dict()
        
        return insights
        
    except Exception as e:
        print(f"Error in get_crime_insights: {e}")
        return get_fallback_insights()

def generate_specific_recommendations(df, crime_type, state, district):
    """Generate specific policy recommendations based on crime data"""
    recommendations = []
    
    # Calculate crime statistics
    if crime_type in df.columns:
        crime_data = df[crime_type]
        total_crimes = crime_data.sum()
        avg_crimes = crime_data.mean()
        
        # Crime-type specific recommendations
        if crime_type == 'Murder':
            if total_crimes > 100:
                recommendations.append("Establish specialized homicide investigation units")
                recommendations.append("Enhance forensic capabilities and quick response teams")
            recommendations.append("Strengthen community conflict resolution programs")
            recommendations.append("Improve witness protection programs")
            
        elif crime_type == 'Rape':
            if total_crimes > 50:
                recommendations.append("Set up fast-track courts for sexual assault cases")
                recommendations.append("Establish 24/7 women's helpline and support centers")
            recommendations.append("Implement comprehensive sex education in schools")
            recommendations.append("Enhance street lighting and public transport safety")
            
        elif crime_type == 'Theft':
            if total_crimes > 500:
                recommendations.append("Increase CCTV surveillance in commercial areas")
                recommendations.append("Launch community watch programs")
            recommendations.append("Improve property marking and registration systems")
            recommendations.append("Enhance patrol frequency in high-risk areas")
            
        elif crime_type == 'Burglary':
            if total_crimes > 300:
                recommendations.append("Promote smart home security systems")
                recommendations.append("Increase night patrols in residential areas")
            recommendations.append("Community awareness programs on home security")
            recommendations.append("Neighborhood watch initiatives")
            
        elif crime_type == 'Kidnapping':
            if total_crimes > 20:
                recommendations.append("Strengthen anti-human trafficking units")
                recommendations.append("Enhance border and transportation security")
            recommendations.append("Public awareness campaigns on child safety")
            recommendations.append("Improve emergency response systems")
            
        elif crime_type == 'Forgery':
            if total_crimes > 100:
                recommendations.append("Establish cyber crime and financial fraud cells")
                recommendations.append("Enhance document verification systems")
            recommendations.append("Public awareness on financial fraud prevention")
            recommendations.append("Strengthen inter-agency coordination for financial crimes")
            
        elif crime_type == 'Riots':
            if total_crimes > 50:
                recommendations.append("Develop community mediation programs")
                recommendations.append("Enhance rapid response teams for public order")
            recommendations.append("Inter-community dialogue initiatives")
            recommendations.append("Social media monitoring for hate speech prevention")
        
        # Severity-based recommendations
        if total_crimes > 1000:
            recommendations.append("Allocate additional police resources and funding")
            recommendations.append("Implement integrated command and control centers")
        elif total_crimes > 500:
            recommendations.append("Enhance police training and equipment")
            recommendations.append("Develop crime hotspot mapping and analysis")
        
        # Area-specific recommendations
        if state == 'Delhi UT':
            recommendations.append("Leverage Delhi's advanced surveillance infrastructure")
            recommendations.append("Coordinate with multiple police jurisdictions in NCT")
        elif state == 'Maharashtra':
            recommendations.append("Utilize Mumbai's established crime branch capabilities")
            recommendations.append("Metropolitan policing strategies implementation")
    
    # Add general recommendations if specific ones are few
    if len(recommendations) < 3:
        recommendations.extend([
            "Improve street lighting and public infrastructure",
            "Community policing and engagement programs",
            "Regular crime prevention awareness campaigns",
            "Enhanced police-community relations"
        ])
    
    return recommendations[:8]  # Return top 8 recommendations

def get_fallback_insights():
    """Return default insights when data is not available"""
    return {
        'top_crimes': {},
        'trends': {},
        'recommendations': [
            "Improve street lighting in high-crime areas",
            "Increase police patrol frequency", 
            "Community policing initiatives",
            "CCTV camera installation in sensitive areas",
            "Public awareness campaigns about crime prevention"
        ],
        'crime_analysis': {},
        'area_info': {}
    }