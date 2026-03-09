from fastapi import APIRouter, UploadFile
from services import pdf_services,batch_pdf_services
from typing import List

router = APIRouter()

@router.post("/pdf2img")
async def convert_pdf_to_img(file: UploadFile):
    return await pdf_services.pdf_to_img(file)

@router.post("/docx2pdf")
async def convert_docx_to_pdf(file: UploadFile):
    return await pdf_services.docx_to_pdf(file)

@router.post("/xlsx2pdf")
async def convert_xlsx_to_pdf(file: UploadFile):
    return await pdf_services.xlsx_to_pdf(file)

@router.post("/ppt2pdf")
async def convert_ppt_to_pdf(file: UploadFile):
    return await pdf_services.ppt_to_pdf(file)

@router.post("/pdf2docx")
async def convert_pdf_to_docx(file: UploadFile):
    return await pdf_services.pdf_to_docx(file)

# Batch Processing Routes
@router.post("/batch-docx2pdf")
async def convert_docx_to_pdf(files: List[UploadFile]):
    return await batch_pdf_services.batch_docx_to_pdf(files)

@router.post("/batch-xlsx2pdf")
async def convert_xlsx_to_pdf(files: List[UploadFile]):
    return await batch_pdf_services.batch_xlsx_to_pdf(files)

@router.post("/batch-ppt2pdf")
async def convert_ppt_to_pdf(files: List[UploadFile]):
    return await batch_pdf_services.batch_ppt_to_pdf(files)

@router.post("/batch-pdf2img")
async def convert_pdf_to_img(files: List[UploadFile]):
    return await batch_pdf_services.batch_pdf_to_img(files)

@router.post("/batch-pdf2docx")
async def convert_pdf_to_img(files: List[UploadFile]):
    return await batch_pdf_services.batch_pdf_to_docx(files)