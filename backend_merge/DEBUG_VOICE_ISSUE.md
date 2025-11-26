# Debugging Voice Response Issue

## Problem
Botpress was previously able to listen to voice and send back response voice URLs, but it's not working anymore after registration code changes.

## Quick Diagnosis Steps

### Step 1: Test the Endpoint Directly

Run this command in a new terminal to test if the voice endpoint itself works:

```bash
cd c:\Users\arsen\Desktop\Bafoka-teamZ\backend_merge
python test_voice_endpoint.py
```

**Expected Result:** Should return JSON with `audio_url` field.

### Step 2: Check Botpress Logs

In Botpress Studio:
1. Open the **Logs** panel (bottom right)
2. Send a voice message
3. Look for the API call to `/api/voice/process`
4. Check the response - does it include `audio_url`?

### Step 3: Verify Botpress Configuration

Check your Botpress workflow for voice handling:

**Current configuration (from botpress_guide.md line 63-74):**
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}"
}
```

**❗ MISSING:** The `output_format` parameter!

**Recommended fix:**
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}",
  "output_format": "both"
}
```

### Step 4: Verify Response Handling in Botpress

After the API call, check how you're accessing the audio URL:

**Correct way:**
```
{{data.response.body.audio_url}}
```

**Common mistakes:**
- `{{response.audio_url}}` ❌
- `{{data.audio_url}}` ❌
- `{{audio_url}}` ❌

## Most Likely Causes

### Cause 1: Botpress Response Handling Changed
When you updated the registration flow, you might have also updated how responses are handled.

**Solution:** Check the voice workflow in Botpress and ensure the "Play Audio" or "Send Audio" card is using:
```
{{data.response.body.audio_url}}
```

### Cause 2: Output Format Default Changed
If Botpress is somehow sending `"output_format": "text"`, no audio will be generated.

**Solution:** Explicitly add `"output_format": "both"` to the request payload.

### Cause 3: Error During Audio Generation
The endpoint might be failing silently during TTS generation.

**Solution:** Check Flask logs for errors. Run this in PowerShell:
```powershell
# Watch the Flask logs in real-time
# Send a voice message from Botpress while watching
```

## Detailed Checklist

- [ ] **Test endpoint directly** with `test_voice_endpoint.py`
- [ ] **Check Botpress logs** for the API response
- [ ] **Verify `output_format` parameter** is sent from Botpress
- [ ] **Check audio URL access pattern** in Botpress workflow
- [ ] **Verify gTTS is working** (run: `pip show gtts`)
- [ ] **Check static folder permissions** for audio file saving
- [ ] **Test with a simple voice message** like "check my balance"

## Quick Fix to Try

### Update botpress_guide.md

Change the voice processing request body from:
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}"
}
```

To:
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}",
  "output_format": "both"
}
```

### Update Botpress Workflow

1. Go to Botpress Studio
2. Find the workflow that handles voice messages (likely triggered by "User Sends Audio")
3. Find the "Call API" card for `/api/voice/process`
4. Add `"output_format": "both"` to the request body
5. Verify the response is accessed with `{{data.response.body.audio_url}}`
6. Save and publish

## Test Commands

### Test 1: Simple curl test
```bash
curl -X POST http://localhost:5000/api/voice/process \
  -H "Content-Type: application/json" \
  -d "{\"audio_url\":\"https://example.com/test.mp3\",\"phone\":\"+237600000001\",\"output_format\":\"both\"}"
```

### Test 2: Check what Botpress is sending
Add this logging to app.py around line 445:
```python
LOG.info(f"Received voice request: {data}")
LOG.info(f"Output format: {output_format}")
```

Then check Flask logs when Botpress sends a voice message.

## If Still Not Working

1. **Share the Flask logs** when processing a voice message from Botpress
2. **Share the Botpress workflow** JSON for voice handling
3. **Test with curl** to verify endpoint works independently

## Related Files
- Voice endpoint: [app.py lines 412-553](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/bot/app.py#L412-L553)
- Configuration guide: [botpress_guide.md](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/botpress_guide.md)
- Test script: [test_voice_endpoint.py](file:///c:/Users/arsen/Desktop/Bafoka-teamZ/backend_merge/test_voice_endpoint.py)
