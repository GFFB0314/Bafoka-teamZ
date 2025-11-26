# Quick Reference: Botpress Voice Configuration

## 🎯 The One Change You Need

### Current (Missing audio_url):
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}"
}
```

### ✅ Updated (Returns audio_url):
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}",
  "output_format": "both"
}
```

---

## 📋 Botpress Voice Workflow - Quick Setup

### 1️⃣ Configuration Variable (One-time setup)
**Location:** Variables → Configuration

```
Name: apiBaseUrl
Type: Configuration
Scope: Bot
Value: https://your-ngrok-url.ngrok-free.app
```

### 2️⃣ Workflow Trigger
**Type:** User Sends Audio (or Message Type = Audio)

### 3️⃣ API Call Card
**Method:** POST
**URL:** `{{config.apiBaseUrl}}/api/voice/process`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}",
  "output_format": "both"
}
```

**Save Response To:** `voiceResponse`

### 4️⃣ Display Response

**Option A: Text + Audio (Recommended)**
```
Text: {{voiceResponse.data.response_text}}
Audio: {{voiceResponse.data.audio_url}}
```

**Option B: Audio Only**
```
Audio: {{voiceResponse.data.audio_url}}
```

**Optional: Show Transcription**
```
Text: I heard: "{{voiceResponse.data.transcription}}"
```

---

## 🔌 API Response Structure

When Botpress calls `/api/voice/process`, it receives:

```json
{
  "success": true,
  "transcription": "check my balance",
  "response_text": "User not found. /register first.",
  "audio_url": "https://abc123.ngrok-free.app/static/audio/output/response_xyz123.mp3"
}
```

### Accessing Response Data in Botpress:
- Success: `{{voiceResponse.data.success}}`
- Transcription: `{{voiceResponse.data.transcription}}`
- Text Response: `{{voiceResponse.data.response_text}}`
- Audio URL: `{{voiceResponse.data.audio_url}}`

---

## 🎨 Complete Workflow Visual

```
┌─────────────────────────────────────┐
│  User Sends Voice Message           │
│  "Check my balance"                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Trigger: User Sends Audio          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Call API                           │
│  POST /api/voice/process            │
│  {                                  │
│    "audio_url": "...",              │
│    "phone": "+237...",              │
│    "output_format": "both"          │
│  }                                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Backend Processing:                │
│  1. Download audio                  │
│  2. Transcribe (Whisper)            │
│  3. Process command (NLU)           │
│  4. Execute command                 │
│  5. Generate audio (gTTS)           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Response Received:                 │
│  {                                  │
│    "transcription": "...",          │
│    "response_text": "...",          │
│    "audio_url": "https://..."       │
│  }                                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Send to User:                      │
│  📝 Text: response_text             │
│  🔊 Audio: audio_url                │
└─────────────────────────────────────┘
```

---

## 🧪 Testing Checklist

### Before Testing:
- [ ] Ngrok is running
- [ ] `apiBaseUrl` variable updated with current ngrok URL
- [ ] Botpress bot published
- [ ] Flask server running (`python .\app.py`)

### Send Voice Message:
- [ ] Say: "Check my balance"
- [ ] Verify bot responds with audio
- [ ] Check Flask logs for `[VOICE]` entries

### Expected Flask Logs:
```
[VOICE] Received JSON request: {'audio_url': '...', 'phone': '...', 'output_format': 'both'}
[VOICE] Parameters - Phone: +237..., Output Format: both
[VOICE] Transcribing audio with Whisper...
[VOICE] Transcription: check my balance
[VOICE] Executing command: /balance
[VOICE] Command response: User not found. /register first.
[VOICE] Generating audio response with gTTS...
[VOICE] ✅ Audio response URL generated: https://...
```

### If Audio URL Missing:
Look for: `⚠️ Skipping audio generation - output_format is 'text'`
**Fix:** Add `"output_format": "both"` to Botpress request

---

## 🔧 Common Botpress Variables

### Event Variables (Built-in):
- `{{event.payload.audioUrl}}` - Voice message URL from WhatsApp
- `{{event.payload.from}}` - User's phone (format: `whatsapp:+237...`)
- `{{event.payload.text}}` - Text content (empty for audio)

### Custom Variables (You create):
- `{{config.apiBaseUrl}}` - Your ngrok URL
- `{{voiceResponse}}` - API response storage
- `{{user.phone}}` - User's normalized phone (you can set this)

---

## ⚡ Quick Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| No audio response | Botpress logs → API response | Add `"output_format": "both"` |
| API call fails | Ngrok running? | Restart ngrok, update `apiBaseUrl` |
| Wrong transcription | Flask logs → transcription | Speak more clearly |
| Command not recognized | Flask logs → NLU output | Check VOICE_COMMAND_GUIDE.md |
| 500 error | Flask terminal | Check error stack trace |

---

## 📞 Support Commands for Voice

### Users Should Say:
- **Balance:** "Check my balance" or "How much money do I have"
- **Register:** "Register me, my name is John from Bameka, I'm 25, I do farming"
- **Simple Register:** "Register me, I am Alice"
- **Transfer:** "Transfer 100 to plus two three seven..."
- **Search:** "Find a plumber" or "Search for farming"
- **Help:** "Help" or "What can you do"

---

## 📁 Files Reference

- **Full Setup Guide:** [BOTPRESS_VOICE_SETUP.md](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/BOTPRESS_VOICE_SETUP.md)
- **Voice Commands:** [VOICE_COMMAND_GUIDE.md](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/VOICE_COMMAND_GUIDE.md)
- **Debug Guide:** [DEBUG_VOICE_ISSUE.md](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/DEBUG_VOICE_ISSUE.md)
- **API Reference:** [botpress_guide.md](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/botpress_guide.md)

---

## ✅ That's It!

**Just add `"output_format": "both"` and you're done!** 🎉

The backend is already fixed and ready to handle voice commands properly.
