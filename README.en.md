# AboBot

[Русский](README.md) · **English**

[![CI](https://github.com/EDeev/chatping_abobot/actions/workflows/ci.yml/badge.svg)](https://github.com/EDeev/chatping_abobot/actions/workflows/ci.yml)
[![Docker](https://github.com/EDeev/chatping_abobot/actions/workflows/docker.yml/badge.svg)](https://github.com/EDeev/chatping_abobot/actions/workflows/docker.yml)
[![License](https://img.shields.io/github/license/EDeev/chatping_abobot)](LICENSE)

A Telegram bot for group chats. It:
- pings a member when their name comes up in a message or a voice note;
- keeps statistics for the chat and every member;
- fixes text typed in the wrong keyboard layout;
- transcribes and voices messages;
- runs playful events.

The bot speaks Russian.

**Status:** personal project, running since 2021 · bot [@chat_abobot](https://t.me/chat_abobot) · over
20,000 users from 45 chats in the bot's database (October 2026)

**Stack:** Python 3.10+ · aiogram 3 · PostgreSQL (asyncpg) · pymorphy3 · pyenchant · SpeechRecognition · gTTS · Docker

## Features

- **Name mentions.** Words of a message are reduced to their base form (pymorphy3) and compared with
  members' names, so any grammatical case of a name mentions the right person. A custom name can be set with `/edit`. Names are also found
  in voice notes up to a minute long.
- **`/all`** mentions every member. A long list is split into several messages.
- **Big chats (over 100 members).**
  - `/all` is for admins only, at most once in 5 minutes, and only for people who wrote in the last 30 days.
  - The same person is mentioned by name at most once a minute.
- **All-time and monthly statistics** (`/stat_group`, `/stat_user`): messages, replies, commands, links,
  media, stickers, voice and video notes. Months are kept, so `/month 2026-09` shows any month's summary
  and `/top` shows the most active members for the month or all time (`/top all`).
- **`/settings`** — per-chat switches: name mentions, names in voice notes (audio goes to Google), text
  events, deleting service messages. Admins can change them.
- **Wrong keyboard layout.** A message like `ghbdtn` is repeated as «привет». English words are recognized
  with a dictionary (pyenchant) and left alone.
- **Voice.** `/recognize` as a reply to a voice note transcribes it; «Озвучь - текст» turns text into a
  voice note.
- **Events:**
  - random numbers;
  - reversing text;
  - a language game;
  - mock fights;
  - picture reactions.

  Turned off with `/stop_bot` or in `/settings`.
- Deleting service messages (joins, leaves, title and photo changes) when the bot is an admin.
- **Tracking the bot in groups.** The bot records which groups it is in and with which rights: Telegram
  events plus a check on start and every 6 hours. Changes are kept as history. If the bot is removed, the
  group's statistics stay; only the mark that the bot is no longer there changes.

## Running

```bash
git clone https://github.com/EDeev/chatping_abobot.git && cd chatping_abobot
cp .env.example .env      # BOT_TOKEN from @BotFather
docker compose up -d      # the bot and PostgreSQL
```

Prebuilt image: `docker pull ghcr.io/edeev/chatping_abobot` or `docker pull dcr.deev.su/edeev/chatping_abobot`.
Tables are created on first start (`code/schema.sql`).

Without Docker you need:
- Python 3.10+;
- PostgreSQL;
- the enchant system library with an English dictionary (`apt install libenchant-2-2 hunspell-en-us`).

Then: `pip install -r requirements.txt` and `cd code && BOT_TOKEN=… DATABASE_URL=postgresql://… python bot.py`.

Migrating data from the old version (four SQLite databases):
`python scripts/migrate_sqlite.py --sqlite-dir path/to/db --dsn postgresql://…`. The script checks the
totals after the transfer.

## Deployment

[@chat_abobot](https://t.me/chat_abobot) runs on a home server as a systemd service: its own venv, settings in
`/etc/abobot.env`, PostgreSQL on the same server. The nightly backup dumps the database, and the statistics
feed a Metabase dashboard.

## How it works

```
code/bot.py          entry point, error reports to a tech chat, checking the bot's status in groups
code/handlers/       routers: help, settings, stats, mentions, voice, events, chat (bot in groups, service messages)
code/db.py           PostgreSQL queries
code/schema.sql      schema: chats, users, members, chat_stats and member_stats by period, bot_status_history
code/nlp.py          base forms of names, keyboard layout, reversal, escaping
scripts/             migration from SQLite
data/                event pictures and the greeting
```

All-time and current-month counters grow in a single query (`INSERT … ON CONFLICT DO UPDATE`), so
simultaneous messages are not lost. Database calls are asynchronous and speech recognition and synthesis
(Google Web Speech and gTTS) run in a separate thread, so the bot never freezes. Messages use HTML markup and
user text is escaped.

## Development

```bash
pip install -r requirements-dev.txt
ruff check --select E9,F,B code tests && pytest
```

The tests need PostgreSQL (`TEST_DATABASE_URL`). What they cover:
- counters by period;
- mentions and big-chat limits;
- splitting `/all`;
- the bot's status in groups and its history;
- migration from SQLite;
- keyboard layout and escaping.

CI runs them on Python 3.10 and 3.12.

The Docker image is built on `v*` tags and published to GitHub Packages and `dcr.deev.su`.

## License

MIT — see [LICENSE](LICENSE).

## Author

**Egor Deev** — [GitHub](https://github.com/EDeev) · [Telegram](https://t.me/DeevEgor) · [egor@deev.space](mailto:egor@deev.space)

---

<div align="center">
  <sub>⭐ If you find this project useful, give it a star on GitHub!</sub>
  <p><sub>Made with ❤️ — <a href="https://deev.space">deev.space</a></sub></p>
</div>
