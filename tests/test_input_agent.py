import pytest
from app.agents.input_agent import InputAgent, PresentationInput


def test_valid_single_slide():
    """Test parsing a single valid slide"""
    content = "[SLIDE_START][TITLE_START]Introduction to AI[TITLE_END][BULLET_START]AI is transforming our world[BULLET_END][BULLET_START]Machine Learning is key[BULLET_END][SLIDE_END]"
    
    result = InputAgent.validate_input(content=content)
    
    assert len(result.slides) == 1
    assert result.slides[0].title == "Introduction to AI"
    assert len(result.slides[0].content) == 2
    assert result.slides[0].content[0] == "AI is transforming our world"


def test_valid_single_slide_with_newlines():
    """Test parsing with newlines (should be ignored)"""
    content = """[SLIDE_START]
    [TITLE_START]Introduction to AI[TITLE_END]
    [BULLET_START]AI is transforming our world[BULLET_END]
    [BULLET_START]Machine Learning is key[BULLET_END]
    [SLIDE_END]"""
    
    result = InputAgent.validate_input(content=content)
    
    assert len(result.slides) == 1
    assert result.slides[0].title == "Introduction to AI"
    assert len(result.slides[0].content) == 2


def test_valid_multiple_slides():
    """Test parsing multiple slides"""
    content = "[SLIDE_START][TITLE_START]Slide 1[TITLE_END][BULLET_START]Content 1[BULLET_END][BULLET_START]Content 2[BULLET_END][SLIDE_END][SLIDE_START][TITLE_START]Slide 2[TITLE_END][BULLET_START]Content A[BULLET_END][BULLET_START]Content B[BULLET_END][BULLET_START]Content C[BULLET_END][SLIDE_END]"
    
    result = InputAgent.validate_input(content=content)
    
    assert len(result.slides) == 2
    assert result.slides[0].title == "Slide 1"
    assert result.slides[1].title == "Slide 2"
    assert len(result.slides[1].content) == 3


def test_multiple_slides_with_formatting():
    """Test multiple slides with nice formatting"""
    content = """
    [SLIDE_START]
        [TITLE_START]Slide 1[TITLE_END]
        [BULLET_START]Point 1[BULLET_END]
        [BULLET_START]Point 2[BULLET_END]
    [SLIDE_END]
    
    [SLIDE_START]
        [TITLE_START]Slide 2[TITLE_END]
        [BULLET_START]Point A[BULLET_END]
        [BULLET_START]Point B[BULLET_END]
    [SLIDE_END]
    """
    
    result = InputAgent.validate_input(content=content)
    assert len(result.slides) == 2


def test_empty_input():
    """Test that empty input raises error"""
    with pytest.raises(ValueError, match="Input is empty"):
        InputAgent.validate_input(content="")


def test_missing_title():
    """Test that slide without title raises error"""
    content = "[SLIDE_START][BULLET_START]Some content[BULLET_END][SLIDE_END]"
    
    with pytest.raises(ValueError, match="Missing title"):
        InputAgent.validate_input(content=content)


def test_empty_title():
    """Test that empty title raises error"""
    content = "[SLIDE_START][TITLE_START][TITLE_END][BULLET_START]Content[BULLET_END][SLIDE_END]"
    
    with pytest.raises(ValueError, match="Title is empty"):
        InputAgent.validate_input(content=content)


def test_missing_content():
    """Test that slide without content raises error"""
    content = "[SLIDE_START][TITLE_START]Title Only[TITLE_END][SLIDE_END]"
    
    with pytest.raises(ValueError, match="has no content"):
        InputAgent.validate_input(content=content)


def test_no_slides():
    """Test that input without slides raises error"""
    content = "Just some random text"
    
    with pytest.raises(ValueError, match="No slides found"):
        InputAgent.validate_input(content=content)


def test_total_content_lines():
    """Test total content lines property"""
    content = "[SLIDE_START][TITLE_START]Slide 1[TITLE_END][BULLET_START]Line 1[BULLET_END][BULLET_START]Line 2[BULLET_END][SLIDE_END][SLIDE_START][TITLE_START]Slide 2[TITLE_END][BULLET_START]Line A[BULLET_END][BULLET_START]Line B[BULLET_END][BULLET_START]Line C[BULLET_END][SLIDE_END]"
    
    result = InputAgent.validate_input(content=content)
    assert result.total_content_lines == 5


def test_special_characters_in_content():
    """Test that special characters are preserved"""
    content = "[SLIDE_START][TITLE_START]Code Example[TITLE_END][BULLET_START]Use <div> tags[BULLET_END][BULLET_START]Function: doSomething()[BULLET_END][SLIDE_END]"
    
    result = InputAgent.validate_input(content=content)
    assert result.slides[0].content[0] == "Use <div> tags"
    assert result.slides[0].content[1] == "Function: doSomething()"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
