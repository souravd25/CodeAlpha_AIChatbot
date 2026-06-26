/* ============================================
   UniBot - University Student AI Chatbot
   JavaScript Logic
   CodeAlpha Cloud Computing Internship
   ============================================ */


// ── Configuration ──────────────────────────────────────────

// Gemini API endpoint (free tier)
const GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

// System prompt: tells Gemini how to behave
const SYSTEM_PROMPT = `You are UniBot, a friendly and helpful AI assistant for university students.
You help with:
- Study tips, exam preparation, time management
- Computer science, engineering, cloud computing topics
- Career advice, internships, resume writing, LinkedIn
- Postgraduate applications, scholarships, IELTS/GRE prep
- AWS, Azure, Google Cloud, CCNA certifications
Keep answers concise, friendly, and encouraging.
Use **bold** for important terms.`;


// ── State Variables ─────────────────────────────────────────

let apiKey = sessionStorage.getItem("gemini_key") || "";  // Stored key
let isLoading = false;                                      // Prevent double sends


// ── On Page Load ────────────────────────────────────────────

updateBanner();  // Show or hide the API key banner


// ── API Key Functions ────────────────────────────────────────

// Show the banner if no key is saved, hide it if key exists
function updateBanner() {
  document.getElementById("apiBanner").style.display = apiKey ? "none" : "flex";
}

// Save the API key when user clicks Save Key
function saveKey() {
  const input = document.getElementById("apiKeyInput");
  const val = input.value.trim();

  // Basic validation — just check it's not empty
  if (val.length < 10) {
    alert("Please enter a valid Gemini API key.");
    return;
  }

  // Save to session storage (cleared when browser tab closes)
  apiKey = val;
  sessionStorage.setItem("gemini_key", val);
  updateBanner();

  // Show a welcome message
  addBotMessage("✅ API key saved! I'm ready to help. Ask me anything about university life!");
}


// ── Quick Chip Buttons ───────────────────────────────────────

// When user clicks a chip button, send that text as a message
function sendChip(button) {
  // Remove the emoji prefix (e.g. "📅 " from "📅 Exam prep tips")
  const text = button.textContent.replace(/^\S+\s/, "");
  document.getElementById("userInput").value = text;
  sendMessage();
}


// ── Chat Helper Functions ────────────────────────────────────

// Add a timestamp line in the chat
function addTimestamp() {
  const chat = document.getElementById("chat");
  const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const ts = document.createElement("div");
  ts.className = "timestamp";
  ts.textContent = time;
  chat.appendChild(ts);
}

// Add a message bubble (role = "bot" or "user")
function addMessage(text, role) {
  const chat = document.getElementById("chat");

  // Remove empty state on first message
  const emptyState = document.getElementById("emptyState");
  if (emptyState) emptyState.remove();

  // Create message row
  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  // Create avatar
  const avatar = document.createElement("div");
  avatar.className = `avatar ${role}`;
  avatar.textContent = role === "bot" ? "🎓" : "👤";

  // Create bubble
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;

  // Convert **bold** markdown to <strong> tags
  bubble.innerHTML = text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");

  row.appendChild(avatar);
  row.appendChild(bubble);
  chat.appendChild(row);

  // Scroll to bottom
  chat.scrollTop = chat.scrollHeight;
}

// Shortcut functions
function addBotMessage(text)  { addMessage(text, "bot");  }
function addUserMessage(text) { addMessage(text, "user"); }

// Show animated typing dots while waiting for response
function showTyping() {
  const chat = document.getElementById("chat");
  const row = document.createElement("div");
  row.className = "message-row bot";
  row.id = "typingIndicator";
  row.innerHTML = `
    <div class="avatar bot">🎓</div>
    <div class="bubble bot">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>`;
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
}

// Remove typing dots
function hideTyping() {
  const indicator = document.getElementById("typingIndicator");
  if (indicator) indicator.remove();
}


// ── Auto-resize Textarea ─────────────────────────────────────

const textarea = document.getElementById("userInput");

textarea.addEventListener("input", () => {
  textarea.style.height = "auto";
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
});

// Send on Enter key (Shift+Enter for new line)
textarea.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});


// ── Main Send Function ───────────────────────────────────────

async function sendMessage() {
  // Guard checks
  if (isLoading) return;
  if (!apiKey) {
    alert("Please enter your Gemini API key first!");
    return;
  }

  const text = textarea.value.trim();
  if (!text) return;

  // Update UI state
  isLoading = true;
  textarea.value = "";
  textarea.style.height = "auto";
  document.getElementById("sendBtn").disabled = true;

  // Show user message
  addTimestamp();
  addUserMessage(text);
  showTyping();

  try {
    // Call Gemini API
    const response = await fetch(`${GEMINI_API_URL}?key=${apiKey}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        system_instruction: {
          parts: [{ text: SYSTEM_PROMPT }]
        },
        contents: [{
          parts: [{ text: text }]
        }]
      })
    });

    const data = await response.json();
    hideTyping();

    // Handle successful response
    if (data.candidates && data.candidates[0]) {
      const reply = data.candidates[0].content.parts[0].text.trim();
      addTimestamp();
      addBotMessage(reply);

    // Handle API error response
    } else if (data.error) {
      addBotMessage(`⚠️ Error: ${data.error.message}`);

    } else {
      addBotMessage("⚠️ Unexpected response. Please try again.");
    }

  } catch (error) {
    // Handle network errors
    hideTyping();
    addBotMessage("⚠️ Network error. Please check your internet connection.");
    console.error("Gemini API error:", error);
  }

  // Reset UI state
  isLoading = false;
  document.getElementById("sendBtn").disabled = false;
  textarea.focus();
}
