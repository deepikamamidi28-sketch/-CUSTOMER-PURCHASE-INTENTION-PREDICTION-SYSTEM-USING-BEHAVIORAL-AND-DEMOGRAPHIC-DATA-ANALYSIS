"""
Customer Behavioral Analysis Utilities
Provides utilities for customer segmentation, behavior analysis, and dataset generation
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

class CustomerSegmentationAnalyzer:
    """
    Analyzes customer behavior and performs segmentation
    """
    
    def __init__(self, df):
        """Initialize the analyzer with customer data"""
        self.df = df
        self.scaler = StandardScaler()
        
    def segment_customers(self, n_clusters=4):
        """Perform customer segmentation using K-Means"""
        X = self.df.drop('Purchase_Intention', axis=1)
        X_scaled = self.scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        self.df['Segment'] = clusters
        
        return clusters
    
    def analyze_segment_characteristics(self):
        """Analyze characteristics of each customer segment"""
        segment_analysis = {}
        
        for segment in self.df['Segment'].unique():
            segment_data = self.df[self.df['Segment'] == segment]
            
            segment_analysis[segment] = {
                'Size': len(segment_data),
                'Percentage': len(segment_data) / len(self.df) * 100,
                'Avg_Age': segment_data['Age'].mean(),
                'Avg_Income': segment_data['Income'].mean(),
                'Avg_Browsing_Hours': segment_data['Browsing_Hours'].mean(),
                'Avg_Product_Views': segment_data['Product_Views'].mean(),
                'Avg_Cart_Additions': segment_data['Cart_Additions'].mean(),
                'Purchase_Rate': segment_data['Purchase_Intention'].mean() * 100
            }
        
        return segment_analysis
    
    def identify_high_value_customers(self, threshold_percentile=75):
        """Identify high-value customers based on purchase behavior"""
        high_value_threshold = self.df['Avg_Order_Value'].quantile(threshold_percentile / 100)
        high_value_mask = self.df['Avg_Order_Value'] >= high_value_threshold
        
        high_value_customers = self.df[high_value_mask]
        
        return high_value_customers, high_value_threshold
    
    def analyze_purchase_drivers(self):
        """Analyze key drivers of purchase intention"""
        purchasers = self.df[self.df['Purchase_Intention'] == 1]
        non_purchasers = self.df[self.df['Purchase_Intention'] == 0]
        
        drivers = {}
        
        for col in self.df.drop(['Purchase_Intention', 'Segment'], axis=1).columns:
            purchaser_mean = purchasers[col].mean()
            non_purchaser_mean = non_purchasers[col].mean()
            
            drivers[col] = {
                'Purchaser_Mean': purchaser_mean,
                'Non_Purchaser_Mean': non_purchaser_mean,
                'Difference': purchaser_mean - non_purchaser_mean,
                'Ratio': purchaser_mean / (non_purchaser_mean + 1e-8)
            }
        
        return drivers
    
    def get_customer_lifetime_value(self):
        """Calculate customer lifetime value metrics"""
        clv_metrics = {
            'Avg_CLV': (self.df['Avg_Order_Value'] * self.df['Previous_Purchases']).mean(),
            'Max_CLV': (self.df['Avg_Order_Value'] * self.df['Previous_Purchases']).max(),
            'Min_CLV': (self.df['Avg_Order_Value'] * self.df['Previous_Purchases']).min(),
            'Median_CLV': (self.df['Avg_Order_Value'] * self.df['Previous_Purchases']).median()
        }
        
        return clv_metrics


class CustomerBehaviorPredictor:
    """
    Predicts customer behavior and engagement patterns
    """
    
    def __init__(self, df):
        """Initialize the predictor"""
        self.df = df
        
    def predict_engagement_level(self):
        """Predict customer engagement level"""
        engagement_score = (
            0.2 * (self.df['Browsing_Hours'] / self.df['Browsing_Hours'].max()) +
            0.25 * (self.df['Product_Views'] / self.df['Product_Views'].max()) +
            0.25 * (self.df['Website_Visits'] / self.df['Website_Visits'].max()) +
            0.15 * (self.df['Email_Opens'] / self.df['Email_Opens'].max()) +
            0.15 * (self.df['Cart_Additions'] / self.df['Cart_Additions'].max())
        )
        
        engagement_level = pd.cut(engagement_score, bins=3, labels=['Low', 'Medium', 'High'])
        
        return engagement_level, engagement_score
    
    def predict_churn_risk(self):
        """Predict customer churn risk"""
        # Customers with low engagement and no recent purchases are at higher risk
        churn_risk = (
            0.4 * (1 - self.df['Website_Visits'] / self.df['Website_Visits'].max()) +
            0.3 * (1 - self.df['Email_Opens'] / self.df['Email_Opens'].max()) +
            0.3 * (1 - self.df['Browsing_Hours'] / self.df['Browsing_Hours'].max())
        )
        
        churn_level = pd.cut(churn_risk, bins=3, labels=['Low', 'Medium', 'High'])
        
        return churn_level, churn_risk
    
    def predict_upsell_opportunity(self):
        """Predict upsell opportunity for customers"""
        upsell_score = (
            0.3 * (self.df['Previous_Purchases'] / self.df['Previous_Purchases'].max()) +
            0.3 * (self.df['Avg_Order_Value'] / self.df['Avg_Order_Value'].max()) +
            0.2 * (self.df['Product_Views'] / self.df['Product_Views'].max()) +
            0.2 * (self.df['Cart_Additions'] / self.df['Cart_Additions'].max())
        )
        
        upsell_level = pd.cut(upsell_score, bins=3, labels=['Low', 'Medium', 'High'])
        
        return upsell_level, upsell_score


def generate_and_save_customer_datasets(output_dir='/home/ubuntu'):
    """
    Generate and save all sample customer datasets
    """
    print("Generating customer behavioral datasets...")
    
    # Generate customer dataset
    from customer_purchase_prediction import generate_customer_dataset
    
    df = generate_customer_dataset(n_samples=1000)
    
    # Save raw dataset
    print("  Saving raw customer dataset...")
    df.to_csv(f'{output_dir}/customer_data.csv', index=False)
    print(f"  ✓ Raw dataset saved")
    
    # Perform segmentation
    print("  Performing customer segmentation...")
    analyzer = CustomerSegmentationAnalyzer(df.copy())
    segments = analyzer.segment_customers(n_clusters=4)
    
    segment_analysis = analyzer.analyze_segment_characteristics()
    
    segment_df = pd.DataFrame([
        {
            'Segment': seg,
            'Size': data['Size'],
            'Percentage': data['Percentage'],
            'Avg_Age': data['Avg_Age'],
            'Avg_Income': data['Avg_Income'],
            'Avg_Browsing_Hours': data['Avg_Browsing_Hours'],
            'Purchase_Rate': data['Purchase_Rate']
        }
        for seg, data in segment_analysis.items()
    ])
    
    segment_df.to_csv(f'{output_dir}/customer_segments.csv', index=False)
    print(f"  ✓ Segment analysis saved")
    
    # Identify high-value customers
    print("  Identifying high-value customers...")
    high_value_customers, threshold = analyzer.identify_high_value_customers()
    high_value_customers.to_csv(f'{output_dir}/high_value_customers.csv', index=False)
    print(f"  ✓ High-value customers saved")
    
    # Analyze purchase drivers
    print("  Analyzing purchase drivers...")
    drivers = analyzer.analyze_purchase_drivers()
    
    driver_df = pd.DataFrame([
        {
            'Feature': feature,
            'Purchaser_Mean': data['Purchaser_Mean'],
            'Non_Purchaser_Mean': data['Non_Purchaser_Mean'],
            'Difference': data['Difference'],
            'Impact_Ratio': data['Ratio']
        }
        for feature, data in drivers.items()
    ])
    
    driver_df = driver_df.sort_values('Difference', ascending=False)
    driver_df.to_csv(f'{output_dir}/purchase_drivers.csv', index=False)
    print(f"  ✓ Purchase drivers saved")
    
    # Predict engagement levels
    print("  Predicting customer engagement levels...")
    predictor = CustomerBehaviorPredictor(df)
    engagement_level, engagement_score = predictor.predict_engagement_level()
    churn_level, churn_risk = predictor.predict_churn_risk()
    upsell_level, upsell_score = predictor.predict_upsell_opportunity()
    
    predictions_df = df.copy()
    predictions_df['Engagement_Level'] = engagement_level
    predictions_df['Engagement_Score'] = engagement_score
    predictions_df['Churn_Risk_Level'] = churn_level
    predictions_df['Churn_Risk_Score'] = churn_risk
    predictions_df['Upsell_Opportunity'] = upsell_level
    predictions_df['Upsell_Score'] = upsell_score
    
    predictions_df.to_csv(f'{output_dir}/customer_predictions.csv', index=False)
    print(f"  ✓ Customer predictions saved")
    
    return df, segment_analysis, high_value_customers, drivers


if __name__ == '__main__':
    df, segments, high_value, drivers = generate_and_save_customer_datasets()
    
    print("\nDataset Summary:")
    print(f"Total Customers: {len(df)}")
    print(f"Features: {list(df.columns)}")
    
    print("\nSegment Summary:")
    for seg, data in segments.items():
        print(f"  Segment {seg}: {data['Size']} customers ({data['Percentage']:.1f}%)")
    
    print("\nPurchase Drivers (Top 5):")
    driver_df = pd.DataFrame([
        {
            'Feature': feature,
            'Difference': data['Difference']
        }
        for feature, data in drivers.items()
    ]).sort_values('Difference', ascending=False)
    
    for idx, row in driver_df.head(5).iterrows():
        print(f"  {row['Feature']}: {row['Difference']:.4f}")
