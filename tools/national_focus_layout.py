"""Compact row spacing, with country-specific extended technology schedules."""
import re
import german_focus_revision as german

def coordinates(records,nation):
    if nation=='GER':return german.COORDS
    out={r[0]:german.COORDS[r[0]] for r in records if r[0].startswith(('C','P')) or r[0]=='O2'}
    upper=max(int(re.search(r'\d+',r[0])[0]) for r in records if r[0][0] in ('I','G','M'))
    lower=max(5,upper+1)
    for r in records:
        n=r[0]
        if n in out:continue
        p=n[0];i=int(n[1:])
        x={'I':22,'G':24,'M':26,'T':9,'H':11,'W':13,'A':15,'S':19,'B':21,'R':23}[p]
        out[n]=(x,i if p in ('I','G','M') else lower+i-1)
    return out

def hidden_links(node,nation):
    if nation=='GER':return german.HIDDEN_LINKS.get(node,[])
    # Draw lower branches exactly like the tank branches, with no lines
    # crossing their first focuses or descending from the upper electronics.
    if node in ('C70','O2'):return german.HIDDEN_LINKS.get(node,[])
    if re.fullmatch('[THAWSBR]1',node):return ['C00']
    if re.fullmatch(r'[AWSBR]\d+',node):return ['C25']
    return []
