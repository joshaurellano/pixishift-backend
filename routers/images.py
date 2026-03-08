from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse
from services import image_services

router = APIRouter()

@router.post("/convert")
async def convert_image(file: UploadFile, out_img_format: str):
    return await image_services.convert(file, out_img_format)

@router.post("/remove-bg")
async def remove_background(file: UploadFile):
    return await image_services.remove_bg(file)