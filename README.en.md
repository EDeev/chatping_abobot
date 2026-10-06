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

**Stack:** Python 3.12 · aiogram 3 · pymorphy3 · pyenchant · SpeechRecognition · gTTS · SQLite · Docker

## Features

- **Name mentions.** Words of a message are reduced to their base form (pymorphy3) and compared with
  members' names, so any grammatical case of a name mentions the right person. A custom name can be set with `/edit`. Names are also found
  in voice notes up to a minute long.
- **`/all`** mentions every member.
- **All-time and monthly statistics** (`/stat_group`, `/stat_user`): messages, replies, commands, links,
  media, stickers, voice and video notes. Monthly numbers reset at the start of each month.
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

  Turned off with `/stop_bot`.
- Deleting service messages (joins, leaves, title and photo changes) when the bot is an admin.

## Running

```bash
git clone https://github.com/EDeev/chatping_abobot.git && cd chatping_abobot
cp .env.example .env      # BOT_TOKEN from @BotFather
docker compose up -d
```

Prebuilt image: `docker pull ghcr.io/edeev/chatping_abobot` or `docker pull dcr.deev.su/edeev/chatping_abobot`.
The SQLite databases are created on first start.

Without Docker you need Python 3.12, the enchant system library and an English dictionary
(`apt install libenchant-2-2 hunspell-en-us`). Then: `pip install -r requirements.txt` and
`cd code && BOT_TOKEN=… python bot.py`.

## How it works

```
code/bot.py        entry point and monthly statistics reset
code/handlers.py   message, command, voice and event handlers
code/script.py     statistics, name lookup, keyboard layout, text reversal
code/sql.py        four SQLite databases: groups, users, all-time and monthly statistics
data/              event pictures and the greeting
```

Member statistics live in a separate table per chat — that is how the bot's production databases are
built. Counters are incremented in a single query, so simultaneous messages are not lost. Speech recognition
and synthesis (Google Web Speech and gTTS) run in a separate thread, so the bot never freezes.

## Development

```bash
pip install -r requirements-dev.txt
ruff check --select E9,F,B code tests && pytest
```

What the tests cover:
- statistics counters;
- mentions and `/all`;
- the monthly reset;
- keyboard layout, reversal and escaping;
- loading of the bot's handlers.

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
