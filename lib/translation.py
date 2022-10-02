import hashlib
import os
import random
import requests
import time
from typing import Optional

_BAIDU_APP_ID = os.environ['BAIDU_APP_ID']
_BAIDU_APP_KEY = os.environ['BAIDU_APP_KEY']

assert _BAIDU_APP_ID is not None
assert _BAIDU_APP_KEY is not None

API_URL = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

#  lang_code, baidu_api_id, language name
LANGUAGE_MAP = {
    'ar': 'ara',  # Arabic
    'bg': 'bul',  # Bulgarian
    'cs': 'cs',  # Czech
    'da': 'dan',  # Danish
    'de': 'de',  # German
    'el': 'el',  # Greek
    'en': 'en',  # English
    'es': 'spa',  # Spanish
    'et': 'est',  # Estonian
    'fi': 'fin',  # Finnish
    'fr': 'fra',  # French
    'hu': 'hu',  # Hungarian
    'it': 'it',  # Italian
    'ja': 'jp',  # Japanese
    'ko': 'kor',  # Korean
    'nl': 'nl',  # Dutch
    'pl': 'pl',  # Polish
    'pt': 'pt',  # Portuguese
    'ro': 'rom',  # Romanian
    'ru': 'ru',  # Russian
    'sl': 'slo',  # Slovenian
    'sv': 'swe',  # Swedish
    'th': 'th',  # Thai
    'vi': 'vie',  # Vietnamese
    'zh-Hans': 'zh',  # Chinese (Simplified)
    'zh-Hant': 'cht',  # Chinese (Traditional)
    'lzh': 'wyw',  # Classical Chinese
}

def md5(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def chunks(lst, chunksize: int=16):
    return [lst[i:i+chunksize] for i in range(0, len(lst), chunksize)]

def translate_chunk(chunk: str, src: str, dst: str) -> list[str]:
    sentence = '\n'.join(chunk)

    salt = str(random.randrange(32768, 67108864))
    sign = md5(_BAIDU_APP_ID + sentence + salt + _BAIDU_APP_KEY)
    payload = {
        'q': sentence,
        'from': src,
        'to': dst,
        'appid': _BAIDU_APP_ID,
        'salt': salt,
        'sign': sign,
    }

    while True:
        try:
            r = requests.post(API_URL, data=payload)
            r.raise_for_status()
            obj = r.json()
            assert 'error_code' not in obj
        except Exception as e:
            print(e)
            continue
        break

    results = [result['dst'] for result in obj['trans_result']]
    return results

def translate(article: str, src: Optional[str]=None, dst: str='zh-Hans') -> str:
    if src == None:
        src = 'auto'
    if dst == src:
        return article
    dst = LANGUAGE_MAP[dst]

    sentences_src = article.split('\n')
    sentences_src_chunked = chunks(sentences_src)

    sentences_dst = []
    for chunk in sentences_src_chunked:
        results = translate_chunk(chunk, src, dst)
        sentences_dst.extend(results)
        time.sleep(2.)  # Baidu API has rate limits

    return '\n'.join(sentences_dst)
