from ml_model import train_crime_model

if __name__ == '__main__':
    print("Training crime prediction model...")
    predictor = train_crime_model()
    print("Model training completed!")