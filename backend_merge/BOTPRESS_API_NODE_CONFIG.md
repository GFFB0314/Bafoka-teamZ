# Botpress "Call API" Node - Exact Configuration

## 🎯 What Code/Configuration Goes in "Call API" Node

When you add a **"Call API"** card in Botpress, here's EXACTLY what you put in each field:

---

## 📝 Field-by-Field Configuration

### 1️⃣ **Method** (Dropdown)
```
POST
```

### 2️⃣ **URL** (Text field)
```
{{config.apiBaseUrl}}/api/voice/process
```

**Explanation:**
- `{{config.apiBaseUrl}}` - This is the variable you created with your ngrok URL
- `/api/voice/process` - The endpoint path on your Flask backend

**Full URL will be:** `https://your-ngrok-url.ngrok-free.app/api/voice/process`

---

### 3️⃣ **Headers** (JSON/Code field)
```json
{
  "Content-Type": "application/json"
}
```

**Or if there's a separate field for each header:**
- **Key:** `Content-Type`
- **Value:** `application/json`

---

### 4️⃣ **Body** (JSON/Code field) ⚠️ **MOST IMPORTANT**
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}",
  "output_format": "both"
}
```

**Line-by-line explanation:**
- `"audio_url": "{{event.payload.audioUrl}}"` - The URL of the voice message WhatsApp sent
- `"phone": "{{event.payload.from}}"` - User's phone number (format: `whatsapp:+237...`)
- `"output_format": "both"` - **THE CRITICAL LINE** - Tells backend to generate audio response

---

### 5️⃣ **Save Response To** (Variable name field)
```
voiceResponse
```

**Or:**
```
workflow.voiceResponse
```

**Explanation:** This creates a variable to store the API response. You'll use it later like:
- `{{voiceResponse.data.transcription}}`
- `{{voiceResponse.data.response_text}}`
- `{{voiceResponse.data.audio_url}}`

---

### 6️⃣ **Timeout** (Number field, optional)
```
60000
```

**Explanation:** 60 seconds (60,000 milliseconds). Voice processing can take 10-30 seconds, so use a generous timeout.

---

## 🖼️ Visual Layout in Botpress

Here's what the "Call API" card looks like when configured:

```
┌─────────────────────────────────────────────────────┐
│  Call API                                           │
├─────────────────────────────────────────────────────┤
│  Method:     [POST ▼]                               │
│                                                     │
│  URL:        {{config.apiBaseUrl}}/api/voice/process│
│                                                     │
│  Headers:                                           │
│  ┌───────────────────────────────────────────────┐ │
│  │ {                                             │ │
│  │   "Content-Type": "application/json"          │ │
│  │ }                                             │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Body:                                             │
│  ┌───────────────────────────────────────────────┐ │
│  │ {                                             │ │
│  │   "audio_url": "{{event.payload.audioUrl}}",  │ │
│  │   "phone": "{{event.payload.from}}",          │ │
│  │   "output_format": "both"                     │ │
│  │ }                                             │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Save Response To:  voiceResponse                  │
│                                                     │
│  Timeout (ms):      60000                          │
│                                                     │
│  [Save]  [Cancel]                                  │
└─────────────────────────────────────────────────────┘
```

---

## 💡 Alternative: Execute Code Card

If you prefer to use an **"Execute Code"** card instead of "Call API", here's the JavaScript code:

```javascript
const axios = require('axios');

// API endpoint
const apiUrl = `${bp.config.apiBaseUrl}/api/voice/process`;

// Request payload
const payload = {
  audio_url: event.payload.audioUrl,
  phone: event.payload.from,
  output_format: 'both'  // ← CRITICAL LINE
};

try {
  // Make API call
  const response = await axios.post(apiUrl, payload, {
    headers: {
      'Content-Type': 'application/json'
    },
    timeout: 60000  // 60 seconds
  });
  
  // Save response to workflow variable
  workflow.voiceResponse = response.data;
  workflow.success = true;
  
  // Log for debugging
  console.log('[Voice] Transcription:', response.data.transcription);
  console.log('[Voice] Response:', response.data.response_text);
  console.log('[Voice] Audio URL:', response.data.audio_url);
  
} catch (error) {
  // Handle errors
  workflow.success = false;
  workflow.error = error.message;
  console.error('[Voice] Error:', error.message);
}
```

**When to use "Execute Code" vs "Call API":**
- **Call API:** Simpler, visual, no coding needed (RECOMMENDED)
- **Execute Code:** More control, better error handling, logging

---

## 🔍 Understanding the Variables

### Input Variables (From Botpress/WhatsApp):

**`{{event.payload.audioUrl}}`**
- **What it is:** URL to the voice message file
- **Example value:** `https://media.whatsapp.com/v/t62.7117-24/...`
- **Source:** WhatsApp sends this when user records voice message

**`{{event.payload.from}}`**
- **What it is:** User's phone number in WhatsApp format
- **Example value:** `whatsapp:+237600123456`
- **Source:** WhatsApp user identifier

**`{{config.apiBaseUrl}}`**
- **What it is:** Your Flask backend URL
- **Example value:** `https://abc123.ngrok-free.app`
- **Source:** You set this in Variables → Configuration

### Output Variable (Response):

**`voiceResponse`** (or `workflow.voiceResponse`)

After the API call completes, this contains:
```json
{
  "data": {
    "success": true,
    "transcription": "check my balance",
    "response_text": "User not found. /register first.",
    "audio_url": "https://abc123.ngrok-free.app/static/audio/output/response_xyz.mp3"
  },
  "status": 200,
  "statusText": "OK",
  "headers": {...}
}
```

---

## 📊 Complete Example with Real Data

### What Botpress Sends:
```json
POST https://abc123.ngrok-free.app/api/voice/process

Headers:
{
  "Content-Type": "application/json"
}

Body:
{
  "audio_url": "https://media.whatsapp.com/v/t62.7117-24/12345.ogg",
  "phone": "whatsapp:+237600123456",
  "output_format": "both"
}
```

### What Flask Backend Returns:
```json
200 OK

{
  "success": true,
  "transcription": "check my balance",
  "response_text": "User not found. /register first.",
  "audio_url": "https://abc123.ngrok-free.app/static/audio/output/response_abc123.mp3"
}
```

### How You Access It in Next Cards:
```javascript
{{voiceResponse.data.success}}        // true
{{voiceResponse.data.transcription}}  // "check my balance"
{{voiceResponse.data.response_text}}  // "User not found. /register first."
{{voiceResponse.data.audio_url}}      // "https://abc123.ngrok-free.app/static/..."
```

---

## ✅ Quick Copy-Paste Reference

### For "Call API" Card:

**Method:**
```
POST
```

**URL:**
```
{{config.apiBaseUrl}}/api/voice/process
```

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}",
  "output_format": "both"
}
```

**Save Response To:**
```
voiceResponse
```

**Timeout:**
```
60000
```

---

## 🚨 Common Mistakes to Avoid

### ❌ Wrong:
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}"
}
```
**Problem:** Missing `output_format` → No audio response generated

### ❌ Wrong:
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}",
  "output_format": "text"
}
```
**Problem:** `output_format` set to "text" → No audio response

### ❌ Wrong:
```
{{variables.apiBaseUrl}}/api/voice/process
```
**Problem:** Should be `{{config.apiBaseUrl}}` (not `variables`)

### ✅ Correct:
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}",
  "output_format": "both"
}
```
**Perfect!** ✨

---

## 🧪 How to Test Your Configuration

### Step 1: Publish Bot
Click "Publish" in Botpress

### Step 2: Send Voice Message
Say: "Check my balance"

### Step 3: Check Botpress Logs
Look for:
```
HTTP POST /api/voice/process
Request: {"audio_url":"...","phone":"...","output_format":"both"}
Response: {"success":true,"transcription":"...","audio_url":"..."}
```

### Step 4: Check Flask Logs
Should show:
```
[VOICE] Parameters - Phone: +237..., Output Format: both
[VOICE] ✅ Audio response URL generated: https://...
```

If you see `⚠️ Skipping audio generation`, the `output_format` wasn't sent correctly.

---

## 📚 Summary

**In your "Call API" node, you need:**

1. **Method:** POST
2. **URL:** `{{config.apiBaseUrl}}/api/voice/process`
3. **Headers:** `{"Content-Type": "application/json"}`
4. **Body:** 
   ```json
   {
     "audio_url": "{{event.payload.audioUrl}}",
     "phone": "{{event.payload.from}}",
     "output_format": "both"
   }
   ```
5. **Save Response To:** `voiceResponse`
6. **Timeout:** `60000`

**That's it!** Just copy these exact values into the corresponding fields in your Botpress "Call API" card. 🎯
