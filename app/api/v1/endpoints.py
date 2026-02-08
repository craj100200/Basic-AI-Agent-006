from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
from app.agents.input_agent import InputAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.slide_agent import SlideAgent
from app.agents.video_agent import VideoAgent

from app.api.v1.schemas import (
    ValidateInputRequest,
    ValidateInputResponse,
    SlideResponse,
    CreatePlanRequest,
    CreatePlanResponse,
    ThemeResponse,
    SlideLayoutResponse,
    ErrorResponse,
    RenderSlidesRequest,
    RenderSlidesResponse,
    GenerateVideoRequest,
    GenerateVideoResponse,

)
from app.config import settings
from app.utils.logger import logger

router = APIRouter(tags=["Presentation Agent"])


@router.post(
    "/validate-input",
    response_model=ValidateInputResponse,
    summary="Validate presentation input",
    description="Parse and validate presentation content in custom slide format"
)
def validate_input(request: ValidateInputRequest):
    """
    **Step 1: Input Agent**
    
    Validates and parses presentation input in the format:
```
    [SLIDE_START][TITLE_START]Title[TITLE_END][BULLET_START]Point 1[BULLET_END][SLIDE_END]
```
    
    Returns structured, validated slide data.
    """
    try:
        logger.info("API: Received input validation request")
        
        # Run Input Agent
        result = InputAgent.validate_input(content=request.content)
        
        # Build response
        response = ValidateInputResponse(
            status="success",
            message=f"Successfully validated {len(result.slides)} slides",
            slide_count=len(result.slides),
            total_content_lines=result.total_content_lines,
            slides=[
                SlideResponse(
                    title=slide.title,
                    content=slide.content,
                    content_count=len(slide.content)
                )
                for slide in result.slides
            ]
        )
        
        logger.info(f"API: Validation successful - {len(result.slides)} slides")
        return response
        
    except ValueError as e:
        logger.warning(f"API: Validation failed - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("API: Unexpected error during validation")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/validate-input-file",
    response_model=ValidateInputResponse,
    summary="Validate presentation from uploaded file",
    description="Upload a .txt file containing presentation in custom slide format"
)
async def validate_input_file(file: UploadFile = File(...)):
    """
    **Step 1: Input Agent (File Upload)**
    
    Upload a text file containing presentation content.
    File should use the same tag-based format.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are supported")
        
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        logger.info(f"API: Received file upload - {file.filename}")
        
        # Run Input Agent
        result = InputAgent.validate_input(content=text_content)
        
        # Build response
        response = ValidateInputResponse(
            status="success",
            message=f"Successfully validated {len(result.slides)} slides from {file.filename}",
            slide_count=len(result.slides),
            total_content_lines=result.total_content_lines,
            slides=[
                SlideResponse(
                    title=slide.title,
                    content=slide.content,
                    content_count=len(slide.content)
                )
                for slide in result.slides
            ]
        )
        
        logger.info(f"API: File validation successful - {len(result.slides)} slides")
        return response
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    except ValueError as e:
        logger.warning(f"API: File validation failed - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("API: Unexpected error during file validation")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/create-plan",
    response_model=CreatePlanResponse,
    summary="Create presentation plan",
    description="Generate a complete presentation plan with theme and layout decisions"
)
def create_plan(request: CreatePlanRequest):
    """
    **Step 2: Planner Agent**
    
    Takes validated slide content and creates a complete presentation plan including:
    - Theme selection (colors, fonts)
    - Slide durations based on content
    - Font sizes optimized for readability
    - Layout decisions
    
    Available themes:
    - corporate_blue (default)
    - modern_dark
    - minimal_light
    - vibrant_purple
    """
    try:
        logger.info("API: Received plan creation request")
        
        # Step 1: Validate input
        validated_input = InputAgent.validate_input(content=request.content)
        logger.info(f"Input validated: {len(validated_input.slides)} slides")
        
        # Step 2: Create plan
        plan = PlannerAgent.create_plan(
            validated_input=validated_input,
            theme_name=request.theme_name
        )
        
        # Build response
        response = CreatePlanResponse(
            status="success",
            message=f"Plan created for {plan.slide_count} slides, total duration: {plan.total_duration}s",
            theme=ThemeResponse(
                name=plan.theme.name,
                background_color=plan.theme.background_color,
                text_color=plan.theme.text_color,
                accent_color=plan.theme.accent_color,
                font_family=plan.theme.font_family
            ),
            slides=[
                SlideLayoutResponse(
                    slide_number=slide.slide_number,
                    title=slide.title,
                    content=slide.content,
                    layout=slide.layout,
                    duration_seconds=slide.duration_seconds,
                    font_size_title=slide.font_size_title,
                    font_size_content=slide.font_size_content
                )
                for slide in plan.slides
            ],
            total_duration=plan.total_duration,
            slide_count=plan.slide_count
        )
        
        logger.info(f"API: Plan created successfully - {plan.slide_count} slides, {plan.total_duration}s")
        return response
        
    except ValueError as e:
        logger.warning(f"API: Plan creation failed - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("API: Unexpected error during plan creation")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/themes",
    summary="List available themes",
    description="Get list of all available presentation themes"
)
def list_themes():
    """
    **Get Available Themes**
    
    Returns all available themes with their color configurations.
    """
    themes = [
        ThemeResponse(
            name=theme.name,
            background_color=theme.background_color,
            text_color=theme.text_color,
            accent_color=theme.accent_color,
            font_family=theme.font_family
        )
        for theme in PlannerAgent.THEMES.values()
    ]
    
    return {
        "status": "success",
        "themes": themes,
        "count": len(themes)
    }


@router.post(
    "/render-slides",
    response_model=RenderSlidesResponse,
    summary="Render presentation slides",
    description="Generate PNG images for all slides in the presentation"
)
def render_slides(request: RenderSlidesRequest):
    """
    **Step 3: Slide Agent**
    
    Takes presentation content and generates PNG images for each slide.
    
    Process:
    1. Validates input (Step 1)
    2. Creates plan (Step 2)
    3. Renders slides as PNG images (Step 3)
    
    Returns list of generated slide filenames.
    """
    try:
        logger.info("API: Received slide rendering request")
        
        # Step 1: Validate input
        validated_input = InputAgent.validate_input(content=request.content)
        logger.info(f"Input validated: {len(validated_input.slides)} slides")
        
        # Step 2: Create plan
        plan = PlannerAgent.create_plan(
            validated_input=validated_input,
            theme_name=request.theme_name
        )
        logger.info(f"Plan created: {plan.slide_count} slides, theme={plan.theme.name}")
        
        # Step 3: Render slides
        slide_agent = SlideAgent()
        result = slide_agent.render_slides(plan)
        
        # Build response
        response = RenderSlidesResponse(
            status="success",
            message=f"Successfully rendered {result.slide_count} slides",
            slide_count=result.slide_count,
            slide_filenames=[path.name for path in result.slide_paths],
            theme_used=plan.theme.name,
            total_duration=plan.total_duration
        )
        
        logger.info(f"API: Slides rendered successfully - {result.slide_count} files")
        return response
        
    except ValueError as e:
        logger.warning(f"API: Slide rendering failed - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("API: Unexpected error during slide rendering")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/download-slide/{filename}",
    summary="Download a rendered slide",
    description="Download a specific slide PNG by filename"
)
def download_slide(filename: str):
    """
    **Download Slide Image**
    
    Downloads a rendered slide PNG file.
    Filename should be like: slide_001.png
    """
    from fastapi.responses import FileResponse
    
    # Security: prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    slide_path = settings.WORKSPACE_DIR / "slides" / filename
    
    if not slide_path.exists():
        raise HTTPException(status_code=404, detail=f"Slide not found: {filename}")
    
    return FileResponse(
        slide_path,
        media_type="image/png",
        filename=filename
    )




@router.post(
    "/generate-video",
    response_model=GenerateVideoResponse,
    summary="Generate presentation video",
    description="Complete end-to-end video generation from content"
)
def generate_video(request: GenerateVideoRequest):
    """
    **Step 4: Video Agent (Complete Pipeline)**
    
    Generates a complete presentation video from content.
    
    Full process:
    1. Validates input (Input Agent)
    2. Creates plan (Planner Agent)
    3. Renders slides (Slide Agent)
    4. Generates video (Video Agent)
    
    Returns video file information with download link.
    """
    try:
        logger.info("API: Received video generation request")
        
        # Step 1: Validate input
        validated_input = InputAgent.validate_input(content=request.content)
        logger.info(f"Step 1 complete: {len(validated_input.slides)} slides validated")
        
        # Step 2: Create plan
        plan = PlannerAgent.create_plan(
            validated_input=validated_input,
            theme_name=request.theme_name
        )
        logger.info(f"Step 2 complete: Plan created ({plan.total_duration}s, theme={plan.theme.name})")
        
        # Step 3: Render slides
        slide_agent = SlideAgent()
        slide_result = slide_agent.render_slides(plan)
        logger.info(f"Step 3 complete: {slide_result.slide_count} slides rendered")
        
        # Step 4: Generate video
        video_agent = VideoAgent()
        video_result = video_agent.create_video(
            plan=plan,
            slide_result=slide_result,
            output_filename=request.filename
        )
        logger.info(f"Step 4 complete: Video generated ({video_result.file_size_mb}MB)")
        
        # Build response
        response = GenerateVideoResponse(
            status="success",
            message=f"Video generated successfully: {video_result.video_path.name}",
            video_filename=video_result.video_path.name,
            duration_seconds=video_result.duration_seconds,
            slide_count=video_result.slide_count,
            file_size_mb=video_result.file_size_mb,
            resolution=video_result.resolution,
            fps=video_result.fps,
            theme_used=plan.theme.name
        )
        
        logger.info(f"API: Video generation complete - {video_result.video_path.name}")
        return response
        
    except ValueError as e:
        logger.warning(f"API: Video generation failed - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("API: Unexpected error during video generation")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/download-video/{filename}",
    summary="Download generated video",
    description="Download a generated presentation video"
)
def download_video(filename: str):
    """
    **Download Video**
    
    Downloads a generated video file.
    Filename should be like: presentation.mp4
    """
    from fastapi.responses import FileResponse
    
    # Security: prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    if not filename.endswith('.mp4'):
        raise HTTPException(status_code=400, detail="Only .mp4 files are supported")
    
    video_path = settings.WORKSPACE_DIR / "videos" / filename
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Video not found: {filename}")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=filename
    )


@router.get(
    "/list-videos",
    summary="List generated videos",
    description="Get list of all generated videos"
)
def list_videos():
    """
    **List Videos**
    
    Returns list of all generated video files with metadata.
    """
    video_dir = settings.WORKSPACE_DIR / "videos"
    
    if not video_dir.exists():
        return {"status": "success", "videos": [], "count": 0}
    
    videos = []
    for video_file in video_dir.glob("*.mp4"):
        file_size_mb = video_file.stat().st_size / (1024 * 1024)
        videos.append({
            "filename": video_file.name,
            "size_mb": round(file_size_mb, 2),
            "created_at": video_file.stat().st_mtime
        })
    
    # Sort by creation time (newest first)
    videos.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "status": "success",
        "videos": videos,
        "count": len(videos)
    }
