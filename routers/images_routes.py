from fastapi import APIRouter, UploadFile
from services import image_services
from services import batch_img_services
from typing import List

router = APIRouter()

@router.post("/convert")
async def convert_image(file: UploadFile, out_img_format: str):
    return await image_services.convert(file, out_img_format)

@router.post("/remove-bg")
async def remove_background(file: UploadFile):
    return await image_services.remove_bg(file)

@router.post("/image-compress")
async def compress_image(file: UploadFile, quality: int = 80):
    return await image_services.img_compress(file, quality)

@router.post("/image-resize")
async def resize_image(
    file: UploadFile, 
    img_width: float, 
    img_height: float,
    unit: str = "px",
    dpi: int = 96
    ):
    return await image_services.img_resize(file, img_width, img_height, unit, dpi)

@router.post("/batch-convert")
async def batch_convert(
    files: List[UploadFile],
    out_img_format: str
):
    return await batch_img_services.batch_img_convert(files)

@router.post("/batch-remove")
async def batch_remove(
    files: List[UploadFile],
):
    return await batch_img_services.batch_img_remove_bg(files)

@router.post("/batch-compress")
async def batch_remove(
    files: List[UploadFile],
    quality: int = 80
):
    return await batch_img_services.batch_img_compress(files, quality)