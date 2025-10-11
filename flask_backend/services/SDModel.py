import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import pickle
import warnings
warnings.filterwarnings('ignore')

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
donor_csv = os.path.join(BASE_DIR, "donor_fake.csv")
receiver_csv = os.path.join(BASE_DIR, "receiver_fake.csv")



np.random.seed(42)

def preprocess_data(df, target_col):
    """Preprocess data for machine learning"""
    # Separate features and target
    X = df.drop([target_col] + [col for col in df.columns if col.endswith('_id')], axis=1)
    y = df[target_col]
    
    # Encode categorical variables
    label_encoders = {}
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le
    
    return X, y, label_encoders

class FoodDonationPredictor:
    """Food Donation Supply & Demand Prediction Model"""
    
    def __init__(self):
        self.donor_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.receiver_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.donor_encoders = {}
        self.receiver_encoders = {}
        self.is_trained = False
        self.training_progress = 0
        self.donor_data_size = 0
        self.receiver_data_size = 0
        
    def train(self, donor_csv_path, receiver_csv_path):
        """Train both donor and receiver models from CSV files"""
        
        self.training_progress = 0
        print("Training Progress: 0% - Loading data...")
        
        # Load data
        try:
            donor_data = pd.read_csv(donor_csv_path)
            receiver_data = pd.read_csv(receiver_csv_path)
            self.donor_data_size = len(donor_data)
            self.receiver_data_size = len(receiver_data)
            self.training_progress = 10
            print(f"Training Progress: 10% - Loaded {len(donor_data)} donor records and {len(receiver_data)} receiver records")
        except Exception as e:
            raise Exception(f"Error loading data: {e}")
        
        # Since we don't have target variables, we'll use a simple heuristic-based approach
        # Generate synthetic targets based on feature patterns
        self.training_progress = 20
        print("Training Progress: 20% - Generating target variables...")
        
        # For donors: higher chance of donation on weekends and with higher past donation count
        donor_data['will_donate'] = 0
        weekend_mask = donor_data['day_of_week'].isin(['Saturday', 'Sunday'])
        high_donation_mask = donor_data['past_donation_count'] > donor_data['past_donation_count'].median()
        high_customers_mask = donor_data['avg_customers_served'] > donor_data['avg_customers_served'].median()
        
        donor_data.loc[weekend_mask | (high_donation_mask & high_customers_mask), 'will_donate'] = 1
        
        # For receivers: higher chance of request with higher past request count and during events
        receiver_data['will_request'] = 0
        event_mask = receiver_data['seasonal_event'] == 1
        high_request_mask = receiver_data['past_request_count'] > receiver_data['past_request_count'].median()
        shelter_kitchen_mask = receiver_data['receiver_type'].isin(['shelter', 'community kitchen'])
        
        receiver_data.loc[event_mask | (high_request_mask & shelter_kitchen_mask), 'will_request'] = 1
        
        self.training_progress = 30
        print("Training Progress: 30% - Preprocessing donor data...")
        
        # Train donor model
        print("\nTraining Donor Model...")
        X_donor, y_donor, donor_encoders = preprocess_data(donor_data, 'will_donate')
        self.donor_encoders = donor_encoders
        
        self.training_progress = 40
        print("Training Progress: 40% - Splitting donor data...")
        
        X_train, X_test, y_train, y_test = train_test_split(X_donor, y_donor, test_size=0.2, random_state=42)
        
        self.training_progress = 50
        print("Training Progress: 50% - Training donor model...")
        
        self.donor_model.fit(X_train, y_train)
        
        donor_accuracy = accuracy_score(y_test, self.donor_model.predict(X_test))
        self.training_progress = 60
        print(f"Training Progress: 60% - Donor Model Accuracy: {donor_accuracy:.3f}")
        
        # Train receiver model
        self.training_progress = 70
        print("Training Progress: 70% - Preprocessing receiver data...")
        print("\nTraining Receiver Model...")
        
        X_receiver, y_receiver, receiver_encoders = preprocess_data(receiver_data, 'will_request')
        self.receiver_encoders = receiver_encoders
        
        self.training_progress = 80
        print("Training Progress: 80% - Splitting receiver data...")
        
        X_train, X_test, y_train, y_test = train_test_split(X_receiver, y_receiver, test_size=0.2, random_state=42)
        
        self.training_progress = 90
        print("Training Progress: 90% - Training receiver model...")
        
        self.receiver_model.fit(X_train, y_train)
        
        receiver_accuracy = accuracy_score(y_test, self.receiver_model.predict(X_test))
        
        self.training_progress = 100
        self.is_trained = True
        print(f"Training Progress: 100% - Training Complete!")
        print(f"Receiver Model Accuracy: {receiver_accuracy:.3f}")
        
        return {
            "donor_accuracy": donor_accuracy,
            "receiver_accuracy": receiver_accuracy,
            "donor_data_size": self.donor_data_size,
            "receiver_data_size": self.receiver_data_size,
            "training_progress": self.training_progress,
            "status": "training_complete"
        }
    
    def predict_donor(self, features):
        """
        Predict donor donation probability
        
        Args:
            features (dict): {
                'day_of_week': str,        # 'Monday', 'Tuesday', etc.
                'avg_customers_served': int,
                'past_donation_count': int
            }
        
        Returns:
            dict: {
                'will_donate': bool,
                'probability': float,
                'confidence': str
            }
        """
        
        if not self.is_trained:
            return {"error": "Model not trained. Call train() first."}
        
        try:
            # Encode categorical variables
            day_encoded = self.donor_encoders['day_of_week'].transform([features['day_of_week']])[0]
            
            # Create feature array
            feature_array = np.array([[
                day_encoded,
                features['avg_customers_served'], 
                features['past_donation_count']
            ]])
            
            prediction = self.donor_model.predict(feature_array)[0]
            probability = self.donor_model.predict_proba(feature_array)[0][1]
            
            # Determine confidence level
            if probability > 0.8 or probability < 0.2:
                confidence = "high"
            elif probability > 0.6 or probability < 0.4:
                confidence = "medium"
            else:
                confidence = "low"
            
            return {
                '_id': features["_id"],
                'will_donate': bool(prediction),
                'probability': float(round(probability, 3)),
                'confidence': confidence
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {e}"}
    
    def predict_receiver(self, features):
        """
        Predict receiver food request probability
        
        Args:
            features (dict): {
                'receiver_type': str,      # 'orphanage', 'old-age home', 'shelter', 'community kitchen'
                'day_of_week': str,        # 'Monday', 'Tuesday', etc.
                'seasonal_event': int,     # 0 or 1
                'past_request_count': int
            }
        
        Returns:
            dict: {
                'will_request': bool,
                'probability': float,
                'confidence': str
            }
        """
        
        if not self.is_trained:
            return {"error": "Model not trained. Call train() first."}
        
        try:
            # Encode categorical variables
            receiver_type_encoded = self.receiver_encoders['receiver_type'].transform([features['receiver_type']])[0]
            day_encoded = self.receiver_encoders['day_of_week'].transform([features['day_of_week']])[0]
            
            # Create feature array
            feature_array = np.array([[
                receiver_type_encoded, 
                day_encoded, 
                features['seasonal_event'], 
                features['past_request_count']
            ]])
            
            prediction = self.receiver_model.predict(feature_array)[0]
            probability = self.receiver_model.predict_proba(feature_array)[0][1]
            
            # Determine confidence level
            if probability > 0.8 or probability < 0.2:
                confidence = "high"
            elif probability > 0.6 or probability < 0.4:
                confidence = "medium"
            else:
                confidence = "low"
            
            return {
                'will_request': bool(prediction),
                'probability': float(round(probability, 3)),
                'confidence': confidence
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {e}"}
    
    def get_training_status(self):
        """Get current training status and progress"""
        return {
            "is_trained": self.is_trained,
            "training_progress": self.training_progress,
            "donor_data_size": self.donor_data_size,
            "receiver_data_size": self.receiver_data_size,
            "total_data_size": self.donor_data_size + self.receiver_data_size,
            "status": "complete" if self.is_trained else "in_progress" if self.training_progress > 0 else "not_started"
        }
    
    def save_model(self, filepath):
        """Save the trained model to a file"""
        
        if not self.is_trained:
            return {"error": "Model not trained. Cannot save untrained model."}
        
        try:
            model_data = {
                'donor_model': self.donor_model,
                'receiver_model': self.receiver_model,
                'donor_encoders': self.donor_encoders,
                'receiver_encoders': self.receiver_encoders,
                'is_trained': self.is_trained,
                'training_progress': self.training_progress,
                'donor_data_size': self.donor_data_size,
                'receiver_data_size': self.receiver_data_size
            }
            
            with open(filepath, 'wb') as file:
                pickle.dump(model_data, file)
            
            return {
                "status": "success",
                "message": f"Model saved successfully to {filepath}",
                "file_path": filepath
            }
            
        except Exception as e:
            return {"error": f"Failed to save model: {e}"}
    
    def load_model(self, filepath):
        """Load a trained model from a file"""
        
        try:
            with open(filepath, 'rb') as file:
                model_data = pickle.load(file)
            
            self.donor_model = model_data['donor_model']
            self.receiver_model = model_data['receiver_model']
            self.donor_encoders = model_data['donor_encoders']
            self.receiver_encoders = model_data['receiver_encoders']
            self.is_trained = model_data['is_trained']
            self.training_progress = model_data['training_progress']
            self.donor_data_size = model_data['donor_data_size']
            self.receiver_data_size = model_data['receiver_data_size']
            
            return {
                "status": "success",
                "message": f"Model loaded successfully from {filepath}",
                "donor_data_size": self.donor_data_size,
                "receiver_data_size": self.receiver_data_size,
                "is_trained": self.is_trained
            }
            
        except Exception as e:
            return {"error":e}
    
    def predict_both(self, donor_features, receiver_features):
        """
        Predict both donor donation and receiver request
        
        Returns:
            dict: {
                'donor': {...},
                'receiver': {...},
                'match_probability': float
            }
        """
        
        donor_result = self.predict_donor(donor_features)
        receiver_result = self.predict_receiver(receiver_features)
        
        # Calculate match probability
        if 'error' not in donor_result and 'error' not in receiver_result:
            match_prob = (donor_result['probability'] + receiver_result['probability']) / 2
        else:
            match_prob = 0.0
        
        return {
            'donorId' : donor_features["_id"],
            'receiverId': receiver_features["_id"],
            # 'donor': donor_result,
            # 'receiver': receiver_result,
            'match_probability': float(round(match_prob, 3))
        }

# Example usage
if __name__ == "__main__":
    # Initialize model
    model = FoodDonationPredictor()
    
    # Train model (replace with your CSV paths)
    try:
        training_result = model.train(donor_csv.csv, receiver_csv.csv)
        print(f"Training result: {training_result}")
        
        # Save the trained model
        save_result = model.save_model("food_donation_modelT.pkl")
        print(f"Save result: {save_result}")
        
    except Exception as e:
        print(f"Training failed: {e}")
        exit()
    
    # Example of loading a saved model
    # new_model = FoodDonationPredictor()
    # load_result = new_model.load_model("food_donation_model.pkl")
    # print(f"Load result: {load_result}")
    
    # Example predictions
    print("\n" + "="*50)
    print("EXAMPLE PREDICTIONS")
    print("="*50)
    
    # Donor prediction
    donor_input = {
        '_Id':"Hx4567",
        'day_of_week': 'Saturday',
        'avg_customers_served': 350,
        'past_donation_count': 12
    }
    
    donor_prediction = model.predict_donor(donor_input)
    print(f"\nDonor Prediction:")
    print(f"Input: {donor_input}")
    print(f"Output: {donor_prediction}")
    
    # Receiver prediction
    receiver_input = {
        '_Id':"recv123",
        'receiver_type': 'shelter',
        'day_of_week': 'Sunday',
        'seasonal_event': 1,
        'past_request_count': 18
    }
    
    receiver_prediction = model.predict_receiver(receiver_input)
    print(f"\nReceiver Prediction:")
    print(f"Input: {receiver_input}")
    print(f"Output: {receiver_prediction}")
    
    # Combined prediction
    combined_prediction = model.predict_both(donor_input, receiver_input)
    print(f"\nCombined Prediction:")
    print(f"Output: {combined_prediction}")