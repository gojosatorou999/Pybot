import http.server
import socketserver
import urllib.parse

PORT = 8080

# Exactly 18 hardcoded input/output mappings
CHATBOT_RESPONSES = {
    "hello": "Hello! I'm a simple Python chatbot. How can I help you today?",
    "how are you": "I am doing great, running smoothly on Python's built-in server!",
    "what is your name": "I am PyBot, a basic chatbot made with Python and HTML.",
    "who created you": "I was created by a brilliant programmer using pure Python!",
    "what is python": "Python is a powerful, elegant, and beginner-friendly programming language.",
    "what is html": "HTML stands for HyperText Markup Language, the backbone of all web pages.",
    "why no css": "To keep things simple, clean, and retro, just as you requested!",
    "why no javascript": "Because server-side Python can handle everything without complex JS!",
    "tell me a joke": "Why do programmers wear glasses? Because they can't C#!",
    "what is 2+2": "2 + 2 is 4. Math is one of my strong suits!",
    "what is the meaning of life": "To write clean Python code and enjoy the journey!",
    "favorite food": "I feast on electrical signals and data packets, but Python files are my favorite!",
    "favorite color": "I really like Python blue and snake green!",
    "bye": "Goodbye! It was nice chatting with you. Have a great day!",
    "how old are you": "I am brand new! I was started just moments ago.",
    "what time is it": "It's time to build amazing things with Python!",
    "help": "You can ask me: 'tell me a joke', 'what is python', 'favorite color', 'how are you', or just say 'hello'!",
    "weather": "Inside this CPU, it is a comfortable 72°F and 100% digital!"
}

# Global variables to store the last interaction
last_user_message = ""
last_bot_reply = ""

def get_bot_response(user_message):
    # Normalize user input: lowercase, strip extra whitespace, remove common punctuation at the end
    cleaned = user_message.lower().strip().rstrip('?!.')
    
    # Try exact match
    if cleaned in CHATBOT_RESPONSES:
        return CHATBOT_RESPONSES[cleaned]
    
    # Try partial matching/contains
    for key, response in CHATBOT_RESPONSES.items():
        if key in cleaned or cleaned in key:
            return response
            
    # Default fallback response if no match is found
    return "I'm sorry, I don't quite understand that. Type 'help' to see a list of things you can ask me!"

class ChatbotHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global last_user_message, last_bot_reply
        # Handle reset/clear request
        if self.path == "/clear":
            last_user_message = ""
            last_bot_reply = ""
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
            return
            
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        # Build the HTML content
        html = self.render_html()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        global last_user_message, last_bot_reply
        
        # Parse the form data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)
        
        user_message = params.get('user_input', [''])[0].strip()
        
        if user_message:
            last_user_message = user_message
            last_bot_reply = get_bot_response(user_message)
            
        # Redirect to GET to prevent form resubmission on refresh
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def render_html(self):
        # Generate the latest message in pure HTML
        if not last_user_message:
            message_html = "<p><em>No messages yet. Say hello to start the chat!</em></p>"
        else:
            message_html = f"""<p><b>You:</b> {last_user_message}</p>
            <p><b>PyBot:</b> {last_bot_reply}</p>"""
        
        # Pure HTML interface without CSS and JS
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>PyBot: Python Chatbot</title>
</head>
<body>
    <h1>PyBot: A Python Chatbot</h1>
    <p>This chatbot is built using only Python's standard library.</p>
    <hr>
    
    <h3>Response</h3>
    <div>
        {message_html}
    </div>
    
    <hr>
    
    <form method="POST" action="/">
        <label for="user_input"><b>You:</b> </label>
        <input type="text" id="user_input" name="user_input" size="50" required placeholder="Type something... (e.g., 'hello', 'tell me a joke', 'help')">
        <input type="submit" value="Send">
    </form>
    
    <hr>
    
</body>
</html>
"""
        return html_template

if __name__ == "__main__":
    handler = ChatbotHandler
    # Avoid standard handler static files behavior
    handler.directory = "."
    
    # Allow prompt reuse of the port
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Chatbot server started at http://localhost:{PORT}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
