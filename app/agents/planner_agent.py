from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.agents.input_agent import PresentationInput, Slide
from app.utils.logger import logger


class ThemeConfig(BaseModel):
    """Visual theme configuration"""
    name: str
    background_color: str = Field(..., description="Hex color for background")
    text_color: str = Field(..., description="Hex color for text")
    accent_color: str = Field(..., description="Hex color for accents/highlights")
    font_family: str = Field(default="Arial", description="Font family name")


class SlideLayout(BaseModel):
    """Layout configuration for a single slide"""
    slide_number: int
    title: str
    content: List[str]
    layout: str = Field(..., description="Layout type: title_and_bullets, title_only, etc.")
    duration_seconds: int = Field(..., ge=3, le=15, description="Duration in seconds")
    font_size_title: int = Field(..., ge=24, le=72)
    font_size_content: int = Field(..., ge=16, le=48)


class PresentationPlan(BaseModel):
    """Complete presentation plan with theme and slide layouts"""
    theme: ThemeConfig
    slides: List[SlideLayout]
    total_duration: int = Field(..., description="Total video duration in seconds")
    
    @property
    def slide_count(self) -> int:
        return len(self.slides)


class PlannerAgent:
    """
    Rule-based Planner Agent that makes design decisions for presentations.
    
    Rules:
    - Content-based duration: More bullets = longer duration
    - Font sizing: Adjusts based on text length
    - Theme selection: Uses predefined themes
    - Layout: Currently supports "title_and_bullets"
    """
    
    # Predefined themes
    THEMES = {
        "corporate_blue": ThemeConfig(
            name="corporate_blue",
            background_color="#1e3a8a",
            text_color="#ffffff",
            accent_color="#60a5fa",
            font_family="Arial"
        ),
        "modern_dark": ThemeConfig(
            name="modern_dark",
            background_color="#1f2937",
            text_color="#f9fafb",
            accent_color="#10b981",
            font_family="Helvetica"
        ),
        "minimal_light": ThemeConfig(
            name="minimal_light",
            background_color="#f3f4f6",
            text_color="#111827",
            accent_color="#3b82f6",
            font_family="Arial"
        ),
        "vibrant_purple": ThemeConfig(
            name="vibrant_purple",
            background_color="#7c3aed",
            text_color="#ffffff",
            accent_color="#fbbf24",
            font_family="Arial"
        )
    }
    
    @staticmethod
    def calculate_slide_duration(content_lines: List[str]) -> int:
        """
        Calculate optimal slide duration based on content.
        
        Rules:
        - Base: 3 seconds
        - Add 1 second per bullet point
        - Cap at 15 seconds max
        """
        base_duration = 3
        per_bullet_time = 1
        
        duration = base_duration + (len(content_lines) * per_bullet_time)
        
        # Cap at 15 seconds
        return min(duration, 15)
    
    @staticmethod
    def calculate_font_sizes(title: str, content_lines: List[str]) -> Dict[str, int]:
        """
        Calculate optimal font sizes based on text length.
        
        Rules:
        - Long titles get smaller fonts
        - Many bullets get smaller content fonts
        """
        # Title font size
        if len(title) > 50:
            title_font = 36
        elif len(title) > 30:
            title_font = 42
        else:
            title_font = 48
        
        # Content font size
        avg_content_length = sum(len(line) for line in content_lines) / len(content_lines) if content_lines else 0
        
        if avg_content_length > 80:
            content_font = 24
        elif avg_content_length > 50:
            content_font = 28
        else:
            content_font = 32
        
        # Reduce font if too many bullets
        if len(content_lines) > 6:
            content_font = max(20, content_font - 4)
        
        return {
            "title": title_font,
            "content": content_font
        }
    
    @staticmethod
    def select_theme(theme_name: str = None) -> ThemeConfig:
        """
        Select a theme by name, or use default.
        
        Args:
            theme_name: Optional theme name from THEMES dict
            
        Returns:
            ThemeConfig object
        """
        if theme_name and theme_name in PlannerAgent.THEMES:
            logger.info(f"Selected theme: {theme_name}")
            return PlannerAgent.THEMES[theme_name]
        
        # Default theme
        default = "corporate_blue"
        logger.info(f"Using default theme: {default}")
        return PlannerAgent.THEMES[default]
    
    @staticmethod
    def create_plan(
        validated_input: PresentationInput,
        theme_name: str = None
    ) -> PresentationPlan:
        """
        Create a complete presentation plan from validated input.
        
        Args:
            validated_input: Output from InputAgent
            theme_name: Optional theme name (default: corporate_blue)
            
        Returns:
            PresentationPlan with all design decisions made
        """
        logger.info(f"Planner Agent: Creating plan for {len(validated_input.slides)} slides")
        
        # Select theme
        theme = PlannerAgent.select_theme(theme_name)
        
        # Plan each slide
        slide_layouts = []
        total_duration = 0
        
        for idx, slide in enumerate(validated_input.slides, 1):
            # Calculate duration
            duration = PlannerAgent.calculate_slide_duration(slide.content)
            total_duration += duration
            
            # Calculate font sizes
            fonts = PlannerAgent.calculate_font_sizes(slide.title, slide.content)
            
            # Create layout
            layout = SlideLayout(
                slide_number=idx,
                title=slide.title,
                content=slide.content,
                layout="title_and_bullets",  # Only layout supported for now
                duration_seconds=duration,
                font_size_title=fonts["title"],
                font_size_content=fonts["content"]
            )
            
            slide_layouts.append(layout)
            logger.debug(f"Slide {idx}: '{slide.title}' - {duration}s, title={fonts['title']}px, content={fonts['content']}px")
        
        plan = PresentationPlan(
            theme=theme,
            slides=slide_layouts,
            total_duration=total_duration
        )
        
        logger.info(f"Planner Agent: Plan created - {plan.slide_count} slides, {plan.total_duration}s total duration")
        return plan
