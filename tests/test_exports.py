import io
import os
import zipfile
import pytest
from pypdf import PdfReader
from app.models.catalog import demo_profile, TEMPLATES

pytestmark = pytest.mark.skipif(os.getenv('RUN_EXPORT_TESTS') != '1', reason='Set RUN_EXPORT_TESTS=1 for real Chromium integration')

@pytest.mark.parametrize('template',[t['id'] for t in TEMPLATES])
def test_real_pdf(client,template):
    data=demo_profile();data['template']=template
    data['sections']['contact']['phone']='SECRET-PHONE'
    data['hiddenFields']=['contact.0.phone']
    result=client.post('/api/export/pdf',json=data)
    assert result.status_code==200,result.json
    pdf=PdfReader(io.BytesIO(result.data))
    assert 1<=len(pdf.pages)<=3
    text=''.join(p.extract_text() for p in pdf.pages)
    assert 'Aarav Mehta' in text
    assert 'SECRET-PHONE' not in text
    assert abs(float(pdf.pages[0].mediabox.width)-595.3)<2
    assert len(result.data)<2*1024*1024
    assert any('/Font' in p['/Resources'] for p in pdf.pages)


def test_long_hindi_pdf_and_images(client):
    data=demo_profile();data['language']='hi';data['sections']['personal']['name']='आरव मेहता'
    data['sections']['education']=[{'degree':f'Qualification {i}','institution':'A university with a very long institution name'} for i in range(12)]
    data['sections']['about']['introduction']='मुझे किताबें पढ़ना और यात्रा करना पसंद है। '*90
    result=client.post('/api/export/pdf',json=data)
    assert result.status_code==200,result.json
    pdf=PdfReader(io.BytesIO(result.data));assert len(pdf.pages)>1
    text=''.join(p.extract_text() for p in pdf.pages)
    assert 'Qualification 11' in text
    assert 'आरव' in text
    image=client.post('/api/export/jpg',json=data)
    assert image.status_code==200,image.json
    assert image.mimetype=='application/zip'
    with zipfile.ZipFile(io.BytesIO(image.data)) as files:
        assert len(files.namelist())==len(pdf.pages)
        assert all(files.read(n).startswith(b'\xff\xd8') for n in files.namelist())


def test_png_export(client):
    data=demo_profile();data['sections']['family']={};data['sections']['partner']={}
    result=client.post('/api/export/png',json=data)
    assert result.status_code==200,result.json
    assert result.data.startswith((b'\x89PNG',b'PK'))


def test_full_bleed_and_keep_section_together(client):
    import pypdfium2 as pdfium
    data = demo_profile(); data['template'] = 'ivory'
    data['sections']['personal']['city'] = 'Bengaluru, Karnataka, India — ' * 5
    data['sections']['personal']['nativePlace'] = 'Ahmedabad, Gujarat — ' * 7
    data['sections']['education'] = [{'degree': f'EDUCATION_ENTRY_{i:02d}', 'institution': 'National Institute of Design, Ahmedabad'} for i in range(12)]
    result = client.post('/api/export/pdf', json=data)
    assert result.status_code == 200, result.json
    reader = PdfReader(io.BytesIO(result.data))
    texts = [page.extract_text() for page in reader.pages]
    first = next(i for i, text in enumerate(texts) if 'EDUCATION_ENTRY_00' in text)
    last = next(i for i, text in enumerate(texts) if 'EDUCATION_ENTRY_11' in text)
    assert first == last, 'The education section must stay on one page when it fits.'
    assert first > 0, 'The whole section should move after the introduction page.'
    with pdfium.PdfDocument(result.data) as pdf:
        for i in range(len(pdf)):
            page = pdf[i]; bitmap = page.render(scale=.5); image = bitmap.to_pil().convert('RGB')
            # The ivory paper reaches every corner, including otherwise empty pages.
            for x, y in [(1,1),(image.width-2,1),(1,image.height-2),(image.width-2,image.height-2)]:
                pixel = image.getpixel((x,y))
                assert all(abs(a-b)<=3 for a,b in zip(pixel,(251,248,238))), (i,pixel)
            bitmap.close(); page.close()
