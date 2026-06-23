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
- Cloud computing: AWS, Azure, GCP, DevOps, certifications (CCNA, AWS SAA, etc.)
Keep responses concise, friendly, and practical. Use **bold** for key terms.
Always be encouraging and supportive to students."""


def handler(request):
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }

    if request.method == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": cors_headers,
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()
    except Exception:
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": json.dumps({"error": "Invalid JSON"})
        }

    if not user_message:
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": json.dumps({"error": "Message is required"})
        }

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": "OpenAI API key not configured"})
        }

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
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({"reply": reply})
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return {
            "statusCode": 502,
            "headers": cors_headers,
            "body": json.dumps({"error": f"OpenAI error {e.code}", "details": error_body})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)})
        }
