from PIL import Image
from fastapi.responses import StreamingResponse
from io import BytesIO
from pathlib import Path
from rembg import remove

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