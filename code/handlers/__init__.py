from . import chat, events, help, mentions, settings, stats, voice

# порядок важен: команды раньше общего обработчика текста
routers = [chat.router, help.router, settings.router, stats.router, mentions.router, voice.router, events.router]
