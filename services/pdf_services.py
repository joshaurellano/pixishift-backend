from fastapi.responses import StreamingResponse
from fastapi import UploadFile
from io import BytesIO
from pathlib import Path
import pymupdf
import zipfile
import subprocess
import tempfile
import os

ALLOWED_TYPES = {
    'docx': (
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'application/wps-office.docx'
    ),
    'xlsx': (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'application/wps-office.xlsx'
    ),
    'ppt': (
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint',
        'application/wps-office.ppt',
        'application/wps-office.pptx'
    ),
}

# ---- Helper ----

async def convert_to_pdf(file: UploadFile, file_type: str):
    if file.content_type not in ALLOWED_TYPES[file_type]:
        return {'message': f'File is not a {file_type}'}

    contents = await file.read()
    base_name = Path(file.filename).stem

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, file.filename)
        with open(input_path, 'wb') as f:
            f.write(contents)

        subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf',
            '--outdir', tmpdir, input_path
        ], check=True)

        pdf_path = os.path.join(tmpdir, f"{base_name}.pdf")
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

    output_buffer = BytesIO(pdf_bytes)
    output_buffer.seek(0)

    return StreamingResponse(
        output_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={base_name}.pdf"}
    )

# ---- Services ----

async def docx_to_pdf(file: UploadFile):
    return await convert_to_pdf(file, 'docx')

async def xlsx_to_pdf(file: UploadFile):
    return await convert_to_pdf(file, 'xlsx')

async def ppt_to_pdf(file: UploadFile):
    return await convert_to_pdf(file, 'ppt')

async def pdf_to_img(file: UploadFile):
    if file.content_type != 'application/pdf':
        return {'message': 'File is not a pdf'}

    contents = await file.read()
    user_file = pymupdf.open(stream=contents, filetype="pdf")
    base_name = Path(file.filename).stem

    if user_file.page_count == 1:
        page = user_file[0]
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        output_buffer = BytesIO(img_bytes)
        output_buffer.seek(0)

        return StreamingResponse(
            output_buffer,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={base_name}.png"}
        )
    else:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for page_num in range(user_file.page_count):
                page = user_file[page_num]
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                zip_file.writestr(f"{base_name}_page{page_num + 1}.png", img_bytes)
        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={base_name}_pages.zip"}
        )