from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database
import requests
from pydantic import BaseModel
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not HUGGINGFACE_API_KEY:
    raise ValueError("Missing HUGGINGFACE_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TextRequest(BaseModel):
    text: str

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def get_products_info(db: Session) -> str:
    try:
        products = db.query(models.Product).all()
        if not products:
            return "No products found in the database."
        return "\n".join([
            f"{product.name}: {product.description} - ${product.price}" 
            for product in products
        ])
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return f"Error retrieving products: {str(e)}"

def get_suppliers_info(db: Session) -> str:
    try:
        suppliers = db.query(models.Supplier).all()
        if not suppliers:
            return "No suppliers found in the database."
        suppliers_text = "\n".join([
            f"{supplier.name}: {supplier.contact_info} - Categories: {supplier.product_categories}" 
            for supplier in suppliers
        ])
        
        try:
            summary_response = query({
                "inputs": f"Summarize this supplier information: {suppliers_text}"
            })
            return summary_response[0]["summary_text"]
        except Exception as e:
            logger.error(f"Error summarizing suppliers: {e}")
            return suppliers_text
    except Exception as e:
        logger.error(f"Error getting suppliers: {e}")
        return f"Error retrieving suppliers: {str(e)}"

def get_specific_product(db: Session, product_keyword: str) -> str:
    try:
        products = db.query(models.Product).filter(
            (models.Product.name.ilike(f"%{product_keyword}%")) |
            (models.Product.description.ilike(f"%{product_keyword}%")) |
            (models.Product.category.ilike(f"%{product_keyword}%"))
        ).all()
        
        if not products:
            return f"No products found matching '{product_keyword}'."
        
        product_info = []
        for product in products:
            supplier = db.query(models.Supplier).filter(
                models.Supplier.id == product.supplier_id
            ).first()
            
            supplier_name = supplier.name if supplier else "Unknown Supplier"
            
            product_info.append(
                f"Product: {product.name}\n"
                f"Description: {product.description}\n"
                f"Price: ${product.price}\n"
                f"Category: {product.category}\n"
                f"Supplier: {supplier_name}\n"
                f"Brand: {product.brand}\n"
                "-------------------"
            )
        
        return "\n".join(product_info)
    except Exception as e:
        logger.error(f"Error getting specific product: {e}")
        return f"Error retrieving product information: {str(e)}"

@app.post("/chat/")
async def chat_endpoint(request: TextRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received message: {request.text}")
        message = request.text.lower()
        
        # Check for specific product queries
        specific_product_keywords = ["show me", "find", "search for", "tell me about", "looking for"]
        is_specific_product_query = any(keyword in message for keyword in specific_product_keywords)
        
        if is_specific_product_query and "product" in message:
            # Extract the product keyword (everything after the trigger phrase)
            for keyword in specific_product_keywords:
                if keyword in message:
                    product_keyword = message.split(keyword)[-1].replace("product", "").strip()
                    if product_keyword:
                        response_text = get_specific_product(db, product_keyword)
                        break
            else:
                response_text = "Please specify what product you're looking for."
        # General product query
        elif "product" in message:
            response_text = get_products_info(db)
        # Supplier query
        elif "supplier" in message:
            response_text = get_suppliers_info(db)
        # General query
        else:
            try:
                summary_response = query({"inputs": message})
                response_text = summary_response[0]["summary_text"]
            except Exception as e:
                logger.error(f"Error in summarization: {e}")
                response_text = "I couldn't process that request."
        
        logger.info(f"Generated response: {response_text}")
        return {"response": response_text}
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return {"response": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

