from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.request
import urllib.error
import json

app = Flask(__name__)
CORS(app)

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


@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    if not data or not data.get("message"):
        return jsonify({"error": "Message is required"}), 400

    user_message = data["message"].strip()
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return jsonify({"error": "OpenAI API key not configured"}), 500

    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }).encode("utf-8")

    req = urllib.request.Request(
        url="https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            reply = result["choices"][0]["message"]["content"].strip()
            return jsonify({"reply": reply})
    except urllib.error.HTTPError as e:
        return jsonify({"error": f"OpenAI error: {e.code}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
