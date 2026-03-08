from fastapi import APIRouter, UploadFile
from services import pdf_services

router = APIRouter()

@router.post("/pdf2img")
async def convert_pdf_to_img(file: UploadFile):
    return await pdf_services.pdf_to_img(file)