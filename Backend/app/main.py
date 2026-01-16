from fastapi import APIRouter, HTTPException,Query
import redis, json, os
from .db import DatabaseConn, Product
from .ml.product_recommendation import AdvancedRecommender

router = APIRouter()

redis_host = os.getenv('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

rec_engine = AdvancedRecommender()
MODEL_READY = False

@router.on_event("startup")
def load_model():
    global MODEL_READY
    rec_engine.fit()
    MODEL_READY = True

@router.get("/recommend/{product_id}")
def recommend_by_id(product_id: int):
    return rec_engine.recommend(product_id)    


@router.get("/recommend")
def get_recommendations(
    product_name: str = Query(..., description="Product name user clicked or searched")
):
    if not MODEL_READY:
        raise HTTPException(503, "Recommendation model not ready")
    df = rec_engine.df
    matches = df[df["name"].str.contains(product_name, case=False, na=False)]
    if matches.empty:
        raise HTTPException(404, "No matching product found")
    product_id = int(matches.iloc[0]["id"])
    return rec_engine.recommend(product_id)


@router.get("/{product_id}")
def db_fetch(product_id: int):
    key = f"product:{product_id}"
    cache_ = r.get(key)
    if cache_:
        print("CACHE HIT")
        data = json.loads(cache_)
        data["Hit"] = True
        return data
    
    db = DatabaseConn()
    try:
        data = db.get_table(product_id)
        if not data:
            row = rec_engine.df[rec_engine.df['id'] == product_id]
            if not row.empty:
                return {
                    "id": int(row.iloc[0]['id']),
                    "name": row.iloc[0]['name'],
                    "desp": row.iloc[0]['desp'],
                    "price": float(row.iloc[0]['prices']),
                    "quantity": int(row.iloc[0]['quantity']),
                    "Hit": False
                }
            raise HTTPException(status_code=404, detail="Product not found")
        
        r.setex(key, 10, json.dumps(data, default=str))
        data["Hit"] = False
        return data 
    except Exception as e:
        if "1146" in str(e): 
             db.create_table()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/add_product")
def add_new_product(product: Product):
    db = DatabaseConn()
    try:
        data = db.add_product(product)
        if not data:
            raise HTTPException(status_code=409, detail="Product could not be added (Check ID)")
        return data 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.put("/update")
def update_product(product: Product):
    db = DatabaseConn()
    try:
        data = db.update_product(product)
        if not data:
            raise HTTPException(status_code=409, detail="Product could not be updated (Check ID)")
        
        key = f"product:{product.id}"
        r.delete(key)
        print(f"Cache Cleared for {key}")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.delete("/{prod_id}")
def delete_product(prod_id: int):
    db = DatabaseConn()
    try:
        data = db.delete(prod_id)
        if not data:
            raise HTTPException(status_code=404, detail="Product could not be deleted (Check ID)") 
        
        key = f"product:{prod_id}"
        r.delete(key)
        print(f"Cache Cleared for {key}")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()