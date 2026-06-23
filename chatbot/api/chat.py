from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

SYSTEM_PROMPT = """You are UniBot, a friendly and knowledgeable AI assistant 
designed specifically to help university students. You assist with:

- Academic topics: study tips, exam preparation, time management, assignment writing
- Course subjects: mathematics, computer science, engineering, cloud computing, networking
- Career guidance: internships, resume building, LinkedIn, job applications
- Postgraduate advice: Masters applications, scholarships, GRE/IELTS preparation
- University life: stress management, group projects, deadlines, campus life
- Cloud computing concepts: AWS, Azure, GCP, DevOps, certifications (CCNA, AWS SAA, etc.)

Keep responses concise, friendly, and practical. Use bullet points for lists.
Use **bold** for key terms. Maximum 3 paragraphs unless a longer answer is needed.
Always be encouraging and supportive to students."""


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            user_message = data.get("message", "").strip()
        except Exception:
            self._respond(400, {"error": "Invalid JSON"})
            return

        if not user_message:
            self._respond(400, {"error": "Message is empty"})
            return

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self._respond(500, {"error": "API key not configured"})
            return

        # Call OpenAI
        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                reply = result["choices"][0]["message"]["content"].strip()
            self._respond(200, {"reply": reply})
        except urllib.error.HTTPError as e:
            self._respond(502, {"error": f"OpenAI error: {e.code}"})
        except Exception as e:
            self._respond(502, {"error": str(e)})

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, status, body_dict):
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body_dict).encode("utf-8"))

    def log_message(self, format, *args):
        pass  # suppress default logging
