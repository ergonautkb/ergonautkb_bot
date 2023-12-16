from settings import RULES_URL


def get_welcome_message(id, name):
    return (
        f'Hey <a href="tg://user?id={id}">{name}</a>!\n\n'
        "If you want to write in this chat, please, read the "
        f'<a href="{RULES_URL}">rules</a> and press the '
        "button below."
    )


def get_full_welcome_message(id, name):
    return (
        get_welcome_message(id, name) + "\n\nThanks for reading the rules! "
        "Now you are free to chat."
    )


def get_returning_welcome_message(id, name):
    return f'Hey, <a href="tg://user?id={id}">{name}</a>!\n\nWe were missing you!'
