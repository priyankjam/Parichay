import copy
import pytest
from app.models.catalog import empty_profile, demo_profile, TEMPLATES
from app.models.profile import Profile, ValidationError


def test_sensitive_fields_not_required():
    profile = Profile.parse(empty_profile())
    assert profile.document()['sections'] == []


def test_hidden_information_removed_from_document():
    raw = demo_profile()
    raw['sections']['career'][0]['income'] = 'CONFIDENTIAL INCOME'
    raw['sections']['culture']['caste'] = 'CONFIDENTIAL CASTE'
    raw['hiddenFields'] = ['career.0.income', 'personal.0.name']
    raw['hiddenSections'] = ['culture']
    doc = Profile.parse(raw).document()
    assert not doc['name']
    assert 'CONFIDENTIAL' not in str(doc)
    assert 'Product Designer' in str(doc)


def test_template_switch_preserves_profile():
    raw = demo_profile()
    for theme in TEMPLATES:
        changed = copy.deepcopy(raw)
        changed['template'] = theme['id']
        result = Profile.parse(changed).document()
        assert result['template'] == theme['id']
        assert result['name'] == 'Aarav Mehta'
        assert 'National Institute of Design' in str(result)


def test_hindi_labels_and_custom_fields():
    raw = demo_profile(); raw['language'] = 'hi'; raw['sections']['personal']['name'] = 'आरव मेहता'
    raw['customSections'] = [{'id': 'custom-test', 'title': 'विशेष जानकारी', 'fields': [{'label': 'भाषाएँ', 'value': 'हिन्दी, मराठी'}]}]
    result = Profile.parse(raw).document()
    assert result['name'] == 'आरव मेहता'
    assert 'व्यक्तिगत विवरण' in str(result)
    assert 'हिन्दी, मराठी' in str(result)


@pytest.mark.parametrize('mutation', [
    lambda p: p.update(schemaVersion=99),
    lambda p: p.update(template='../secret'),
    lambda p: p['sections']['personal'].update(age='17'),
    lambda p: p['sections']['personal'].update(age='999'),
    lambda p: p['sections']['contact'].update(email='not-an-email'),
    lambda p: p['sections']['astrology'].update(birthDate='2030-01-01'),
    lambda p: p['sections'].update(education=[{}]*13),
    lambda p: p['sections']['about'].update(introduction='x'*6001),
    lambda p: p.update(hiddenSections='culture'),
    lambda p: p.update(photos=['https://example.com/photo.png']),
    lambda p: p.update(customSections=[{'id':'<script>', 'fields':[]}]),
])
def test_invalid_profiles_rejected(mutation):
    raw = empty_profile(); mutation(raw)
    with pytest.raises(ValidationError): Profile.parse(raw)


def test_unknown_keys_not_retained():
    raw = empty_profile(); raw['admin'] = True; raw['sections']['personal']['secret'] = 'not a field'
    result = Profile.parse(raw).data
    assert 'admin' not in result
    assert 'secret' not in result['sections']['personal']


def test_family_three_fields_and_labels():
    raw = empty_profile()
    raw['sections']['family'] = {'father': 'Raj, architect', 'mother': 'Neeta, teacher', 'siblings': 'One sister'}
    parsed = Profile.parse(raw)
    assert not isinstance(parsed.data['sections']['family'], list)
    rows = parsed.document()['sections'][0]['groups'][0]
    assert [row['label'] for row in rows] == ['Father', 'Mother', 'Siblings']
    raw['hiddenFields'] = ['family.0.mother']
    assert 'Neeta' not in str(Profile.parse(raw).document())


def test_old_family_draft_migrates_without_changing_original():
    raw = empty_profile(); raw['schemaVersion'] = 1
    raw['sections']['family'] = [
        {'relationship': 'Father', 'name': 'Raj', 'occupation': 'Architect', 'description': 'Loves music'},
        {'relationship': 'Mother', 'name': 'Neeta', 'occupation': 'Teacher'},
        {'relationship': 'Sister', 'name': 'Mira', 'description': 'Studying design'},
    ]
    parsed = Profile.parse(raw)
    assert parsed.data['schemaVersion'] == 2
    assert parsed.data['sections']['family']['father'] == 'Raj\nArchitect\nLoves music'
    assert 'Mira' in parsed.data['sections']['family']['siblings']
    assert isinstance(raw['sections']['family'], list)


def test_old_hidden_family_values_are_preserved_but_stay_hidden():
    raw = empty_profile(); raw['schemaVersion'] = 1
    raw['sections']['family'] = [{'relationship': 'Father', 'name': 'PRIVATE NAME', 'occupation': 'Architect'},
                                  {'relationship': 'Guardian', 'name': 'Alex', 'description': 'Supportive family'}]
    raw['hiddenFields'] = ['family.0.name']
    parsed = Profile.parse(raw)
    assert 'PRIVATE NAME' in str(parsed.data)
    assert 'PRIVATE NAME' not in str(parsed.document())
    assert 'Architect' in str(parsed.document()) and 'Alex' in str(parsed.document())
    raw['hiddenSections'] = ['family']
    assert not Profile.parse(raw).document()['sections']
