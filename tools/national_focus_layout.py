"""Apply the German two-block layout without changing national tree contents."""
import german_focus_revision as german


def coordinates(records, nation):
    if nation=='GER':return german.COORDS
    out={r[0]:german.COORDS[r[0]] for r in records if r[0].startswith('C') or r[0]=='O2'}
    codes={r[0] for r in records}
    for prefix,x in [('I',22),('G',24),('M',26)]:
        for y,c in enumerate(sorted((c for c in codes if c.startswith(prefix)),key=lambda c:int(c[len(prefix):])),1):
            out[c]=(x,y)
    out.update({'T1':(10,5),'A1':(14,5)})
    for prefix,x in [('TA',9),('TB',11),('AA',13),('AB',15)]:
        for y,c in enumerate(sorted((c for c in codes if c.startswith(prefix)),key=lambda c:int(c[len(prefix):])),6):
            out[c]=(x,y)
    assert codes==out.keys(),codes-out.keys()
    return out


def hidden_links(node,nation):
    if nation=='GER':return german.HIDDEN_LINKS.get(node,[])
    return {'T1':['C00'],'A1':['C00'],'C70':['C00'],'O2':['I1'],'M2':['I1']}.get(node,[])
