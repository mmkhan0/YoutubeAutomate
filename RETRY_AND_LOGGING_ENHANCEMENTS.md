# Retry Logic and Logging Enhancements

## Overview
Added comprehensive retry logic and enhanced logging throughout the YouTube automation system for production-grade reliability.

## Changes Made

### 1. Retry Decorator (run_automation.py)
Added a flexible retry decorator with exponential backoff:

```python
@retry_on_failure(
    max_retries=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(Exception,),
    logger=logger
)
```

**Features:**
- Exponential backoff: 1s → 2s → 4s → 8s
- Configurable retry attempts (default: 3)
- Catches specific exception types
- Detailed logging of each retry attempt
- Debug-level stack traces on failure

### 2. FFmpeg Retry Logic (kids_video_creator.py)
Enhanced `_run_ffmpeg()` method with intelligent retry:

**Improvements:**
- ✅ Maximum 3 retry attempts for transient errors
- ✅ Detects transient failures (I/O errors, network issues, broken pipe)
- ✅ Exponential backoff (2^attempt seconds)
- ✅ 1-hour timeout for long operations
- ✅ Better error messages with context
- ✅ Real-time progress feedback
- ✅ FFmpeg warning detection and logging

**Transient Errors Handled:**
- Resource temporarily unavailable
- Connection reset
- Broken pipe
- I/O error

### 3. Enhanced Logging Throughout Pipeline

#### Progress Indicators
```
🎯 STEP 1: Selecting topic (1/7 steps)
✓ Topic selected: "The Amazing Journey of a Seed"
   Category: Science
   Language: en
```

#### Timing Information
```
⏱️  Elapsed: 45.3s (0.8 min)
✓ Video created successfully in 247.8s (4.1 min)
```

#### Cost Tracking
```
📊 Cost Breakdown:
   • Script generation: ~$0.01 (GPT-4o-mini)
   • Image generation: ~$0.32 (8 images × $0.04)
   • Voiceover: $0.00 (gTTS FREE)
   • Total: ~$0.33 per video
```

#### Resource Information
```
📁 File size: 22.10 MB
🎬 Resolution: 1920x1080 @ 60 FPS
🖼️  Images: 8 generated
🎵 Duration: 180s (3.0 min)
```

### 4. Detailed Error Context

**Before:**
```
✗ Image generation failed: Exception
```

**After:**
```
✗ Image generation failed: OpenAIError: Rate limit exceeded
📝 Error type: OpenAIError
🔍 Context: API quota exceeded for current billing period
💡 Suggestion: Check your OpenAI API usage at platform.openai.com
📚 Stack trace: [DEBUG level]
```

### 5. Retry Statistics in Logs

**Example Output:**
```
⚠️  _step_generate_images failed (attempt 1/3): Rate limit exceeded
🔄 Retrying in 1.0 seconds...

⚠️  _step_generate_images failed (attempt 2/3): Rate limit exceeded
🔄 Retrying in 2.0 seconds...

✓ _step_generate_images completed successfully on attempt 3
```

## Modules with Existing Retry Logic

These modules already had retry logic (now standardized):

1. **kids_topic_selector.py**
   - MAX_RETRIES = 3
   - Exponential backoff: delay * (2^attempt-1)
   
2. **kids_image_generator.py**
   - MAX_RETRIES = 3
   - RETRY_DELAY = 2 seconds
   
3. **youtube_uploader.py**
   - MAX_RETRIES = 10
   - RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
   - Resumable upload with 5MB chunks

## Modules Enhanced with New Retry Logic

1. **run_automation.py** (orchestrator)
   - Added retry_on_failure decorator
   - Can be applied to any pipeline step
   - Consistent error handling across all steps

2. **kids_video_creator.py** (FFmpeg operations)
   - Added retry logic to _run_ffmpeg()
   - Handles transient disk I/O errors
   - Detects and retries on temporary failures

## Configuration

### Default Retry Parameters
```python
MAX_RETRIES = 3           # Maximum attempts
RETRY_DELAY_BASE = 1.0    # Initial delay (seconds)
BACKOFF_MULTIPLIER = 2.0  # Exponential backoff
```

### FFmpeg Specific
```python
FFMPEG_MAX_RETRIES = 3
FFMPEG_TIMEOUT = 3600     # 1 hour
```

## Testing Recommendations

1. **Normal Operation**
   ```bash
   python run_automation.py --category=science --language=en
   ```
   - Verify no errors introduced
   - Check log output formatting
   - Confirm timing accuracy

2. **Simulated Failures**
   - Temporarily disable internet
   - Set invalid API keys
   - Test with corrupted input files
   - Verify retry behavior

3. **Load Testing**
   - Generate multiple videos in sequence
   - Monitor retry statistics
   - Check resource cleanup

## Benefits

### Reliability
- ✅ Automatic recovery from transient failures
- ✅ No manual intervention needed for temporary issues
- ✅ Graceful degradation (continues when possible)

### Debugging
- ✅ Clear error messages with context
- ✅ Detailed stack traces in debug mode
- ✅ Timing information for performance analysis
- ✅ Cost tracking for budget planning

### Visibility
- ✅ Progress indicators (Step 3/7)
- ✅ Real-time status updates
- ✅ Resource utilization metrics
- ✅ Success/failure statistics

### Production Ready
- ✅ Handles API rate limits
- ✅ Recovers from network issues
- ✅ Manages disk I/O errors
- ✅ Resilient to temporary outages

## Log Levels

```python
DEBUG   - Stack traces, detailed FFmpeg output
INFO    - Progress updates, success messages
WARNING - Retry attempts, non-critical failures
ERROR   - Critical failures, operation aborts
```

## Example: Full Pipeline Log with Retries

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 YouTube Kids Video Automation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Category: Science
🌍 Language: en
⏱️  Started: 2024-02-06 18:54:00

======================================================================
🧹 CLEANUP: Preparing workspace
======================================================================
✓ Cleanup complete:
  • Audio files:  18 deleted
  • Image files:  40 deleted
  • Video clips:  12 deleted
  • Old videos:   2 deleted
  • Space freed:  185.42 MB
  • Videos kept:  3 most recent

======================================================================
🎯 STEP 1: Selecting topic (1/7)
======================================================================
✓ Topic selected: "The Amazing Journey of a Seed: From Planting to Growing"
   Category: Science
   Language: en
   ⏱️  Elapsed: 2.3s

======================================================================
📝 STEP 2: Generating script (2/7)
======================================================================
✓ Script generated successfully
   Sections: 8
   Words: 450
   Target duration: 180s (3.0 min)
   Estimated cost: ~$0.01 (script generation)
   ⏱️  Elapsed: 15.7s

======================================================================
🎨 STEP 3: Generating images (3/7)
======================================================================
⚠️  Image generation failed (attempt 1/3): Rate limit exceeded
🔄 Retrying in 1.0 seconds...

🎨 Generating images (attempt 2/3)...
✓ Successfully generated 8 images
   Est. cost: ~$0.32 (DALL-E 3)
   Images saved to: output/images/
   Style: Pixar-Disney 3D cartoon
   ⏱️  Elapsed: 47.2s (retry succeeded)

======================================================================
📥 STEP 4: Downloading Pexels clips (4/7)
======================================================================
🎯 Target: 5 video clips
✓ Downloaded 5 clips in 8.3s
   Clips saved to: output/videos/clips/

======================================================================
🎤 STEP 5: Generating voiceover (5/7)
======================================================================
🌍 Language: en
🔊 Provider: gTTS (FREE)
🎵 Synthesizing speech...
✓ Voiceover generated in 3.1s
   Duration: 178.5s (3.0 min)
   File size: 2.84 MB
   Saved to: output/audio/voiceover_20240206_185421.mp3
   Est. cost: $0.00 (gTTS FREE)

======================================================================
🎬 STEP 6: Creating final video (6/7)
======================================================================
🖼️  Images: 8
🎵 Audio: voiceover_20240206_185421.mp3
🎬 FFmpeg: 60 FPS, Ken Burns effect, motion blur
🎬 Starting video rendering (this may take several minutes)...

🎬 Starting FFmpeg process...
⚠️  FFmpeg failed (attempt 1/3): Transient error detected
🔄 Retrying in 2s...

🎬 Starting FFmpeg process (attempt 2/3)...
✓ FFmpeg completed successfully in 234.7s

✓ Video created successfully in 247.8s (4.1 min)
   File size: 22.10 MB
   Resolution: 1920x1080 @ 60 FPS
   Saved to: output/videos/video_20240206_185400.mp4

======================================================================
📊 FINAL COST BREAKDOWN
======================================================================
• Script: $0.01
• Images: $0.32 (8 × $0.04)
• Voiceover: $0.00 (gTTS)
• Total: ~$0.33

✓ Pipeline completed successfully in 5.1 minutes
```

## Error Recovery Examples

### 1. API Rate Limit
```
⚠️  OpenAI API rate limit exceeded
🔄 Retrying in 2.0 seconds...
✓ Request succeeded on retry
```

### 2. Network Timeout
```
⚠️  Network timeout connecting to api.openai.com
🔄 Retrying in 4.0 seconds...
✓ Connection re-established
```

### 3. FFmpeg Transient Error
```
⚠️  FFmpeg I/O error: Resource temporarily unavailable
🔄 Retrying in 2.0 seconds...
✓ FFmpeg completed successfully
```

### 4. Disk Space Issue
```
⚠️  Insufficient disk space
🧹 Running automatic cleanup...
✓ Freed 185 MB
🔄 Retrying operation...
✓ Operation completed successfully
```

## Next Steps

1. **Monitor Logs** - Check for repeated retry patterns
2. **Adjust Limits** - Tune MAX_RETRIES based on failure analysis
3. **Add Metrics** - Track retry success rate over time
4. **Alert System** - Set up notifications for repeated failures

## Summary

The system is now production-ready with:
- ✅ Automatic retry on transient failures
- ✅ Comprehensive error logging with context
- ✅ Progress tracking and timing information
- ✅ Cost tracking for budget management
- ✅ Resource usage visibility
- ✅ Graceful degradation on non-critical failures

No configuration changes needed - retry logic is automatic and transparent.
