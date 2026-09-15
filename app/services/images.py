"""Decode and re-encode all images. Never trust extensions, MIME headers or metadata."""
import base64
import binascii
import io
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError
from app.models.profile import ValidationError

MAX_IMAGE_BYTES = 8 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 24_000_000


def normalize_image(data):
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValidationError('Choose a JPEG, PNG or WebP photo under 8 MB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                if source.format not in ('JPEG', 'PNG', 'WEBP'):
                    raise ValidationError('Only JPEG, PNG and WebP photos are supported.')
                if getattr(source, 'is_animated', False):
                    raise ValidationError('Please use a still photo.')
                source.load()
                photo = ImageOps.exif_transpose(source)
                photo.thumbnail((1600, 1600))
                if photo.mode in ('RGBA', 'LA') or 'transparency' in photo.info:
                    rgba = photo.convert('RGBA')
                    background = Image.new('RGBA', rgba.size, 'white')
                    background.alpha_composite(rgba)
                    photo = background.convert('RGB')
                else:
                    photo = photo.convert('RGB')
                photo.info.clear()
                out = io.BytesIO()
                photo.save(out, format='JPEG', quality=88, optimize=True)
                return 'data:image/jpeg;base64,' + base64.b64encode(out.getvalue()).decode('ascii')
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning, ValueError) as exc:
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError('This image could not be read. Please choose another photo.') from None


def normalize_data_image(value):
    if not isinstance(value, str) or not value.startswith(('data:image/jpeg;base64,', 'data:image/png;base64,', 'data:image/webp;base64,')) or len(value) > 12 * 1024 * 1024:
        raise ValidationError('Invalid photo. External image URLs are not accepted.')
    try:
        binary = base64.b64decode(value.split(',', 1)[1], validate=True)
    except (binascii.Error, ValueError):
        raise ValidationError('The photo data is incomplete.') from None
    return normalize_image(binary)
