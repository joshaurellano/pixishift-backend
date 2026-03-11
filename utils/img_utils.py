def convert_to_pixels(value: float, unit: str, dpi: int = 96) -> int:
    unit = unit.lower()
    if unit == 'px':
        return int(value)
    elif unit == 'in':
        return int(value * dpi)
    elif unit == 'cm':
        return int((value / 2.54) * dpi)
    elif unit == 'mm':
        return int((value / 10 / 2.54) * dpi)
    else:
        return None