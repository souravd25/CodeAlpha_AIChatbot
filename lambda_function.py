import json
import os
import urllib.request
import urllib.error

# ── System prompt ─────────────────────────────────────────────────────────────
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


def lambda_handler(event, context):
    # ── CORS headers (required for browser fetch calls) ───────────────────────
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Content-Type": "application/json"
    }

    # Handle preflight OPTIONS request
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}

    # ── Parse request body ────────────────────────────────────────────────────
    try:
        body = json.loads(event.get("body", "{}"))
        user_message = body.get("message", "").strip()
    except (json.JSONDecodeError, AttributeError):
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Invalid request body"})
        }

    if not user_message:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Message cannot be empty"})
        }

    # ── Get OpenAI API key from environment variable ──────────────────────────
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "OpenAI API key not configured"})
        }

    # ── Call OpenAI API ───────────────────────────────────────────────────────
    openai_payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }).encode("utf-8")

    request = urllib.request.Request(
        url="https://api.openai.com/v1/chat/completions",
        data=openai_payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            reply = result["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"OpenAI HTTPError {e.code}: {error_body}")
        return {
            "statusCode": 502,
            "headers": headers,
            "body": json.dumps({"error": f"OpenAI API error: {e.code}"})
        }
    except urllib.error.URLError as e:
        print(f"OpenAI URLError: {e.reason}")
        return {
            "statusCode": 502,
            "headers": headers,
            "body": json.dumps({"error": "Failed to reach OpenAI API"})
        }
    except (KeyError, IndexError) as e:
        print(f"Unexpected OpenAI response format: {e}")
        return {
            "statusCode": 502,
            "headers": headers,
            "body": json.dumps({"error": "Unexpected response from OpenAI"})
        }

    # ── Return reply to frontend ──────────────────────────────────────────────
    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({"reply": reply})
    }
