# ===== AI GENERATED: render_presentation_document =====
# Purpose: Render a conspicuously fictional image for development-only seeded OR records.
# Inputs: Demo record reference and document kind; no real signatures or company data.
# Returns: PNG bytes generated locally without a storage-service dependency.
# Flow: Draw a presentation placard; label it invalid for business use; encode in memory.

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def render_presentation_document(reference: str, kind: str) -> bytes:
    image = Image.new("RGB", (1000, 650), "#f3f4f6")
    drawing = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=32)
    drawing.rectangle((25, 25, 975, 625), outline="#f97316", width=8)
    lines = [
        "BM ENTERPRISES - PRESENTATION ONLY",
        "FICTIONAL DEMONSTRATION DOCUMENT",
        "",
        f"Reference: {reference}",
        f"Type: {kind}",
        "",
        "Not a business receipt or delivery confirmation.",
        "No real signature or company stamp.",
        "No money or goods changed hands.",
    ]
    for position, line in enumerate(lines):
        drawing.text((60, 65 + position * 52), line, fill="#111827", font=font)
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
