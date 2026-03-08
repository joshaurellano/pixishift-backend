from PIL import Image
from fastapi.responses import StreamingResponse
from io import BytesIO
from pathlib import Path
from rembg import remove
from utils.img_utils import convert_to_pixels


IMAGE_FORMATS = ['PNG', 'WEBP', 'JPG', 'JPEG', 'AVIF', 'BMP', 'TIFF']

async def convert(file, out_img_format: str):
    if 'image' not in file.content_type:
        return {'message': 'File is not an image'}
    
    contents = await file.read()
    img = Image.open(BytesIO(contents))

    if out_img_format.upper() not in IMAGE_FORMATS:
        return {'message': 'Desired output is not accepted'}
    
    if out_img_format.upper() == img.format.upper():
        return {'message': 'Desired output should not be the same as original'}
    
    if out_img_format.upper() in ('JPEG', 'JPG', 'BMP') and img.mode != 'RGB':
        img = img.convert('RGB')
        
    if out_img_format.upper() == 'JPG':
        out_img_format = 'JPEG'

    img_name = Path(file.filename).stem
    output_buffer = BytesIO()
    img.save(output_buffer, format=out_img_format.upper())
    output_buffer.seek(0)

    return StreamingResponse(
        output_buffer,
        media_type=f"image/{out_img_format.lower()}",
        headers={"Content-Disposition": f"attachment; filename={img_name}_converted.{out_img_format.lower()}"}
    )

async def remove_bg(file):
    if 'image' not in file.content_type:
        return {'message': 'File is not an image'}

    contents = await file.read()
    img = Image.open(BytesIO(contents))
    removed = remove(img)

    img_name = Path(file.filename).stem
    output_buffer = BytesIO()
    removed.save(output_buffer, format='PNG')
    output_buffer.seek(0)

    return StreamingResponse(
        output_buffer,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename={img_name}_nobg.png"}
    )

async def img_compress(file, quality: int = 80):
    if 'image' not in file.content_type:
        return {'message': 'File is not an image'}

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

    return StreamingResponse(
        output_buffer,
        media_type=f"image/{img_format.lower()}",
        headers={"Content-Disposition": f"attachment; filename={img_name}_compressed.{img_format.lower()}"}
    )

async def img_resize(
        file, 
        img_width: float, 
        img_height: float,
        unit: str = "px",
        dpi: int = 96):
    
    if 'image' not in file.content_type:
        return {'message': 'File is not an image'}
    
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

    return StreamingResponse(
        output_buffer,
        media_type=f"image/{img_format.lower()}",
        headers={"Content-Disposition": f"attachment; filename={img_name}_resized.{img_format.lower()}"}
    )