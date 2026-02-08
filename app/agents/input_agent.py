from typing import List
from pydantic import BaseModel, Field, validator
from pathlib import Path
from app.config import settings
from app.utils.logger import logger


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
    Supports the custom [SLIDE_START]...[SLIDE_END] format.
    """
    
    @staticmethod
    def parse_slide_format(raw_text: str) -> PresentationInput:
        """
        Parse the [SLIDE_START]...[SLIDE_END] format into structured slides.
        
        Expected format:
        [SLIDE_START]
        [TITLE_START]Your Title Here[TITLE_END]
        Content line 1
        Content line 2
        [SLIDE_END]
        
        Args:
            raw_text: Raw text input in the custom format
            
        Returns:
            PresentationInput: Validated presentation structure
            
        Raises:
            ValueError: If format is invalid or validation fails
        """
        slides = []
        current_slide_active = False
        current_title = None
        current_content = []
        in_title = False
        
        lines = raw_text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines outside of slides
            if not line and not current_slide_active:
                continue
            
            if line == '[SLIDE_START]':
                if current_slide_active:
                    raise ValueError(f"Line {line_num}: Nested [SLIDE_START] detected. Close previous slide first.")
                current_slide_active = True
                current_content = []
                current_title = None
                logger.debug(f"Started new slide at line {line_num}")
                
            elif line == '[SLIDE_END]':
                if not current_slide_active:
                    raise ValueError(f"Line {line_num}: [SLIDE_END] without matching [SLIDE_START]")
                
                if not current_title:
                    raise ValueError(f"Line {line_num}: Slide ended without a title")
                
                if not current_content:
                    raise ValueError(f"Line {line_num}: Slide '{current_title}' has no content")
                
                slides.append(Slide(title=current_title, content=current_content))
                logger.debug(f"Completed slide: '{current_title}' with {len(current_content)} content lines")
                current_slide_active = False
                
            elif line == '[TITLE_START]':
                if not current_slide_active:
                    raise ValueError(f"Line {line_num}: [TITLE_START] outside of slide")
                if in_title:
                    raise ValueError(f"Line {line_num}: Nested [TITLE_START] detected")
                in_title = True
                
            elif line == '[TITLE_END]':
                if not in_title:
                    raise ValueError(f"Line {line_num}: [TITLE_END] without matching [TITLE_START]")
                in_title = False
                
            elif in_title:
                if current_title:
                    raise ValueError(f"Line {line_num}: Multiple title lines detected. Title should be on one line.")
                current_title = line
                
            elif current_slide_active and line:
                # This is content
                current_content.append(line)
        
        # Check for unclosed slides
        if current_slide_active:
            raise ValueError("Unclosed slide detected. Missing [SLIDE_END]")
        
        if in_title:
            raise ValueError("Unclosed title detected. Missing [TITLE_END]")
        
        if not slides:
            raise ValueError("No slides found in input")
        
        logger.info(f"Successfully parsed {len(slides)} slides")
        return PresentationInput(slides=slides)
    
    @staticmethod
    def validate_input(content: str = None, file_path: Path = None) -> PresentationInput:
        """
        Main entry point for Input Agent.
        Validates and parses presentation input from either direct content or file.
        
        Args:
            content: Raw text content in slide format
            file_path: Path to text file containing slide format
            
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
