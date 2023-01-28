import bs4
import json as j

class Globals:
    CSFD_URL = "https://www.csfd.cz"
    MOVIES_URL = "https://www.csfd.cz/film/"
    CREATORS_URL = "https://www.csfd.cz/tvurce/"
    CREATORS_SORT_URL = "https://www.csfd.cz/tvurce/<cid>?sort=<sort>"

def tojson(o):
    if type(o) not in [dict, list]:
        return o
    return j.dumps(o, indent=4, ensure_ascii=False)

def url_prepare(s, d):
    for k, v in d.items():
        s = s.replace("<" + str(k) + ">", str(v))
    return s

def url(s):
    if not s:
        return None
    if s.startswith("//"):
        return "https:" + s
    return s

def extract_id(u):
    return int(u.split("/")[2].split("-")[0])

def clean(s):
    s = s.replace("\n", " ").replace("\t", " ")
    return " ".join(s.split())

def soup(content):
    return bs4.BeautifulSoup(content, "lxml")

def is_tag(tag):
    return isinstance(tag, bs4.element.Tag)

def is_str(tag):
    return isinstance(tag, bs4.element.NavigableString)

def sel(s, select, _all=False):
    if _all:
        return s.select(select)
    return s.select_one(select)

def asel(s, select):
    return sel(s, select, _all=True)

def text(s, select=None, recursive=False, strip=True, rec_tags=None):
    tag = s if is_tag(s) and not select else sel(s, select)
    if recursive:
        tx = tag.text
    else:
        rec_tags = rec_tags or []
        is_in_rec_tags = lambda a: is_tag(a) and (rec_tags and a.name in rec_tags)
        filtered = [t for t in tag.contents if is_str(t) or is_in_rec_tags(t)]
        tx = "".join([x.text if is_tag(x) else x for x in filtered])
    return tx.strip() if strip else tx
