import re
from dataclasses import dataclass
from datetime import date
from .catalog import SECTIONS, TEMPLATES, empty_profile
from .migrations import migrate_profile


class ValidationError(ValueError):
    pass


def clean_text(value, limit=200):
    if not isinstance(value, str):
        raise ValidationError('Please use text for profile details.')
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value).strip()
    if len(value) > limit:
        raise ValidationError(f'A field is too long. Please keep it under {limit} characters.')
    return value


@dataclass
class Profile:
    data: dict

    @classmethod
    def parse(cls, raw, validate_photos=True):
        try:
            raw = migrate_profile(raw)
        except (ValueError, TypeError, AttributeError):
            raise ValidationError('This saved draft could not be upgraded. Keep your original backup.') from None
        if not isinstance(raw, dict) or raw.get('schemaVersion') != 2:
            raise ValidationError('This draft format is not supported. Please use a version 1 or 2 backup.')
        p = empty_profile()
        if raw.get('gender', '') not in ('', 'male', 'female'):
            raise ValidationError('Please choose a valid gender.')
        p['gender'] = raw.get('gender', '')
        for key, allowed in [('language', ['en', 'hi']), ('template', [t['id'] for t in TEMPLATES]),
                             ('forWhom', ['myself', 'son', 'daughter', 'sibling', 'relative', 'client', 'other'])]:
            if raw.get(key) not in allowed:
                raise ValidationError(f'Please choose a valid {key}.')
            p[key] = raw[key]
        from .collection import SACRED_ART
        presentation = raw.get('presentation', {})
        if not isinstance(presentation, dict):
            raise ValidationError('Invalid design options.')
        sacred = presentation.get('sacred_art', 'default')
        direction = presentation.get('direction', 'auto')
        salutation = presentation.get('salutation', False)
        if sacred not in ['default', *SACRED_ART] or direction not in ('auto', 'ltr', 'rtl') or not isinstance(salutation, bool):
            raise ValidationError('Please choose valid design options.')
        p['presentation'] = dict(sacred_art=sacred, direction=direction, salutation=salutation)
        sections = raw.get('sections', {})
        if not isinstance(sections, dict):
            raise ValidationError('Invalid sections in this draft.')
        total = 0
        for spec in SECTIONS:
            value = sections.get(spec['key'], [] if spec.get('repeat') else {})
            entries = value if spec.get('repeat') else [value]
            if not isinstance(entries, list) or len(entries) > 12:
                raise ValidationError('Each section supports up to 12 entries.')
            normalized = []
            for entry in entries:
                if not isinstance(entry, dict):
                    raise ValidationError('Invalid entry in this draft.')
                row = {}
                for field in spec['fields']:
                    text = clean_text(entry.get(field['key'], ''), field['limit'])
                    if text and field['key'] == 'age' and (not text.isascii() or not text.isdigit() or not 18 <= int(text) <= 120):
                        raise ValidationError('Age must be between 18 and 120. This tool is for adults.')
                    if text and field['type'] == 'email' and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', text):
                        raise ValidationError('Please check the email address.')
                    if text and field['type'] == 'date':
                        try:
                            born = date.fromisoformat(text)
                            today = date.today()
                            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                            if not 18 <= age <= 120:
                                raise ValueError()
                        except ValueError:
                            raise ValidationError('Please enter a valid adult date of birth.')
                    row[field['key']] = text
                    total += len(text)
                normalized.append(row)
            p['sections'][spec['key']] = normalized if spec.get('repeat') else normalized[0]
        custom = raw.get('customSections', [])
        if not isinstance(custom, list) or len(custom) > 8:
            raise ValidationError('You can add up to 8 custom sections.')
        ids = set()
        for section in custom:
            if not isinstance(section, dict):
                raise ValidationError('Invalid custom section.')
            sid = clean_text(section.get('id', ''), 60)
            if not re.fullmatch(r'custom-[a-zA-Z0-9-]+', sid) or sid in ids:
                raise ValidationError('Invalid custom section ID.')
            ids.add(sid)
            fields = section.get('fields', [])
            if not isinstance(fields, list) or len(fields) > 12:
                raise ValidationError('A custom section supports up to 12 fields.')
            title = clean_text(section.get('title', ''), 120)
            rows = []
            for row in fields:
                if not isinstance(row, dict):
                    raise ValidationError('Invalid custom field.')
                label = clean_text(row.get('label', ''), 120)
                value = clean_text(row.get('value', ''), 3000)
                total += len(label) + len(value)
                rows.append(dict(label=label, value=value))
            p['customSections'].append(dict(id=sid, title=title, fields=rows))
        if total > 40000:
            raise ValidationError('This profile is too long. Please keep the total under 40,000 characters.')
        for key in ['hiddenSections', 'hiddenFields']:
            values = raw.get(key, [])
            if not isinstance(values, list) or len(values) > 300:
                raise ValidationError('Invalid visibility choices.')
            p[key] = [clean_text(v, 120) for v in values]
        photos = raw.get('photos', [])
        if not isinstance(photos, list) or len(photos) > 5:
            raise ValidationError('Please choose up to five photos.')
        if validate_photos:
            from app.services.images import normalize_data_image
            p['photos'] = [normalize_data_image(photo) for photo in photos]
        else:
            p['photos'] = photos
        return cls(p)

    def document(self):
        p, result = self.data, []
        lang = p['language']
        hidden = set(p['hiddenFields'])
        for spec in SECTIONS:
            key = spec['key']
            if key in p['hiddenSections']:
                continue
            values = p['sections'][key]
            entries = values if spec.get('repeat') else [values]
            groups = []
            for i, entry in enumerate(entries):
                rows = []
                for field in spec['fields']:
                    fid = f'{key}.{i}.{field["key"]}'
                    value = entry.get(field['key'], '')
                    if value and fid not in hidden and not (key == 'personal' and field['key'] == 'name'):
                        rows.append(dict(key=field['key'], label=field['label'][lang], value=value, prose=field['type'] == 'textarea'))
                if rows:
                    groups.append(rows)
            if groups:
                result.append(dict(title=spec['title'][lang], groups=groups, key=key))
        for section in p['customSections']:
            if section['id'] in p['hiddenSections']:
                continue
            rows = [dict(label=f['label'], value=f['value'], prose=False) for i, f in enumerate(section['fields'])
                    if f['value'] and f'{section["id"]}.{i}' not in hidden]
            if rows:
                result.append(dict(title=section['title'] or ('More about me' if lang == 'en' else 'अन्य विवरण'), groups=[rows], key=section['id']))
        personal = p['sections']['personal']
        name_visible = 'personal' not in p['hiddenSections'] and 'personal.0.name' not in hidden
        name = personal.get('name', '') if name_visible else ''
        photos = [] if 'photos' in p['hiddenSections'] else p['photos']
        return dict(name=name, sections=result, photos=photos, language=lang, presentation=p.get('presentation', {}), template=p['template'],illustrated=p['template'].startswith('figma-'),
                    eyebrow='A personal introduction' if lang == 'en' else 'एक व्यक्तिगत परिचय')
