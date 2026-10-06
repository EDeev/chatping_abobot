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

**Статус:** личный проект, работает с 2021 года · бот [@chat_abobot](https://t.me/chat_abobot) · в базе
бота больше 20 000 пользователей из 45 чатов (октябрь 2026)

**Стек:** Python 3.12 · aiogram 3 · pymorphy3 · pyenchant · SpeechRecognition · gTTS · SQLite · Docker

## Возможности

- **Упоминания по имени.** Слова сообщения приводятся к начальной форме (pymorphy3) и сравниваются с
  именами участников, поэтому участницу Машу позовут и «Маша», и «позови Машу», и «с Машей». Своё имя
  для упоминаний можно задать командой `/edit`. Имена ищутся и в голосовых до минуты.
- **`/all`** — упомянуть всех участников.
- **Статистика за всё время и за месяц** (`/stat_group`, `/stat_user`): сообщения, ответы, команды,
  ссылки, медиа, стикеры, голосовые и кружочки. Месячная обнуляется в начале месяца.
- **Неправильная раскладка.** Сообщение вида `ghbdtn` бот повторит как «привет». Английские слова он
  отличает по словарю (pyenchant) и не трогает.
- **Голос.** `/recognize` ответом на голосовое — расшифровка; «Озвучь - текст» — голосовое из текста.
- **Ивенты:**
  - «Число от 1 до 100»;
  - «Переверни - …»;
  - «Переведи - …» — на кирпичный язык;
  - «Подраться с …»;
  - «Чмокнуть» и другие действия с картинками.

  Отключаются командой `/stop_bot`.
- Удаление служебных сообщений (вход, выход, смена названия и фото) — если у бота права администратора.

## Запуск

```bash
git clone https://github.com/EDeev/chatping_abobot.git && cd chatping_abobot
cp .env.example .env      # BOT_TOKEN от @BotFather
docker compose up -d
```

Готовый образ: `docker pull ghcr.io/edeev/chatping_abobot` или `docker pull dcr.deev.su/edeev/chatping_abobot`.
Базы SQLite создаются при первом запуске.

Без Docker нужны Python 3.12, системная библиотека enchant и английский словарь
(`apt install libenchant-2-2 hunspell-en-us`). Затем: `pip install -r requirements.txt` и
`cd code && BOT_TOKEN=… python bot.py`.

## Как устроено

```
code/bot.py        запуск и ежемесячное обнуление статистики
code/handlers.py   обработчики сообщений, команд, голосовых и ивентов
code/script.py     учёт статистики, поиск имён, раскладка, переворот текста
code/sql.py        четыре базы SQLite: группы, пользователи, статистика за всё время и за месяц
data/              картинки ивентов и приветствие
```

Статистика участников хранится в отдельной таблице на каждый чат — так устроены рабочие базы бота.
Счётчики увеличиваются одним запросом, поэтому одновременные сообщения не теряются. Распознавание и синтез
речи (Google Web Speech и gTTS) идут в отдельном потоке, чтобы бот не замирал.

## Разработка

```bash
pip install -r requirements-dev.txt
ruff check --select E9,F,B code tests && pytest
```

Что проверяют тесты:
- счётчики статистики;
- упоминания и `/all`;
- обнуление месячной статистики;
- раскладку, переворот и экранирование;
- что обработчики бота загружаются.

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
