# 🚀 FREE System Quick Start Guide

Get your **100% FREE** YouTube automation running in 15 minutes!

---

## ✅ Prerequisites Check

Before starting, confirm you have:
- [x] Python 3.10+ installed
- [x] FFmpeg installed
- [x] YouTube API configured
- [ ] Gemini API key (we'll get this now)

---

## 📝 Step-by-Step Setup

### 1️⃣ Get FREE Gemini API Key (2 minutes)

1. Go to: **https://makersuite.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Click **"Create API key in new project"**
5. Copy the key (starts with `AIza...`)

**✓ FREE Tier Includes:**
- 60 requests per minute
- 1500 requests per day
- Plenty for video automation!

### 2️⃣ Configure Environment (1 minute)

Open `.env` file and add your Gemini key:

```env
GEMINI_API_KEY=AIza...your_key_here...
```

Save the file. That's it!

### 3️⃣ Install FREE Dependencies (10 minutes)

```bash
# Navigate to project
cd D:\Projects\YoutubeAutomate

# Activate virtual environment
.venv\Scripts\activate

# Install FREE packages
pip install -r requirements_free.txt

# For NVIDIA GPU (MUCH FASTER):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Note:** First-time download is ~4GB (Stable Diffusion model). Be patient!

### 4️⃣ Generate Your First FREE Video (5 minutes)

```bash
python free_automation.py --category kids --language en
```

**What happens:**
1. ✓ Gemini generates script (10 seconds)
2. ✓ Stable Diffusion creates images (2-15 minutes depending on GPU/CPU)
3. ✓ gTTS generates voiceover (5 seconds)
4. ✓ FFmpeg animates video (30 seconds)
5. ✓ Uploads to YouTube (1 minute)

**First video may take longer** due to model downloads.

---

## 🎯 Quick Commands

### Generate Different Categories

```bash
# Kids video (cartoon animals, educational stories)
python free_automation.py --category kids

# Tech video (programming, technology explained)
python free_automation.py --category tech

# Science video (experiments, fun facts)
python free_automation.py --category science
```

### Generate Different Languages

```bash
# Hindi video
python free_automation.py --language hi

# Spanish video
python free_automation.py --language es

# French video
python free_automation.py --language fr
```

### Generate Multiple Videos

```bash
# Generate 3 videos in one run
python free_automation.py --count 3

# Generate 5 Hindi kids videos
python free_automation.py --category kids --language hi --count 5
```

---

## 💡 Windows Task Scheduler (Automated Daily Videos)

### Quick Setup (3 minutes)

1. **Edit `run_free.bat`** - Set your preferences:
   ```batch
   set CATEGORY=kids
   set LANGUAGE=en
   set COUNT=1
   ```

2. **Open Task Scheduler**:
   - Press `Win + R`
   - Type: `taskschd.msc`
   - Press Enter

3. **Create Task**:
   - Click "Create Basic Task"
   - Name: `YouTube FREE Automation`
   - Trigger: **Daily at 9:00 AM**
   - Action: **Start a program**
   - Program: `D:\Projects\YoutubeAutomate\run_free.bat`
   - Start in: `D:\Projects\YoutubeAutomate`
   - ✓ Finish

**Done!** Videos will generate automatically every day at 9 AM.

---

## 🔧 Troubleshooting

### ❌ "GEMINI_API_KEY not found"

**Fix:** Add your Gemini API key to `.env` file

```env
GEMINI_API_KEY=AIzaSy...your_key_here
```

### ❌ "No module named 'diffusers'"

**Fix:** Install dependencies

```bash
pip install -r requirements_free.txt
```

### ❌ "CUDA out of memory"

**Fix:** Use CPU mode (slower but works)

The system automatically falls back to CPU if GPU fails.

Or reduce image size in `free_automation.py`:
```python
width=768, height=512  # Instead of 1024x576
```

### ❌ Stable Diffusion taking forever (20+ min per image)

**Fix:** Install CUDA (for NVIDIA GPU)

```bash
# Check if you have NVIDIA GPU
nvidia-smi

# Install CUDA-accelerated PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA is working
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

**Speed comparison:**
- CPU: 2-3 minutes per image
- GPU: 10-20 seconds per image ⚡

### ❌ Where are my generated videos?

**Location:** `output/` folder

Each generation creates a new folder:
```
output/
└── kids_en_20240115_090523/
    ├── video/
    │   └── final_video.mp4    ← Your video here!
    ├── images/
    ├── audio/
    └── script.json
```

---

## 📊 Performance Expectations

### With GPU (NVIDIA + CUDA)
```
Total time per video: ~4 minutes
Cost per video: $0.00 ✓
```

### With CPU Only
```
Total time per video: ~17 minutes
Cost per video: $0.00 ✓
```

---

## 🎬 Test Everything Works

### Test 1: Gemini API
```bash
python -c "from src.free_gemini_generator import GeminiFreeScriptGenerator; print('✓ Gemini working')"
```

### Test 2: Stable Diffusion
```bash
python src/free_stable_diffusion.py
```
Creates test image in: `output/test_images/test_cartoon.png`

### Test 3: TTS
```bash
python src/free_tts_generator.py
```
Creates test audio in: `output/test_audio/test_speech.mp3`

### Test 4: FFmpeg
```bash
python src/free_video_animator.py
```

### Test 5: Full Pipeline
```bash
python free_automation.py --category kids --language en
```

---

## 🎉 You're Ready!

Your FREE YouTube automation is now working!

### What You Can Do Now:

1. **Generate videos on demand**
   ```bash
   python free_automation.py --category kids
   ```

2. **Set up daily automation**
   - Configure `run_free.bat`
   - Add to Task Scheduler
   - Videos generate automatically!

3. **Scale up**
   - Generate multiple videos per day
   - Try different languages
   - Experiment with styles

---

## 💰 Cost Breakdown

**Traditional Paid System:**
- OpenAI GPT-4: $0.20/video
- DALL-E 3: $0.20/video
- **Total: $0.40/video**

**Your FREE System:**
- Gemini API: **$0.00**
- Stable Diffusion: **$0.00**
- TTS: **$0.00**
- FFmpeg: **$0.00**
- **Total: $0.00/video**

**Unlimited videos at ZERO cost!** 🎊

---

## 📚 Next Steps

- Read full documentation: [README_FREE.md](README_FREE.md)
- Customize styles and categories
- Optimize for your hardware
- Set up automated scheduling

---

## 🆘 Need Help?

1. **Check logs:**
   ```bash
   type logs\free_automation.log
   ```

2. **Common issues solved in:** [README_FREE.md](README_FREE.md#-troubleshooting)

3. **Test individual components** (see "Test Everything Works" above)

---

## ✨ Enjoy Your FREE Video Automation!

Start generating now:
```bash
python free_automation.py --category kids --language en
```

**Cost: $0.00** | **Time: 4-17 minutes** | **Result: Professional YouTube video!** 🚀
5. **Review videos** - Check output before changing to public

---

**Ready to automate!** 🚀

Run: `python run_automation.py`
