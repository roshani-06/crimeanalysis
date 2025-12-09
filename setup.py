import os
import pandas as pd

def setup_project():
    # Create directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    print("Project structure created successfully!")
    print("Please ensure your crime_data.csv file is in the data/ directory")

if __name__ == '__main__':
    setup_project()