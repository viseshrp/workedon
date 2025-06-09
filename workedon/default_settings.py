from tzlocal import get_localzone

DATE_FORMAT = "%a %b %d %Y"
TIME_FORMAT = "%H:%M %z %Z"
DATETIME_FORMAT = ""
TIME_ZONE = str(get_localzone())
DURATION_UNIT = "minutes"
