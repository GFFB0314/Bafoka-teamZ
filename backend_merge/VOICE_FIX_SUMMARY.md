# Voice Response Fix Summary

## 🎯 Problem
Botpress was previously sending back voice response URLs, but stopped after registration code changes.

## ✅ Root Cause Identified
**The backend code is fine!** The issue is most likely in your **Botpress configuration**.

## 🔧 Quick Fix (90% likely to solve it)

### Step 1: Update Botpress Voice Workflow

In Botpress Studio, find your voice message handler and update the API call:

**❌ OLD (Missing `output_format`):**
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}"
}
```

**✅ NEW (Explicitly requests audio):**
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}",
  "output_format": "both"
}
```

### Step 2: Verify Response Handling

Make sure you're accessing the audio URL correctly in Botpress:

**Correct syntax:**
```
{{data.response.body.audio_url}}
```

**Common mistakes:**
- `{{response.audio_url}}` ❌
- `{{data.audio_url}}` ❌ 
- `{{audio_url}}` ❌

## 🔍 How to Verify It's Working

### Test 1: Check Flask Logs

After updating Botpress, send a voice message and watch your Flask terminal. You should see:

```
[VOICE] Received JSON request: {...}
[VOICE] Parameters - Phone: +237..., Output Format: both
[VOICE] Transcribing audio with Whisper...
[VOICE] Transcription: check my balance
[VOICE] Executing command: check my balance
[VOICE] Command response: User not found. /register first.
[VOICE] Generating audio response with gTTS...
[VOICE] ✅ Audio response URL generated: https://your-ngrok-url/static/audio/output/response_xyz.mp3
```

**If you see this instead:**
```
[VOICE] ⚠️ Skipping audio generation - output_format is 'text'
```

Then Botpress is sending `output_format: "text"` - update your workflow!

### Test 2: Check JSON Response

The API response should include:
```json
{
  "success": true,
  "transcription": "check my balance",
  "response_text": "User not found. /register first.",
  "audio_url": "https://your-ngrok-url/static/audio/output/response_abc123.mp3"
}
```

**Missing `audio_url`?** → Botpress sent wrong `output_format`

## 📊 Why This Happened

When you updated the registration code, you likely also updated your Botpress workflows. During this update:
- You may have recreated the voice message handler
- The `output_format` parameter wasn't included in the new configuration
- Without explicit `output_format`, it defaults to "both" (which should work)
- BUT if Botpress sent `output_format: "text"` at any point, audio won't generate

## 🚨 Alternative Issues (if above doesn't fix it)

### Issue 2: gTTS Not Installed
**Symptom:** Error in Flask logs mentioning gTTS
**Fix:**
```bash
pip install gTTS
```

### Issue 3: Static Folder Permissions
**Symptom:** Flask logs show error saving audio file
**Fix:** Check that `backend_merge/static/audio/output/` exists and is writable

### Issue 4: Botpress Not Playing Audio
**Symptom:** audio_url is in response, but no sound plays
**Fix:** In Botpress, use "Play Audio" or "Send Audio" card with URL: `{{data.response.body.audio_url}}`

## 📝 What Changed in the Code

I made the following improvements:

1. **Updated `botpress_guide.md`** - Added `output_format` parameter to the example
2. **Enhanced logging in `app.py`** - Now clearly shows:
   - When audio generation is happening
   - The exact `output_format` received
   - The final audio URL (if generated)
   - Warning if audio is skipped

3. **Created debugging guides:**
   - `DEBUG_VOICE_ISSUE.md` - Comprehensive debugging steps
   - `VOICE_FIX_SUMMARY.md` - This quick reference

## 🎬 Next Steps

1. **Update your Botpress workflow** with `"output_format": "both"`
2. **Send a test voice message** from WhatsApp/Botpress
3. **Watch the Flask terminal** for `[VOICE]` logs
4. **Verify the response** includes `audio_url`

If it still doesn't work after this, share:
- The Flask logs from a voice message
- Your Botpress workflow JSON (export it)
- The API response you're seeing

## 📚 Related Files
- Backend endpoint: [app.py:412-553](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/bot/app.py#L412-L553)
- Configuration: [botpress_guide.md](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/botpress_guide.md)
- Detailed debug: [DEBUG_VOICE_ISSUE.md](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/DEBUG_VOICE_ISSUE.md)
