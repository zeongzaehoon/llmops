"""
Phase 2 characterization tests (Task #15).

Pins the image media-type resolution that is duplicated inline (byte-identical
logic) across x.py / google.py / bedrock.py:

    detected = detect_image_format(data)
    media_type = f"image/{detected}" if detected else "image/jpeg"

Extracted into client.common.resolve_image_media_type. These tests define the
exact contract so the extraction provably preserves behavior. Pure function —
no SDK / network.
"""
from client.common import resolve_image_media_type

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
GIF = b"GIF89a" + b"\x00" * 16
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 8
BMP = b"BM" + b"\x00" * 16
UNKNOWN = b"not-an-image-header"


def test_known_formats_map_to_image_mime():
    assert resolve_image_media_type(PNG) == "image/png"
    assert resolve_image_media_type(JPEG) == "image/jpeg"
    assert resolve_image_media_type(GIF) == "image/gif"
    assert resolve_image_media_type(WEBP) == "image/webp"
    assert resolve_image_media_type(BMP) == "image/bmp"


def test_unknown_bytes_fall_back_to_jpeg():
    assert resolve_image_media_type(UNKNOWN) == "image/jpeg"
    assert resolve_image_media_type(b"") == "image/jpeg"


def test_non_bytes_input_falls_back_to_jpeg():
    # x.py base64 branch passes a base64 *string*; detect_image_format returns
    # None for str input, so the existing behavior is "image/jpeg". Preserve it.
    assert resolve_image_media_type("iVBORw0KGgo=") == "image/jpeg"
