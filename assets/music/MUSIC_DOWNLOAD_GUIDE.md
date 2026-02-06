# 🎵 Quick Music Download Guide

## Step-by-Step: Get Free Music in 5 Minutes

### Option 1: YouTube Audio Library (RECOMMENDED)

**Why?** Best quality, 100% free, perfect for kids content

1. **Go to YouTube Studio**
   - Visit: https://studio.youtube.com
   - Log in with your YouTube account

2. **Open Audio Library**
   - Click left sidebar: "Audio Library"
   - Click "Free music" tab

3. **Filter for Kids Music**
   - Mood: Select "Happy", "Bright", or "Upbeat"
   - Genre: Browse all (no specific kids filter)
   - Duration: 2-5 minutes preferred

4. **Download These Tracks**

   **For upbeat_kids.mp3:**
   - Search: "Happy Alley" or "Carefree"
   - Duration: 2-3 minutes
   - Mood: Happy/Bright
   - Download → Save as: `upbeat_kids.mp3`

   **For gentle_learning.mp3:**
   - Search: "Floating" or "Wallpaper"
   - Duration: 2-5 minutes
   - Mood: Calm/Inspiring
   - Download → Save as: `gentle_learning.mp3`

   **For playful_melody.mp3:**
   - Search: "Jingle Bells" or "Monkeys Spinning Monkeys"
   - Duration: 2-3 minutes
   - Mood: Playful/Funny
   - Download → Save as: `playful_melody.mp3`

   **For happy_piano.mp3:**
   - Search: "Piano" in title + Filter mood: Happy
   - Examples: "Sneaky Snitch", "Tiny Creatures"
   - Download → Save as: `happy_piano.mp3`

   **For cheerful_ukulele.mp3:**
   - Search: "Ukulele" in title
   - Examples: "Island", "Hey!", "Beach"
   - Download → Save as: `cheerful_ukulele.mp3`

5. **Move Files**
   ```
   Move all 5 MP3 files to:
   D:\Projects\YoutubeAutomate\assets\music\
   ```

---

### Option 2: Bensound (Easy Alternative)

1. Go to: https://www.bensound.com/royalty-free-music
2. Click "Kids" or "Happy" category
3. Download these tracks:

   - **"Ukulele"** → Save as `cheerful_ukulele.mp3`
   - **"Sweet"** → Save as `happy_piano.mp3`
   - **"Happy Rock"** → Save as `upbeat_kids.mp3`
   - **"Tenderness"** → Save as `gentle_learning.mp3`
   - **"LittleIdea"** → Save as `playful_melody.mp3`

4. **IMPORTANT**: Add attribution to video descriptions:
   ```
   Music by Bensound.com
   ```

---

### Option 3: Quick Test (Use Placeholder)

If you want to test without downloading:

1. **Use any MP3 file** as a placeholder
2. Copy it 5 times with different names:
   ```powershell
   Copy-Item "any_music.mp3" "upbeat_kids.mp3"
   Copy-Item "any_music.mp3" "gentle_learning.mp3"
   Copy-Item "any_music.mp3" "playful_melody.mp3"
   Copy-Item "any_music.mp3" "happy_piano.mp3"
   Copy-Item "any_music.mp3" "cheerful_ukulele.mp3"
   ```

⚠️ **Note**: Replace with proper royalty-free music before publishing!

---

## ✅ Verification

After downloading, verify files:

```powershell
Get-ChildItem "D:\Projects\YoutubeAutomate\assets\music" -Filter *.mp3 | Select-Object Name, Length

# Should show:
# upbeat_kids.mp3
# gentle_learning.mp3
# playful_melody.mp3
# happy_piano.mp3
# cheerful_ukulele.mp3
```

---

## 🎵 File Requirements

Each MP3 should be:
- ✅ 2-5 minutes long
- ✅ Instrumental only (no vocals)
- ✅ Happy/positive tone
- ✅ 48kHz sample rate (preferred)
- ✅ 192 kbps or higher

---

## 🚀 Quick PowerShell Command

Run this to check if music is ready:

```powershell
$musicDir = "D:\Projects\YoutubeAutomate\assets\music"
$required = @("upbeat_kids.mp3", "gentle_learning.mp3", "playful_melody.mp3", "happy_piano.mp3", "cheerful_ukulele.mp3")

Write-Host "`n🎵 Music Setup Status:" -ForegroundColor Cyan
foreach ($file in $required) {
    $path = Join-Path $musicDir $file
    if (Test-Path $path) {
        $size = [math]::Round((Get-Item $path).Length / 1MB, 2)
        Write-Host "  ✅ $file ($size MB)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file (missing)" -ForegroundColor Red
    }
}
Write-Host ""
```

---

## 🎬 Ready to Use!

Once all 5 files are in place:

```bash
python run_automation.py --category kids --language en
```

You'll see in logs:
```
✅ Mixed audio with background music (category: english_alphabet)
```

---

## 📝 Attribution Templates

If using music that requires attribution:

**For Bensound:**
```
Music: "Track Name" by Bensound.com
License: Creative Commons (CC BY-ND 3.0)
```

**For Incompetech:**
```
Music: "Track Name" by Kevin MacLeod (incompetech.com)
License: Creative Commons (CC BY 4.0)
```

**For YouTube Audio Library:**
```
No attribution required! ✅
```

---

## 💡 Tips

- **Test First**: Download 1-2 tracks, test, then get the rest
- **Backup**: Keep original downloads in a separate folder
- **Quality**: Higher bitrate = better quality (aim for 192+ kbps)
- **Length**: Longer tracks (3-5 min) need less looping
- **License**: Always check if attribution required

---

**Need Help?** Check the full guide: `assets/music/README.md`
