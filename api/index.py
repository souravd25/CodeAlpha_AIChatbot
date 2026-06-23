import os
import json
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


def handler(request):
    # Handle CORS preflight
    if request.method == "OPTIONS":
        from http.server import BaseHTTPRequestHandler
        pass

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }

    if request.method == "OPTIONS":
        return Response("", 200, headers)

    if request.method != "POST":
        return Response(json.dumps({"error": "Method not allowed"}), 405, headers)

    try:
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()
    except Exception:
        return Response(json.dumps({"error": "Invalid JSON"}), 400, headers)

    if not user_message:
        return Response(json.dumps({"error": "Message is required"}), 400, headers)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return Response(json.dumps({"error": "OpenAI API key not configured"}), 500, headers)

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
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            reply = result["choices"][0]["message"]["content"].strip()
            return Response(json.dumps({"reply": reply}), 200, headers)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return Response(json.dumps({"error": f"OpenAI error: {e.code}", "details": error_body}), 502, headers)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 500, headers)
