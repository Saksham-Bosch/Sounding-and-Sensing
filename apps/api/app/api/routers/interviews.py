from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_interviews():
    return {"message": "Interviews endpoint placeholder"}
