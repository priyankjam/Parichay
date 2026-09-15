import pytest
from app.models.catalog import empty_profile
from app.models.profile import Profile, ValidationError


def test_gender_is_optional_and_survives_normalization():
    old = empty_profile()
    old.pop('gender')
    assert Profile.parse(old).data['gender'] == ''
    for gender in ('male', 'female'):
        profile = empty_profile()
        profile['gender'] = gender
        parsed = Profile.parse(profile)
        assert parsed.data['gender'] == gender
        assert not parsed.document()['sections']
        assert not parsed.data['photos']


def test_invalid_gender_rejected():
    profile = empty_profile()
    profile['gender'] = '<script>'
    with pytest.raises(ValidationError):
        Profile.parse(profile)
