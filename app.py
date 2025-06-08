from flask import Flask, request, jsonify, send_from_directory
from gradio_client import Client
import time
import logging
import os

app = Flask(__name__, static_folder='.')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Initialize Gradio client or fallback to mock responses
gradio_client = None
GRADIO_API_URL = "https://2ac1bafcb9dec6af1d.gradio.live"

def initialize_gradio_client():
    global gradio_client
    try:
        logger.info(f"Attempting to connect to Gradio API at {GRADIO_API_URL}")
        # Add timeout parameter and increase it for better connection chances
        gradio_client = Client(GRADIO_API_URL, timeout=60)
        logger.info("Successfully connected to Gradio API")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Gradio API: {str(e)}")
        return False

# Mock response function for when Gradio API is unavailable
def get_mock_response(message, case_type, relevant_acts, client_position):
    legal_responses = {
        "Civil Suit": "Based on the principles of civil law and the facts presented, I would argue that the plaintiff's claims lack sufficient evidentiary basis. The burden of proof rests with the plaintiff, and they have not established a prima facie case.",
        "Criminal Trial": "The prosecution must prove beyond reasonable doubt that all elements of the offense are satisfied. In this case, there appear to be significant gaps in the chain of evidence that cast reasonable doubt on the defendant's culpability.",
        "Constitutional Matter": "This matter raises important constitutional questions regarding the balance between individual rights and the public interest. I would refer to Article 21 of the Indian Constitution which guarantees protection of life and personal liberty.",
        "Corporate Dispute": "In corporate matters like this, the doctrine of separate legal entity as established in Salomon v. Salomon & Co would be applicable. The shareholders cannot be held personally liable for the company's actions.",
        "Family Law": "Family disputes require a balanced approach that considers the welfare of all parties involved, particularly any minor children. The Hindu Marriage Act provides clear guidance on such matters.",
        "Property Dispute": "Property disputes must be evaluated based on documented evidence of ownership and possession. The Transfer of Property Act establishes that a clear chain of title is essential for establishing ownership claims."
    }
    
    # Return either a case-specific response or a generic one
    return legal_responses.get(case_type, f"As your legal adversary, I would challenge your position on the grounds of {relevant_acts}. The {client_position} must establish stronger legal standing.")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/chat', methods=['POST'])
def chat():
    # Get data from request
    data = request.json
    message = data.get('message', '')
    
    # Get form data from request
    case_type = data.get('case_type', 'Civil Suit')
    relevant_acts = data.get('relevant_acts', 'Indian Penal Code, Code of Criminal Procedure')
    client_position = data.get('client_position', 'Plaintiff/Petitioner')
    
    # Store conversation history
    chatbot = data.get('chatbot', [])
    
    logger.info(f"Received chat request: {message}, Case Type: {case_type}, Relevant Acts: {relevant_acts}, Client Position: {client_position}")
    
    # Try to use Gradio client if available, otherwise use mock response
    if gradio_client is not None:
        try:
            logger.info("Attempting to call Gradio API...")
            response_text = gradio_client.predict(
                message=message,
                chatbot=chatbot,
                case_type=case_type,
                relevant_acts=relevant_acts,
                client_position=client_position,
                api_name="/submit_message"
            )
            logger.info(f"Successfully received response from Gradio API: {response_text[:100]}...")
            result = response_text  # Store the actual response text
        except Exception as e:
            logger.error(f"Error calling Gradio API: {str(e)}")
            result = get_mock_response(message, case_type, relevant_acts, client_position)
    else:
        logger.info("Using mock response (Gradio API unavailable)")
        result = get_mock_response(message, case_type, relevant_acts, client_position)
    
    # Return the response
    return jsonify({"response": result})

@app.route('/status', methods=['GET'])
def status():
    """Endpoint to check if the server is running and if Gradio API is available"""
    status = {
        "server": "running",
        "gradio_api": "connected" if gradio_client is not None else "disconnected",
        "gradio_url": GRADIO_API_URL
    }
    return jsonify(status)

@app.route('/update-gradio-url', methods=['POST'])
def update_gradio_url():
    """Endpoint to update the Gradio API URL"""
    global GRADIO_API_URL, gradio_client
    data = request.json
    new_url = data.get('url', '')
    
    if not new_url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Disconnect existing client if any
    gradio_client = None
    
    GRADIO_API_URL = new_url
    success = initialize_gradio_client()
    
    if success:
        return jsonify({"status": "success", "message": "Gradio API URL updated successfully"})
    else:
        return jsonify({"status": "error", "message": "Failed to connect to the new Gradio API URL"}), 500

@app.route('/test-gradio', methods=['GET'])
def test_gradio():
    """Endpoint to test the Gradio connection with a simple message"""
    if gradio_client is None:
        return jsonify({"status": "error", "message": "Gradio client not initialized"}), 500
    
    try:
        # Test with a simple message
        response = gradio_client.predict(
            message="Test connection",
            chatbot=[],
            case_type="Civil Suit",
            relevant_acts="Indian Penal Code",
            client_position="Plaintiff/Petitioner",
            api_name="/submit_message"
        )
        return jsonify({"status": "success", "message": "Gradio connection successful", "response": response})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Gradio connection failed: {str(e)}"}), 500

@app.route('/retry-connection', methods=['POST'])
def retry_connection():
    """Endpoint to retry the Gradio connection"""
    success = initialize_gradio_client()
    
    if success:
        return jsonify({"status": "success", "message": "Successfully connected to Gradio API"})
    else:
        return jsonify({"status": "error", "message": "Failed to connect to Gradio API"}), 500

if __name__ == '__main__':
    # Try to initialize Gradio client
    initialize_gradio_client()
    
    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)