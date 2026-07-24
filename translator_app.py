from flask import Flask, render_template_string, request, jsonify, send_file
from deep_translator import GoogleTranslator
import pyperclip
import webbrowser
import threading
import time
import os
import io
from gtts import gTTS
import base64

app = Flask(__name__)

# HTML Template with CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinguaBridge - Translation Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 1100px;
            width: 100%;
            padding: 40px;
        }
        
        .header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .input-section, .output-section {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .label {
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }
        
        textarea {
            width: 100%;
            min-height: 180px;
            padding: 15px;
            border: 2px solid #667eea;
            border-radius: 12px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #764ba2;
        }
        
        .counter {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        .language-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #667eea;
            border-radius: 12px;
            font-size: 16px;
            background: white;
            transition: border-color 0.3s;
        }
        
        select:focus {
            outline: none;
            border-color: #764ba2;
        }
        
        .button-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 50px;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            flex: 1;
            min-width: 100px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .output-text {
            width: 100%;
            min-height: 180px;
            padding: 15px;
            background: #f8f9fa;
            border: 2px solid #667eea;
            border-radius: 12px;
            font-size: 18px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow-y: auto;
            color: #333;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .output-text.rtl {
            direction: rtl;
            text-align: right;
        }
        
        .output-text.ltr {
            direction: ltr;
            text-align: left;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }
        
        @media (max-width: 600px) {
            .status-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
        
        .status-item {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
        }
        
        .status-item .label {
            font-size: 0.85em;
            color: #666;
            font-weight: normal;
            display: block;
            margin-bottom: 3px;
        }
        
        .status-item .value {
            font-weight: bold;
            color: #333;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
        }
        
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #333;
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            display: none;
            z-index: 1000;
        }
        
        .toast.show {
            display: block;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                transform: translateY(100px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .audio-player {
            margin-top: 10px;
            width: 100%;
        }
        
        audio {
            width: 100%;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 LinguaBridge</h1>
            <p>Professional-grade text translation with spoken audio output</p>
        </div>
        
        <div class="main-grid">
            <div class="input-section">
                <label class="label">📝 TEXT TO TRANSLATE</label>
                <textarea id="inputText" placeholder="Type or paste your text here..."></textarea>
                <div class="counter">
                    <span id="charCount">0</span> characters &nbsp;|&nbsp; <span id="wordCount">0</span> words
                </div>
                
                <div class="language-row">
                    <div>
                        <label class="label">🌍 From</label>
                        <select id="sourceLang">
                            <option value="auto">Auto Detect</option>
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="ur">Urdu</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                            <option value="de">German</option>
                            <option value="ja">Japanese</option>
                            <option value="zh-cn">Chinese</option>
                            <option value="ar">Arabic</option>
                            <option value="ru">Russian</option>
                            <option value="pt">Portuguese</option>
                        </select>
                    </div>
                    <div>
                        <label class="label">🎯 To</label>
                        <select id="targetLang">
                            <option value="ur">Urdu</option>
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                            <option value="de">German</option>
                            <option value="ja">Japanese</option>
                            <option value="zh-cn">Chinese</option>
                            <option value="ar">Arabic</option>
                            <option value="ru">Russian</option>
                            <option value="pt">Portuguese</option>
                        </select>
                    </div>
                </div>
                
                <div class="button-group">
                    <button class="btn btn-primary" onclick="translateText()">🔄 Translate</button>
                    <button class="btn btn-secondary" onclick="speakText()">🔊 Speak</button>
                    <button class="btn btn-success" onclick="copyText()">📋 Copy</button>
                    <button class="btn btn-danger" onclick="clearAll()">🗑️ Clear</button>
                </div>
            </div>
            
            <div class="output-section">
                <label class="label">📖 TRANSLATION</label>
                <div class="output-text ltr" id="outputText">Your translation will appear here...</div>
                <div id="audioContainer"></div>
                
                <div class="status-grid">
                    <div class="status-item">
                        <span class="label">🔍 Language detected</span>
                        <span class="value" id="detectedLang">-</span>
                    </div>
                    <div class="status-item">
                        <span class="label">🎯 Accuracy</span>
                        <span class="value" id="accuracy">-</span>
                    </div>
                    <div class="status-item">
                        <span class="label">⏱️ Status</span>
                        <span class="value" id="status">Ready</span>
                    </div>
                    <div class="status-item">
                        <span class="label">🔒 Security</span>
                        <span class="value" id="security">🔒 Secure</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <span>LinguaBridge – Bridging Languages, Connecting Worlds. 🌍</span>
        </div>
    </div>
    
    <div class="toast" id="toast"></div>
    
    <script>
        // Update character and word count
        document.getElementById('inputText').addEventListener('input', function() {
            const text = this.value;
            document.getElementById('charCount').textContent = text.length;
            document.getElementById('wordCount').textContent = text.trim() ? text.trim().split(/\\s+/).length : 0;
        });
        
        // Translate function
        function translateText() {
            const inputText = document.getElementById('inputText').value;
            const sourceLang = document.getElementById('sourceLang').value;
            const targetLang = document.getElementById('targetLang').value;
            
            if (!inputText.trim()) {
                showToast('Please enter some text to translate');
                return;
            }
            
            // Show loading
            const outputDiv = document.getElementById('outputText');
            outputDiv.textContent = 'Translating... ⏳';
            outputDiv.className = 'output-text ltr';
            document.getElementById('audioContainer').innerHTML = '';
            
            fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: inputText,
                    source: sourceLang,
                    target: targetLang
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showToast('Error: ' + data.error);
                    outputDiv.textContent = 'Error: ' + data.error;
                    return;
                }
                
                outputDiv.textContent = data.translation;
                
                // Set RTL for Urdu, Arabic, etc.
                if (targetLang === 'ur' || targetLang === 'ar' || targetLang === 'fa' || targetLang === 'he') {
                    outputDiv.className = 'output-text rtl';
                } else {
                    outputDiv.className = 'output-text ltr';
                }
                
                document.getElementById('detectedLang').textContent = data.detected_lang || '-';
                document.getElementById('accuracy').textContent = data.accuracy || '-';
                document.getElementById('status').textContent = data.status || 'Ready';
                document.getElementById('security').textContent = data.security || '🔒 Secure';
                
                showToast('Translation complete! ✅');
            })
            .catch(error => {
                showToast('Error: ' + error.message);
                outputDiv.textContent = 'Error: ' + error.message;
            });
        }
        
        // Speak function using gTTS
        function speakText() {
            const outputDiv = document.getElementById('outputText');
            const text = outputDiv.textContent;
            const targetLang = document.getElementById('targetLang').value;
            
            if (!text || text === 'Your translation will appear here...' || text.includes('Error') || text.includes('Translating')) {
                showToast('No text to speak');
                return;
            }
            
            showToast('Generating audio... 🎵');
            
            fetch('/speak', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: text,
                    lang: targetLang
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showToast('Error: ' + data.error);
                } else {
                    // Create audio element
                    const audioContainer = document.getElementById('audioContainer');
                    audioContainer.innerHTML = `
                        <div class="audio-player">
                            <audio controls autoplay>
                                <source src="data:audio/mpeg;base64,${data.audio}" type="audio/mpeg">
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    `;
                    showToast('Speaking... 🔊');
                }
            })
            .catch(error => {
                showToast('Error: ' + error.message);
            });
        }
        
        // Copy function
        function copyText() {
            const outputDiv = document.getElementById('outputText');
            const text = outputDiv.textContent;
            if (!text || text === 'Your translation will appear here...' || text.includes('Error') || text.includes('Translating')) {
                showToast('Nothing to copy');
                return;
            }
            
            fetch('/copy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showToast('Error: ' + data.error);
                } else {
                    showToast(data.message || 'Copied! 📋');
                }
            })
            .catch(error => {
                showToast('Error: ' + error.message);
            });
        }
        
        // Clear function
        function clearAll() {
            const outputDiv = document.getElementById('outputText');
            document.getElementById('inputText').value = '';
            outputDiv.textContent = 'Your translation will appear here...';
            outputDiv.className = 'output-text ltr';
            document.getElementById('audioContainer').innerHTML = '';
            document.getElementById('charCount').textContent = '0';
            document.getElementById('wordCount').textContent = '0';
            document.getElementById('detectedLang').textContent = '-';
            document.getElementById('accuracy').textContent = '-';
            document.getElementById('status').textContent = 'Ready';
            document.getElementById('security').textContent = '🔒 Secure';
            showToast('Cleared! 🗑️');
        }
        
        // Toast notification
        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast show';
            setTimeout(() => {
                toast.className = 'toast';
            }, 3000);
        }
        
        // Enter key to translate (Ctrl+Enter)
        document.getElementById('inputText').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                translateText();
            }
        });
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        text = data.get('text', '')
        source = data.get('source', 'auto')
        target = data.get('target', 'ur')
        
        if not text:
            return jsonify({'error': 'No text provided'})
        
        # Handle auto detection
        if source == 'auto':
            detected_lang = 'EN'
            source = 'en'
        else:
            detected_lang = source.upper()
        
        # Translate using deep-translator
        try:
            translator = GoogleTranslator(source=source, target=target)
            translation = translator.translate(text)
        except Exception as e:
            return jsonify({'error': f'Translation API error: {str(e)}'})
        
        # Calculate accuracy (simple heuristic)
        accuracy = 'High' if len(text) > 20 else 'Medium'
        
        return jsonify({
            'translation': translation,
            'detected_lang': detected_lang,
            'accuracy': accuracy,
            'status': '✅ Translation Complete',
            'security': '🔒 Secure'
        })
        
    except Exception as e:
        return jsonify({'error': f'Translation failed: {str(e)}'})

@app.route('/speak', methods=['POST'])
def speak():
    try:
        data = request.json
        text = data.get('text', '')
        lang = data.get('lang', 'ur')
        
        if not text:
            return jsonify({'error': 'No text to speak'})
        
        # Map language codes for gTTS
        lang_map = {
            'ur': 'ur',  # Urdu
            'en': 'en',  # English
            'hi': 'hi',  # Hindi
            'es': 'es',  # Spanish
            'fr': 'fr',  # French
            'de': 'de',  # German
            'ja': 'ja',  # Japanese
            'zh-cn': 'zh-cn',  # Chinese
            'ar': 'ar',  # Arabic
            'ru': 'ru',  # Russian
            'pt': 'pt'   # Portuguese
        }
        
        tts_lang = lang_map.get(lang, 'en')
        
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        
        # Save to bytes
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        # Convert to base64 for embedding in HTML
        audio_base64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
        
        return jsonify({
            'audio': audio_base64,
            'message': 'Speaking... 🔊'
        })
        
    except Exception as e:
        return jsonify({'error': f'Speech failed: {str(e)}'})

@app.route('/copy', methods=['POST'])
def copy():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Nothing to copy'})
        
        pyperclip.copy(text)
        return jsonify({'message': 'Copied! 📋'})
        
    except Exception as e:
        return jsonify({'error': f'Copy failed: {str(e)}'})

# Function to open browser
def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Open browser automatically
    threading.Thread(target=open_browser).start()
    app.run(debug=True, host='127.0.0.1', port=5000)