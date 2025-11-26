# Quick Fix Checklist for Your Botpress Flow

## 🎯 Based on Your Screenshot

Your flow structure is **perfect**! Just need to fix the Execute Code.

---

## ✅ What's Already Good:
- ✅ Entry → Voice_Trigger → Call_Voice_API → Response (correct flow)
- ✅ Error handling branch
- ✅ Proper routing conditions
- ✅ Exit points

---

## 🔧 What to Fix:

### 1️⃣ **"Call_Voice_API" Node - Replace Execute Code**

**Open your "Call_Voice_API" execute code card and replace with:**

```javascript
const axios = require('axios');

const audioUrl = event.payload.audioUrl;
const userPhone = event.payload.from;

if (!audioUrl || !userPhone) {
  workflow.error = 'Missing audio URL or phone';
  workflow.responseText = 'Sorry, I could not process your request.';
  return;
}

try {
  const response = await axios.post(
    `${bp.config.apiBaseUrl}/api/voice/process`,
    {
      audio_url: audioUrl,
      phone: userPhone,
      output_format: 'both'  // ⚠️ THIS LINE IS CRITICAL!
    },
    {
      headers: { 'Content-Type': 'application/json' },
      timeout: 60000
    }
  );

  if (response.data && response.data.success) {
    workflow.transcription = response.data.transcription || '';
    workflow.responseText = response.data.response_text || 'No response';
    workflow.audioUrl = response.data.audio_url || null;
    workflow.error = null;
    
    console.log('[Voice] Success:', workflow.transcription);
  } else {
    workflow.error = response.data.error || 'Backend error';
    workflow.responseText = 'Sorry, I could not process your voice message.';
    workflow.audioUrl = null;
  }
} catch (error) {
  workflow.error = error.message;
  workflow.responseText = 'Sorry, an error occurred. Please try again.';
  workflow.audioUrl = null;
  console.error('[Voice] Exception:', error.message);
}
```

---

### 2️⃣ **"Send_Voice_Response" Node**

Make sure you have **TWO cards:**

**Card 1: Text Message**
```
{{workflow.responseText}}
```

**Card 2: Audio/Voice Message**
- Type: **Send Audio** or **Play Audio**
- Audio URL: `{{workflow.audioUrl}}`

---

### 3️⃣ **Routing Conditions**

After "Call_Voice_API", your condition should be:

**To "Send_Voice_Response" (success):**
```javascript
workflow.error === null
```

**To "Voice_Error_Response" (error):**
```javascript
workflow.error !== null
```

---

## 🎯 The One Critical Line

The most important fix is this line in your Execute Code:

```javascript
output_format: 'both'  // ← Add this!
```

Without it, your backend won't generate audio responses.

---

## 🧪 Test After Fixing

1. **Update** Execute Code in "Call_Voice_API"
2. **Publish** bot
3. **Send** voice: "Check my balance"
4. **Should receive:** Text + Audio response
5. **Check Flask logs** for:
   ```
   [VOICE] Parameters - Phone: +237..., Output Format: both
   [VOICE] ✅ Audio response URL generated: https://...
   ```

If you see:
```
[VOICE] ⚠️ Skipping audio generation - output_format is 'text'
```
Then the fix wasn't applied correctly.

---

## ✅ Your Flow is Almost Perfect!

Just copy the Execute Code above into your "Call_Voice_API" node and you're done! 🎉
