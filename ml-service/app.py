import os
import sys
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add the wafModel directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'wafModel'))

app = FastAPI(title="WAF ML Detection Service", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model (loaded once on startup)
tokenizer = None
model = None

class DetectionRequest(BaseModel):
    method: str = "GET"
    path: str = "/"
    headers: Dict[str, str] = {}
    body: str = ""
    query_params: Dict[str, str] = {}

class DetectionResponse(BaseModel):
    is_attack: bool
    confidence: float
    prediction: str
    threat_type: str
    processing_time_ms: float

def load_ml_model():
    """Load the DistilBERT model once on startup"""
    global tokenizer, model
    
    try:
        from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
        import torch
        
        model_directory = os.path.join(os.path.dirname(__file__), '..', 'wafModel')
        
        print(f"Loading model from: {model_directory}")
        tokenizer = DistilBertTokenizer.from_pretrained(model_directory)
        model = DistilBertForSequenceClassification.from_pretrained(model_directory)
        model.eval()
        
        print("✅ ML Model loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading ML model: {e}")
        return False

def classify_request(request_text: str) -> Dict[str, Any]:
    """
    Classify a request using the loaded DistilBERT model
    """
    global tokenizer, model
    
    if tokenizer is None or model is None:
        raise HTTPException(status_code=500, detail="ML model not loaded")
    
    try:
        import torch
        import time
        
        start_time = time.time()
        
        # Tokenize the input text
        inputs = tokenizer(request_text, return_tensors="pt", truncation=True, padding=True)

        # Perform inference
        with torch.no_grad():
            logits = model(**inputs).logits
        
        # Apply softmax to get probabilities
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        
        # Get prediction
        predicted_class_id = logits.argmax().item()
        confidence_score = probabilities[0][predicted_class_id].item()

        prediction = "Anomalous" if predicted_class_id == 1 else "Benign"
        is_attack = predicted_class_id == 1
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            "is_attack": is_attack,
            "confidence": confidence_score,
            "prediction": prediction,
            "threat_type": "AI-Detected Anomaly" if is_attack else "Normal Traffic",
            "processing_time_ms": round(processing_time, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML inference error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Load ML model on startup"""
    success = load_ml_model()
    if not success:
        print("⚠️ Starting without ML model - using fallback detection")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_status = "loaded" if (tokenizer is not None and model is not None) else "not_loaded"
    return {
        "status": "healthy",
        "model_status": model_status,
        "service": "WAF ML Detection"
    }

@app.post("/analyze", response_model=DetectionResponse)
async def analyze_request(request_data: DetectionRequest):
    """
    Analyze a request for threats using ML model
    """
    try:
        # Create request signature for ML analysis
        request_signature = f"{request_data.method} {request_data.path}"
        
        # Add query parameters if present
        if request_data.query_params:
            query_string = "&".join([f"{k}={v}" for k, v in request_data.query_params.items()])
            request_signature += f"?{query_string}"
        
        # Add body content if present
        if request_data.body:
            request_signature += f" {request_data.body}"
        
        # Get ML prediction
        result = classify_request(request_signature)
        
        return DetectionResponse(**result)
        
    except Exception as e:
        # Fallback to simple rule-based detection if ML fails
        is_suspicious = any([
            "union" in request_data.path.lower(),
            "select" in request_data.path.lower(),
            "<script" in request_data.path.lower(),
            "../" in request_data.path
        ])
        
        return DetectionResponse(
            is_attack=is_suspicious,
            confidence=0.8 if is_suspicious else 0.2,
            prediction="Suspicious" if is_suspicious else "Benign",
            threat_type="Rule-based Detection" if is_suspicious else "Normal Traffic",
            processing_time_ms=1.0
        )

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "WAF ML Detection Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "/analyze",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting WAF ML Detection Service...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )