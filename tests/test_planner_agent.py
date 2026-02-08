import pytest
from app.agents.input_agent import InputAgent
from app.agents.planner_agent import PlannerAgent


def test_create_plan_single_slide():
    """Test creating plan for single slide"""
    content = "[SLIDE_START][TITLE_START]Test[TITLE_END][BULLET_START]Point 1[BULLET_END][BULLET_START]Point 2[BULLET_END][SLIDE_END]"
    
    validated = InputAgent.validate_input(content=content)
    plan = PlannerAgent.create_plan(validated)
    
    assert plan.slide_count == 1
    assert plan.slides[0].slide_number == 1
    assert plan.slides[0].title == "Test"
    assert len(plan.slides[0].content) == 2
    assert plan.slides[0].duration_seconds >= 3


def test_create_plan_multiple_slides():
    """Test creating plan for multiple slides"""
    content = "[SLIDE_START][TITLE_START]Slide 1[TITLE_END][BULLET_START]A[BULLET_END][SLIDE_END][SLIDE_START][TITLE_START]Slide 2[TITLE_END][BULLET_START]B[BULLET_END][BULLET_START]C[BULLET_END][SLIDE_END]"
    
    validated = InputAgent.validate_input(content=content)
    plan = PlannerAgent.create_plan(validated)
    
    assert plan.slide_count == 2
    assert plan.total_duration > 0


def test_duration_calculation():
    """Test that duration increases with more bullets"""
    # 2 bullets
    short = "[SLIDE_START][TITLE_START]Short[TITLE_END][BULLET_START]A[BULLET_END][BULLET_START]B[BULLET_END][SLIDE_END]"
    # 6 bullets
    long = "[SLIDE_START][TITLE_START]Long[TITLE_END][BULLET_START]A[BULLET_END][BULLET_START]B[BULLET_END][BULLET_START]C[BULLET_END][BULLET_START]D[BULLET_END][BULLET_START]E[BULLET_END][BULLET_START]F[BULLET_END][SLIDE_END]"
    
    short_plan = PlannerAgent.create_plan(InputAgent.validate_input(content=short))
    long_plan = PlannerAgent.create_plan(InputAgent.validate_input(content=long))
    
    assert long_plan.slides[0].duration_seconds > short_plan.slides[0].duration_seconds


def test_theme_selection():
    """Test theme selection"""
    content = "[SLIDE_START][TITLE_START]Test[TITLE_END][BULLET_START]Content[BULLET_END][SLIDE_END]"
    validated = InputAgent.validate_input(content=content)
    
    # Test different themes
    for theme_name in ["corporate_blue", "modern_dark", "minimal_light", "vibrant_purple"]:
        plan = PlannerAgent.create_plan(validated, theme_name=theme_name)
        assert plan.theme.name == theme_name


def test_default_theme():
    """Test that default theme is applied"""
    content = "[SLIDE_START][TITLE_START]Test[TITLE_END][BULLET_START]Content[BULLET_END][SLIDE_END]"
    validated = InputAgent.validate_input(content=content)
    
    plan = PlannerAgent.create_plan(validated)
    assert plan.theme.name == "corporate_blue"


def test_font_size_adjustment():
    """Test that long titles get smaller fonts"""
    short_title = "[SLIDE_START][TITLE_START]Short[TITLE_END][BULLET_START]Content[BULLET_END][SLIDE_END]"
    long_title = "[SLIDE_START][TITLE_START]This is a very long title that should trigger smaller font size adjustment[TITLE_END][BULLET_START]Content[BULLET_END][SLIDE_END]"
    
    short_plan = PlannerAgent.create_plan(InputAgent.validate_input(content=short_title))
    long_plan = PlannerAgent.create_plan(InputAgent.validate_input(content=long_title))
    
    assert long_plan.slides[0].font_size_title < short_plan.slides[0].font_size_title


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
