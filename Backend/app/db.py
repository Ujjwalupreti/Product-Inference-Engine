import urllib.parse
import mysql.connector
from pydantic import BaseModel, Field, BeforeValidator, EmailStr
from typing import Optional
from typing_extensions import Annotated
import os
from motor.motor_asyncio import AsyncIOMotoClient

MONGO_URI = os.getenv("MONGO_URI","mongodb://localhost:27017")
DB_NAME = "Ecomm_user"

PyObjectId = Annotated[str, BeforeValidator(str)]    
class User(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id",default=None)    
    username: str
    email:EmailStr
    hashed_password:str
    role: str = "user"

class Product(BaseModel):
    id:int
    name:str
    desp:Optional[str] = None
    price:int
    quantity:int
    total:Optional[float] = None
    
class Signup(BaseModel):
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

db_config = {
    'user': 'root',
    'password':'Ujjwalsql@2500',
    'host': os.getenv('DB_HOST', 'localhost'),
    'database':'Test1'
}

class MongoDB:
    client: AsyncIOMotoClient = None
    db = None
    
    def connect(self):
        self.client = AsyncIOMotoClient(
            MONGO_URI,
            maxPoolSize = 10,
            minPoolSize = 1,
            serverSelectionTimeoutMS=5000)
        self.db = self.client[DB_NAME]
        print("Connected to MongoDB(User Store)")
        
    def close(self):
        if self.client:
            self.client.close()
            print("Closed Mongodb Connection")    

class DatabaseConn:
    def __init__(self):
        self.conn = mysql.connector.connect(**db_config)
        self.cursor = self.conn.cursor(dictionary=True)

    def create_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS products (
                id int primary key,
                name varchar(30) not null,
                desp varchar(200),
                price decimal(9,2) not null check(price>=0),
                quantity int not null check(quantity>0),
                total decimal(10,2)
            )
            """
            
            self.cursor.execute(query)
            self.conn.commit()
            print("Table 'products' created successfully.")
            
        except mysql.connector.Error as err:
            print(f"Error creating table: {err}")

    def get_table(self, product_id: int):
        try:
            query = "SELECT * FROM products WHERE id = %s"
            self.cursor.execute(query, (product_id,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error fetching: {err}")
            return None
    
    def add_product(self,product:Product):
        try:
            total = product.price * product.quantity
            query = """ INSERT INTO products VALUES 
            (%s,%s,%s,%s,%s,%s);
            """    
            self.cursor.execute(query,(product.id,product.name,product.desp,product.price,product.quantity,total,))
            self.conn.commit()
            return {"message": "Product added successfully", "id": product.id}
        except mysql.connector.Error as err:
            print(f"DB Error: {err}")
            return None
        
    def update_product(self,product:Product):
        data = product.model_dump()
        try:
            prod_id = data.pop("id")
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            vals = list(data.values())
            vals.append(prod_id)
            
            query = f"UPDATE products SET {set_clause} where id = %s"
            
            self.cursor.execute(query, vals)
            self.conn.commit()
            
            return {"message": "Product updated successfully"}
        except Exception as err:
            print(f"Error:{err}")
            return None
        
    def delete(self,prod_id):
        try:
            query = "Delete from products where id = %s"
            self.cursor.execute(query,(prod_id,))
            self.conn.commit()
            
            if self.cursor.rowcount == 0:
                return None
            
            return {"message": "Product Deleted successfully"}       
        except mysql.connector.Error as err:
            print(f"Error:{err}")
            return None
        
    def close(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()