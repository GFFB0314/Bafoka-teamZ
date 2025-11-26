# Voice Command Guide

## ✅ Fixed NLU Issues

I've fixed the NLU (Natural Language Understanding) to properly recognize voice commands. The main issues were:

1. **Registration Commands** - NLU wasn't building complete pipe-separated commands
2. **Pattern Matching** - Too restrictive for natural speech
3. **Skill Detection** - Wasn't extracting skills from spoken language

## 🎤 How to Use Voice Commands

### 1. Registration

**Say this:**
> "Register me, my name is John from Bameka, I'm 25, I do farming"

**Or simpler:**
> "Register me, I am Alice"

**What happens:**
- NLU extracts: name="John", community="BAMEKA", age="25", skill="Farming"
- Converts to: `/register BAMEKA | John | 25 | Farming`
- Backend receives properly formatted command

**Supported communities:**
- Bameka
- Batoufam  
- Fondjomekwet

**Supported skills (automatically detected):**
- Farming, Plumbing, Electrician, Carpenter
- Teacher, Mechanic, Tailor, Cooking, Cleaning
- Medicine, Nursing, Driving, Welding, Painting, Masonry

### 2. Check Balance

**Say this:**
> "Check my balance"
> "How much money do I have"
> "What's my balance"

**Converts to:** `/balance`

### 3. Transfer Money

**Say this:**
> "Transfer 100 to +237600123456"
> "Send 500 to +237..."

**Converts to:** `/transfer +237600123456 100`

### 4. Post Service Offer

**Say this:**
> "I offer plumbing for 500"
> "I do farming for 1000"

**What happens:**
- Detects service and price
- Creates: `/offer Plumbing Service | Professional plumbing services available | 500`

### 5. Search Services

**Say this:**
> "Search for plumber"
> "Find carpenter"
> "Looking for farming"

**Converts to:** `/search plumber`

### 6. Get Help

**Say this:**
> "Help"
> "What can you do"

**Converts to:** `/start`

## 🔍 Testing Your Voice Commands

### Step 1: Restart Flask Server

Since we updated the NLU, you need to restart:

```powershell
# In the terminal running app.py, press Ctrl+C to stop
# Then restart:
python .\app.py
```

### Step 2: Send Voice Messages

Send a voice message from Botpress/WhatsApp saying:
> "Check my balance"

Watch the Flask logs for:
```
[VOICE] Transcription: check my balance
[VOICE] Executing command: check my balance
[VOICE] Command response: ...
```

### Step 3: Try Registration

Say:
> "Register me, my name is John from Bameka, I'm 25, I do farming"

Logs should show:
```
[VOICE] Transcription: register me my name is john from bameka i'm 25 i do farming
[VOICE] Executing command: /register BAMEKA | John | 25 | Farming
```

## 🐛 Troubleshooting

### Issue: Commands still not recognized

**Check logs for the transcription:**
- If transcription is wrong → Whisper issue (speak clearly)
- If transcription is right but command is wrong → NLU issue

**Example:**
```
[VOICE] Transcription: check my balance  ✅ Good transcription
[VOICE] Executing command: /balance      ✅ Good NLU conversion
```

### Issue: Registration fails

**Make sure you say all parts:**
- Name: "my name is John" or "I am John"
- Community: "from Bameka" or "at Batoufam"  
- Age: "I'm 25" or "25 years old"
- Skill: "I do farming" or mention any skill keyword

**Minimum required:**
> "Register me, my name is John"

This will default to BAMEKA community, age 25, and "General" skill.

### Issue: Whisper hears wrong words

**Tips for better recognition:**
- Speak clearly and slowly
- Say numbers distinctly ("two five" not "twenty-five")
- Use English or simple French
- Reduce background noise

## 📊 What Changed in NLU

### Before (Broken):
```python
# Only returned incomplete command
if intent == 'register':
    parts = ['/register']
    if entities.get('name'):
        parts.append(entities['name'])
    return ' '.join(parts)
    # Result: "/register John" ❌ (missing required fields)
```

### After (Fixed):
```python
# Returns complete pipe-separated command
if intent == 'register':
    community = entities.get('community', 'BAMEKA')
    name = entities.get('name', '')
    age = entities.get('age', '25')
    skill = detect_skill(text) or 'General'
    
    return f"/register {community} | {name} | {age} | {skill}"
    # Result: "/register BAMEKA | John | 25 | Farming" ✅
```

## 🎯 Key Improvements

1. **Complete Command Construction** - NLU now builds the full pipe-separated format
2. **Skill Detection** - Automatically detects skills from natural speech
3. **Better Patterns** - More flexible regex patterns for natural language
4. **Default Values** - Uses sensible defaults (BAMEKA, age 25) if not specified
5. **Improved Help Text** - Shows full example with all fields

## 📁 Files Modified

- **`bot/nlu.py`** - Fixed command construction and pattern matching
- **`bot/app.py`** - Enhanced logging for voice processing
- **`botpress_guide.md`** - Added missing `output_format` parameter

## 🚀 Next Steps

1. **Restart your Flask server** to load the fixed NLU
2. **Test with voice messages** through Botpress
3. **Watch the logs** to see transcription → command conversion
4. **Verify** commands execute correctly

The NLU should now properly recognize your voice commands! 🎉
