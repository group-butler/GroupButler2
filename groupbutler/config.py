import os

# temp hack
class Config:
    old_update_threshold = 1000000
    token = os.environ["TG_TOKEN"]

config = Config()
