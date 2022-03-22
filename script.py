from base import ERR, ERR_, TRU, TRU_, ALB
from string import digits, punctuation
from datetime import date, datetime
from sql import SQLighter
import re

db = SQLighter('groups.db')


def lang_form(text, smbl='г'):
    for i in range(len(text)):
        word = []
        for j in text[i]:
            if j in ALB:
                word.append(str(str(j) + str(smbl) + str(j).lower()))
            else:
                word.append(str(j))
        text[i] = ''.join(word)
    return ' '.join(text)


def times():
    today = datetime.now().date()
    sel = date(2021, 2, 2)
    ext = date(2023, 10, 3)

    itg = str((ext - today).days)
    if int(itg[-1]) == 1:
        return f'{itg} день)'
    elif 1 < int(itg[-1]) < 5:
        return f'{itg} дня)'
    else:
        return f'{itg} дней)'


def autozak(name):
    num = str(len(name))
    if int(num[-1]) == 1:
        return f'{num} минута.'
    elif 1 < int(num[-1]) < 5:
        return f'{num} минуты.'
    else:
        return f'{num} минут.'


def update_stat(var, message, main=False):
    db.statistics_group(message.chat.id, var)
    db.user_statistic(message.from_user.id, message.chat.id, var)
    if main:
        db.statistics_group(message.chat.id, 1)
        db.user_statistic(message.from_user.id, message.chat.id, 1)
    return


def notice(name, all_users, id_group, id_var):
    names = db.name_lst(id_group)
    ids, no_copy = db.id_lst(id_group), []

    if all_users:
        usr = ["<a href=\""+'tg://user?id='+ids[i]+"\">"+names[i].title()+"</a>" for i in range(len(names))
               if names[i] != name.lower()]
        usr.append(f'{usr[-2]} и {usr[-1]}')
        del usr[-2], usr[-2]
        return f'{", ".join(usr)} вас вызывает {name}'
    else:
        for i in name:
            if i not in no_copy:
                no_copy.append(i)
                
        if len(no_copy) > 1:
            usr = ["<a href=\""+'tg://user?id='+ids[names.index(_)]+"\">"+_.title()+"</a>" for _ in no_copy
                   if id_var != ids[names.index(_)]]
            usr.append(f'{usr[-2]} и {usr[-1]}')
            del usr[-2], usr[-2]
            return f"{', '.join(usr)} вас упомянули)"
        else:
            usr = "<a href=\""+'tg://user?id='+ids[names.index(no_copy[0])].title()+"\">"+no_copy[0].title()+"</a>"
            return f"{usr}, тебя упомянули)"


def cheker(bk, original, id_group, user):
    flag = True

    if flag is True:
        if (len([z for z in bk if (z in digits) or (z in punctuation)]) == len(bk)) or (bk[0] == '/'):
            flag = False

    if (flag is True) and (len(bk) > 4):
        for x in range(3, len(bk)):
            http = "".join([bk[x - 3], bk[x - 2], bk[x - 1], bk[x]])
            if 'http' in http:
                db.statistics_group(id_group, 4)
                db.user_statistic(user, id_group, 4)
                flag = False
                break

    if flag is False:
        if 'tiktok' in "".join(bk).split('.'):
            db.statistics_group(id_group, 5)
            db.user_statistic(user, id_group, 5)
    
    if flag:
        count, raw = 0, 0
        for word in original:
            for smvl in word:
                raw += 1
                if (smvl in ERR) or (smvl in ERR_) or (smvl in digits):
                    count += 1
        return len(bk) - raw + count
    else:
        return int('-1')


def translator(original):
    itg = []
    for word in original:
        raw_word = []
        for smvl in word:
            if smvl in ERR:
                count = 0
                for _ in ERR:
                    if smvl == _:
                        raw_word.append(TRU[count])
                        break
                    count += 1
            elif smvl in ERR_:
                count = 0
                for _ in ERR_:
                    if smvl == _:
                        raw_word.append(TRU_[count])
                        break
                    count += 1
            elif smvl in NUM:
                raw_word.append(smvl)
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

        wrd, rev, lst, txt = no_pct.split(), [], [], []
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