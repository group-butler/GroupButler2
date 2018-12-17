""" pins plugin module
"""
from groupbutler import plugin
from groupbutler.language import translate as _t

@plugin.registry.register
class PinsPlugin(plugin.Plugin):
    """ The pins plugin allows users to create and pin messages. Unlike
    messages by pinned by users, messages sent by bots can be edited forever,
    thus not requiring you to re-pin the message
    """
    @plugin.register_command("setpin")
    async def set_pin(self, message):
        await self.tgapi.reply_to(message, _t("setpin!"))
