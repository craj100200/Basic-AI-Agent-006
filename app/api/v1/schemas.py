from pydantic import BaseModel, Field
from typing import List, Optional


# Existing schemas (keep these)
class ValidateInputRequest(BaseModel):
    """Request body for input validation endpoint"""
    
    content: str = Field(
        ...,
        description="Raw presentation content in tag-based format",
        example="[SLIDE_START][TITLE_START]Introduction to AI[TITLE_END][BULLET_START]AI is transforming our world[BULLET_END][BULLET_START]Machine Learning is a key component[BULLET_END][SLIDE_END]"
    )


class SlideResponse(BaseModel):
    """Individual slide in response"""
    
    title: str
    content: List[str]
    content_count: int


class ValidateInputResponse(BaseModel):
    """Response from input validation endpoint"""
    
    status: str
    message: str
    slide_count: int
    total_content_lines: int
    slides: List[SlideResponse]


# NEW: Planner schemas
class CreatePlanRequest(BaseModel):
    """Request body for creating presentation plan"""
    
    content: str = Field(
        ...,
        description="Raw presentation content in tag-based format"
    )
    theme_name: Optional[str] = Field(
        None,
        description="Theme name: corporate_blue, modern_dark, minimal_light, vibrant_purple"
    )


class ThemeResponse(BaseModel):
    """Theme configuration in response"""
    
    name: str
    background_color: str
    text_color: str
    accent_color: str
    font_family: str


class SlideLayoutResponse(BaseModel):
    """Slide layout in response"""
    
    slide_number: int
    title: str
    content: List[str]
    layout: str
    duration_seconds: int
    font_size_title: int
    font_size_content: int


class CreatePlanResponse(BaseModel):
    """Response from plan creation endpoint"""
    
    status: str
    message: str
    theme: ThemeResponse
    slides: List[SlideLayoutResponse]
    total_duration: int
    slide_count: int


class ErrorResponse(BaseModel):
    """Error response format"""
    
    status: str = "error"
    detail: str


# NEW: Slide rendering schemas
class RenderSlidesRequest(BaseModel):
    """Request body for rendering slides"""
    
    content: str = Field(
        ...,
        description="Raw presentation content in tag-based format"
    )
    theme_name: Optional[str] = Field(
        None,
        description="Theme name: corporate_blue, modern_dark, minimal_light, vibrant_purple"
    )


class RenderSlidesResponse(BaseModel):
    """Response from slide rendering"""
    
    status: str
    message: str
    slide_count: int
    slide_filenames: List[str]
    theme_used: str
    total_duration: int
