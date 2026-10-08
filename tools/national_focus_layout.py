"""Compact layout shared by all seven national technology trees."""
import german_focus_revision as german

def coordinates(records,nation):
    codes={r[0] for r in records}
    assert codes<=german.COORDS.keys(),codes-german.COORDS.keys()
    return {n:german.COORDS[n] for n in codes}

def hidden_links(node,nation):
    return german.HIDDEN_LINKS.get(node,[])
