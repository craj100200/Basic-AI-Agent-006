from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
from app.agents.input_agent import InputAgent
from app.api.v1.schemas import (
    ValidateInputRequest,
    ValidateInputResponse,
    SlideResponse,
    ErrorResponse
)
from app.config import settings
from app.utils.logger import logger

router = APIRouter(tags=["Presentation Agent"])


@router.post(
    "/validate-input",
    response_model=ValidateInputResponse,
    summary="Validate presentation input",
    description="Parse and validate presentation content in custom slide format"
)
def validate_input(request: ValidateInputRequest):
    """
    **Step 1: Input Agent**
    
    Validates and parses presentation input in the format:
```
    [SLIDE_START]
    [TITLE_START]Title Here[TITLE_END]
    Content line 1
    Content line 2
    [SLIDE_END]
```
    
    Returns structured, validated slide data.
    """
    try:
        logger.info("API: Received input validation request")
        
        # Run Input Agent
        result = InputAgent.validate_input(content=request.content)
        
        # Build response
        response = ValidateInputResponse(
            status="success",
            message=f"Successfully validated {len(result.slides)} slides",
            slide_count=len(result.slides),
            total_content_lines=result.total_content_lines,
            slides=[
                SlideResponse(
                    title=slide.title,
                    content=slide.content,
                    content_count=len(slide.content)
                )
                for slide in result.slides
            ]
        )
        
        logger.info(f"API: Validation successful - {len(result.slides)} slides")
        return response
        
    except ValueError as e:
        logger.warning(f"API: Validation failed - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("API: Unexpected error during validation")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/validate-input-file",
    response_model=ValidateInputResponse,
    summary="Validate presentation from uploaded file",
    description="Upload a .txt file containing presentation in custom slide format"
)
async def validate_input_file(file: UploadFile = File(...)):
    """
    **Step 1: Input Agent (File Upload)**
    
    Upload a text file containing presentation content.
    File should use the same [SLIDE_START]...[SLIDE_END] format.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are supported")
        
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        logger.info(f"API: Received file upload - {file.filename}")
        
        # Run Input Agent
        result = InputAgent.validate_input(content=text_content)
        
        # Build response
        response = ValidateInputResponse(
            status="success",
            message=f"Successfully validated {len(result.slides)} slides from {file.filename}",
            slide_count=len(result.slides),
            total_content_lines=result.total_content_lines,
            slides=[
                SlideResponse(
                    title=slide.title,
                    content=slide.content,
                    content_count=len(slide.content)
                )
                for slide in result.slides
            ]
        )
        
        logger.info(f"API: File validation successful - {len(result.slides)} slides")
        return response
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    except ValueError as e:
        logger.warning(f"API: File validation failed - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("API: Unexpected error during file validation")
        raise HTTPException(status_code=500, detail="Internal server error")
