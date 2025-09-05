# Here we collect some reused constants, like the maximum length of a name. They are referenced in db models and schemas

# Warning! These are used in db model definitions. Changing these will require db migration

# User
MAX_FIRST_NAME_LEN = 100
MAX_LAST_NAME_LEN = 100
MAX_TELEPHONE_LEN = 25

# Event
MAX_EVENT_DESC = 3000
MAX_EVENT_TITLE = 100
MAX_EVENT_LOCATION = 50
MAX_EVENT_DRESS_CODE = 20


# News
MAX_NEWS_TITLE = 100
MAX_NEWS_CONTENT = 3000

# Car renting
MAX_CAR_DESC = 1000
MAX_CAR_BLOCK = 1000

# Book ad
MAX_BOOK_TITLE = 100
MAX_BOOK_CONTENT = 300
MAX_BOOK_AUTHOR = 100

# Song
MAX_SONG_TITLE = 200
MAX_SONG_AUTHOR = 200
MAX_SONG_CATEGORY = 100
MAX_SONG_CONTENT = 5000
MAX_SONG_MELODY = 200

# Imgs
MAX_IMG_NAME = 200

# Candidation
MAX_CANDIDATE_DESC = 1000

# Election
MAX_ELECTION_TITLE = 100
MAX_ELECTION_DESC = 5000
MAX_SUB_ELECTION_TITLE = 150

# Groups
MAX_GROUP_NAME = 200
MAX_GROUP_TYPE_NAME = 100
MAX_GROUP_USER_TYPE_NAME = 50

# Adventure mission
MAX_ADVENTURE_MISSION_NAME = 200
MAX_ADVENTURE_MISSION_DESC = 2000

# Nollning
MAX_NOLLNING_NAME = 200
MAX_NOLLNING_DESC = 4000

# Door access
MAX_DOOR_NAME = 200
MAX_DOOR_ACCESS_MOTIVATION = 2000

# Tags
MAX_TAG_NAME = 25

# Pagination
NEWS_PER_PAGE = 20

# Council
MAX_COUNCIL_NAME = 100
MAX_COUNCIL_DESC = 3500

# Albums
MAX_ALBUM_TITLE = 300
MAX_ALBUM_DESC = 2000

# Document
MAX_DOC_TITLE = 300
MAX_DOC_CATEGORY = 100
MAX_DOC_FILE_NAME = 300

# Paths
MAX_PATH_LENGTH = 256

# Posts
MAX_POST_NAME = 60
MAX_POST_DESC = 2000

# Room booking
MAX_ROOM_DESC = 1000
MAX_RECURSION_TIME = 365  # In days, after this time the recursion will stop
MAX_RECURSION_STEPS = 50  # Maximum number of recursions allowed, to prevent infinite loops

# Event User
DEFAULT_USER_PRIORITY = "Övrigt"
