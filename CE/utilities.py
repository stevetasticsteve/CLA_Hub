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
    checked_path = "/home/steve/html/lexicon/checked_list.csv"
    unchecked_path = "/home/steve/html/lexicon/unchecked_list.csv"
    print(CLAHub.base_settings.lexicon[1])
    try:
        with open(checked_path) as f:
            checked_data = csv.reader(f)
            checked_data = tuple([d[0] for d in checked_data])
        with open(unchecked_path) as f:
            unchecked_data = csv.reader(f)
            unchecked_data = tuple([d[0] for d in unchecked_data])
        return checked_data, unchecked_data

    except FileNotFoundError:
        return ("No Lexicon",), ("No Lexicon",)


def set_text_tags_attributes():
    """Set which html tags and attributes are allowable for showing in texts"""
    allowed_attributes = bleach.sanitizer.ALLOWED_ATTRIBUTES
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS
    allowed_tags.append("span")
    allowed_attributes["span"] = ["class"]
    allowed_tags.append("table")
    allowed_attributes["table"] = ["thead"]
    allowed_attributes["table"] = ["tr"]
    allowed_attributes["table"] = ["th"]
    allowed_attributes["table"] = ["td"]
    allowed_attributes["a"].append("onclick")
    allowed_attributes["a"].append("target")
    allowed_attributes["a"].append("rel")
    allowed_attributes["a"].append("class")
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
    words = find_words_in_text(text_obj.orthographic_text.lower())

    # go through whole text and highlight any words notin lexicon
    text = text_obj.orthographic_text.lower()
    checked_lexicon_words, unchecked_lexicon_words = load_lexicon()
    correct_words = 0
    total_words = 0
    # print(words)

    # add red highlighting to words not in lexicon
    for w in words:
        if w in checked_lexicon_words:
            text = highlight_word(w, text, colour="none")
            correct_words += 1
            total_words += 1
            # it is possible for a word to be in both checked and unchecked lists
            # if it is checked it should take priority
            continue
        
        # word is in lexicon
        elif w in unchecked_lexicon_words:
            text = highlight_word(w, text, colour="green")
            total_words += 1
        
        else:
            text = highlight_word(w, text, colour="red")
            total_words += 1
        
    # report accuracy of transcription to text model
    if total_words > 0:
        text_obj.known_words = f"{correct_words/total_words*100:.0f}%"
    # print(f"total={total_words}, correct={correct_words}")
    return text


def highlight_word(word, text, colour="red"):
    """Replace the given word in a text with the same word withn a span tag to colour it"""
    f = re.compile(
        f'(^|[^a-z<>#])({word})($|[^a-z<>-])'
    )  # attempt to avoid highlighting parts of words
    highlight = f'<span class="{colour}">'

    # regex is non overlapping, so we run it twice. Excluding < and > mean we don't hit
    # the same match
    for i in range(2):
        if colour == "red":  # no hyperlink
            text = re.sub(
                f, r"\1{highlight}\2</span>\3".format(highlight=highlight), text
            )
        elif colour == "green":
            text = re.sub(
                f,
                r'\1<a class="no-decoration" href="http://192.168.0.100/lexicon/main_dict.html#{word}" target="_blank" rel="noopener noreferrer">{highlight}\2</span></a>\3'.format(
                    highlight=highlight, word=word
                ),
                text,
            )
        elif colour == "none":
            text = re.sub(
                f,
                r'\1<a class="no-decoration" href="http://192.168.0.100/lexicon/main_dict.html#{word}" target="_blank"rel="noopener noreferrer">\2</a>\3'.format(
                    word=word
                ),
                text,
            )
    return text


def find_words_in_text(text):
    """Split the given text into a list of individual words. Ignore words starting with numbers (timestamps),
    or words in brackets"""
    # remove anything in brackets from the lexicon comparison
    brackets = re.findall(re.compile(r"\([^\)]+\)"), text)
    for b in brackets:
        text = text.replace(b, "")
    
    # remove punctuation

    # find all the Kovol words written, having excluded brackets
    words = re.findall(
        re.compile(r"[a-z]+"), text
    )  # search for a-z only, ignore numbers
    words = list(set(words))
    words.sort(key=lambda x: len(x), reverse=True)
    return words


def format_text_html(text_obj):
    """Apply markdown, timestamp links and lexicon spelling info and return."""
    text = highlight_non_lexicon_words(text_obj)
    text = hyperlink_timestamps(text_obj.id, text)

    allowed_attributes, allowed_tags = set_text_tags_attributes()
    return markdown.markdown(
        bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes)
    )
