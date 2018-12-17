"""helpers for translation and managing languages"""

import contextvars

language_context = contextvars.ContextVar("language") # pylint: disable=invalid-name

def translate(msgid: str) -> str:
    """get the translation for a msgid in the current language context"""
    print("lang:", language_context.get())
    return msgid
