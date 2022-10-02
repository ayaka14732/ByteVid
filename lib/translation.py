import hashlib
import os
import random
import requests

_BAIDU_APP_ID = os.environ['BAIDU_APP_ID']
_BAIDU_APP_KEY = os.environ['BAIDU_APP_KEY']

API_URL = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

#  lang_code, baidu_api_id, language name
LANGUAGES = (
    ('ar', 'ara', 'Arabic'),
    ('bg', 'bul', 'Bulgarian'),
    ('cs', 'cs', 'Czech'),
    ('da', 'dan', 'Danish'),
    ('de', 'de', 'German'),
    ('el', 'el', 'Greek'),
    ('en', 'en', 'English'),
    ('es', 'spa', 'Spanish'),
    ('et', 'est', 'Estonian'),
    ('fi', 'fin', 'Finnish'),
    ('fr', 'fra', 'French'),
    ('hu', 'hu', 'Hungarian'),
    ('it', 'it', 'Italian'),
    ('ja', 'jp', 'Japanese'),
    ('ko', 'kor', 'Korean'),
    ('nl', 'nl', 'Dutch'),
    ('pl', 'pl', 'Polish'),
    ('pt', 'pt', 'Portuguese'),
    ('ro', 'rom', 'Romanian'),
    ('ru', 'ru', 'Russian'),
    ('sl', 'slo', 'Slovenian'),
    ('sv', 'swe', 'Swedish'),
    ('th', 'th', 'Thai'),
    ('vi', 'vie', 'Vietnamese'),
    ('zh', 'cht', 'Chinese'),
    ('lzh', 'wyw', 'Classical Chinese'),
)

LANG_CODE2BAIDU_API_ID = {lang_code: baidu_api_id for lang_code, baidu_api_id, _ in LANGUAGES}

def md5(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def translate(sentence: str, dest: str, src: str='auto') -> str:
    assert _BAIDU_APP_ID is not None
    assert _BAIDU_APP_KEY is not None

    dest = LANG_CODE2BAIDU_API_ID[dest]

    salt = str(random.randrange(32768, 67108864))
    payload = {
        'q': sentence,
        'from': src,
        'to': dest,
        'appid': _BAIDU_APP_ID,
        'salt': salt,
        'sign': md5(_BAIDU_APP_ID + sentence + salt + _BAIDU_APP_KEY),
    }

    r = requests.post(API_URL, data=payload)
    r.raise_for_status()
    obj = r.json()
    assert 'error_code' not in obj
    text = '\n'.join(x['dst'] for x in obj['trans_result'])
    return text
