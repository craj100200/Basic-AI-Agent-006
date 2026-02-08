import pytest
from pathlib import Path
from app.agents.input_agent import InputAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.slide_agent import SlideAgent
from app.agents.video_agent import VideoAgent
from app.config import settings


def test_create_video_single_slide():
    """Test creating video with single slide"""
    content = "[SLIDE_START][TITLE_START]Test Video[TITLE_END][BULLET_START]This is a test[BULLET_END][BULLET_START]Creating video[BULLET_END][SLIDE_END]"
    
    # Run full pipeline
    validated = InputAgent.validate_input(content=content)
    plan = PlannerAgent.create_plan(validated)
    slide_result = SlideAgent().render_slides(plan)
    
    # Generate video
    video_agent = VideoAgent()
    result = video_agent.create_video(plan, slide_result, "test_single.mp4")
    
    assert result.video_path.exists()
    assert result.video_path.suffix == ".mp4"
    assert result.slide_count == 1
    assert result.duration_seconds > 0
    assert result.file_size_mb > 0


def test_create_video_multiple_slides():
    """Test creating video with multiple slides"""
    content = """
    [SLIDE_START][TITLE_START]Slide 1[TITLE_END][BULLET_START]Point A[BULLET_END][SLIDE_END]
    [SLIDE_START][TITLE_START]Slide 2[TITLE_END][BULLET_START]Point B[BULLET_END][SLIDE_END]
    [SLIDE_START][TITLE_START]Slide 3[TITLE_END][BULLET_START]Point C[BULLET_END][SLIDE_END]
    """
    
    validated = InputAgent.validate_input(content=content)
    plan = PlannerAgent.create_plan(validated)
    slide_result = SlideAgent().render_slides(plan)
    
    video_agent = VideoAgent()
    result = video_agent.create_video(plan, slide_result, "test_multi.mp4")
    
    assert result.video_path.exists()
    assert result.slide_count == 3
    assert result.duration_seconds >= 9  # At least 3 seconds per slide


def test_video_resolution():
    """Test that video has correct resolution"""
    content = "[SLIDE_START][TITLE_START]Test[TITLE_END][BULLET_START]Content[BULLET_END][SLIDE_END]"
    
    validated = InputAgent.validate_input(content=content)
    plan = PlannerAgent.create_plan(validated)
    slide_result = SlideAgent().render_slides(plan)
    
    video_agent = VideoAgent()
    result = video_agent.create_video(plan, slide_result, "test_resolution.mp4")
    
    assert result.resolution == "1920x1080"
    assert result.fps == 30


def test_custom_filename():
    """Test creating video with custom filename"""
    content = "[SLIDE_START][TITLE_START]Custom[TITLE_END][BULLET_START]Test[BULLET_END][SLIDE_END]"
    
    validated = InputAgent.validate_input(content=content)
    plan = PlannerAgent.create_plan(validated)
    slide_result = SlideAgent().render_slides(plan)
    
    video_agent = VideoAgent()
    custom_name = "my_custom_video.mp4"
    result = video_agent.create_video(plan, slide_result, custom_name)
    
    assert result.video_path.name == custom_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
