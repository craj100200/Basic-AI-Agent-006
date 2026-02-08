from pydantic import BaseModel, Field
from typing import List


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


class ErrorResponse(BaseModel):
    """Error response format"""
    
    status: str = "error"
    detail: str
