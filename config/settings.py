# File limits
MAX_FILE_SIZE_MB = 5          # 5MB for free users
MAX_BATCH_FILES = 10          # max files per batch

# Allowed formats
ALLOWED_IMAGE_FORMATS = [
    'PNG', 'WEBP', 'JPG', 
    'JPEG', 'BMP', 'TIFF'
]

ALLOWED_PDF_FORMATS = [
    'application/pdf'
]

# ALLOWED_DOCUMENT_FORMATS = [
#     'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
#     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#     'application/vnd.openxmlformats-officedocument.presentationml.presentation'
# ]
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

# Compression defaults
DEFAULT_COMPRESSION_QUALITY = 80
MIN_COMPRESSION_QUALITY = 1
MAX_COMPRESSION_QUALITY = 95

# DPI settings
SCREEN_DPI = 96
PRINT_DPI = 300