import pytest
from app.agents.input_agent import InputAgent, PresentationInput


def test_valid_single_slide():
    """Test parsing a single valid slide"""
    content = """[SLIDE_START]
[TITLE_START]Introduction to AI[TITLE_END]
Artificial Intelligence is transforming our world.
Key areas: Machine Learning, NLP, Computer Vision.
[SLIDE_END]"""
    
    result = InputAgent.validate_input(content=content)
    
    assert len(result.slides) == 1
    assert result.slides[0].title == "Introduction to AI"
    assert len(result.slides[0].content) == 2


def test_valid_multiple_slides():
    """Test parsing multiple slides"""
    content = """[SLIDE_START]
[TITLE_START]Slide 1[TITLE_END]
Content 1
Content 2
[SLIDE_END]
[SLIDE_START]
[TITLE_START]Slide 2[TITLE_END]
Content A
Content B
Content C
[SLIDE_END]"""
    
    result = InputAgent.validate_input(content=content)
    
    assert len(result.slides) == 2
    assert result.slides[0].title == "Slide 1"
    assert result.slides[1].title == "Slide 2"
    assert len(result.slides[1].content) == 3


def test_empty_input():
    """Test that empty input raises error"""
    with pytest.raises(ValueError, match="Input is empty"):
        InputAgent.validate_input(content="")


def test_missing_title():
    """Test that slide without title raises error"""
    content = """[SLIDE_START]
Some content here
[SLIDE_END]"""
    
    with pytest.raises(ValueError, match="without a title"):
        InputAgent.validate_input(content=content)


def test_missing_content():
    """Test that slide without content raises error"""
    content = """[SLIDE_START]
[TITLE_START]Title Only[TITLE_END]
[SLIDE_END]"""
    
    with pytest.raises(ValueError, match="has no content"):
        InputAgent.validate_input(content=content)


def test_unclosed_slide():
    """Test that unclosed slide raises error"""
    content = """[SLIDE_START]
[TITLE_START]Unclosed[TITLE_END]
Content here"""
    
    with pytest.raises(ValueError, match="Unclosed slide"):
        InputAgent.validate_input(content=content)


def test_nested_slide_start():
    """Test that nested SLIDE_START raises error"""
    content = """[SLIDE_START]
[SLIDE_START]
[TITLE_START]Title[TITLE_END]
Content
[SLIDE_END]"""
    
    with pytest.raises(ValueError, match="Nested"):
        InputAgent.validate_input(content=content)


def test_total_content_lines():
    """Test total content lines property"""
    content = """[SLIDE_START]
[TITLE_START]Slide 1[TITLE_END]
Line 1
Line 2
[SLIDE_END]
[SLIDE_START]
[TITLE_START]Slide 2[TITLE_END]
Line A
Line B
Line C
[SLIDE_END]"""
    
    result = InputAgent.validate_input(content=content)
    assert result.total_content_lines == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
