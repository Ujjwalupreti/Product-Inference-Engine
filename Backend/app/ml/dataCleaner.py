import pandas as pd
import numpy as np
import re
import io
from sklearn.base import BaseEstimator, TransformerMixin


base_csv = """id,name,desp,prices,quantity,total
1,Wireless Mouse,Ergonomic wireless mouse with USB receiver,799,120,95880
2,Mechanical Keyboard,RGB backlit mechanical keyboard,3499,60,209940
3,Bluetooth Headphones,Noise cancelling over-ear headphones,5999,45,269955
4,Laptop Stand,Adjustable aluminum laptop stand,1299,80,103920
5,USB-C Hub,6-in-1 USB-C hub with HDMI and USB ports,2499,50,124950
6,Smart Watch,Fitness tracking smartwatch with heart rate monitor,6999,40,279960
7,External Hard Drive,1TB portable external hard drive,4599,35,160965
8,Gaming Chair,Ergonomic gaming chair with lumbar support,12999,20,259980
9,Webcam,Full HD 1080p USB webcam,2999,70,209930
10,Portable Speaker,Bluetooth portable speaker with deep bass,3999,55,219945"""

def load_enhanced_dataset():
    df = pd.read_csv(io.StringIO(base_csv))
    
    # Synthetic Data Generation: Let's create variations to reach ~30 products
    # This simulates a real database where you have multiple types of "Mice", "Keyboards", etc.
    new_rows = []
    last_id = 10
    variations = [("Pro", 1.5), ("Mini", 0.8), ("Budget", 0.5)]
    
    for _, row in df.iterrows():
        for suffix, price_mult in variations:
            last_id += 1
            new_rows.append({
                "id": last_id,
                "name": f"{row['name']} {suffix}",
                "desp": f"{suffix} version of {row['desp']}", # Simple augmentation
                "prices": int(row['prices'] * price_mult),
                "quantity": 50,
                "total": 0
            })
            
    df_extended = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    return df_extended

# ---------------------------------------------------------
# 2. CUSTOM TRANSFORMERS (Fixing "Data Cleaning & Transformation")
# ---------------------------------------------------------

class TextCleaner(BaseEstimator, TransformerMixin):
    """
    Custom Transformer to perform NLP cleaning steps:
    - Lowercasing
    - Removing special characters/punctuation
    - (Optional) Lemmatization could be added here
    """
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        # X is a pandas Series (text column)
        cleaned_text = X.apply(self._clean_text)
        return cleaned_text
    
    def _clean_text(self, text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        # Remove special chars, keep only letters and numbers
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text
