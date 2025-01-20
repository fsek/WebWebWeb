# Here we collect some reused constants, like the maximum length of a name. They are referenced in db models and schemas

# Warning! These are used in db model definitions. Changing these will require db migration

# User
MAX_FIRST_NAME_LEN = 100
MAX_LAST_NAME_LEN = 100
MAX_TELEPHONE_LEN = 20

# Event
MAX_EVENT_DESC = 3000
MAX_EVENT_TITLE = 100

# News
MAX_NEWS_TITLE = 100
MAX_NEWS_CONTENT = 3000

# Car renting
MAX_CAR_DESC = 1000

# Book ad
MAX_BOOK_TITLE = 100
MAX_BOOK_CONTENT = 300
MAX_BOOK_AUTHOR = 100

# Song
MAX_SONG_TITLE = 200
MAX_SONG_AUTHOR = 200
MAX_SONG_CATEGORY = 100
MAX_SONG_CONTENT = 3000
MAX_SONG_MELODY = 200

# Imgs
MAX_IMG_NAME = 200

# Candidation
MAX_CANDIDATE_DESC = 1000

# Election
MAX_ELECTION_DESC = 2000

# Groups
MAX_GROUP_NAME = 200
MAX_GROUP_TYPE_NAME = 100
MAX_GROUP_USER_TYPE_NAME = 50

# Adventure mission
MAX_ADVENTURE_MISSION_NAME = 200
MAX_ADVENTURE_MISSION_DESC = 1000

# Nollning
MAX_NOLLNING_NAME = 200
MAX_NOLLNING_DESC = 2000

# Tags
MAX_TAG_NAME = 25
