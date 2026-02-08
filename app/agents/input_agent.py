from typing import List
from pydantic import BaseModel, Field, validator
from pathlib import Path
from app.config import settings
from app.utils.logger import logger
import re


class Slide(BaseModel):
    """Single slide with title and content"""
    
    title: str = Field(..., description="Slide title")
    content: List[str] = Field(..., description="List of content lines/bullet points")
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Slide title cannot be empty")
        if len(v) > 100:
            raise ValueError("Slide title too long (max 100 characters)")
        return v.strip()
    
    @validator('content')
    def content_validation(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Slide must have at least one content line")
        if len(v) > settings.MAX_CONTENT_LINES_PER_SLIDE:
            raise ValueError(f"Too many content lines (max {settings.MAX_CONTENT_LINES_PER_SLIDE})")
        # Clean and filter empty lines
        cleaned = [line.strip() for line in v if line.strip()]
        if not cleaned:
            raise ValueError("Slide must have at least one non-empty content line")
        return cleaned


class PresentationInput(BaseModel):
    """Validated presentation structure"""
    
    slides: List[Slide] = Field(..., min_items=1, description="List of slides")
    
    @validator('slides')
    def check_slide_count(cls, v):
        if len(v) > settings.MAX_SLIDES:
            raise ValueError(f"Too many slides (max {settings.MAX_SLIDES})")
        return v
    
    @property
    def total_content_lines(self) -> int:
        """Total number of content lines across all slides"""
        return sum(len(slide.content) for slide in self.slides)


class InputAgent:
    """
    Agent responsible for validating and parsing presentation input.
    
    Supported format:
    [SLIDE_START][TITLE_START]Your Title[TITLE_END][BULLET_START]Point 1[BULLET_END][BULLET_START]Point 2[BULLET_END][SLIDE_END]
    
    This format is whitespace/newline independent.
    """
    
    @staticmethod
    def parse_slide_format(raw_text: str) -> PresentationInput:
        """
        Parse the tag-based format into structured slides.
        
        Format:
        [SLIDE_START]
          [TITLE_START]Title Here[TITLE_END]
          [BULLET_START]Bullet point 1[BULLET_END]
          [BULLET_START]Bullet point 2[BULLET_END]
        [SLIDE_END]
        
        Whitespace and newlines are ignored - only tags matter.
        
        Args:
            raw_text: Raw text input in the tag format
            
        Returns:
            PresentationInput: Validated presentation structure
            
        Raises:
            ValueError: If format is invalid or validation fails
        """
        # Remove all newlines and extra whitespace for easier parsing
        # But preserve spaces within content
        normalized_text = ' '.join(raw_text.split())
        
        # Find all slides
        slide_pattern = r'\[SLIDE_START\](.*?)\[SLIDE_END\]'
        slide_matches = re.findall(slide_pattern, normalized_text, re.DOTALL)
        
        if not slide_matches:
            raise ValueError("No slides found. Make sure to use [SLIDE_START]...[SLIDE_END] tags.")
        
        slides = []
        
        for slide_idx, slide_content in enumerate(slide_matches, 1):
            logger.debug(f"Parsing slide {slide_idx}")
            
            # Extract title
            title_pattern = r'\[TITLE_START\](.*?)\[TITLE_END\]'
            title_match = re.search(title_pattern, slide_content)
            
            if not title_match:
                raise ValueError(f"Slide {slide_idx}: Missing title. Use [TITLE_START]...[TITLE_END] tags.")
            
            title = title_match.group(1).strip()
            if not title:
                raise ValueError(f"Slide {slide_idx}: Title is empty")
            
            # Extract bullets/content
            bullet_pattern = r'\[BULLET_START\](.*?)\[BULLET_END\]'
            bullet_matches = re.findall(bullet_pattern, slide_content)
            
            if not bullet_matches:
                raise ValueError(f"Slide {slide_idx}: '{title}' has no content. Use [BULLET_START]...[BULLET_END] tags.")
            
            # Clean up bullets
            content_lines = [bullet.strip() for bullet in bullet_matches if bullet.strip()]
            
            if not content_lines:
                raise ValueError(f"Slide {slide_idx}: '{title}' has no non-empty content")
            
            slides.append(Slide(title=title, content=content_lines))
            logger.debug(f"Slide {slide_idx}: '{title}' with {len(content_lines)} bullets")
        
        logger.info(f"Successfully parsed {len(slides)} slides")
        return PresentationInput(slides=slides)
    
    @staticmethod
    def validate_input(content: str = None, file_path: Path = None) -> PresentationInput:
        """
        Main entry point for Input Agent.
        Validates and parses presentation input from either direct content or file.
        
        Args:
            content: Raw text content in tag format
            file_path: Path to text file containing tag format
            
        Returns:
            PresentationInput: Validated presentation structure
            
        Raises:
            ValueError: If input is invalid or missing
        """
        logger.info("Input Agent: Starting validation")
        
        if content:
            raw_text = content
            logger.debug("Using direct content input")
        elif file_path:
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")
            raw_text = file_path.read_text(encoding='utf-8')
            logger.debug(f"Loaded content from file: {file_path}")
        else:
            raise ValueError("Must provide either 'content' or 'file_path'")
        
        if not raw_text.strip():
            raise ValueError("Input is empty")
        
        # Parse and validate
        result = InputAgent.parse_slide_format(raw_text)
        
        logger.info(f"Input Agent: Validation successful - {len(result.slides)} slides, {result.total_content_lines} total content lines")
        return result
