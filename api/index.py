import urllib.parse
import http.server
import socketserver

PORT = 8080

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
    cleaned = user_message.lower().strip().rstrip('?!.')
    if cleaned in CHATBOT_RESPONSES:
        return CHATBOT_RESPONSES[cleaned]
    for key, response in CHATBOT_RESPONSES.items():
        if key in cleaned or cleaned in key:
            return response
    return "I'm sorry, I don't quite understand that. Type 'help' to see a list of things you can ask me!"

def render_html():
    if not last_user_message:
        message_html = "<p><em>No messages yet. Say hello to start the chat!</em></p>"
    else:
        message_html = f"""<p><b>You:</b> {last_user_message}</p>
        <p><b>PyBot:</b> {last_bot_reply}</p>"""
        
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

# Vercel Serverless Function entrypoint (WSGI compliance)
def app(environ, start_response):
    global last_user_message, last_bot_reply
    
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    if method == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
            
        request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
        params = urllib.parse.parse_qs(request_body)
        user_message = params.get('user_input', [''])[0].strip()
        
        if user_message:
            last_user_message = user_message
            last_bot_reply = get_bot_response(user_message)
            
        # Post-Redirect-Get pattern
        status = '303 See Other'
        response_headers = [('Location', '/')]
        start_response(status, response_headers)
        return [b'']
        
    else: # GET
        if path == '/clear':
            last_user_message = ""
            last_bot_reply = ""
            status = '303 See Other'
            response_headers = [('Location', '/')]
            start_response(status, response_headers)
            return [b'']
            
        response_body = render_html()
        status = '200 OK'
        response_headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(response_body.encode('utf-8'))))
        ]
        start_response(status, response_headers)
        return [response_body.encode('utf-8')]

# For running locally via Python directly
class ChatbotHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global last_user_message, last_bot_reply
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
        self.wfile.write(render_html().encode("utf-8"))

    def do_POST(self):
        global last_user_message, last_bot_reply
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)
        user_message = params.get('user_input', [''])[0].strip()
        if user_message:
            last_user_message = user_message
            last_bot_reply = get_bot_response(user_message)
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

if __name__ == "__main__":
    handler = ChatbotHandler
    handler.directory = "."
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Chatbot server started at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
