from typing import List
import zipfile
from io import BytesIO
from PIL import Image
from rembg import remove
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from pathlib import Path
from config.settings import (
    MAX_BATCH_FILES,
    MAX_FILE_SIZE_MB,
    ALLOWED_IMAGE_FORMATS
)

async def batch_img_convert(files: List[UploadFile], out_img_format: str):
    # Validate format
    if out_img_format.upper() not in ALLOWED_IMAGE_FORMATS:
        return {'message': 'Desired output is not accepted'}

    # Validate batch size
    if len(files) > MAX_BATCH_FILES:
        return {'message': f'Maximum {MAX_BATCH_FILES} files allowed per batch'}

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            # Skip non-image files
            if 'image' not in file.content_type:
                continue

            contents = await file.read()
            img = Image.open(BytesIO(contents))
            img_name = Path(file.filename).stem

            # Handle JPEG transparency
            if out_img_format.upper() in ('JPEG', 'JPG', 'BMP'):
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

            # Handle JPG → JPEG for Pillow
            pillow_format = 'JPEG' if out_img_format.upper() == 'JPG' else out_img_format.upper()

            output_buffer = BytesIO()
            img.save(output_buffer, format=pillow_format)
            output_buffer.seek(0)

            zip_file.writestr(
                f"{img_name}_converted.{out_img_format.lower()}",
                output_buffer.read()
            )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=pixishift_converted.zip"}
    )

async def batch_img_remove_bg(files: List[UploadFile], quality: int = 80):
    # Validate batch size
    if len(files) > MAX_BATCH_FILES:
        return {'message': f'Maximum {MAX_BATCH_FILES} files allowed per batch'}

    zip_buffer = BytesIO()

    output_format = 'PNG'
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            # Skip non-image files
            if 'image' not in file.content_type:
                continue

            contents = await file.read()
            img = Image.open(BytesIO(contents))
            removed = remove(img)
            img_name = Path(file.filename).stem

            output_buffer = BytesIO()
            removed.save(output_buffer, format=output_format)
            output_buffer.seek(0)

            zip_file.writestr(
                f"{img_name}_removedbg.{output_format.lower()}",
                output_buffer.read()
            )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=pixishift_removedbg.zip"}
    )

async def batch_img_compress(files: List[UploadFile], quality: int = 80):

    if len(files) > MAX_BATCH_FILES:
        return {'message': f'Maximum {MAX_BATCH_FILES} files allowed per batch'}

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            if 'image' not in file.content_type:
                continue

            contents = await file.read()
            img = Image.open(BytesIO(contents))

            img_name = Path(file.filename).stem
            img_format = img.format

            if img_format in ('JPEG', 'JPG', 'BMP'):
                if img.mode != 'RGB':
                    img = img.convert('RGB')


            output_buffer = BytesIO()
            img.save(output_buffer, format=img_format, quality=quality, optimize=True)
            output_buffer.seek(0)

            zip_file.writestr(
                f"{img_name}_compressed.{img_format.lower()}",
                output_buffer.read()
            )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=pixishift_compressed.zip"}
    )