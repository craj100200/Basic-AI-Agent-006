from pathlib import Path
from typing import List, Tuple
from pydantic import BaseModel, Field
from app.agents.planner_agent import PresentationPlan
from app.agents.slide_agent import SlideRenderResult
from app.services.video_generator import OpenCVGenerator, VideoGenerator  # Changed
from app.config import settings
from app.utils.logger import logger


class VideoGenerationResult(BaseModel):
    """Result from video generation"""
    video_path: Path
    duration_seconds: int
    slide_count: int
    fps: int
    resolution: str
    file_size_mb: float
    
    class Config:
        arbitrary_types_allowed = True


class VideoAgent:
    """
    Agent responsible for generating video from rendered slides.
    
    Uses OpenCV for lightweight, fast video generation (perfect for Render free tier)
    """
    
    def __init__(self, generator: VideoGenerator = None):
        """
        Initialize Video Agent.
        
        Args:
            generator: Custom video generator (optional, defaults to OpenCVGenerator)
        """
        self.generator = generator or OpenCVGenerator()  # Changed from MoviePyGenerator
    
    def create_video(
        self,
        plan: PresentationPlan,
        slide_result: SlideRenderResult,
        output_filename: str = "presentation.mp4",
        fps: int = 30
    ) -> VideoGenerationResult:
        """
        Create video from rendered slides.
        
        Args:
            plan: Presentation plan with timing information
            slide_result: Result from SlideAgent with rendered images
            output_filename: Name of output video file
            fps: Frames per second (default: 30)
            
        Returns:
            VideoGenerationResult with video details
        """
        logger.info(f"Video Agent: Creating video from {slide_result.slide_count} slides")
        
        # Prepare slide data with durations
        slide_data: List[Tuple[Path, int]] = []
        
        for slide_layout, slide_path in zip(plan.slides, slide_result.slide_paths):
            slide_data.append((slide_path, slide_layout.duration_seconds))
            logger.debug(
                f"Slide {slide_layout.slide_number}: {slide_path.name} "
                f"({slide_layout.duration_seconds}s)"
            )
        
        # Output path
        output_dir = settings.WORKSPACE_DIR / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_filename
        
        # Generate video
        logger.info(f"Generating video: {output_path}")
        self.generator.create_video(
            slide_data=slide_data,
            output_path=output_path,
            fps=fps
        )
        
        # Get file size
        file_size_bytes = output_path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        result = VideoGenerationResult(
            video_path=output_path,
            duration_seconds=plan.total_duration,
            slide_count=slide_result.slide_count,
            fps=fps,
            resolution="1920x1080",
            file_size_mb=round(file_size_mb, 2)
        )
        
        logger.info(
            f"Video Agent: Video created successfully - "
            f"{result.duration_seconds}s, {result.file_size_mb}MB"
        )
        return result
