## 🏗️ Architecture (Complete!)
```
✅ Step 1: Input Agent
   └─ Validates slide format
   
✅ Step 2: Planner Agent
   └─ Decides: layout, colors, duration, fonts
   
✅ Step 3: Slide Agent
   └─ Renders PNG images of slides
   
✅ Step 4: Video Agent  ← NEW!
   └─ Combines slides into MP4 video
   
⏳ Step 5: Critic Agent (Coming soon)
   └─ Quality checks and retry logic
```

## 🎬 Video Generation

### Generate Complete Video (All Steps)
```bash
curl -X POST https://your-app.onrender.com/api/v1/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "content": "[SLIDE_START][TITLE_START]My Presentation[TITLE_END][BULLET_START]Point 1[BULLET_END][BULLET_START]Point 2[BULLET_END][SLIDE_END]",
    "theme_name": "corporate_blue",
    "filename": "my_video.mp4"
  }'
```

### Download Video
```bash
curl https://your-app.onrender.com/api/v1/download-video/presentation.mp4 \
  --output presentation.mp4
```

### List Generated Videos
```bash
curl https://your-app.onrender.com/api/v1/list-videos
```

## 🎥 Video Specifications

- **Resolution:** 1920x1080 (Full HD)
- **FPS:** 30 (smooth playback)
- **Codec:** H.264 (libx264)
- **Format:** MP4
- **Quality:** High

## 📊 Complete Pipeline Example

**Input:**
```json
{
  "content": "[SLIDE_START][TITLE_START]Introduction[TITLE_END][BULLET_START]Welcome[BULLET_END][SLIDE_END][SLIDE_START][TITLE_START]Conclusion[TITLE_END][BULLET_START]Thank you[BULLET_END][SLIDE_END]",
  "theme_name": "modern_dark"
}
```

**Output:**
- ✅ 2 slides validated
- ✅ Plan created (10 seconds total)
- ✅ 2 PNG images rendered
- ✅ MP4 video generated (downloadable)
