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

async def add_img_watermark(
    file, 
    watermark_img):

    if 'image' not in file.content_type:
        return {'message': 'File is not an image'}

    if 'image' not in watermark_img.content_type:
        return {'message': 'Watermark is not an image'}

    img_contents = await file.read()
    watermark_img_contents = await watermark_img.read()

    img = Image.open(BytesIO(img_contents))
    watermark = Image.open(BytesIO(watermark_img_contents))

    img_name = Path(file.filename).stem
    img_format = img.format

    target_width = 200  
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

    return StreamingResponse(
        output_buffer,
        media_type=f"image/{img_format.lower()}",
        headers={"Content-Disposition": f"attachment; filename={img_name}_watermarked.{img_format.lower()}"}
    )

async def image_to_pdf(files):

    images = []

    for file in files:
        if 'image' not in file.content_type:
            return {'message': 'File is not an image'}
        
        contents = await file.read()
        img = Image.open(BytesIO(contents))

        if img.mode != 'RGB':
            img = img.convert('RGB')

        images.append(img)

    if not images:
        return {'message': 'No valid images provided'}
        
    output_buffer = BytesIO()

    images[0].save(
        output_buffer,
        format="PDF",
        save_all=True,
        append_images=images[1:]
    )
        
    output_buffer.seek(0)

    return StreamingResponse(
        output_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=pixishift_images.pdf"}
    )