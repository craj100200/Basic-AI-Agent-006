from pathlib import Path
from typing import List, Tuple
from abc import ABC, abstractmethod
import cv2
import numpy as np
from PIL import Image
from app.utils.logger import logger


class VideoGenerator(ABC):
    """
    Abstract base class for video generation.
    
    This allows us to swap implementations easily.
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


class OpenCVGenerator(VideoGenerator):
    """
    Video generator using OpenCV library.
    
    Pros: Fast, lightweight, low memory usage (perfect for Render free tier)
    Cons: No fancy transitions (but we don't need them for slides)
    """
    
    def __init__(self):
        """Initialize OpenCV generator"""
        self.width = 1920
        self.height = 1080
        
    def create_video(
        self,
        slide_data: List[Tuple[Path, int]],
        output_path: Path,
        fps: int = 30
    ) -> Path:
        """
        Create video using OpenCV.
        
        This is MUCH lighter than MoviePy - uses ~50MB RAM vs 200MB+
        
        Settings:
        - Resolution: 1920x1080 (Full HD)
        - FPS: 30 (smooth playback)
        - Codec: mp4v (widely compatible)
        """
        logger.info(f"OpenCV: Creating video with {len(slide_data)} slides at {fps} fps")
        
        if not slide_data:
            raise ValueError("No slides provided for video generation")
        
        # Validate all slide files exist
        for slide_path, duration in slide_data:
            if not slide_path.exists():
                raise FileNotFoundError(f"Slide not found: {slide_path}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps,
            (self.width, self.height)
        )
        
        if not out.isOpened():
            raise RuntimeError("Failed to initialize video writer")
        
        total_frames = 0
        total_duration = 0
        
        # Process each slide
        for idx, (slide_path, duration) in enumerate(slide_data, 1):
            logger.debug(f"Processing slide {idx}/{len(slide_data)}: {slide_path.name} ({duration}s)")
            
            # Load image using PIL (better compatibility)
            try:
                pil_image = Image.open(slide_path)
                
                # Convert PIL to OpenCV format (RGB -> BGR)
                image_rgb = np.array(pil_image)
                image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
                
                # Resize if needed (should already be correct size)
                if image_bgr.shape[:2] != (self.height, self.width):
                    image_bgr = cv2.resize(image_bgr, (self.width, self.height))
                
            except Exception as e:
                logger.error(f"Failed to load slide {slide_path}: {e}")
                raise
            
            # Calculate number of frames for this slide
            num_frames = int(duration * fps)
            
            # Write the same frame multiple times (one per frame duration)
            for frame_num in range(num_frames):
                out.write(image_bgr)
                total_frames += 1
            
            total_duration += duration
            
            # Free memory
            del image_bgr
            del pil_image
        
        # Release video writer
        out.release()
        
        logger.info(
            f"Video created successfully: {output_path} "
            f"({total_duration}s, {total_frames} frames)"
        )
        return output_path


# Keep MoviePy for reference (commented out to save memory)
# 
# class MoviePyGenerator(VideoGenerator):
#     """MoviePy implementation - heavier but has more features"""
#     
#     def create_video(self, slide_data, output_path, fps=30):
#         from moviepy.editor import ImageClip, concatenate_videoclips
#         
#         clips = []
#         for slide_path, duration in slide_data:
#             clip = ImageClip(str(slide_path)).set_duration(duration)
#             clips.append(clip)
#         
#         final_clip = concatenate_videoclips(clips, method="compose")
#         final_clip.write_videofile(
#             str(output_path),
#             fps=fps,
#             codec='libx264',
#             logger=None,
#             verbose=False
#         )
#         
#         final_clip.close()
#         return output_path
