"""Upgrade guest drafts without discarding legacy family values or disclosure choices."""
from copy import deepcopy

RELATIONS = {
    'father': 'father', 'dad': 'father', 'papa': 'father', 'पिता': 'father', 'पिताजी': 'father',
    'mother': 'mother', 'mom': 'mother', 'mum': 'mother', 'माता': 'mother', 'माँ': 'mother',
    'siblings': 'siblings', 'sibling': 'siblings', 'brother': 'siblings', 'sister': 'siblings',
    'भाई': 'siblings', 'बहन': 'siblings', 'भाई-बहन': 'siblings',
}
LEGACY_FIELDS = [('relationship', 'Relationship', 'रिश्ता'), ('name', 'Name', 'नाम'),
                 ('occupation', 'Occupation', 'पेशा'), ('description', 'Details', 'विवरण')]


def migrate_profile(raw):
    if not isinstance(raw, dict) or raw.get('schemaVersion') != 1:
        return raw
    result = deepcopy(raw)
    family = result.get('sections', {}).get('family', [])
    if not isinstance(family, list) or len(family) > 12:
        raise ValueError('The saved family data could not be upgraded.')
    hidden = result.get('hiddenFields', [])
    hidden_sections = result.get('hiddenSections', [])
    custom = result.get('customSections', [])
    if not all(isinstance(v, list) for v in (hidden, hidden_sections, custom)):
        raise ValueError('Invalid saved visibility choices.')
    new_family = dict(father='', mother='', siblings='')
    legacy = []
    for i, row in enumerate(family):
        if not isinstance(row, dict) or any(not isinstance(v, str) for v in row.values()):
            raise ValueError('The saved family entry is invalid.')
        target = RELATIONS.get(row.get('relationship', '').strip().lower())
        partially_hidden = any(f'family.{i}.{key}' in hidden for key, _, _ in LEGACY_FIELDS)
        if target and not partially_hidden:
            value = '\n'.join(row.get(key, '') for key in ('name', 'occupation', 'description') if row.get(key))
            new_family[target] = '\n\n'.join(v for v in (new_family[target], value) if v)
        else:
            for key, en, hi in LEGACY_FIELDS:
                if row.get(key):
                    legacy.append((dict(label=hi if result.get('language') == 'hi' else en, value=row[key]),
                                   f'family.{i}.{key}' in hidden))
    result['hiddenFields'] = [key for key in hidden if not key.startswith('family.')]
    ids = {s.get('id') for s in custom if isinstance(s, dict)}
    for start in range(0, len(legacy), 12):
        serial = start // 12
        sid = f'custom-legacy-family-{serial}'
        while sid in ids:
            sid += '-old'
        ids.add(sid)
        chunk = legacy[start:start + 12]
        custom.append(dict(id=sid, title='पहले सहेजे गए पारिवारिक विवरण' if result.get('language') == 'hi'
                           else 'Earlier family details', fields=[field for field, _ in chunk]))
        result['hiddenFields'].extend(f'{sid}.{i}' for i, (_, is_hidden) in enumerate(chunk) if is_hidden)
        if 'family' in hidden_sections:
            hidden_sections.append(sid)
    result['sections']['family'] = new_family
    result['customSections'] = custom
    result['schemaVersion'] = 2
    return result
