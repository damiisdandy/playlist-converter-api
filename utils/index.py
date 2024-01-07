import random
import string


def get_playlist_duration(duration: int) -> str:
    """
    Convert milliseconds to format (e.g 2 hours, 30 minutes)
    """
    hours = int(duration / 3600000)
    minutes = int((duration - (3600000 * hours)) / 60000)

    def is_plural(time: int) -> str:
        if time > 1:
            return "s"
        else:
            return ""
    if hours > 0:
        return f"{hours} hour{is_plural(hours)}, {minutes} minute{is_plural(minutes)}"
    else:
        return f"{minutes} minute{is_plural(minutes)}"


def get_track_duration(duration: int) -> str:
    """
    Convert milliseconds to format (e.g 2:32)
    """
    minutes = int(duration / 60000)
    seconds = int((duration - (60000 * minutes)) / 1000)

    def to_tens(num: int):
        if (num < 9):
            return f"{str(num)}0"
        else:
            return str(num)
    return f"{minutes}:{to_tens(seconds)}"


def track_duration_ms(duration: str) -> int:
    """
    Convert format 2:32 to milliseconds
    """
    minutes = int(duration.split(":")[0])
    seconds = int(duration.split(":")[1])
    return (minutes * 60000) + (seconds * 1000)


def generate_random_string(length: int) -> str:
    return ''.join((random.choice(string.ascii_lowercase)
                    for x in range(length)))
