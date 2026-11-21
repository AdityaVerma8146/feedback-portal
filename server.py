import http.server
import json
import os
import socketserver
import time

PORT = 3000
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "local_feedback.json")

DEFAULT_FEEDBACK = [
    {
        "feedbackId": "seed-1",
        "name": "Aditya Verma",
        "email": "aditya@example.com",
        "rating": 5,
        "message": "Feedback portal is running locally and ready for testing!",
        "createdAt": int(time.time()) - 1800
    },
    {
        "feedbackId": "seed-2",
        "name": "Student Reviewer",
        "email": "student@example.com",
        "rating": 5,
        "message": "Clean, responsive design and lightning fast feedback submission.",
        "createdAt": int(time.time()) - 7200
    }
]

def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_FEEDBACK, f, indent=2)
        return DEFAULT_FEEDBACK
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_FEEDBACK

def save_feedback(items):
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

class PortalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/feedback":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            items = load_feedback()
            self.wfile.write(json.dumps({"items": items}).encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/feedback":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            items = load_feedback()
            new_item = {
                "feedbackId": f"local-{int(time.time())}",
                "name": data.get("name", "").strip(),
                "email": data.get("email", "").strip(),
                "rating": int(data.get("rating", 5)),
                "message": data.get("message", "").strip(),
                "createdAt": int(time.time())
            }
            items.insert(0, new_item)
            save_feedback(items)
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Thank you! Feedback saved successfully.",
                "feedbackId": new_item["feedbackId"]
            }).encode("utf-8"))
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    web_dir = os.path.dirname(__file__)
    os.chdir(web_dir)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortalHandler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        httpd.serve_forever()
