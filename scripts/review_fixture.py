"""Exact fictional profile used in the user's 49-PDF, 112-page audit."""
from app.models.catalog import demo_profile

def review_profile():
    p=demo_profile(True)
    p['sections']['personal'].update(maritalStatus='Never married',nationality='Indian')
    p['sections']['career'][0].update(income='INR 22 lakh per year',description='Designing accessible digital products with a multidisciplinary team.')
    p['sections']['education'][0]['specialization']='Human-centred design'
    p['sections']['astrology']={'birthDate':'1997-06-16','birthTime':'09:20','birthPlace':'Ahmedabad, Gujarat'}
    p['customSections']=[{'id':'custom-everyday','title':'Everyday life','fields':[{'label':'A good weekend','value':'A morning walk, cooking with family, and time with a good book.'}]}]
    return p
