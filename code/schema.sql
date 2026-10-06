-- Схема AboBot в PostgreSQL. Применяется при каждом запуске (всё IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS chats (
    id               BIGINT PRIMARY KEY,                 -- id чата в Telegram
    short_id         SERIAL UNIQUE,                      -- внутренний номер («Группа #N» в Metabase)
    title            TEXT,
    events_enabled   BOOLEAN NOT NULL DEFAULT TRUE,      -- текстовые ивенты (/start_bot, /stop_bot)
    mentions_enabled BOOLEAN NOT NULL DEFAULT TRUE,      -- упоминания по имени в сообщениях
    voice_names      BOOLEAN NOT NULL DEFAULT TRUE,      -- поиск имён в голосовых (уходят в Google)
    delete_service   BOOLEAN NOT NULL DEFAULT TRUE,      -- удаление служебных сообщений
    last_all_at      TIMESTAMPTZ,                        -- последний /all (ограничение в больших чатах)
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- бот в чате: статус Telegram (member, administrator, restricted, left, kicked) и права;
    -- если бота исключили, данные чата остаются, меняется только статус
    bot_status       TEXT,
    bot_rights       JSONB,
    bot_status_at    TIMESTAMPTZ,                        -- когда статус изменился
    checked_at       TIMESTAMPTZ,                        -- когда статус последний раз сверялся с Telegram
    member_count     INTEGER,                            -- участников по Telegram на момент сверки
    chat_type        TEXT
);

-- история статуса бота в чатах: добавили, повысили до админа, ограничили, исключили
CREATE TABLE IF NOT EXISTS bot_status_history (
    id         BIGSERIAL PRIMARY KEY,
    chat_id    BIGINT NOT NULL REFERENCES chats (id) ON DELETE CASCADE ON UPDATE CASCADE,
    status     TEXT NOT NULL,
    rights     JSONB,
    source     TEXT NOT NULL,                            -- update (событие Telegram) или check (сверка)
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
    id       BIGINT PRIMARY KEY,                         -- id пользователя в Telegram
    short_id SERIAL UNIQUE
);

CREATE TABLE IF NOT EXISTS members (
    chat_id         BIGINT NOT NULL REFERENCES chats (id) ON DELETE CASCADE ON UPDATE CASCADE,
    user_id         BIGINT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name            TEXT NOT NULL DEFAULT '',            -- имя для упоминаний (в нижнем регистре)
    custom_name     BOOLEAN NOT NULL DEFAULT FALSE,      -- задано командой /edit, не обновляется само
    last_message_at TIMESTAMPTZ,
    left_at         TIMESTAMPTZ,                         -- вышел из чата (статистика сохраняется)
    PRIMARY KEY (chat_id, user_id)
);

-- период: 'all' — за всё время, 'YYYY-MM' — месяц; месяцы хранятся, а не обнуляются
CREATE TABLE IF NOT EXISTS chat_stats (
    chat_id BIGINT NOT NULL REFERENCES chats (id) ON DELETE CASCADE ON UPDATE CASCADE,
    period  TEXT NOT NULL,
    mes INTEGER NOT NULL DEFAULT 0, rep INTEGER NOT NULL DEFAULT 0, com INTEGER NOT NULL DEFAULT 0,
    url INTEGER NOT NULL DEFAULT 0, med INTEGER NOT NULL DEFAULT 0, sti INTEGER NOT NULL DEFAULT 0,
    voi INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (chat_id, period)
);

CREATE TABLE IF NOT EXISTS member_stats (
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    period  TEXT NOT NULL,
    mes INTEGER NOT NULL DEFAULT 0, rep INTEGER NOT NULL DEFAULT 0, com INTEGER NOT NULL DEFAULT 0,
    url INTEGER NOT NULL DEFAULT 0, med INTEGER NOT NULL DEFAULT 0, sti INTEGER NOT NULL DEFAULT 0,
    voi INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (chat_id, user_id, period),
    FOREIGN KEY (chat_id, user_id) REFERENCES members (chat_id, user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS member_stats_period ON member_stats (chat_id, period);

-- бот в чате сейчас (для статистики по действующим группам)
CREATE OR REPLACE VIEW active_chats AS
    SELECT * FROM chats WHERE bot_status IN ('member', 'administrator', 'restricted');
