import pytest
from pathlib import Path
from app.agents.input_agent import InputAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.slide_agent import SlideAgent
from app.config import settings


def test_render_single_slide():
    """Test rendering a single slide"""
    content = "[SLIDE_START][TITLE_START]Test Slide[TITLE_END][BULLET_START]Point 1[BULLET_END][BULLET_START]Point 2[BULLET_END][SLIDE_END]"
    
    validated = InputAgent.validate_input(content=content)
    plan = PlannerAgent.create_plan(validated)
    
    agent = SlideAgent()
    result = agent.render_slides(plan)
    
    assert result.slide_count == 1
    assert len(result.slide_paths) == 1
    assert result.slide_paths[0].exists()
    assert result.slide_paths[0].suffix == ".png"


def test_render_multiple_slides():
    """Test rendering multiple slides"""
    content = "[SLIDE_START][TITLE_START]Slide 1[TITLE_END][BULLET_START]A[BULLET_END][SLIDE_END][SLIDE_START][TITLE_START]Slide 2[TITLE_END][BULLET_START]B[BULLET_END][SLIDE_END]"
    
    validated = InputAgent.validate_input(content=content)
    plan = PlannerAgent.create_plan(validated)
    
    agent = SlideAgent()
    result = agent.render_slides(plan)
    
    assert result.slide_count == 2
    assert len(result.slide_paths) == 2
    
    # Check files exist
    for path in result.slide_paths:
        assert path.exists()
        assert path.suffix == ".png"


def test_slide_filenames():
    """Test that slides are named correctly"""
    content = "[SLIDE_START][TITLE_START]Test[TITLE_END][BULLET_START]Content[BULLET_END][SLIDE_END]"
    
    validated = InputAgent.validate_input(content=content)
    plan = PlannerAgent.create_plan(validated)
    
    agent = SlideAgent()
    result = agent.render_slides(plan)
    
    assert result.slide_paths[0].name == "slide_001.png"


def test_different_themes():
    """Test rendering with different themes"""
    content = "[SLIDE_START][TITLE_START]Test[TITLE_END][BULLET_START]Content[BULLET_END][SLIDE_END]"
    
    validated = InputAgent.validate_input(content=content)
    
    for theme_name in ["corporate_blue", "modern_dark", "minimal_light", "vibrant_purple"]:
        plan = PlannerAgent.create_plan(validated, theme_name=theme_name)
        
        agent = SlideAgent()
        output_dir = settings.WORKSPACE_DIR / "slides" / theme_name
        result = agent.render_slides(plan, output_dir=output_dir)
        
        assert result.slide_count == 1
        assert result.slide_paths[0].exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
