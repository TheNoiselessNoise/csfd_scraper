import bs4
import json
import codecs
from base64 import b64encode

class Globals:
    CSFD_URL = "https://www.csfd.cz"
    MOVIES_URL = "https://www.csfd.cz/film/"
    CREATORS_URL = "https://www.csfd.cz/tvurce/"
    CREATORS_SORT_URL = "https://www.csfd.cz/tvurce/<cid>?sort=<sort>"
    USERS_URL = "https://www.csfd.cz/uzivatel/"
    NEWS_URL = "https://www.csfd.cz/novinky/"
    NEWS_LIST_URL = "https://www.csfd.cz/novinky/?page=<page>"
    MOST_FAVORITE_USERS_URL = "https://www.csfd.cz/uzivatele/"
    MOST_ACTIVE_USERS_URL = "https://www.csfd.cz/uzivatele/nejaktivnejsi/?period=<sort>&country=<origin>"
    ALL_MOST_ACTIVE_USERS_URL = "https://www.csfd.cz/uzivatele/nejaktivnejsi/?period=<sort>"
    SEARCH_AUTOCOMPLETE_URL = "https://www.csfd.cz/api/autocomplete/?s=<type>&q=<search>"
    SEARCH_MOVIES_URL = "https://www.csfd.cz/podrobne-vyhledavani/?page=<page>&sort=<sort>&searchParams=<params>"
    SEARCH_CREATORS_URL = "https://www.csfd.cz/podrobne-vyhledavani/tvurci/?page=<page>&sort=<sort>&searchParams=<params>"
    TEXT_SEARCH_URL = "https://www.csfd.cz/hledat/?pageFilms=<page>&pageSeries=<page>&pageCreators=<page>&pageUsers=<page>&q=<search>"
    TEXT_SEARCH_MOVIES_URL = "https://www.csfd.cz/hledat/?pageFilms=<page>&q=<search>"
    TEXT_SEARCH_SERIES_URL = "https://www.csfd.cz/hledat/?pageSeries=<page>&q=<search>"
    TEXT_SEARCH_CREATORS_URL = "https://www.csfd.cz/hledat/?pageCreators=<page>&q=<search>"
    TEXT_SEARCH_USERS_URL = "https://www.csfd.cz/hledat/?pageUsers=<page>&q=<search>"
    DVDS_MONTHLY_ROOT_URL = "https://www.csfd.cz/dvd/"
    DVDS_YEARLY_URL = "https://www.csfd.cz/dvd/rocne/"
    BLURAYS_MONTHLY_URL = "https://www.csfd.cz/bluray/"
    BLURAYS_YEARLY_URL = "https://www.csfd.cz/bluray/rocne/"
    USER_RATINGS_URL = "https://www.csfd.cz/uzivatel/<uid>/hodnoceni/"
    USER_REVIEWS_URL = "https://www.csfd.cz/uzivatel/<uid>/recenze/"

def encode_params(params):
    params_raw = json.dumps(params, separators=(',', ':')).encode('ascii')
    return codecs.encode(b64encode(params_raw).decode('ascii'), 'rot_13')

def tojson(o):
    if type(o) not in [dict, list]:
        return o
    return json.dumps(o, indent=4, ensure_ascii=False)

def toint(s):
    if type(s) is str:
        return int("".join([c for c in s if c.isdigit()]))
    return s

def url_prepare(s, d):
    for k, v in d.items():
        s = s.replace("<" + str(k) + ">", str(v))
    return s

def url_params(s, params):
    first = True
    for k, v in params.items():
        if v is None:
            continue
        s += ("&" if not first else "?") + str(k) + "=" + str(v)
        first = False
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

def flatten(a):
    return [a] if not isinstance(a, list) else sum(map(flatten, a), [])
