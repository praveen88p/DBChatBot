from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database
import requests
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from langchain.schema import SystemMessage, HumanMessage
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not HUGGINGFACE_API_KEY:
    raise ValueError("Missing HUGGINGFACE_API_KEY. Set it in environment variables.")
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}


app = FastAPI()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "your_api_key_here")
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/products/")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/products/{product_name}")
def get_product(product_name: str, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.name == product_name).first()

@app.get("/suppliers/")
def get_suppliers(db: Session = Depends(get_db)):
    return db.query(models.Supplier).all()

@app.get("/suppliers/{supplier_name}")
def get_supplier(supplier_name: str, db: Session = Depends(get_db)):
    return db.query(models.Supplier).filter(models.Supplier.name == supplier_name).first()


class TextRequest(BaseModel):
    text: str

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


class ChatState:
    def __init__(self, messages=None):
        self.messages = messages or []

    def update(self, new_message):
        self.messages.append(new_message)
        return self

def summarize_text(state: ChatState) -> Dict[str, Any]:
    latest_message = state.messages[-1].content
    summary_response = query({"inputs": latest_message})

    if "error" in summary_response:
        raise HTTPException(status_code=500, detail=summary_response["error"])

    summary = summary_response[0]["summary_text"]
    new_message = SystemMessage(content=summary)
    
    return {"state": state.update(new_message)}

# ✅ Define LangGraph Workflow
workflow = StateGraph(ChatState)
workflow.add_node("summarize", summarize_text)
workflow.set_entry_point("summarize")
workflow.add_edge("summarize", END)
graph_executor = workflow.compile()

# ✅ FastAPI Endpoint for Summarization
@app.post("/summarize/")
def chat_with_bot(request: TextRequest):
    try:
        state = ChatState(messages=[HumanMessage(content=request.text)])
        result = graph_executor.invoke(state)
        return {"summary": result.state.messages[-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

