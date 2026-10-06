# AboBot

**Русский** · [English](README.en.md)

[![CI](https://github.com/EDeev/chatping_abobot/actions/workflows/ci.yml/badge.svg)](https://github.com/EDeev/chatping_abobot/actions/workflows/ci.yml)
[![Docker](https://github.com/EDeev/chatping_abobot/actions/workflows/docker.yml/badge.svg)](https://github.com/EDeev/chatping_abobot/actions/workflows/docker.yml)
[![License](https://img.shields.io/github/license/EDeev/chatping_abobot)](LICENSE)

Telegram-бот для групповых чатов. Он:
- зовёт участника, когда его имя звучит в сообщении или в голосовом;
- ведёт статистику чата и каждого участника;
- исправляет текст, набранный в неправильной раскладке;
- распознаёт и озвучивает голосовые;
- устраивает шуточные ивенты.

**Статус:** личный проект, работает с 2021 года, версия 4 · бот [@chat_abobot](https://t.me/chat_abobot) · в базе
бота больше 20 000 пользователей из 45 чатов (октябрь 2026)

**Стек:** Python 3.10+ · aiogram 3 · PostgreSQL (asyncpg) · pymorphy3 · pyenchant · SpeechRecognition · gTTS · Docker

## Возможности

- **Упоминания по имени.** Слова сообщения приводятся к начальной форме (pymorphy3) и сравниваются с
  именами участников, поэтому участницу Машу позовут и «Маша», и «позови Машу», и «с Машей». Своё имя
  для упоминаний можно задать командой `/edit`. Имена ищутся и в голосовых до минуты.
- **`/all`** — упомянуть всех участников. Длинный список делится на несколько сообщений.
- **Большие чаты (больше 100 участников).**
  - `/all` — только для администраторов, не чаще раза в 5 минут и только для писавших за 30 дней.
  - Одного человека по имени бот зовёт не чаще раза в минуту.
- **Статистика за всё время и по месяцам** (`/stat_group`, `/stat_user`): сообщения, ответы, команды,
  ссылки, медиа, стикеры, голосовые и кружочки. Месяцы хранятся, поэтому `/month 2026-09` покажет итоги
  любого месяца, а `/top` — самых активных за месяц или за всё время (`/top all`).
- **`/settings`** — переключатели для чата: упоминания по имени, поиск имён в голосовых (голос уходит в
  Google), текстовые ивенты, удаление служебных сообщений. Менять могут администраторы.
- **Неправильная раскладка.** Сообщение вида `ghbdtn` бот повторит как «привет». Английские слова он
  отличает по словарю (pyenchant) и не трогает.
- **Голос.** `/recognize` ответом на голосовое — расшифровка; «Озвучь - текст» — голосовое из текста.
- **Ивенты:**
  - «Число от 1 до 100»;
  - «Переверни - …»;
  - «Переведи - …» — на кирпичный язык;
  - «Подраться с …»;
  - «Чмокнуть» и другие действия с картинками.

  Отключаются командой `/stop_bot` или в `/settings`.
- Удаление служебных сообщений (вход, выход, смена названия и фото) — если у бота права администратора.
- **Учёт бота в группах.** Бот записывает, в каких группах состоит и с какими правами: события Telegram
  плюс сверка при запуске и раз в 6 часов. История изменений хранится. Если бота исключили, статистика
  группы не удаляется — меняется только отметка, что бота там больше нет.

## Запуск

```bash
git clone https://github.com/EDeev/chatping_abobot.git && cd chatping_abobot
cp .env.example .env      # BOT_TOKEN от @BotFather
docker compose up -d      # бот и PostgreSQL
```

Готовый образ: `docker pull ghcr.io/edeev/chatping_abobot` или `docker pull dcr.deev.su/edeev/chatping_abobot`.
Таблицы создаются при первом запуске (`code/schema.sql`).

Без Docker нужны:
- Python 3.10+;
- PostgreSQL;
- системная библиотека enchant с английским словарём (`apt install libenchant-2-2 hunspell-en-us`).

Затем: `pip install -r requirements.txt` и `cd code && BOT_TOKEN=… DATABASE_URL=postgresql://… python bot.py`.

Перенос данных старой версии (четыре базы SQLite):
`python scripts/migrate_sqlite.py --sqlite-dir путь/к/db --dsn postgresql://…`. Скрипт сверяет суммы после
переноса.

## Развёртывание

[@chat_abobot](https://t.me/chat_abobot) работает на домашнем сервере как systemd-служба: свой venv, настройки
в `/etc/abobot.env`, база — PostgreSQL на том же сервере. Ночной бэкап снимает дамп базы, статистика
выводится в дашборд Metabase.

## Как устроено

```
code/bot.py          запуск, отправка ошибок в технический чат, сверка статуса бота в группах
code/handlers/       роутеры: help, settings, stats, mentions, voice, events, chat (бот в группах, служебные сообщения)
code/db.py           запросы к PostgreSQL
code/schema.sql      схема: chats, users, members, chat_stats и member_stats по периодам, bot_status_history
code/nlp.py          имена в начальной форме, раскладка, переворот, экранирование
scripts/             перенос данных из SQLite
data/                картинки ивентов и приветствие
```

Счётчики за всё время и за текущий месяц растут одним запросом (`INSERT … ON CONFLICT DO UPDATE`),
поэтому одновременные сообщения не теряются. Запросы к базе асинхронные, а распознавание и синтез речи
(Google Web Speech и gTTS) идут в отдельном потоке — бот не замирает. Разметка сообщений — HTML,
пользовательский текст экранируется.

## Разработка

```bash
pip install -r requirements-dev.txt
ruff check --select E9,F,B code tests && pytest
```

Тестам нужен PostgreSQL (`TEST_DATABASE_URL`). Что они проверяют:
- счётчики по периодам;
- упоминания и ограничения больших чатов;
- деление `/all` на сообщения;
- статус бота в группах и историю;
- перенос из SQLite;
- раскладку и экранирование.

CI прогоняет их на Python 3.10 и 3.12.

Docker-образ собирается по тегу `v*` и публикуется в GitHub Packages и `dcr.deev.su`.

## Лицензия

MIT — см. [LICENSE](LICENSE).

## Автор

**Деев Егор Викторович** — [GitHub](https://github.com/EDeev) · [Telegram](https://t.me/DeevEgor) · [egor@deev.space](mailto:egor@deev.space)

---

<div align="center">
  <sub>⭐ Если проект оказался полезным, поставьте звёздочку на GitHub!</sub>
  <p><sub>Сделано с ❤️ — <a href="https://deev.space">deev.space</a></sub></p>
</div>
