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
