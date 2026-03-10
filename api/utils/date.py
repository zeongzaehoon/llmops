from datetime import datetime, timedelta
from zoneinfo import ZoneInfo



def get_utc_now() -> datetime:
    return datetime.now(ZoneInfo("UTC"))