from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
def root():
    return {
        "status": "KRISTAL ONLINE",
        "service": "KRISTAL API",
    }


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "KRISTAL API",
    }