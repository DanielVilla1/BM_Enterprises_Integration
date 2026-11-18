# ===== AI GENERATED: PillowImageSanitizer =====
# Purpose: Accept only real JPEG/PNG images and strip all metadata (spec 11.2)
# Inputs: raw uploaded bytes
# Returns: SanitizedImage re-encoded without EXIF/GPS, or InvalidImageError
# Flow:
# 1. Check the magic bytes, then let Pillow decode (no extension or header trust)
# 2. Reject oversized pixel counts (decompression bombs)
# 3. Apply EXIF orientation, then re-encode so no metadata survives

from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from ...Contract.i_storage import InvalidImageError, SanitizedImage

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAXIMUM_PIXELS = 50_000_000
JPEG_QUALITY = 90


class PillowImageSanitizer:
    """Implements IImageSanitizer."""

    def __init__(self, maximum_pixels: int = MAXIMUM_PIXELS) -> None:
        self._maximum_pixels = maximum_pixels

    def sanitize(self, raw_content: bytes) -> SanitizedImage:
        if raw_content.startswith(JPEG_MAGIC):
            image_format = "JPEG"
        elif raw_content.startswith(PNG_MAGIC):
            image_format = "PNG"
        else:
            raise InvalidImageError("only JPEG and PNG images are accepted")
        try:
            with Image.open(BytesIO(raw_content)) as image:
                if image.format != image_format:
                    raise InvalidImageError("image content does not match its type")
                if image.width * image.height > self._maximum_pixels:
                    raise InvalidImageError("image dimensions are too large")
                upright = ImageOps.exif_transpose(image)
                return self._encode(upright, image_format)
        except InvalidImageError:
            raise
        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            SyntaxError,
            Image.DecompressionBombError,
        ) as error:
            raise InvalidImageError("the image could not be decoded") from error

    @staticmethod
    def _encode(image: Image.Image, image_format: str) -> SanitizedImage:
        buffer = BytesIO()
        if image_format == "JPEG":
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(buffer, "JPEG", quality=JPEG_QUALITY, optimize=True)
            return SanitizedImage(buffer.getvalue(), "image/jpeg", "jpg")
        image.save(buffer, "PNG", optimize=True)
        return SanitizedImage(buffer.getvalue(), "image/png", "png")
