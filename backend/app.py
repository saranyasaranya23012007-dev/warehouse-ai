
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from backend.detect import detect_objects

app = FastAPI(title="AI Warehouse Management API")

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload folder
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "AI Warehouse Backend is Running!"
    }


@app.get("/health")
def health():
    return {
        "status": "Backend Working"
    }


@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):

    # Check image format
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image"
        )

    # Save uploaded image
    image_path = UPLOAD_DIR / Path(file.filename).name

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty"
            )

        with open(image_path, "wb") as buffer:
            buffer.write(contents)

        # Run YOLO object detection
        counts = detect_objects(str(image_path))

        return {
            "message": "Detection completed",
            "detected_objects": counts
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if image_path.exists():
            image_path.unlink()
