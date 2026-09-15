/** Version 1 → 2: preserve family content and original disclosure choices. */
export function migrateProfile(raw) {
  if (!raw || raw.schemaVersion !== 1) return raw;
  const p = structuredClone(raw);
  const family = p.sections?.family ?? [];
  if (!Array.isArray(family) || family.length > 12 ||
      ![p.hiddenFields, p.hiddenSections, p.customSections].every(Array.isArray)) {
    throw new Error('This saved family data could not be upgraded. Keep your original backup.');
  }
  const relations = {father:'father',dad:'father',papa:'father','पिता':'father','पिताजी':'father',
    mother:'mother',mom:'mother',mum:'mother','माता':'mother','माँ':'mother',
    siblings:'siblings',sibling:'siblings',brother:'siblings',sister:'siblings','भाई':'siblings','बहन':'siblings','भाई-बहन':'siblings'};
  const oldFields = [['relationship','Relationship','रिश्ता'],['name','Name','नाम'],
    ['occupation','Occupation','पेशा'],['description','Details','विवरण']];
  const next = {father:'', mother:'', siblings:''}, legacy = [];
  family.forEach((row, i) => {
    if (!row || typeof row !== 'object' || Array.isArray(row) || Object.values(row).some(v => typeof v !== 'string')) throw new Error('Invalid saved family entry.');
    const target = relations[(row.relationship || '').trim().toLowerCase()];
    const hidden = oldFields.some(([key]) => p.hiddenFields.includes(`family.${i}.${key}`));
    if (target && !hidden) {
      const value = ['name','occupation','description'].map(key => row[key]).filter(Boolean).join('\n');
      next[target] = [next[target],value].filter(Boolean).join('\n\n');
    } else {
      oldFields.forEach(([key,en,hi]) => {
        if (row[key]) legacy.push({field:{label:p.language==='hi'?hi:en,value:row[key]},hidden:p.hiddenFields.includes(`family.${i}.${key}`)});
      });
    }
  });
  p.hiddenFields = p.hiddenFields.filter(key => !key.startsWith('family.'));
  const ids = new Set(p.customSections.map(s=>s.id));
  for (let start=0;start<legacy.length;start+=12) {
    let id=`custom-legacy-family-${start/12}`;
    while(ids.has(id)) id+='-old';
    ids.add(id);
    const chunk=legacy.slice(start,start+12);
    p.customSections.push({id,title:p.language==='hi'?'पहले सहेजे गए पारिवारिक विवरण':'Earlier family details',fields:chunk.map(x=>x.field)});
    chunk.forEach((x,i)=>{if(x.hidden)p.hiddenFields.push(`${id}.${i}`);});
    if(p.hiddenSections.includes('family'))p.hiddenSections.push(id);
  }
  p.sections.family=next;p.schemaVersion=2;
  return p;
}
