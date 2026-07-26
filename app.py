import os
import webbrowser
from threading import Timer
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq

app = Flask(__name__, static_folder='.', static_url_path='')

# Groq API Key setup
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "gsk_your_actual_groq_api_key_here")

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    client = None
    print(f"Warning: Failed to initialize Groq client: {e}")

@app.route('/')
def landing():
    return send_from_directory('.', 'landing.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    messages = data.get('messages', [])
    
    if not client:
        return jsonify({"error": "Groq client is not initialized."}), 500
        
    try:
        system_prompt = {
            "role": "system", 
            "content": "You are SafeRoute AI, an expert fleet safety assistant."
        }
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[system_prompt] + messages,
        )
        
        return jsonify({"response": completion.choices[0].message.content})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8080/')

if __name__ == '__main__':
    # Render provides a dynamic PORT; fall back to 8080 for local testing
    PORT = int(os.environ.get("PORT", 8080))
    print(f"--- SafeRoute Server Running at http://0.0.0.0:{PORT} ---")
    
    # Only open the browser automatically when running locally, not on Render
    if "RENDER" not in os.environ:
        Timer(1.2, lambda: webbrowser.open_new(f'http://127.0.0.1:{PORT}/')).start()
        
    # Bind to 0.0.0.0 so Render can access the application
    app.run(host='0.0.0.0', port=PORT, debug=False)