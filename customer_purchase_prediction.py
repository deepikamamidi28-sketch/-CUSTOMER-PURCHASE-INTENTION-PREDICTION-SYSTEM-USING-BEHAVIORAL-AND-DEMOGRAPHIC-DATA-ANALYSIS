"""
Customer Purchase Intention Prediction System
Predicts customer purchase behavior using behavioral and demographic data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score, roc_curve
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# 1. GENERATE SYNTHETIC CUSTOMER DATASET
# ============================================================================

def generate_customer_dataset(n_samples=1000, random_state=42):
    """Generate synthetic customer behavioral and demographic dataset"""
    np.random.seed(random_state)
    
    # Generate features
    age = np.random.randint(18, 75, n_samples)
    income = np.random.randint(20000, 150000, n_samples)
    browsing_hours = np.random.exponential(2, n_samples)
    product_views = np.random.poisson(5, n_samples)
    cart_additions = np.random.poisson(2, n_samples)
    previous_purchases = np.random.poisson(3, n_samples)
    avg_order_value = np.random.gamma(2, 50, n_samples)
    website_visits = np.random.poisson(8, n_samples)
    email_opens = np.random.binomial(10, 0.4, n_samples)
    
    # Create feature matrix
    X = np.column_stack([
        age, income, browsing_hours, product_views, cart_additions,
        previous_purchases, avg_order_value, website_visits, email_opens
    ])
    
    # Generate target variable (purchase intention)
    # Higher values of certain features increase purchase probability
    purchase_prob = (
        0.02 * (age / 75) +
        0.03 * (income / 150000) +
        0.15 * (browsing_hours / (browsing_hours.max() + 1)) +
        0.20 * (product_views / (product_views.max() + 1)) +
        0.25 * (cart_additions / (cart_additions.max() + 1)) +
        0.15 * (previous_purchases / (previous_purchases.max() + 1)) +
        0.10 * (avg_order_value / (avg_order_value.max() + 1)) +
        0.05 * (website_visits / (website_visits.max() + 1)) +
        0.05 * (email_opens / 10)
    )
    
    y = (purchase_prob > np.median(purchase_prob)).astype(int)
    
    # Create DataFrame
    df = pd.DataFrame(X, columns=[
        'Age', 'Income', 'Browsing_Hours', 'Product_Views', 'Cart_Additions',
        'Previous_Purchases', 'Avg_Order_Value', 'Website_Visits', 'Email_Opens'
    ])
    df['Purchase_Intention'] = y
    
    print("=" * 80)
    print("CUSTOMER PURCHASE INTENTION PREDICTION SYSTEM - DATASET OVERVIEW")
    print("=" * 80)
    print(f"\nTotal Customers: {len(df)}")
    print(f"Total Features: {X.shape[1]}")
    print(f"Target Classes: 2 (0=No Purchase, 1=Purchase)")
    
    print("\nClass Distribution:")
    print(f"  No Purchase (0): {sum(y == 0)} customers ({sum(y == 0)/len(y)*100:.1f}%)")
    print(f"  Purchase (1): {sum(y == 1)} customers ({sum(y == 1)/len(y)*100:.1f}%)")
    
    print("\nFeature Statistics:")
    print(df.describe())
    
    return df

# ============================================================================
# 2. DATA PREPROCESSING
# ============================================================================

def preprocess_data(df):
    """Preprocess customer data"""
    X = df.drop('Purchase_Intention', axis=1)
    y = df['Purchase_Intention']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("\n" + "=" * 80)
    print("DATA PREPROCESSING SUMMARY")
    print("=" * 80)
    print(f"Training set size: {len(X_train)} customers")
    print(f"Test set size: {len(X_test)} customers")
    print(f"Feature scaling: StandardScaler (mean=0, std=1)")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, X, scaler

# ============================================================================
# 3. VISUALIZATION FUNCTIONS
# ============================================================================

def visualize_feature_distribution(df):
    """Visualize distribution of key features by purchase intention"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Customer Feature Distribution by Purchase Intention', 
                 fontsize=14, fontweight='bold')
    
    features = ['Age', 'Income', 'Browsing_Hours', 'Product_Views', 
                'Cart_Additions', 'Previous_Purchases']
    
    for idx, feature in enumerate(features):
        ax = axes[idx // 3, idx % 3]
        
        no_purchase = df[df['Purchase_Intention'] == 0][feature]
        purchase = df[df['Purchase_Intention'] == 1][feature]
        
        ax.hist(no_purchase, bins=20, alpha=0.6, label='No Purchase', color='red')
        ax.hist(purchase, bins=20, alpha=0.6, label='Purchase', color='green')
        ax.set_title(f'{feature} Distribution', fontweight='bold')
        ax.set_xlabel(feature)
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Feature distribution visualization saved")
    plt.close()

def visualize_correlation_heatmap(df):
    """Visualize correlation between features"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    corr_matrix = df.corr()
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, cbar=True, ax=ax, square=True)
    ax.set_title('Feature Correlation Heatmap', fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/correlation_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Correlation heatmap visualization saved")
    plt.close()

def visualize_class_distribution(df):
    """Visualize class distribution"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    counts = df['Purchase_Intention'].value_counts()
    labels = ['No Purchase', 'Purchase']
    colors = ['#ff6b6b', '#51cf66']
    
    # Bar chart
    ax1.bar(labels, counts.values, color=colors, edgecolor='black', alpha=0.8)
    ax1.set_title('Purchase Intention Distribution', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Count')
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie chart
    ax2.pie(counts.values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title('Purchase Percentage Distribution', fontweight='bold', fontsize=12)
    
    plt.suptitle('Customer Purchase Intention Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/class_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Class distribution visualization saved")
    plt.close()

def visualize_model_comparison(results):
    """Visualize model performance comparison"""
    models = list(results.keys())
    accuracy = [results[m]['Accuracy'] for m in models]
    precision = [results[m]['Precision'] for m in models]
    recall = [results[m]['Recall'] for m in models]
    f1 = [results[m]['F1-Score'] for m in models]
    
    x = np.arange(len(models))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(x - 1.5*width, accuracy, width, label='Accuracy', alpha=0.8, edgecolor='black')
    ax.bar(x - 0.5*width, precision, width, label='Precision', alpha=0.8, edgecolor='black')
    ax.bar(x + 0.5*width, recall, width, label='Recall', alpha=0.8, edgecolor='black')
    ax.bar(x + 1.5*width, f1, width, label='F1-Score', alpha=0.8, edgecolor='black')
    
    ax.set_title('Model Performance Comparison', fontweight='bold', fontsize=14)
    ax.set_ylabel('Score')
    ax.set_ylim([0, 1.1])
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/model_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Model comparison visualization saved")
    plt.close()

def visualize_confusion_matrix(y_true, y_pred, model_name):
    """Visualize confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                xticklabels=['No Purchase', 'Purchase'],
                yticklabels=['No Purchase', 'Purchase'])
    plt.title(f'Confusion Matrix - {model_name}', fontweight='bold', fontsize=12)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f'/home/ubuntu/confusion_matrix_{model_name.lower().replace(" ", "_")}.png', 
                dpi=300, bbox_inches='tight')
    print(f"✓ Confusion matrix for {model_name} saved")
    plt.close()

def visualize_roc_curves(results, y_test):
    """Visualize ROC curves for all models"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for idx, (model_name, metrics) in enumerate(results.items()):
        fpr = metrics['FPR']
        tpr = metrics['TPR']
        roc_auc = metrics['ROC-AUC']
        
        ax.plot(fpr, tpr, label=f'{model_name} (AUC = {roc_auc:.3f})', 
                linewidth=2, color=colors[idx])
    
    ax.plot([0, 1], [0, 1], 'k--', label='Random Classifier', linewidth=1)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curves - Model Comparison', fontweight='bold', fontsize=12)
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/roc_curves.png', dpi=300, bbox_inches='tight')
    print("✓ ROC curves visualization saved")
    plt.close()

def visualize_feature_importance(model, feature_names):
    """Visualize feature importance from Random Forest"""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(feature_names)))
    ax.bar(range(len(feature_names)), importances[indices], color=colors, edgecolor='black', alpha=0.8)
    ax.set_xticks(range(len(feature_names)))
    ax.set_xticklabels([feature_names[i] for i in indices], rotation=45, ha='right')
    ax.set_title('Feature Importance - Random Forest Model', fontweight='bold', fontsize=12)
    ax.set_ylabel('Importance')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_importance.png', dpi=300, bbox_inches='tight')
    print("✓ Feature importance visualization saved")
    plt.close()

# ============================================================================
# 4. MODEL BUILDING AND TRAINING
# ============================================================================

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple classification models"""
    print("\n" + "=" * 80)
    print("MODEL TRAINING")
    print("=" * 80)
    
    results = {}
    models = {}
    
    # Logistic Regression
    print("\nTraining Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)
    y_proba_lr = lr_model.predict_proba(X_test)[:, 1]
    
    fpr_lr, tpr_lr, _ = roc_curve(y_test, y_proba_lr)
    roc_auc_lr = roc_auc_score(y_test, y_proba_lr)
    
    results['Logistic Regression'] = {
        'Accuracy': accuracy_score(y_test, y_pred_lr),
        'Precision': precision_score(y_test, y_pred_lr),
        'Recall': recall_score(y_test, y_pred_lr),
        'F1-Score': f1_score(y_test, y_pred_lr),
        'ROC-AUC': roc_auc_lr,
        'FPR': fpr_lr,
        'TPR': tpr_lr
    }
    models['Logistic Regression'] = lr_model
    
    # Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    y_proba_rf = rf_model.predict_proba(X_test)[:, 1]
    
    fpr_rf, tpr_rf, _ = roc_curve(y_test, y_proba_rf)
    roc_auc_rf = roc_auc_score(y_test, y_proba_rf)
    
    results['Random Forest'] = {
        'Accuracy': accuracy_score(y_test, y_pred_rf),
        'Precision': precision_score(y_test, y_pred_rf),
        'Recall': recall_score(y_test, y_pred_rf),
        'F1-Score': f1_score(y_test, y_pred_rf),
        'ROC-AUC': roc_auc_rf,
        'FPR': fpr_rf,
        'TPR': tpr_rf
    }
    models['Random Forest'] = rf_model
    
    # Gradient Boosting
    print("Training Gradient Boosting...")
    gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb_model.fit(X_train, y_train)
    y_pred_gb = gb_model.predict(X_test)
    y_proba_gb = gb_model.predict_proba(X_test)[:, 1]
    
    fpr_gb, tpr_gb, _ = roc_curve(y_test, y_proba_gb)
    roc_auc_gb = roc_auc_score(y_test, y_proba_gb)
    
    results['Gradient Boosting'] = {
        'Accuracy': accuracy_score(y_test, y_pred_gb),
        'Precision': precision_score(y_test, y_pred_gb),
        'Recall': recall_score(y_test, y_pred_gb),
        'F1-Score': f1_score(y_test, y_pred_gb),
        'ROC-AUC': roc_auc_gb,
        'FPR': fpr_gb,
        'TPR': tpr_gb
    }
    models['Gradient Boosting'] = gb_model
    
    return results, models, y_pred_rf

# ============================================================================
# 5. MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("CUSTOMER PURCHASE INTENTION PREDICTION SYSTEM")
    print("Using Machine Learning Classification Techniques")
    print("=" * 80)
    
    # Generate dataset
    print("\n[Step 1] Generating Customer Dataset...")
    df = generate_customer_dataset(n_samples=1000)
    
    # Preprocess data
    print("\n[Step 2] Preprocessing Data...")
    X_train, X_test, y_train, y_test, X_orig, scaler = preprocess_data(df)
    
    # Generate visualizations
    print("\n[Step 3] Generating Visualizations...")
    print("Creating feature distribution visualization...")
    visualize_feature_distribution(df)
    
    print("Creating correlation heatmap...")
    visualize_correlation_heatmap(df)
    
    print("Creating class distribution visualization...")
    visualize_class_distribution(df)
    
    # Train models
    print("\n[Step 4] Training Classification Models...")
    results, models, y_pred_best = train_models(X_train, X_test, y_train, y_test)
    
    # Print results
    print("\n" + "=" * 80)
    print("MODEL PERFORMANCE RESULTS")
    print("=" * 80)
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        print(f"  Accuracy: {metrics['Accuracy']:.4f}")
        print(f"  Precision: {metrics['Precision']:.4f}")
        print(f"  Recall: {metrics['Recall']:.4f}")
        print(f"  F1-Score: {metrics['F1-Score']:.4f}")
        print(f"  ROC-AUC: {metrics['ROC-AUC']:.4f}")
    
    # Generate additional visualizations
    print("\n[Step 5] Generating Additional Visualizations...")
    print("Creating model comparison...")
    visualize_model_comparison(results)
    
    print("Creating confusion matrices...")
    for model_name, model in models.items():
        y_pred = model.predict(X_test)
        visualize_confusion_matrix(y_test, y_pred, model_name)
    
    print("Creating ROC curves...")
    visualize_roc_curves(results, y_test)
    
    print("Creating feature importance...")
    visualize_feature_importance(models['Random Forest'], df.drop('Purchase_Intention', axis=1).columns)
    
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nGenerated Visualizations:")
    print("  1. feature_distribution.png")
    print("  2. correlation_heatmap.png")
    print("  3. class_distribution.png")
    print("  4. model_comparison.png")
    print("  5. confusion_matrix_logistic_regression.png")
    print("  6. confusion_matrix_random_forest.png")
    print("  7. confusion_matrix_gradient_boosting.png")
    print("  8. roc_curves.png")
    print("  9. feature_importance.png")
    
    return df, X_train, X_test, y_train, y_test, results, models

if __name__ == "__main__":
    df, X_train, X_test, y_train, y_test, results, models = main()
