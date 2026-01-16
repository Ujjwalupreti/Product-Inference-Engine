import pandas as pd
import re
import os
from sklearn.base import BaseEstimator, TransformerMixin

def load_enhanced_dataset():
    df = pd.read_csv("products.csv")
    df['name'] = df['name'].fillna('')
    df['desp'] = df['desp'].fillna('')
    return df

class TextCleaner(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        cleaned_text = X.apply(self._clean_text)
        return cleaned_text
    
    def _clean_text(self, text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text