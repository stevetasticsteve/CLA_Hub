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
    try:
        with open(path) as f:
            data = csv.reader(f)
            return tuple([d[0] for d in data])
    except FileNotFoundError:
        return ("")


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
    # remove anything in brackets from the lexicon comparison
    search_text = text_obj.orthographic_text
    brackets = re.findall(re.compile(r"\(.+\)"), search_text)
    for b in brackets:
        search_text = search_text.replace(b, "")

    # find all the Kovol words written, having excluded brackets
    words = re.findall(re.compile(r"[a-zA-Z]+"), search_text) # search for a-z only, ignore numbers and puncuation
    words.sort(key=lambda x: len(x), reverse=True)
    words = list(set(words))

    # go through whole text and highlight any words notin lexicon
    text = text_obj.orthographic_text
    kovol_words = load_lexicon()
    correct_words = 0
    total_words = 0

    # add red highlighting to words not in lexicon
    for w in words:
        if w.lower() not in kovol_words:
            f = re.compile(f"[\s^'\"]{w}[\s$,.\"']") # attempt to avoid highlighting parts of words
            search = re.findall(f, text)
            for s in search:
                text = text.replace(s, f'<span class="red">{s}</span>')

            total_words += 1
            print("incorrect")
        # word is in lexicon
        else:
            print("correct")
            correct_words += 1
            total_words += 1
    
    # report accuracy of transcription to text model
    if total_words > 0:
        text_obj.known_words = f"{correct_words/total_words*100:.0f}%"
    print(f"total={total_words}, correct={correct_words}")
    return text


def format_text_html(text_obj):
    """Apply markdown, timestamp links and lexicon spelling info and return."""
    text = highlight_non_lexicon_words(text_obj)
    text = hyperlink_timestamps(text_obj.id, text)

    allowed_attributes, allowed_tags = set_text_tags_attributes()
    return markdown.markdown(
        bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes)
    )
