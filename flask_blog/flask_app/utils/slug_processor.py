from transliterate import translit
import string
import re


def is_latin(s):
    return min([char in string.ascii_letters for char in re.sub('[^\w]+', '', s)])


def slugify(s):
    if not is_latin(s):
        s = translit(s, reversed=True)
        s = s.replace('\'', '')

    return re.sub('[^\w]+', '-', s).lower()
