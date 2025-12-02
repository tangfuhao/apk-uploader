"""FastAPI application for Android package (APK/AAB) file uploads to Aliyun OSS."""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Optional

from .config import Settings, get_settings
from .uploader import OSSUploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Android Package Uploader API",
    description="API for uploading Android packages (APK/AAB files) to Aliyun OSS",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_uploader(settings: Settings = Depends(get_settings)) -> OSSUploader:
    """Dependency to get OSS uploader instance."""
    return OSSUploader(
        access_key_id=settings.oss_access_key_id,
        access_key_secret=settings.oss_access_key_secret,
        endpoint=settings.oss_endpoint,
        bucket_name=settings.oss_bucket_name,
        region=settings.oss_region,
        prefix=settings.oss_prefix
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Android Package Uploader API",
        "version": "2.0.0",
        "status": "running",
        "supported_formats": ["APK", "AAB"],
        "endpoints": {
            "upload": "/upload",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "android-package-uploader",
        "supported_formats": ["APK", "AAB"]
    }


@app.post("/upload")
async def upload_package(
    file: UploadFile = File(..., description="Android package file to upload (APK or AAB)"),
    custom_name: Optional[str] = Form(None, description="Custom name for the file (optional, without extension)"),
    settings: Settings = Depends(get_settings),
    uploader: OSSUploader = Depends(get_uploader)
):
    """
    Upload an Android package file (APK or AAB) to Aliyun OSS.
    
    Args:
        file: The Android package file to upload (APK or AAB)
        custom_name: Optional custom name for the uploaded file (without extension)
        
    Returns:
        JSON response with upload status and file URL
        
    Raises:
        HTTPException: If validation fails or upload fails
    """
    try:
        # Validate file type
        filename_lower = file.filename.lower()
        if not (filename_lower.endswith('.apk') or filename_lower.endswith('.aab')):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Only APK and AAB files are allowed. Got: {file.filename}"
            )
        
        # Read file content
        logger.info(f"Receiving file: {file.filename}")
        file_content = await file.read()
        
        # Check file size
        file_size = len(file_content)
        if file_size > settings.max_upload_size:
            max_size_mb = settings.max_upload_size / (1024 * 1024)
            actual_size_mb = file_size / (1024 * 1024)
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {max_size_mb}MB, Got: {actual_size_mb:.2f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        # Upload to OSS
        logger.info(f"Uploading {file.filename} to OSS (size: {file_size / (1024*1024):.2f}MB)")
        result = await uploader.upload_file(
            file_content=file_content,
            filename=file.filename,
            custom_name=custom_name
        )
        
        logger.info(f"Upload successful: {result['url']}")
        
        file_type = "APK" if filename_lower.endswith('.apk') else "AAB"
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"{file_type} file uploaded successfully",
                "data": result
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload Android package: {str(e)}"
        )
    finally:
        await file.close()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

