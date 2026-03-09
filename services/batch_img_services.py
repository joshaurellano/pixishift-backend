from typing import List
import zipfile
from io import BytesIO
from PIL import Image
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