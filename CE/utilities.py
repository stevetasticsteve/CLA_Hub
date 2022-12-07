from django.contrib.auth.decorators import login_required
import CLAHub.base_settings

import bleach
import markdown
import re
import time
import datetime


def conditional_login(func):
    if CLAHub.base_settings.LOGIN_EVERYWHERE:
        return login_required(func)
    else:
        return func


def format_text_html(text_obj):
    """Take a string from the database representing a string. Apply markdown and auto linking
    of timestamp info and return."""

    time_stamp_re = re.compile("\d:\d\d:\d\d(?!<)")

    while re.search(time_stamp_re, text_obj.orthographic_text):
        match = re.search(time_stamp_re, text_obj.orthographic_text)
        timestamp = match.group()
        d = time.strptime(timestamp, "%H:%M:%S")
        seconds = datetime.timedelta(
            hours=d.tm_hour, minutes=d.tm_min, seconds=d.tm_sec
        ).total_seconds()
        text_obj.orthographic_text = text_obj.orthographic_text.replace(
            timestamp,
            f'<a href="#a" onClick="{{text_{text_obj.id}_audio.currentTime={seconds}}};">{timestamp}</a>',
        )

    allowed_attributes = bleach.sanitizer.ALLOWED_ATTRIBUTES
    allowed_attributes["a"].append("onclick")

    return markdown.markdown(
        bleach.clean(text_obj.orthographic_text, attributes=allowed_attributes)
    )
