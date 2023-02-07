from django.contrib.auth.decorators import login_required
import CLAHub.base_settings

import bleach
import markdown
import re
import time
import datetime
import csv


def conditional_login(func):
    if CLAHub.base_settings.LOGIN_EVERYWHERE:
        return login_required(func)
    else:
        return func


def load_lexicon():
    """Generates a tuple of all the known Kovol words for quick spell checking"""
    path = "/home/steve/html/lexicon/word_list.csv"
    # path = "word_list.csv"
    with open(path) as f:
        data = csv.reader(f)
        return tuple([d[0] for d in data])


def set_text_tags_attributes():
    """Set which html tags and attributes are allowable for showing in texts"""
    allowed_attributes = bleach.sanitizer.ALLOWED_ATTRIBUTES
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS
    allowed_tags.append("span")
    allowed_attributes["span"] = ["class"]
    allowed_attributes["a"].append("onclick")
    return allowed_attributes, allowed_tags


def hyperlink_timestamps(id, text):
    """add auto links for text timestamps, needs the text and the text object id"""
    time_stamp_re = re.compile("\d:\d\d:\d\d(?!<)")
    while re.search(time_stamp_re, text):
        match = re.search(time_stamp_re, text)
        timestamp = match.group()
        d = time.strptime(timestamp, "%H:%M:%S")
        seconds = datetime.timedelta(
            hours=d.tm_hour, minutes=d.tm_min, seconds=d.tm_sec
        ).total_seconds()
        text = text.replace(
            timestamp,
            f'<a href="#a" onClick="{{text_{id}_audio.currentTime={seconds}}};">{timestamp}</a>',
        )
    return text


def highlight_non_lexicon_words(text_obj):
    """Compare each word to the csv word list from lexicon, highlighting any in red not found"""
    kovol_words = load_lexicon()
    # words = text_obj.orthographic_text.split(" ")
    words = re.split(r"[ \n\r]", text_obj.orthographic_text)
    text = []
    time_stamp_re = re.compile(r"\d:\d\d:\d\d(?!<)")
    digit_re = re.compile(r"(\d)+[.:]*")
    bracket = False  # flag to mark where a bracket starts and ends
    # Create counters for total words and words found in lexicon
    correct_words = 0
    total_words = 0

    for w in words:
        print(f"w='{w}'")
        # ignore timestamp
        if re.search(time_stamp_re, w):
            highlight = False
            print("timestamp")
        # ignore numbers
        elif re.search(digit_re, w):
            highlight = False
            print("number")
        # ignore whitespace
        elif not w.strip():
            highlight = False
            print("whitespace")
        # ignore brackets
        elif w.lstrip().startswith("("):
            highlight = False
            bracket = True
            print("open bracket")
        elif w.rstrip().endswith(")"):
            highlight = False
            bracket = False
            print("close bracket")
        elif bracket:
            highlight = False
            print("in bracket")
        # word not in lexicon
        elif w.strip("? ,.\n\"").lower() not in kovol_words:
            highlight = True
            total_words += 1
            print("incorrect")
        # word is in lexicon
        else:
            print("correct")
            highlight = False
            correct_words += 1
            total_words += 1
        
        if highlight:
            text.append(f'<span class="red">{w}</span>')
        else:
            text.append(w)

    if total_words > 0:
        text_obj.known_words = f"{correct_words/total_words*100:.0f}%"
    print(f"total={total_words}, correct={correct_words}")
    return " ".join(text)


def format_text_html(text_obj):
    """Apply markdown, timestamp links and lexicon spelling info and return."""
    text = highlight_non_lexicon_words(text_obj)
    text = hyperlink_timestamps(text_obj.id, text)

    allowed_attributes, allowed_tags = set_text_tags_attributes()
    return markdown.markdown(
        bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes)
    )
