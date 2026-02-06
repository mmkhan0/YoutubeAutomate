# YouTube Scheduled Publishing

## Overview

Your automation now supports **scheduled publishing** - videos are uploaded immediately when the automation runs, but are scheduled to publish automatically 15 minutes later.

## Why Scheduled Publishing?

- **Review Time**: 15 minutes to verify thumbnail, metadata, and video quality
- **Processing Buffer**: Ensures YouTube has time to process video before going live
- **Last-Minute Changes**: Time to make adjustments if needed
- **Consistent Publishing**: Videos go live at predictable times

## How It Works

1. **Automation runs** at scheduled time (e.g., 9:00 AM)
2. **Video uploads** with `privacyStatus=private` 
3. **Scheduled publish** set to 15 minutes later (9:15 AM)
4. **Video automatically** becomes public at 9:15 AM

## Configuration

**File**: `automation_config.json`

```json
{
  "youtube": {
    "scheduled_publishing": true,     // Enable scheduled publishing
    "publish_delay_minutes": 15,      // Minutes to delay (default: 15)
    "privacy_status": "public"        // Final status after publishing
  }
}
```

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `scheduled_publishing` | `true` | Enable/disable scheduled publishing |
| `publish_delay_minutes` | `15` | Minutes to delay before going live |
| `privacy_status` | `public` | Final privacy status (`public`, `unlisted`) |

## View Scheduled Videos

1. **YouTube Studio** → [https://studio.youtube.com](https://studio.youtube.com)
2. **Content** tab
3. **Filter** by "Scheduled"
4. See publish date/time for each video

## Manual Changes

You can **edit scheduled videos** before they go live:

1. Go to YouTube Studio → Content
2. Click on scheduled video
3. Edit metadata, thumbnail, or schedule
4. Save changes

## Disable Scheduled Publishing

To upload videos immediately without scheduling:

```json
{
  "youtube": {
    "scheduled_publishing": false,
    "privacy_status": "public"
  }
}
```

## Technical Details

### YouTube API Implementation

```python
# Calculate publish time (UTC)
publish_datetime = datetime.utcnow() + timedelta(minutes=15)
publish_at = publish_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

# Upload with scheduled publishing
result = uploader.upload_video(
    video_path=video_path,
    title=title,
    description=description,
    tags=tags,
    privacy_status="public",        # Final status
    publish_at=publish_at,          # Schedule time (ISO 8601)
    made_for_kids=True,
    playlist_id=playlist_id
)
```

### Privacy Status Flow

| Stage | Privacy Status | PublishAt |
|-------|---------------|-----------|
| **Upload** | `private` | `2024-06-15T09:15:00Z` |
| **Scheduled** | `private` | `2024-06-15T09:15:00Z` |
| **Published** | `public` | `null` |

**Note**: YouTube requires initial `privacyStatus=private` when using `publishAt`. The video automatically changes to your configured privacy status at the scheduled time.

## Logs

Scheduled publishing is logged in automation logs:

```
✓ Video uploaded successfully!
  Video ID: abc123xyz
  URL: https://www.youtube.com/watch?v=abc123xyz
  Privacy: private
  📅 Scheduled: Will publish at 2024-06-15T09:15:00Z UTC
  Added to playlist: PLxxx...
```

## Troubleshooting

### Video Stays Private

**Cause**: `publishAt` time is in the past or invalid format

**Fix**: Ensure system clock is accurate and `publish_delay_minutes` > 0

### Can't Find Scheduled Videos

**Fix**: YouTube Studio → Content → Filter dropdown → "Scheduled"

### Want Immediate Publishing

**Fix**: Set `scheduled_publishing: false` in `automation_config.json`

## Task Scheduler Integration

Scheduled publishing works seamlessly with Windows Task Scheduler:

- **Task runs**: 9:00 AM (video uploads)
- **Video publishes**: 9:15 AM (automatically)
- **Next task**: 3:00 PM (next video uploads)
- **Next publish**: 3:15 PM (automatically)

This creates a consistent publishing schedule with built-in review time.

## Best Practices

1. **Consistent Timing**: Schedule Task Scheduler at same times daily
2. **Peak Hours**: Schedule uploads 15 min before peak viewer times
3. **Review Routine**: Check YouTube Studio during the 15-minute window
4. **Batch Uploads**: Upload multiple videos, each scheduled 15 min apart
5. **Monitor**: Check "Scheduled" filter regularly for any issues

## Examples

### Daily Upload Schedule

**Task Scheduler**: Runs 3 times per day

```
9:00 AM  → Upload → Publish at 9:15 AM
2:00 PM  → Upload → Publish at 2:15 PM
7:00 PM  → Upload → Publish at 7:15 PM
```

### Custom Delay

Want 30-minute review window?

```json
{
  "youtube": {
    "scheduled_publishing": true,
    "publish_delay_minutes": 30
  }
}
```

### Immediate Publishing

No delay, publish immediately:

```json
{
  "youtube": {
    "scheduled_publishing": false,
    "privacy_status": "public"
  }
}
```

## Summary

✅ Videos upload immediately when automation runs  
✅ Scheduled to publish 15 minutes later automatically  
✅ Gives you time to review before going live  
✅ Works seamlessly with Task Scheduler  
✅ Fully configurable delay time  
✅ Can disable for immediate publishing  

Your automation now has professional-grade scheduled publishing! 🎉
