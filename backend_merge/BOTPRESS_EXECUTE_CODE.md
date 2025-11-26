# Optimized Botpress Execute Code Cards

## 🎯 For "Call_Voice_API" Node - Execute Code

### ✅ Corrected & Optimized Code

```javascript
/**
 * Process Audio and Retrieve Voice Response
 * This calls your Flask backend to transcribe audio and generate response
 */

const axios = require('axios');

// Get user's audio message URL
const audioUrl = event.payload.audioUrl;
const userPhone = event.payload.from;

// Validate inputs
if (!audioUrl) {
  workflow.error = 'No audio URL provided';
  workflow.responseText = 'Sorry, I did not receive a voice message.';
  return;
}

if (!userPhone) {
  workflow.error = 'No user phone provided';
  workflow.responseText = 'Sorry, I could not identify your phone number.';
  return;
}

try {
  // Call Flask backend - CRITICAL: include output_format!
  const response = await axios.post(
    `${bp.config.apiBaseUrl}/api/voice/process`,
    {
      audio_url: audioUrl,
      phone: userPhone,
      output_format: 'both'  // ⚠️ CRITICAL - ensures audio response
    },
    {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 60000  // 60 seconds for voice processing
    }
  );

  // Check if request was successful
  if (response.data && response.data.success) {
    // Save response data to workflow variables
    workflow.transcription = response.data.transcription || '';
    workflow.responseText = response.data.response_text || 'No response available';
    workflow.audioUrl = response.data.audio_url || null;
    workflow.error = null;  // Clear any previous errors
    
    // Log success (helpful for debugging)
    console.log('[Voice] Success - Transcription:', workflow.transcription);
    console.log('[Voice] Audio URL:', workflow.audioUrl);
    
  } else {
    // Backend returned success: false
    workflow.error = response.data.error || 'Unknown error from backend';
    workflow.responseText = 'Sorry, I could not process your voice message. Please try again.';
    workflow.audioUrl = null;
    
    console.error('[Voice] Backend error:', workflow.error);
  }
  
} catch (error) {
  // Network or timeout error
  workflow.error = error.message || 'API call failed';
  workflow.responseText = 'Sorry, I encountered an error processing your voice message. Please try again.';
  workflow.audioUrl = null;
  
  console.error('[Voice] API call error:', error.message);
  
  // Log more details for debugging
  if (error.response) {
    console.error('[Voice] Status:', error.response.status);
    console.error('[Voice] Response:', error.response.data);
  }
}
```

---

## 🔧 For "Voice_Trigger" Node - Conditions

Your conditions look correct, but here's the optimized version:

### Option 1: Using Intent (if you have voice intent)
```javascript
// Check if this is a voice message
event.payload && event.payload.type === 'audio'
```

### Option 2: Using Audio URL presence
```javascript
// Check if audio URL exists
event.payload && event.payload.audioUrl
```

### Recommended: Combined Check
```javascript
// Most robust check
event.payload && 
event.payload.audioUrl && 
event.payload.audioUrl.length > 0
```

---

## 🎯 For Conditional Routing After API Call

### Success Condition (Route to Send_Voice_Response):
```javascript
workflow.error === null && workflow.audioUrl !== null
```

### Error Condition (Route to Voice_Error_Response):
```javascript
workflow.error !== null
```

---

## 📤 For "Send_Voice_Response" Node

### Text Message Card:
```
{{workflow.responseText}}
```

### Optional: Show Transcription (helpful for users)
```
I heard: "{{workflow.transcription}}"

{{workflow.responseText}}
```

### Audio Card:
**Audio URL:**
```
{{workflow.audioUrl}}
```

**Important:** Make sure you're using "Send Audio" or "Play Audio" card type, not just text.

---

## ⚠️ For "Voice_Error_Response" Node

### Error Message:
```
{{workflow.responseText}}
```

### Or more detailed:
```
Sorry, I couldn't process your voice message. 

Error: {{workflow.error}}

Please try sending a text message instead, or try your voice message again.
```

---

## 🚨 Common Issues Fixed in Above Code

### Issue 1: Missing `output_format` ❌
```javascript
// WRONG - No output_format
{
  audio_url: audioUrl,
  phone: userPhone
}
```

```javascript
// CORRECT ✅
{
  audio_url: audioUrl,
  phone: userPhone,
  output_format: 'both'  // ← CRITICAL!
}
```

### Issue 2: Not Checking Response Success ❌
```javascript
// WRONG - Assuming success
workflow.responseText = response.data.response_text;
```

```javascript
// CORRECT ✅
if (response.data && response.data.success) {
  workflow.responseText = response.data.response_text;
}
```

### Issue 3: Poor Error Handling ❌
```javascript
// WRONG - Generic catch
catch (error) {
  console.log(error);
}
```

```javascript
// CORRECT ✅
catch (error) {
  workflow.error = error.message;
  workflow.responseText = 'Sorry, I encountered an error...';
  console.error('[Voice] Details:', error.response?.data);
}
```

---

## 📊 Complete Workflow Variables Reference

After the "Call_Voice_API" Execute Code runs, you'll have these variables:

| Variable | Type | Example Value | When Set |
|----------|------|---------------|----------|
| `workflow.transcription` | string | "check my balance" | Always on success |
| `workflow.responseText` | string | "User not found..." | Always |
| `workflow.audioUrl` | string/null | "https://...response.mp3" | Only if output_format="both" |
| `workflow.error` | string/null | null or error message | Always |

---

## ✅ Updated Flow Recommendations

Based on your screenshot, here are the recommended fixes:

### 1. **Voice_Trigger Node:**
Keep your current trigger, but ensure condition is:
```javascript
event.payload && event.payload.audioUrl
```

### 2. **Call_Voice_API Node:**
Replace Execute Code with the optimized version above ☝️

### 3. **Conditional After API Call:**
- **Success path:** `workflow.error === null`
- **Error path:** `workflow.error !== null`

### 4. **Send_Voice_Response Node:**
- Text card: `{{workflow.responseText}}`
- Audio card: `{{workflow.audioUrl}}`

### 5. **Voice_Error_Response Node:**
- Text card: `{{workflow.responseText}}` or custom error message

---

## 🎨 Improved Flow Diagram

```
Entry (always)
    │
    ▼
Voice_Trigger
    │ Condition: event.payload.audioUrl exists
    ├─ YES ─────────────────┐
    │                       ▼
    │               Call_Voice_API
    │                (Execute Code)
    │                       │
    │                       ▼
    │               Check Error?
    │               (workflow.error !== null)
    │                   ├─ NO (Success) ─────┐
    │                   │                    ▼
    │                   │          Send_Voice_Response
    │                   │           - Text: responseText
    │                   │           - Audio: audioUrl
    │                   │                    │
    │                   │                    ├─► Exit
    │                   │                    │
    │                   └─ YES (Error) ──────┤
    │                                        ▼
    │                           Voice_Error_Response
    │                            - Text: error message
    │                                        │
    │                                        └─► Exit
    │
    └─ NO ──────────────────────► Standard
                                      │
                                      └─► Exit
```

---

## 💾 Complete Execute Code (Copy-Paste Ready)

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
      output_format: 'both'  // CRITICAL LINE
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
    console.error('[Voice] Error:', workflow.error);
  }
} catch (error) {
  workflow.error = error.message;
  workflow.responseText = 'Sorry, an error occurred. Please try again.';
  workflow.audioUrl = null;
  console.error('[Voice] Exception:', error.message);
}
```

---

## 🧪 How to Test

1. **Replace** your Execute Code in "Call_Voice_API" with the code above
2. **Publish** your bot
3. **Send** voice message: "Check my balance"
4. **Watch** Botpress logs for `[Voice]` entries
5. **Verify** you receive both text and audio response

---

## 📝 Summary

**Key Corrections:**
1. ✅ Added `output_format: 'both'` (CRITICAL!)
2. ✅ Improved error handling
3. ✅ Better response validation
4. ✅ Added logging for debugging
5. ✅ Proper timeout (60 seconds)
6. ✅ Validated inputs before API call

Your flow structure is good! Just update the Execute Code and you're all set! 🚀
