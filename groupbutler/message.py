"""
message Module
Contains the Message object and related functionality
"""

from enum import Enum
from typing import Optional

Storage = None

"""
class MessageType(Enum):
    ANIMATION = 0
    AUDIO = 1
    CONTACT = 2
    DOCUMENT = 3
    GAME = 4
    LOCATION = 5
    PHOTO = 6
    STICKER = 7
    VENUE = 8
    VIDEO = 9
    VIDEO_NOTE = 10
    VOICE = 11
    TEXT = 12
    LINK = 13
"""

MEDIA_TYPES = {
    "audio",
    #"animation",
    "contact",
    "document",
    "game",
    "location",
    "photo",
    "sticker",
    "venue",
    "video",
    "video_note",
    "voice",
}

class Message():
    """represents a message received via the API"""

    def __init__(self, json_object: dict, storage: Storage):
        """create a new `Message` from a JSON object received from Telegram"""
        self.message_obj = json_object
        self.storage = storage

    async def is_from_admin(self) -> bool:
        """check if the message sender is an admin. This might hit either the Cache or the API"""
        if self.message_obj["chat"]["type"] == "private": # in private chats, there are no admins
            return False

        # TODO: message.lua has further conditions, which I don't quite understand

        # TODO: fetch from admin cache

    def __getitem__(self, item: str):
        """Shortcut for raw access to the messages json data"""
        return self.message_obj[item]

    def __contains__(self, item: str) -> bool:
        """Shortcut for raw access to the messages json data"""
        return item in self.message_obj

    def get(self, key, default=None):
        """Return the value for key if key is in the dictionary, else default.
        If default is not given, it defaults to None, so that this method never
        raises a KeyError.

        Shortcut for raw access to the messages json data"""
        return self.message_obj.get(key, default)

    def __repr__(self):
        return "Message({})".format(self.message_obj)

    # Helpers for quickly accessing common values
    @property
    def chat_type(self) -> str:
        """the chat type"""
        return self["chat"]["type"]

    @property
    def from_id(self) -> str:
        """the sender id"""
        return self["from"]["id"]

    @property
    def chat_id(self) -> str:
        """the chat id"""
        return self["chat"]["id"]

    @property
    def msg_id(self) -> str:
        """the message id"""
        return self["message_id"]

    @property
    def from_public_chat(self) -> bool:
        """if the message is from a public chat"""
        return "username" in self["chat"]

    @property
    def type(self) -> str:
        """the "main" type of the message. This is the one the most relevant
        for antispam. Hence, e.g. "link" is a type.
        """
        msg = self.message_obj
        # lua -- TODO: update database to use "animation" instead of "gif"
        if "animation" in self.message_obj:
            return "gif"

        for mtype in MEDIA_TYPES:
            if mtype in msg:
                return mtype

        # clickable links in the message show up under the "entities" key
        for entity in msg.get("entities", ()):
            if entity["type"] in ("url", "text_link"):
                return "link"

        # if it's nothing else, it's probably just text
        return "text"

    def get_file_id(self) -> Optional[int]:
        """get a file ID for the contents of the Message"""
         # lua -- TODO: remove this once db migration for gif messages has been completed
        if self["animation"]:
            return self["animation"]["file_id"]
        if self["photo"]:
            # the last photo contains the one of highest resolution, although
            # this is not officially part of the API. We can pick any image id,
            # it doesn't matter for our purposes.
            return self["photo"][-1]["file_id"]

        # get the the JSON object that stores the information for the media type
        mediatype_object = self.message_obj.get(self.type)

        if mediatype_object is not None:
            return mediatype_object["file_id"]

        return None

class InlineKeyboard:
    """helper to create inline buttons"""
    def __init__(self):
        self.buttons = []
