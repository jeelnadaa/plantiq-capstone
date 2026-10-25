import io

import pytest
from fastapi import HTTPException
from PIL import Image

from app.core.uploads import check_audio, clean_image, decode_data_url, sanitize_filename, sniff_audio
from tests.conftest import image_bytes, webm_bytes

pytestmark = pytest.mark.unit


def _exif_with_gps() -> bytes:
    img = Image.new("RGB", (10, 10))
    exif = img.getexif()
    exif[0x010F] = "SecretCam"  # Make
    exif[0x8825] = {1: "N", 2: (13.0, 18.0, 58.0)}  # GPS IFD
    return exif.tobytes()


def test_jpeg_reencoded_and_exif_stripped():
    raw = image_bytes(exif=_exif_with_gps())
    assert b"SecretCam" in raw
    out = clean_image(raw, "photo.jpg")
    assert out.data.startswith(b"\xff\xd8\xff")
    assert b"SecretCam" not in out.data
    assert not Image.open(io.BytesIO(out.data)).getexif()


@pytest.mark.parametrize("fmt", ["PNG", "WEBP"])
def test_png_and_webp_become_jpeg(fmt):
    out = clean_image(image_bytes(fmt), "leaf.png")
    assert out.data.startswith(b"\xff\xd8\xff") and out.filename == "leaf.jpg"


def test_rejects_empty_non_image_and_polyglot():
    for bad, code in [(b"", 400), (b"GIF89a....", 415), (b"%PDF-1.7 ...", 415), (b"MZ\x90\x00 exe", 415),
                      (b"<svg onload=alert(1)>", 415)]:
        with pytest.raises(HTTPException) as e:
            clean_image(bad)
        assert e.value.status_code == code


def test_rejects_truncated_jpeg():
    with pytest.raises(HTTPException) as e:
        clean_image(b"\xff\xd8\xff\xe0" + b"\x00" * 50)
    assert e.value.status_code == 400


def test_rejects_oversize_bytes():
    with pytest.raises(HTTPException) as e:
        clean_image(b"\xff\xd8\xff" + b"0" * (10 * 1024 * 1024 + 1))
    assert e.value.status_code == 413


def test_rejects_huge_dimensions():
    with pytest.raises(HTTPException) as e:
        clean_image(image_bytes("PNG", size=(5000, 10)))
    assert e.value.status_code == 400


def test_max_side_downscales():
    out = clean_image(image_bytes(size=(3000, 1500)), max_side=1000)
    assert max(out.width, out.height) == 1000


@pytest.mark.parametrize("name,expected", [
    ("../../etc/passwd", "passwd.jpg"), ("..\\..\\win.ini", "win.jpg"), ("leaf photo (1).png", "leaf_photo__1_.jpg"),
    (".hidden", "hidden.jpg"), (None, "leaf.jpg"), ("a" * 300 + ".jpg", "a" * 120 + ".jpg"),
])
def test_sanitize_filename(name, expected):
    out = sanitize_filename(name)
    assert out == expected
    assert "/" not in out and "\\" not in out and not out.startswith(".")


def test_decode_data_url():
    import base64

    raw = image_bytes()
    assert decode_data_url("data:image/jpeg;base64," + base64.b64encode(raw).decode()) == raw
    with pytest.raises(HTTPException):
        decode_data_url("data:image/jpeg;base64,@@@notbase64@@@")


@pytest.mark.parametrize("data,kind", [
    (webm_bytes(), "webm"), (b"OggS" + b"\0" * 10, "ogg"), (b"RIFF\0\0\0\0WAVEfmt ", "wav"), (b"ID3\x03", "mp3"),
    (b"\0\0\0\x18ftypmp42", "mp4"), (b"fLaC\0", "flac"),
])
def test_audio_sniffing(data, kind):
    assert sniff_audio(data) == kind


def test_audio_guard():
    assert check_audio(webm_bytes()) == "webm"
    for bad, code in [(b"", 400), (b"not audio at all", 415), (b"OggS" + b"\0" * (10 * 1024 * 1024 + 1), 413)]:
        with pytest.raises(HTTPException) as e:
            check_audio(bad)
        assert e.value.status_code == code
