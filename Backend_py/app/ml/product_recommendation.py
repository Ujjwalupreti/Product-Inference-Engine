from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from .dataCleaner import TextCleaner,load_enhanced_dataset

class AdvancedRecommender:
    def __init__(self):
        self.df = None
        self.pipeline = None
        self.model = None
        self.feature_matrix = None
        
    def build_pipeline(self):
        """
        Constructs the Sklearn Pipeline with Feature Union.
        This combines NLP features (TF-IDF) with Numerical features (Price).
        """
        # A. NLP Pipeline for 'desp'
        text_pipeline = Pipeline([
            ('cleaner', TextCleaner()), # Our custom class
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=500))
        ])
        
        # B. Numerical Pipeline for 'prices'
        # We scale prices so they don't overpower the text vectors
        num_pipeline = Pipeline([
            ('scaler', MinMaxScaler()) 
        ])
        
        # C. Column Transformer (The Glue)
        # Applies text_pipeline to 'desp' and num_pipeline to 'prices'
        self.pipeline = ColumnTransformer([
            ('nlp_features', text_pipeline, 'desp'),
            ('num_features', num_pipeline, ['prices'])
        ])
        
        # D. The Estimator (Model)
        # Using KNN (Unsupervised) is efficient for finding similar items
        self.model = NearestNeighbors(n_neighbors=5, metric='cosine', algorithm='brute')

    def fit(self):
        """Loads data, transforms features, and fits the model."""
        # 1. Load Data
        self.df = load_enhanced_dataset()
        print(f"✅ Loaded {len(self.df)} products (after augmentation)")
        
        # 2. Build Pipeline
        self.build_pipeline()
        
        # 3. Run the Pipeline (Feature Extraction)
        # This converts our raw dataframe into a numeric matrix
        self.feature_matrix = self.pipeline.fit_transform(self.df)
        print("✅ Feature Extraction Complete (Text + Price normalized)")
        
        # 4. Train the Model
        self.model.fit(self.feature_matrix)
        print("✅ KNN Model Trained")

    def recommend(self, product_id: int, n_recommendations: int = 3):
        """
        Predicts nearest neighbors for a given product ID.
        """
        if self.df is None:
            raise Exception("Model not trained. Call .fit() first.")
            
        # 1. Locate the product in our dataframe
        product_idx = self.df.index[self.df['id'] == product_id].tolist()
        if not product_idx:
            return None
        
        product_idx = product_idx[0]
        
        # 2. Get the feature vector for this specific product
        # We transform just this one row to match the training data shape
        query_vector = self.feature_matrix[product_idx]
        
        # 3. Ask Model for Neighbors
        # returns (distances, indices)
        distances, indices = self.model.kneighbors(query_vector, n_neighbors=n_recommendations+1)
        
        # 4. Format Results
        results = []
        for i in range(1, len(indices[0])): # Skip index 0 (it's the product itself)
            idx = indices[0][i]
            dist = distances[0][i]
            
            item = self.df.iloc[idx]
            results.append({
                "id": int(item['id']),
                "name": item['name'],
                "price": float(item['prices']),
                "similarity_score": round(1 - dist, 4) # Convert distance to similarity
            })
            
        return results


if __name__ == "__main__":
    rec_engine = AdvancedRecommender()
    rec_engine.fit()
    
    # Test for ID 1 (Wireless Mouse)
    print("\n--- Recommendations for Product ID 1 (Wireless Mouse) ---")
    recs = rec_engine.recommend(1)
    for r in recs:
        print(r)