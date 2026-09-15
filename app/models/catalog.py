"""One field registry feeds the editor and normalized document builder."""


def field(key, en, hi, kind='text', sensitive=False, limit=200):
    return dict(key=key, label={'en': en, 'hi': hi}, type=kind, sensitive=sensitive, limit=limit)


SECTIONS = [
    dict(key='personal', title={'en': 'Personal details', 'hi': 'व्यक्तिगत विवरण'}, fields=[
        field('name', 'Full name', 'पूरा नाम'), field('age', 'Age', 'उम्र', 'number'),
        field('height', 'Height', 'कद'), field('city', 'Current city', 'वर्तमान शहर'),
        field('nativePlace', 'Native place', 'मूल निवास'), field('motherTongue', 'Mother tongue', 'मातृभाषा'),
        field('maritalStatus', 'Marital status', 'वैवाहिक स्थिति'), field('nationality', 'Nationality', 'राष्ट्रीयता')]),
    dict(key='education', repeat=True, title={'en': 'Education', 'hi': 'शिक्षा'}, fields=[
        field('degree', 'Qualification', 'योग्यता'), field('institution', 'Institution', 'संस्थान'),
        field('specialization', 'Specialization', 'विशेषज्ञता'), field('year', 'Year', 'वर्ष')]),
    dict(key='career', repeat=True, title={'en': 'Career', 'hi': 'करियर'}, fields=[
        field('role', 'Profession / role', 'पेशा / पद'), field('company', 'Company / business', 'कंपनी / व्यवसाय'),
        field('location', 'Work location', 'कार्यस्थल'), field('income', 'Income (include currency & period)', 'आय (मुद्रा और अवधि सहित)', sensitive=True),
        field('description', 'A little about your work', 'आपके काम के बारे में', 'textarea', limit=3000)]),
    dict(key='family', title={'en': 'Family', 'hi': 'परिवार'}, fields=[
        field('father', 'Father', 'पिता', 'textarea', limit=6000),
        field('mother', 'Mother', 'माता', 'textarea', limit=6000),
        field('siblings', 'Siblings', 'भाई-बहन', 'textarea', limit=6000)]),
    dict(key='culture', title={'en': 'Culture & traditions', 'hi': 'संस्कृति और परंपराएँ'}, fields=[
        field('religion', 'Religion', 'धर्म', sensitive=True), field('community', 'Community', 'समुदाय', sensitive=True),
        field('caste', 'Caste', 'जाति', sensitive=True), field('subCaste', 'Sub-caste', 'उपजाति', sensitive=True),
        field('gotra', 'Gotra', 'गोत्र', sensitive=True)]),
    dict(key='astrology', title={'en': 'Birth & astrology', 'hi': 'जन्म और ज्योतिष'}, fields=[
        field('birthDate', 'Date of birth', 'जन्म तिथि', 'date', True), field('birthTime', 'Birth time', 'जन्म समय', 'time', True),
        field('birthPlace', 'Birthplace', 'जन्म स्थान', sensitive=True), field('rashi', 'Rashi', 'राशि', sensitive=True),
        field('nakshatra', 'Nakshatra', 'नक्षत्र', sensitive=True), field('manglik', 'Manglik (if relevant)', 'मांगलिक (यदि प्रासंगिक हो)', sensitive=True)]),
    dict(key='about', title={'en': 'A little about me', 'hi': 'मेरे बारे में'}, fields=[
        field('introduction', 'Your introduction', 'आपका परिचय', 'textarea', limit=6000),
        field('interests', 'Interests & hobbies', 'रुचियाँ और शौक', 'textarea', limit=2000)]),
    dict(key='partner', title={'en': 'What I value in a partner', 'hi': 'जीवनसाथी से अपेक्षाएँ'}, fields=[
        field('preferences', 'What matters to you?', 'आपके लिए क्या महत्वपूर्ण है?', 'textarea', limit=4000)]),
    dict(key='contact', title={'en': 'Get in touch', 'hi': 'संपर्क'}, fields=[
        field('name', 'Contact person', 'संपर्क व्यक्ति', sensitive=True), field('relationship', 'Relationship to you', 'आपसे संबंध', sensitive=True),
        field('phone', 'Phone / WhatsApp', 'फ़ोन / व्हाट्सऐप', 'tel', True), field('email', 'Email', 'ईमेल', 'email', True)])
]

TEMPLATES = [
    dict(id='editorial', name='Minimal Editorial', hi='मिनिमल एडिटोरियल', caption='A quiet kind of confidence', color='#2f4945', family='Minimal'),
    dict(id='professional', name='Modern Professional', hi='मॉडर्न प्रोफेशनल', caption='Clear, considered, contemporary', color='#344e6a', family='Modern'),
    dict(id='warm', name='Warm Indian', hi='वॉर्म इंडियन', caption='Rooted in warmth', color='#a95739', family='Warm'),
    dict(id='traditional', name='Elegant Traditional', hi='एलिगेंट ट्रेडिशनल', caption='Timeless, with a personal touch', color='#763c43', family='Traditional'),
    dict(id='ivory', name='Premium Ivory', hi='प्रीमियम आइवरी', caption='Understated and beautifully balanced', color='#7a6848', family='Premium')
]


from app.models.designs import FIGMA_DESIGNS
TEMPLATES.extend(FIGMA_DESIGNS)
from app.models.collection import COLLECTION
TEMPLATES.extend(COLLECTION)
for template in TEMPLATES:
    template['thumbnail'] = f"/static/artwork/thumbnails/{template['id']}.webp"

def empty_profile():
    return dict(schemaVersion=2, forWhom='myself', gender='', language='en', template='editorial',
                sections={s['key']: ([{}] if s.get('repeat') else {}) for s in SECTIONS},
                hiddenSections=[], hiddenFields=[], customSections=[], photos=[],
                presentation=dict(sacred_art='default', direction='ltr', salutation=False))


def demo_profile(include_photo=False):
    p = empty_profile()
    p['sections'].update({
        'personal': dict(name='Aarav Mehta', age='29', height='178 cm', city='Bengaluru, India', nativePlace='Ahmedabad', motherTongue='Gujarati'),
        'education': [dict(degree='M.Des, Interaction Design', institution='National Institute of Design', year='2019'), dict(degree='B.Des, Communication Design', institution='Srishti Institute', year='2017')],
        'contact': dict(name='Aarav Mehta', email='aarav@example.com'),
        'career': [dict(role='Product Designer', company='Independent design studio', location='Bengaluru')],
        'family': dict(father='Rajesh Mehta · Architect', mother='Neeta Mehta · Teacher',
                       siblings='One younger sister, pursuing her postgraduate studies.'),
        'about': dict(introduction='A designer by profession and a curious soul at heart. I find joy in slow Sunday mornings, a good book, and discovering a new trail. I believe in building a life filled with kindness, laughter and a little adventure.', interests='Photography · Hiking · Indian classical music · Coffee'),
        'partner': dict(preferences='Someone kind and curious, who values an equal partnership and finds joy in the everyday.')
    })
    if include_photo:
        # Public sample artwork is opt-in and never assigned to an empty user draft.
        import base64
        from pathlib import Path
        portrait = Path(__file__).resolve().parents[1] / 'static/artwork/demo-portrait.jpg'
        p['photos'] = ['data:image/jpeg;base64,' + base64.b64encode(portrait.read_bytes()).decode('ascii')]
    return p
