from pathlib import Path
from typing import List, Tuple
from abc import ABC, abstractmethod
from moviepy.editor import ImageClip, concatenate_videoclips
from app.utils.logger import logger


class VideoGenerator(ABC):
    """
    Abstract base class for video generation.
    
    This allows us to swap implementations (MoviePy → OpenCV) easily.
    """
    
    @abstractmethod
    def create_video(
        self,
        slide_data: List[Tuple[Path, int]],
        output_path: Path,
        fps: int = 30
    ) -> Path:
        """
        Create video from slides.
        
        Args:
            slide_data: List of (slide_path, duration_seconds) tuples
            output_path: Path where video should be saved
            fps: Frames per second
            
        Returns:
            Path to saved video file
        """
        pass


class MoviePyGenerator(VideoGenerator):
    """
    Video generator using MoviePy library.
    
    Current implementation - easy to use, feature-rich.
    UPGRADE_LATER: Swap to OpenCVGenerator for better performance.
    """
    
    def __init__(self):
        """Initialize MoviePy generator"""
        self.codec = 'libx264'  # H.264 codec for maximum compatibility
        self.audio_codec = 'aac'  # Standard audio codec
        self.preset = 'medium'  # Encoding speed vs compression (ultrafast/fast/medium/slow)
        
    def create_video(
        self,
        slide_data: List[Tuple[Path, int]],
        output_path: Path,
        fps: int = 30
    ) -> Path:
        """
        Create video using MoviePy.
        
        Settings:
        - Resolution: 1920x1080 (Full HD)
        - FPS: 30 (smooth playback)
        - Codec: H.264 (libx264)
        - Quality: High
        """
        logger.info(f"MoviePy: Creating video with {len(slide_data)} slides at {fps} fps")
        
        if not slide_data:
            raise ValueError("No slides provided for video generation")
        
        # Validate all slide files exist
        for slide_path, duration in slide_data:
            if not slide_path.exists():
                raise FileNotFoundError(f"Slide not found: {slide_path}")
        
        clips = []
        total_duration = 0
        
        # Create clips for each slide
        for idx, (slide_path, duration) in enumerate(slide_data, 1):
            logger.debug(f"Processing slide {idx}/{len(slide_data)}: {slide_path.name} ({duration}s)")
            
            # Create image clip with specified duration
            clip = ImageClip(str(slide_path)).set_duration(duration)
            clips.append(clip)
            total_duration += duration
        
        logger.info(f"Total video duration: {total_duration} seconds")
        
        # Concatenate all clips
        logger.info("Concatenating clips...")
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write video file
        logger.info(f"Writing video to: {output_path}")
        final_clip.write_videofile(
            str(output_path),
            fps=fps,
            codec=self.codec,
            audio_codec=self.audio_codec,
            preset=self.preset,
            logger=None,  # Suppress MoviePy's verbose logging
            verbose=False
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        logger.info(f"Video created successfully: {output_path} ({total_duration}s)")
        return output_path


# UPGRADE_LATER: OpenCV implementation for better performance
#
# class OpenCVGenerator(VideoGenerator):
#     """
#     Video generator using OpenCV.
#     
#     Pros: Faster, lighter, better performance on Render
#     Cons: More complex code, manual frame calculation
#     """
#     
#     def create_video(
#         self,
#         slide_data: List[Tuple[Path, int]],
#         output_path: Path,
#         fps: int = 30
#     ) -> Path:
#         import cv2
#         import numpy as np
#         
#         # Video settings
#         width, height = 1920, 1080
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
#         
#         for slide_path, duration in slide_data:
#             img = cv2.imread(str(slide_path))
#             frames = int(duration * fps)
#             
#             for _ in range(frames):
#                 out.write(img)
#         
#         out.release()
#         return output_path
