from fastapi.responses import StreamingResponse
from fastapi import UploadFile
from io import BytesIO
from pathlib import Path
from typing import List
import pymupdf
import zipfile
import subprocess
import tempfile
import os
from pdf2docx import Converter
from utils.libreoffice_path_utils import get_libreoffice_path
from config.settings import (
    MAX_BATCH_FILES,
    MAX_FILE_SIZE_MB,
    ALLOWED_IMAGE_FORMATS,
    ALLOWED_TYPES
)

# ---- Helper ----
async def batch_convert_to_pdf(files: List[UploadFile], file_type: str):
    if len(files) > MAX_BATCH_FILES:
        return {'message': f'Maximum {MAX_BATCH_FILES} files allowed per batch'}

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            # Skip invalid file types
            if file.content_type not in ALLOWED_TYPES[file_type]:
                continue

            contents = await file.read()
            base_name = Path(file.filename).stem

            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = os.path.join(tmpdir, file.filename)

                with open(input_path, 'wb') as f:
                    f.write(contents)

                subprocess.run([
                    get_libreoffice_path(), '--headless', '--convert-to', 'pdf',
                    '--outdir', tmpdir, input_path
                ], check=True)

                pdf_path = os.path.join(tmpdir, f"{base_name}.pdf")

                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()

            zip_file.writestr(
                f"{base_name}_converted.pdf",
                pdf_bytes
            )

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=pixishift_pdfs.zip"}
    )

# ---- Services ----
async def batch_docx_to_pdf(files: List[UploadFile]):
    return await batch_convert_to_pdf(files, 'docx')

async def batch_xlsx_to_pdf(files: List[UploadFile]):
    return await batch_convert_to_pdf(files, 'xlsx')

async def batch_ppt_to_pdf(files: List[UploadFile]):
    return await batch_convert_to_pdf(files, 'ppt')

async def batch_pdf_to_img(files: List[UploadFile]):
    if len(files) > MAX_BATCH_FILES:
        return {'message': f'Maximum {MAX_BATCH_FILES} files allowed per batch'}

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            # Skip invalid file types
            if file.content_type != 'application/pdf':
                continue
 
            contents = await file.read()
            pdf = pymupdf.open(stream=contents, filetype="pdf")
            base_name = Path(file.filename).stem

            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                zip_file.writestr(
                    f"{base_name}_scanned_page{page_num + 1}.png",
                    img_bytes
                )

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=pixishift_pdf_images.zip"}
    )

async def batch_pdf_to_docx(files: List[UploadFile]):
    if len(files) > MAX_BATCH_FILES:
        return {'message': f'Maximum {MAX_BATCH_FILES} files allowed per batch'}

    zip_buffer = BytesIO()
    failed_files = []

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            # Skip invalid file types
            if file.content_type != 'application/pdf':
                continue
    
            contents = await file.read()
            base_name = Path(file.filename).stem

            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = os.path.join(tmpdir, file.filename)
                output_path = os.path.join(tmpdir, f"{base_name}.docx")

                # Write pdf to temporary path
                with open(input_path, 'wb') as f:
                    f.write(contents)
            
                cv = Converter(input_path)
                cv.convert(output_path)
                cv.close()

                if not os.path.exists(output_path):
                        print(f"Conversion failed - output not found: {base_name}")
                        failed_files.append(base_name)
                        continue

                with open(output_path, 'rb') as f:
                    docx_bytes = f.read()

            zip_file.writestr(
                f"{base_name}_converted.docx",
                docx_bytes
            )

    zip_buffer.seek(0)
    if failed_files:
        print(f"Failed files: {failed_files}")
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=pixishift_pdf_docx.zip"}
    )
    