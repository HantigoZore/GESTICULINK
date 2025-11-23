# ✅ Testing Checklist for GESTICULINK

Use this checklist to verify the facial recognition and voice interaction system.

## 🔧 Prerequisites

- [ ] Python 3.8 or higher installed
- [ ] Git repository cloned
- [ ] Working camera connected
- [ ] Working microphone connected (optional for voice features)
- [ ] Internet connection (optional for OpenAI and Google Speech API)

## 📦 Installation Testing

### Step 1: Environment Setup
- [ ] Created virtual environment: `python -m venv venv`
- [ ] Activated virtual environment
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] No critical errors during installation

**Note**: Some warnings about dlib or PyAudio are acceptable if you're using alternatives.

### Step 2: Configuration (Optional)
- [ ] Copied `.env.example` to `.env`
- [ ] Added `OPENAI_API_KEY` if testing AI features
- [ ] File `.env` is in `.gitignore` (security check)

## 🎥 Hardware Testing

### Camera Test
Run: `python scripts/test_camera.py`

- [ ] Camera opens successfully
- [ ] Video feed is displayed
- [ ] Face detection works (green rectangles around faces)
- [ ] Frame counter increments
- [ ] Can quit with Q or ESC

**Expected**: Green rectangles around detected faces, smooth video feed

### Microphone Test
Run: `python scripts/test_microphone.py`

- [ ] Microphone list displayed
- [ ] Default microphone initialized
- [ ] Ambient noise adjustment successful
- [ ] Speech recognition attempts work (at least 1/3 successful)
- [ ] Spanish text is recognized correctly

**Expected**: At least one successful speech recognition

## 👤 Facial Recognition Testing

### Step 1: Capture Faces
Run: `python scripts/capture_faces.py --name "Test Person" --images 5`

- [ ] Camera opens
- [ ] Face detection works in live preview
- [ ] Can capture images by pressing SPACE
- [ ] Images saved to `dataset/Test Person/`
- [ ] Captured 5 images successfully

**Tips**: 
- Position face clearly in frame
- Use good lighting
- Capture from slightly different angles

### Step 2: Train System
Run: `python scripts/train_encodings.py`

- [ ] Dataset directory found
- [ ] Person directories detected
- [ ] Faces detected in images
- [ ] Encodings created successfully
- [ ] File `models/encodings.pickle` created
- [ ] Summary shows correct number of encodings

**Expected**: "Training Complete!" message with encoding count

### Step 3: Test Recognition
Run: `python scripts/example_run.py --no-voice`

- [ ] System initializes without errors
- [ ] Camera opens
- [ ] Video feed displays
- [ ] Your face is detected (bounding box)
- [ ] Your name appears on the bounding box
- [ ] Confidence score is shown
- [ ] Green box for known person (or red for Unknown)

**Expected**: Green box with your name and confidence > 0.6

### Step 4: Test Multiple People (Optional)
- [ ] Capture faces for another person
- [ ] Retrain: `python scripts/train_encodings.py`
- [ ] Run recognition again
- [ ] Both people are correctly identified
- [ ] System distinguishes between people

## 🗣️ Voice Assistant Testing

### Step 1: Offline Mode (No OpenAI)
Run: `python scripts/example_run.py --no-openai`

- [ ] System starts successfully
- [ ] Press SPACE to activate voice
- [ ] Say "Hola" - System responds "Hola, ¿cómo estás?"
- [ ] Say "Adiós" - System responds "Hasta luego"
- [ ] TTS voice is audible and clear
- [ ] Spanish responses work

**Test Commands**:
- "Hola" → Greeting
- "¿Cómo estás?" → Status response
- "¿Quién soy?" → Identification (if face recognized)
- "Gracias" → Acknowledgment
- "Adiós" → Goodbye

### Step 2: Auto-Greeting
Run: `python scripts/example_run.py --no-openai`

- [ ] Position your face in view
- [ ] System recognizes you
- [ ] Automatic greeting occurs (first time only)
- [ ] Greeting includes your name
- [ ] Cooldown prevents repeated greetings

**Expected**: "Hola [Your Name], es un gusto verte de nuevo."

### Step 3: Manual Greeting
While system is running:

- [ ] Position your face in view
- [ ] Press 'G' key
- [ ] System greets you by name
- [ ] Voice output is clear

### Step 4: With OpenAI (Optional)
Run: `python scripts/example_run.py`

**Prerequisites**: OPENAI_API_KEY in .env

- [ ] System starts successfully
- [ ] Press SPACE and say something
- [ ] OpenAI generates contextual response
- [ ] Response is relevant to your question
- [ ] System speaks the response
- [ ] Can have back-and-forth conversation

**Test Conversation**:
- "¿Qué puedes hacer?" → AI explains capabilities
- "Cuéntame un chiste" → AI tells a joke
- "¿Quién soy?" → AI uses face recognition context

## 🔄 Integration Testing

### Full System Test
Run: `python scripts/example_run.py`

- [ ] Facial recognition works
- [ ] Voice interaction works
- [ ] Auto-greeting on recognition
- [ ] Can manually greet with 'G'
- [ ] Can interact via SPACE + voice
- [ ] Can reload encodings with 'R'
- [ ] Can quit cleanly with Q or ESC

### Keyboard Controls Test
While system running:

- [ ] SPACE - Activates voice listening
- [ ] G - Triggers manual greeting
- [ ] R - Reloads face encodings
- [ ] Q - Quits system
- [ ] ESC - Also quits system

## 📊 Performance Testing

### Frame Rate Test
Run system and observe:

- [ ] Video is smooth (not choppy)
- [ ] Face recognition updates reasonably fast
- [ ] No significant lag in video feed
- [ ] System remains responsive

**Acceptable**: 10-15 FPS or higher for recognition updates

### Recognition Accuracy Test
With trained faces:

- [ ] Correct person identified > 80% of time
- [ ] Confidence scores > 0.6 for correct matches
- [ ] Few false positives (Unknown labeled as known)
- [ ] System handles slight angle changes
- [ ] Works in different lighting (reasonable range)

## 🔒 Security Testing

### Environment Variables
- [ ] `.env` file is not committed to git
- [ ] `.env` is listed in `.gitignore`
- [ ] No API keys visible in code
- [ ] `.env.example` has placeholders only

### File Permissions
- [ ] `dataset/` directory is not committed
- [ ] `models/` directory is not committed
- [ ] `*.pickle` files are not committed
- [ ] `__pycache__/` directories are not committed

## 📝 Documentation Testing

### Quick Start Guide
- [ ] QUICKSTART.md instructions are clear
- [ ] All commands work as documented
- [ ] Installation steps are accurate
- [ ] Troubleshooting tips are helpful

### API Documentation
- [ ] API_DOCUMENTATION.md code examples work
- [ ] Import statements are correct
- [ ] Example code runs without errors

### README
- [ ] Installation instructions work
- [ ] Usage examples are accurate
- [ ] Troubleshooting section is helpful
- [ ] Links work correctly

## 🐛 Error Handling Testing

### Missing Dependencies Test
- [ ] System provides clear error if OpenCV missing
- [ ] System provides clear error if face_recognition missing
- [ ] Graceful degradation if optional deps missing

### Missing Files Test
- [ ] Clear error if encodings.pickle not found
- [ ] Helpful message directing to training step
- [ ] System doesn't crash on missing files

### Camera Issues Test
- [ ] Clear error message if camera not found
- [ ] Suggestion to check camera ID
- [ ] Test script helps diagnose issue

### Microphone Issues Test
- [ ] Clear error if microphone not accessible
- [ ] Lists available microphones for diagnosis
- [ ] System can run without microphone (--no-voice)

## ✅ Sign-Off Checklist

### Critical Tests (Must Pass)
- [ ] Camera test successful
- [ ] Face capture works
- [ ] Training creates encodings
- [ ] Recognition identifies people
- [ ] System runs without crashes

### Important Tests (Should Pass)
- [ ] Voice interaction works (with or without OpenAI)
- [ ] Documentation is clear and accurate
- [ ] Error messages are helpful
- [ ] Performance is acceptable

### Optional Tests (Nice to Have)
- [ ] OpenAI integration works
- [ ] Multiple people recognized correctly
- [ ] Works on different cameras
- [ ] Good performance in various lighting

## 🎉 Success Criteria

**System is working correctly if**:
✅ At least 1 person can be captured, trained, and recognized
✅ Voice interaction works in offline mode
✅ Documentation helps resolve any issues encountered
✅ System runs without critical errors

## 📞 Getting Help

If tests fail:
1. Check QUICKSTART.md for basic setup
2. Review README.md troubleshooting section
3. Run diagnostic scripts (test_camera.py, test_microphone.py)
4. Check error messages and logs
5. Open an issue on GitHub with details

## 📊 Test Results Template

```
Date: [YYYY-MM-DD]
Tester: [Your Name]
System: [Windows/Linux/Mac]
Python Version: [X.X.X]

Installation: PASS/FAIL
Hardware Tests: PASS/FAIL
Facial Recognition: PASS/FAIL
Voice Assistant: PASS/FAIL
Integration: PASS/FAIL
Documentation: PASS/FAIL

Notes:
[Any issues or observations]

Overall: PASS/FAIL
```

---

**Happy Testing!** 🚀

If all critical tests pass, the system is ready for use!
