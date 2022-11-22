from base import ERR, ERR_, TRU, TRU_, ALB
from string import digits, punctuation
import re, sql

# инициализируем соединение с БД
db = sql.Base('../db/base.db')
du = sql.User('../db/users.db')
dg = sql.Group('../db/groups.db')
dm = sql.Month('../db/month.db')


def upd_stat(user_id, group_id, var_id, name, mes=False):
    name = re.sub(r'[^\w\s]', '', name.lower())
    if not du.user_exists(user_id):
        du.add_user(user_id)
    user_id = du.get_user_id(user_id)

    if not du.group_exists(group_id):
        du.add_group(group_id)
    group_id = du.get_group_id(group_id)

    if not db.group_exists(group_id):
        db.add_group(group_id)
        dg.created_group(group_id)

    if not dg.user_exists(user_id, group_id):
        dg.add_user(group_id, user_id, name)

    db.update_stat(group_id, var_id)
    dg.update_stat(user_id, group_id, var_id)

    if not db.group_exists_month(group_id):
        db.add_group_month(group_id)
        dm.created_group(group_id)
        dm.add_user(group_id, user_id)
    else:
        if not dm.user_exists(user_id, group_id):
            dm.add_user(group_id, user_id)

    db.update_month_stat(group_id, var_id)
    dm.update_stat(user_id, group_id, var_id)

    if mes:
        db.update_month_stat(group_id, 1)
        dg.update_stat(user_id, group_id, 1)
        dm.update_stat(user_id, group_id, 1)
        db.update_stat(group_id, 1)

    if not db.edit_user_exists(user_id):
        dg.update_name(user_id, group_id, name)


def lang_form(text, smbl='г'):
    for i in range(len(text)):
        word = [str(j) + str(smbl) + str(j).lower() if j in ALB else str(j) for j in text[i]]
        text[i] = ''.join(word)
    return ' '.join(text)


def notice(name, all_users, group_id, author):
    names = [i[0] for i in dg.all_names(group_id)]
    ids = [du.get_first_user_id(i[0]) for i in dg.all_ids(group_id)]

    if all_users:
        name = dg.user_name(name, group_id)
        usr = ["<a href=\""+'tg://user?id='+str(ids[i])+"\">"+names[i].title()+"</a>" for i in range(len(names))
               if names[i] != name.lower()]
        usr.append(f'{usr[-2]} и {usr[-1]}')
        del usr[-2], usr[-2]
        return f'{", ".join(usr)} вас вызывает {name.title()}'
    else:
        no_copy = []
        for i in name:
            if i not in no_copy:
                no_copy.append(i)
                
        if len(no_copy) > 1:  # ПЕРЕПИСАТЬ КОД ГАВНА КУСОК
            usr = ["<a href=\""+'tg://user?id='+str(ids[names.index(_)])+"\">"+_.title()+"</a>" for _ in no_copy
                   if int(author) != ids[names.index(_)]]
            usr.append(f'{usr[-2]} и {usr[-1]}')
            del usr[-2], usr[-2]
            return f"{', '.join(usr)} вас упомянули)"
        else:
            usr = "<a href=\""+'tg://user?id='+str(ids[names.index(no_copy[0])])+"\">"+no_copy[0].title()+"</a>"
            return f"{usr}, тебя упомянули)"


def checker(signs, words, group_id, user_id, name):
    if len([z for z in signs if (z in digits) or (z in punctuation)]) == len(signs) or signs[0] == '/':
        return int('-1')

    if len(signs) > 4:
        for x in range(3, len(signs)):
            http = "".join([signs[x - 3], signs[x - 2], signs[x - 1], signs[x]])
            if 'http' in http:
                upd_stat(user_id, group_id, 4, name)
                return int('-1')

    count, raw = 0, 0
    for word in words:
        for symbol in word:
            raw += 1
            if (symbol in ERR) or (symbol in ERR_) or (symbol in digits):
                count += 1
    return len(signs) - raw + count


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