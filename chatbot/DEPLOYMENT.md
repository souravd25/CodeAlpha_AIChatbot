# Task 4: UniBot — AWS Deployment Guide
## CodeAlpha Cloud Computing Internship

---

## Files in this project
```
chatbot/
├── index.html          ← Frontend (deploy to S3)
├── lambda_function.py  ← Backend (deploy to Lambda)
└── DEPLOYMENT.md       ← This guide
```

---

## PART A — Deploy Lambda (Backend)

### Step 1: Open AWS Lambda
1. Log in to https://aws.amazon.com
2. Search **Lambda** in the top search bar → click it
3. Click **"Create function"**

### Step 2: Configure the function
- Select: **Author from scratch**
- Function name: `UniBot`
- Runtime: **Python 3.12**
- Architecture: x86_64
- Click **"Create function"**

### Step 3: Add the code
1. In the **Code source** tab, you'll see a file `lambda_function.py`
2. Delete all existing code
3. Copy-paste the entire content of `lambda_function.py` from this project
4. Click **"Deploy"** (orange button)

### Step 4: Add your OpenAI API key
1. Click the **"Configuration"** tab
2. Click **"Environment variables"** → **"Edit"**
3. Click **"Add environment variable"**
   - Key: `OPENAI_API_KEY`
   - Value: your OpenAI API key (get one at platform.openai.com)
4. Click **"Save"**

### Step 5: Set timeout
1. Still in **Configuration** tab → click **"General configuration"** → **"Edit"**
2. Set Timeout to **30 seconds**
3. Click **"Save"**

---

## PART B — Create API Gateway (Public URL)

### Step 1: Add a trigger to Lambda
1. Go back to your Lambda function
2. Click **"Add trigger"**
3. Select **"API Gateway"**
4. Choose: **Create a new API**
5. API type: **HTTP API**
6. Security: **Open**
7. Click **"Add"**

### Step 2: Get your API URL
1. After trigger is created, click on the **API Gateway** link shown
2. Copy the **Invoke URL** — it looks like:
   `https://xxxxxxxxxx.execute-api.ap-southeast-1.amazonaws.com/default/UniBot`
3. Save this URL — you'll need it next

---

## PART C — Update Frontend

1. Open `index.html` in any text editor
2. Find this line near the top of the `<script>` section:
   ```
   const API_URL = "YOUR_API_GATEWAY_URL_HERE";
   ```
3. Replace `YOUR_API_GATEWAY_URL_HERE` with the URL you copied above
4. Save the file

---

## PART D — Host Frontend on S3

### Step 1: Create an S3 bucket
1. Search **S3** in AWS → Click **"Create bucket"**
2. Bucket name: `unibot-chatbot-yourname` (must be globally unique)
3. Region: same as your Lambda (e.g. ap-southeast-1 for Singapore)
4. **Uncheck** "Block all public access" → confirm the warning
5. Click **"Create bucket"**

### Step 2: Enable static website hosting
1. Click your bucket → **Properties** tab
2. Scroll to **"Static website hosting"** → **Edit**
3. Enable it
4. Index document: `index.html`
5. Click **"Save changes"**

### Step 3: Set bucket policy (make it public)
1. Click **Permissions** tab → **Bucket policy** → **Edit**
2. Paste this (replace `YOUR-BUCKET-NAME`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    }
  ]
}
```
3. Click **"Save changes"**

### Step 4: Upload your file
1. Click **Objects** tab → **"Upload"**
2. Upload `index.html`
3. Click **"Upload"**

### Step 5: Get your live URL
1. Go to **Properties** → **Static website hosting**
2. Copy the **Bucket website endpoint**
3. Open it in your browser — your chatbot is LIVE! 🎉

---

## PART E — Test It

Open your S3 website URL and try:
- "What are some good exam preparation tips?"
- "Tell me about AWS certifications"
- "How do I write a good resume for internships?"
- "What is cloud computing?"

---

## For LinkedIn Post
Include:
- Live S3 URL
- GitHub repo: `CodeAlpha_AIChatbot`
- Tag: @CodeAlpha
- Show a screen recording of the chatbot answering questions

## GitHub Upload
```
Repository name: CodeAlpha_AIChatbot
Files to push: index.html, lambda_function.py, DEPLOYMENT.md
```
