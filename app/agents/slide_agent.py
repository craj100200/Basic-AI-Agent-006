from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from app.agents.planner_agent import PresentationPlan
from app.services.slide_renderer import SlideRenderer
from app.config import settings
from app.utils.logger import logger


class SlideRenderResult(BaseModel):
    """Result from rendering slides"""
    slide_paths: List[Path] = Field(..., description="Paths to generated slide images")
    slide_count: int
    output_directory: Path
    
    class Config:
        arbitrary_types_allowed = True


class SlideAgent:
    """
    Agent responsible for rendering slide images from presentation plan.
    
    Uses SlideRenderer service to create PNG images.
    """
    
    def __init__(self, renderer: SlideRenderer = None):
        """
        Initialize Slide Agent.
        
        Args:
            renderer: Custom renderer instance (optional, defaults to SlideRenderer)
                      UPGRADE_LATER: Can swap in GradientRenderer or PremiumRenderer
        """
        self.renderer = renderer or SlideRenderer()
    
    def render_slides(
        self,
        plan: PresentationPlan,
        output_dir: Path = None
    ) -> SlideRenderResult:
        """
        Render all slides from a presentation plan.
        
        Args:
            plan: Presentation plan from PlannerAgent
            output_dir: Output directory (defaults to workspace/slides)
            
        Returns:
            SlideRenderResult with paths to generated images
        """
        logger.info(f"Slide Agent: Rendering {plan.slide_count} slides")
        
        # Use default output directory if not specified
        if output_dir is None:
            output_dir = settings.WORKSPACE_DIR / "slides"
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Render all slides
        slide_paths = self.renderer.render_multiple_slides(
            layouts=plan.slides,
            theme=plan.theme,
            output_dir=output_dir
        )
        
        result = SlideRenderResult(
            slide_paths=slide_paths,
            slide_count=len(slide_paths),
            output_directory=output_dir
        )
        
        logger.info(f"Slide Agent: Successfully rendered {result.slide_count} slides to {output_dir}")
        return result
