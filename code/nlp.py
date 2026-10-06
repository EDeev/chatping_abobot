"""Обработка текста: имена, неправильная раскладка, переворот, кирпичный язык"""
import re
from html import escape
from string import digits, punctuation

import enchant
import pymorphy3

from base import ALB, ERR, ERR_, TRU, TRU_

morph = pymorphy3.MorphAnalyzer()
engl_dict = enchant.Dict("en_US")


def h(text):
    """Экранирование для HTML-разметки сообщений"""
    return escape(str(text), quote=False)


def mention(user_id, name):
    return f'<a href="tg://user?id={int(user_id)}">{h(str(name).title())}</a>'


def join_names(items):
    """«а», «а и б», «а, б и в»"""
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " и " + items[-1]


def clean_name(name):
    """Имя участника для упоминаний: нижний регистр, без знаков препинания"""
    return re.sub(r'[^\w\s]', '', (name or "").lower()).strip()


def words_normal(text):
    """Слова сообщения в начальной форме"""
    return [morph.parse(w)[0].normal_form for w in re.sub(r'[^\w\s]', '', text.lower()).split()]


def find_names(text, names):
    """Имена участников, упомянутые в тексте (в любой форме), без повторов"""
    found = []
    for word in words_normal(text):
        if word in names and word not in found:
            found.append(word)
    return found


def inflect_past(word):
    """Глагол в прошедшем времени; если pymorphy3 не справился — как есть"""
    form = morph.parse(word.lower())[0].inflect({'past', 'sing', 'indc'})
    return form.word if form else word


def genitive(name):
    form = morph.parse(name)[0].inflect({"gent"})
    return form.word if form else name


def has_url(text):
    return "http" in text.lower()


def wrong_layout(text):
    """Сообщение целиком набрано латиницей в русской раскладке (и это не английские слова)"""
    if not text or text[0] == '/' or all(c in digits or c in punctuation or c.isspace() for c in text):
        return False
    if any(not c.isspace() and c not in ERR and c not in ERR_ and c not in digits for c in text):
        return False
    words = [w for w in re.sub(r'[^\w\s]', '', text.lower()).split() if len(w) > 1]
    return not any(engl_dict.check(w) for w in words)


def lang_form(text, smbl='г'):
    for i in range(len(text)):
        word = [str(j) + str(smbl) + str(j).lower() if j in ALB else str(j) for j in text[i]]
        text[i] = ''.join(word)
    return ' '.join(text)


def translator(words):
    itg = []
    for word in words:
        raw_word = []
        for symbol in word:
            if symbol in ERR:
                count = 0
                for _ in ERR:
                    if symbol == _:
                        raw_word.append(TRU[count])
                        break
                    count += 1
            elif symbol in ERR_:
                count = 0
                for _ in ERR_:
                    if symbol == _:
                        raw_word.append(TRU_[count])
                        break
                    count += 1
        itg.append("".join(raw_word))
    return " ".join(itg)


def revers(message, var):
    no_pct = re.sub(r'[^\w\s]', '', message)

    if var:
        sml, pnc, pct, prf = [i for i in message] + [str(0)], [], [], False
        for i in sml:
            if i in punctuation or i == ' ':
                pnc.append(i)
                prf, flag = True if sml.index(i) == 0 else False, False
            else:
                flag = True

            if flag and len(pnc) > 0:
                pct.append(''.join(pnc))
                pnc = []

        wrd, rev, txt = no_pct.split(), [], []
        for i in wrd:
            word, up, itg = [i[-1 - l].lower() for l in range(len(i))], [], []

            for _ in i:
                up.append(True if _ in TRU_ else False)
            for j in range(len(up)):
                itg.append(word[j].upper() if up[j] else word[j])

            rev.append(''.join(itg))

        if prf:
            for i in range(len(pct)):
                txt = (txt + [pct[i]]) if (i + 1) == len(pct) and len(pct) > len(rev) else (txt + [pct[i], rev[i]])
            return ''.join(txt)
        else:
            for i in range(len(rev)):
                if i > 0:
                    txt.append(pct[i - 1])
                txt.append(rev[i])
                if (i + 1) == len(rev) and len(pct) == len(rev):
                    txt.append(pct[i])
            return ''.join(txt)
    else:
        sml = [i for i in message]
        return ''.join([sml[-1 - i] for i in range(len(sml))])