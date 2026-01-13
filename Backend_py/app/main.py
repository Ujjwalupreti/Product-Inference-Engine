# /app/main.py
from fastapi import APIRouter, HTTPException
import redis, json, os
from .db import DatabaseConn, Product

# 1. Change FastAPI() to APIRouter()
router = APIRouter()

# 2. Redis Connection (Specific for Product caching)
redis_host = os.getenv('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

# 3. Routes (Notice we use @router.get instead of @app.get)

@router.get("/fetch/{product_id}")
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
            raise HTTPException(status_code=404, detail="Product not found")
        
        r.setex(key, 10, json.dumps(data, default=str))
        data["Hit"] = False
        return data 
    except Exception as e:
        # Note: In production, careful with creating tables on error
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

@router.delete("/delete/{prod_id}")
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

@router.get("/all")
def fetch_all():
    return [{"message": "Fetch all not implemented in DB class yet"}]