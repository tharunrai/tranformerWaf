from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

# --- Configuration ---
MODEL_DIRECTORY = "."

# --- 1. Load the Fine-Tuned Model ---
print("Loading the model...")
try:
    tokenizer = DistilBertTokenizer.from_pretrained(MODEL_DIRECTORY)
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIRECTORY)
    # Set the model to evaluation mode (important for inference)
    model.eval()
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# --- 2. Create the Prediction Function (MODIFIED) ---
def classify_request(request_text):
    """
    Classifies a request and returns the label and confidence score.
    """
    # Tokenize the input text
    inputs = tokenizer(request_text, return_tensors="pt", truncation=True, padding=True)

    # Perform inference without calculating gradients
    with torch.no_grad():
        logits = model(**inputs).logits
    
    # NEW: Apply softmax to convert logits to probabilities
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    
    # Get the prediction (0 for Benign, 1 for Anomalous)
    predicted_class_id = logits.argmax().item()
    
    # NEW: Get the confidence score for the predicted class
    confidence_score = probabilities[0][predicted_class_id].item()

    label = "Anomalous" if predicted_class_id == 1 else "Benign"

    # NEW: Return a dictionary with both the label and the score
    return {
        "prediction": label,
        "confidence": confidence_score
    }

# --- 3. Main Interactive Loop (MODIFIED) ---
if __name__ == "__main__":
    print("\n--- Model Test Terminal ---")
    print("Enter a request string to classify it.")
    
    while True:
        # Prompt the user for input
        user_input = input("\nEnter a request string (or 'quit' to exit) > ")
        
        # Check if the user wants to exit
        if user_input.lower() in ['quit', 'exit']:
            print("Exiting...")
            break
            
        # Get the prediction and print it
        result = classify_request(user_input)
        prediction = result["prediction"]
        score = result["confidence"]
        
        # NEW: Print both the prediction and the formatted score
        print(f"   └── Prediction: {prediction} (Confidence: {score:.2%})")