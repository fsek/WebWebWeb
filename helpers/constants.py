# Here we collect some reused constants, like the maximum length of a name. They are referenced in db models and schemas

# Warning! These are used in db model definitions. Changing these will require db migration

## User
MAX_FIRSTNAME_LEN = 100
MAX_LASTNAME_LEN = 100
MAX_TELEPHONE_LEN = 20

## Event
MAX_EVENT_DESC = 3000
MAX_EVENT_TITLE = 100

## News
MAX_NEWS_TITLE = 100
MAX_NEWS_CONTENT = 3000


# Song
MAX_SONG_TITLE = 200
MAX_SONG_AUTHOR = 200
MAX_SONG_CATEGORY = 100
MAX_SONG_CONTENT = 3000
MAX_SONG_MELODY = 200

# Imgs
MAX_IMG_NAME = 200
