import platform

def get_libreoffice_path():
    if platform.system() == "Windows":
        return r"C:\Program Files\LibreOffice\program\soffice.exe"
    else:
        return "libreoffice"
