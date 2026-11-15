# ===== AI GENERATED: image_test_support =====
# Purpose: Build real JPEG/PNG test images, with metadata when asked
# Inputs: size and metadata options
# Returns: image bytes for upload tests
# Flow:
# 1. JPEGs may carry EXIF (camera make, GPS, orientation)
# 2. PNGs may carry text chunks
# 3. Helpers read metadata back so tests can prove it was stripped

from io import BytesIO

from PIL import Image
from PIL.PngImagePlugin import PngInfo

EXIF_MAKE = 0x010F
EXIF_ORIENTATION = 0x0112
EXIF_GPS_IFD = 0x8825


def make_jpeg(
    width: int = 40, height: int = 20, with_metadata: bool = False, orientation: int | None = None
) -> bytes:
    image = Image.new("RGB", (width, height), (200, 30, 30))
    exif = Image.Exif()
    if with_metadata:
        exif[EXIF_MAKE] = "SecretCameraMaker"
        gps = exif.get_ifd(EXIF_GPS_IFD)
        gps[1] = "N"
        gps[2] = (14.0, 35.0, 0.0)
        gps[3] = "E"
        gps[4] = (121.0, 3.0, 0.0)
    if orientation is not None:
        exif[EXIF_ORIENTATION] = orientation
    buffer = BytesIO()
    options = {"exif": exif} if (with_metadata or orientation) else {}
    image.save(buffer, "JPEG", **options)
    return buffer.getvalue()


def make_png(width: int = 30, height: int = 30, with_text: bool = False) -> bytes:
    image = Image.new("RGBA", (width, height), (10, 120, 200, 255))
    info = PngInfo()
    if with_text:
        info.add_text("Author", "SecretAuthorName")
    buffer = BytesIO()
    image.save(buffer, "PNG", pnginfo=info if with_text else None)
    return buffer.getvalue()


def exif_tags(content: bytes) -> dict[int, object]:
    with Image.open(BytesIO(content)) as image:
        return dict(image.getexif())


def image_size(content: bytes) -> tuple[int, int]:
    with Image.open(BytesIO(content)) as image:
        return image.size


def png_text(content: bytes) -> dict[str, object]:
    with Image.open(BytesIO(content)) as image:
        return dict(image.info)
