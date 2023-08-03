import datetime
import re
import time

import bleach
import markdown
from django.contrib.auth.decorators import login_required

import CLAHub.base_settings


def conditional_login(func):
    if CLAHub.base_settings.LOGIN_EVERYWHERE:
        return login_required(func)
    else:
        return func


def set_text_tags_attributes():
    """Set which html tags and attributes are allowable for showing in
    texts."""
    allowed_attributes = bleach.sanitizer.ALLOWED_ATTRIBUTES

    #: Set of allowed tags
    allowed_tags = frozenset(
        (
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "code",
            "em",
            "i",
            "li",
            "ol",
            "strong",
            "ul",
            "span",
        )
    )

    allowed_attributes["span"] = ["class"]
    allowed_attributes["a"].append("onclick")
    allowed_attributes["a"].append("target")
    allowed_attributes["a"].append("rel")
    allowed_attributes["a"].append("class")
    allowed_attributes["a"].append("data-tooltip")
    return allowed_attributes, allowed_tags


def hyperlink_timestamps(id, text):
    """Add auto links for text timestamps, needs the text and the text object
    id."""
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
    """Compare each word to the csv word list from lexicon, highlighting any in
    red not found."""
    words = find_words_in_text(text_obj.orthographic_text.lower())
    # go through whole text and highlight any words notin lexicon
    text = text_obj.orthographic_text.lower()
    correct_words = 0
    total_words = 0

    # loop through words found in text and highlight
    for w in words:
        # find lexicon entry
        lex = [l for l in CLAHub.base_settings.lexicon if l["kgu"] == w]

        # no entry, highlight red
        if not lex:
            text = highlight_word(w, text, colour="red")
            total_words += 1
            continue

        lex = lex[0]  # take the 1st index of list

        # checked entry, black with link
        if lex["checked"]:
            text = highlight_word(w, text, colour="none", lexicon=lex)
            correct_words += 1
            total_words += 1
            # it is possible for a word to be in both checked and unchecked lists
            # if it is checked it should take priority
        # unchecked entry, green with link
        else:
            text = highlight_word(w, text, colour="green", lexicon=lex)
            total_words += 1

    for w in words:
        text = add_tooltip(w, text)
    # report accuracy of transcription to text model
    if total_words > 0:
        text_obj.known_words = f"{correct_words/total_words*100:.0f}%"
    return text


def highlight_word(word, text, colour="red", lexicon=None):
    """Replace the given word in a text with the same word withn a span tag to
    colour it."""
    f = re.compile(
        f"(^|[^a-z<>#])({word})($|[^a-z<>-])"
    )  # attempt to avoid highlighting parts of words
    highlight = f'<span class="{colour}">'

    # set the right link
    if lexicon:
        link = 'href="{lexicon_web_address}#{headword}"'.format(
            lexicon_web_address=CLAHub.base_settings.lexicon_web_address,
            headword=lexicon["headword"],
        )

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
                r'\1<a class="no-decoration" {link} target="_blank" rel="noopener noreferrer">{highlight}\2</span></a>\3'.format(
                    highlight=highlight, word=word, link=link
                ),
                text,
            )
        elif colour == "none":
            text = re.sub(
                f,
                r'\1<a class="no-decoration" {link} target="_blank" rel="noopener noreferrer">\2</a>\3'.format(
                    word=word, link=link
                ),
                text,
            )
    return text


def add_tooltip(word, text):
    """Add a data-tooltip css attribute to any anchors."""
    # find the lexicon entry to get english for tooltip
    lex = [l for l in CLAHub.base_settings.lexicon if l["kgu"] == word]
    if lex:
        lex = lex[0]
        if lex["pos"].startswith("v"):
            tooltip_text = f'{lex["eng"]}:  {lex["pos"]}'
        else:
            tooltip_text = lex["eng"]
    # return original text if no tooltip to add
    else:
        return text

    replace = re.compile(
        '(noreferrer")>(<span class="green">)?{word}'.format(word=word)
    )

    # do a text replace to insert a data-tooltip attribute
    return re.sub(
        replace,
        r'\1 data-tooltip="{tooltip_text}">\2{word}'.format(
            tooltip_text=tooltip_text, word=word
        ),
        text,
    )


def find_words_in_text(text):
    """Split the given text into a list of individual words.

    Ignore words starting with numbers (timestamps), or words in
    brackets
    """
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
