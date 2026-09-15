/** Stable choices; the existing plain-text field remains compatible with saved drafts. */
export const hobbies = [
 ['reading','Reading','पढ़ना'],['travel','Travelling','यात्रा'],['music','Music','संगीत'],
 ['cooking','Cooking','खाना बनाना'],['fitness','Fitness','फ़िटनेस'],['yoga','Yoga','योग'],
 ['hiking','Hiking','पैदल यात्रा'],['photography','Photography','फ़ोटोग्राफ़ी'],
 ['movies','Movies','फ़िल्में'],['dancing','Dancing','नृत्य'],['art','Art & painting','कला और चित्रकारी'],
 ['gardening','Gardening','बागवानी'],['sports','Sports','खेल'],['writing','Writing','लेखन'],
 ['volunteering','Volunteering','समाज सेवा'],['meditation','Meditation','ध्यान']
];
export const hobbyLabel=(value,language)=>{const item=hobbies.find(h=>h.includes(value));return item?item[language==='hi'?2:1]:value;};
export const selectedHobbies=value=>[...new Set((value||'').split(/\s*[·,\n]\s*/).map(v=>v.trim()).filter(Boolean).map(v=>hobbies.find(h=>h.includes(v))?.[0]||v))];
export const hobbyText=(values,language)=>values.map(v=>hobbyLabel(v,language)).join(' · ');
