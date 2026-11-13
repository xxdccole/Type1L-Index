def tidy_title(c):
    t=clean(c.get('title'));st=c.get('subtitle') or []
    if st and clean(st[0]) and clean(st[0]).lower() not in t.lower(): t=t.rstrip(':')+': '+clean(st[0])
    return t
