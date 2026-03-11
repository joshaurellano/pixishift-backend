from typing import List
import zipfile
from io import BytesIO
from PIL import Image
from rembg import remove
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from pathlib import Path
from utils.img_utils import convert_to_pixels
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

async def batch_add_img_watermark(
    files, 
    watermark_img):

    if len(files) > MAX_BATCH_FILES:
        return {'message': f'Maximum {MAX_BATCH_FILES} files allowed per batch'}

    if 'image' not in watermark_img.content_type:
        return {'message': 'Watermark is not an image'}
    
    zip_buffer = BytesIO()

    watermark_img_contents = await watermark_img.read()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            if 'image' not in file.content_type:
                continue

            img_contents = await file.read()

            img = Image.open(BytesIO(img_contents))
            watermark = Image.open(BytesIO(watermark_img_contents))

            img_name = Path(file.filename).stem
            img_format = img.format

            target_width = 100  
            aspect_ratio = float(target_width) / watermark.width
            target_height = int(watermark.height * aspect_ratio)
            watermark = watermark.resize((target_width, target_height),Image.Resampling.LANCZOS)
            
            watermarked_image = img.copy()
            position = (img.width - watermark.width, img.height - watermark.height)

            if watermark.mode == 'RGBA':
                if watermarked_image.mode != 'RGBA':
                    watermarked_image = watermarked_image.convert('RGBA')
                watermarked_image.paste(watermark, position, mask=watermark)
            else:
                watermarked_image.paste(watermark, position)

            if img_format.upper() in ('JPEG', 'JPG') and watermarked_image.mode == 'RGBA':
                watermarked_image = watermarked_image.convert('RGB')

            output_buffer = BytesIO()
            watermarked_image.save(output_buffer, format=img_format)
            output_buffer.seek(0)

            zip_file.writestr(
                f"{img_name}_watermarked.{img_format.lower()}",
                output_buffer.read()
            )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type=f"application/zip",
        headers={"Content-Disposition": f"attachment; filename=pixishift_watermarked.zip"}
    )

async def batch_img_resize(
        files, 
        img_width: float, 
        img_height: float,
        unit: str = "px",
        dpi: int = 96):

    if len(files) > MAX_BATCH_FILES:
        return {'message': f'Maximum {MAX_BATCH_FILES} files allowed per batch'}
        
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            if 'image' not in file.content_type:
                continue
    
            allowed_units = ['px', 'in', 'cm', 'mm']
            if unit.lower() not in allowed_units:
                return {'message': f'Unit not supported. Use: {allowed_units}'}
            
            final_width = convert_to_pixels(img_width, unit, dpi)
            final_height = convert_to_pixels(img_height, unit, dpi)

            if not final_width or not final_height:
                return {'message': 'Invalid dimensions'}

            contents = await file.read()
            img = Image.open(BytesIO(contents))
            img_format = img.format
            img_name = Path(file.filename).stem
            
            img = img.resize((final_width, final_height), Image.LANCZOS)

            output_buffer = BytesIO()
            img.save(output_buffer, format=img_format)
            output_buffer.seek(0)

            zip_file.writestr(
                f"{img_name}_resized.{img_format.lower()}",
                output_buffer.read()
            )
    
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=pixishift_resized.zip"}
    )