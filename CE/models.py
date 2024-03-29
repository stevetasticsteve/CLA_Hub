import re

import bleach
from django.core import exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager

import CE.settings
import people.models
from CLAHub import tools

integer_regex = re.compile("\d+")
anchor_regex = re.compile("<a.*?</a>")


def check_if_index_within_html_anchor(string, index):
    # Returns true if the index provided sits within an <a></a> tag in the provided string
    num_anchors = len(re.findall(anchor_regex, string))
    for anchor in range(num_anchors):
        match = re.search(anchor_regex, string)
        if index >= match.start():
            if index <= match.end():
                return True
        string = string[match.end() :]
        index = index - match.end()


class CultureEvent(models.Model):
    title = models.CharField(max_length=60, blank=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=20)
    # plain text description is what the user has entered. description is a processed version of the plain text
    # that adds hyperlinks and is displayed escaped so the html generates
    description = models.TextField(blank=True)
    description_plain_text = models.TextField(blank=True)

    differences = models.TextField(blank=True)
    interpretation = models.TextField(blank=True)
    slug = models.SlugField(
        unique=True
    )  # set in save function, form doesn't need to validate it
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        self.check_unique_title()
        # copy the user's input from plain text to description to be processed
        # uses bleach to remove potentially harmful HTML code
        self.description = bleach.clean(self.description_plain_text)

        if CE.settings.auto_cross_reference:
            self.auto_cross_ref()
        else:
            self.find_tag()
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def check_unique_title(self):
        ces = CultureEvent.objects.exclude(pk=self.pk)
        if self.title.lower() in [ce.title.lower() for ce in ces]:
            raise exceptions.ValidationError("CE already exists", code="invalid")

    def find_tag(self):
        # todo case sensitive, shouldn't be
        # find anything in the plain text description with {} around it and replace it with a hyperlink if valid
        # only triggers if auto_cross_reference is False
        tags = re.findall(r"{.+?}", self.description)
        ce_slugs = self.list_slugs()
        for tag in tags:
            content = tag
            content = content.strip("{")
            content = content.strip("}")
            for i, title_slug in enumerate(ce_slugs):
                # if slug found within {} replace with hyperlink
                if title_slug in slugify(content):
                    title_deslug = title_slug.replace("-", " ")
                    slug_href = '<a href="' + title_slug + '">' + title_deslug + "</a>"
                    self.description = self.description.replace(
                        "{" + title_deslug + "}", slug_href
                    )
                # if none of the title slugs are found remove the {}
                elif i == len(ce_slugs) - 1:
                    self.description = self.description.replace(tag, content)

    def auto_cross_ref(self):
        # search the plain text description for slugs and replace them with hyperlinks if found
        # only triggers if auto_cross_reference is True

        # turn user entered data into a slug and search it for slugs that represent CEs
        slugged_description = slugify(self.description_plain_text)
        ce_slugs = self.list_slugs()
        ce_slugs.sort(key=len)
        ce_slugs.reverse()  # order longest to shortest = greedy matching
        # check the slugged description for each ce title starting longest, going to shortest
        for title_slug in ce_slugs:
            if title_slug in slugged_description:
                # Loop variables to track when to move on
                i = 0
                start_next_search = 0
                # progressively work through text to find all occurrences of slug
                while i < slugged_description.count(title_slug):
                    i += 1
                    # retrieve the title so a string can be returned that matches the case
                    ce_title = CultureEvent.objects.get(slug=title_slug).title
                    slug_href = (
                        '<a href="' + title_slug + '">' + ce_title + "</a>"
                    )  # anchor to insert

                    # find the index of the match. Set start point for next loop
                    position = self.description.lower().find(
                        ce_title.lower(), start_next_search
                    )
                    start_next_search = position + len(slug_href)

                    # if the match is in a preexisting anchor move the loop on
                    if check_if_index_within_html_anchor(self.description, position):
                        continue

                    # insert the anchor at the desired position, replacing the found match
                    # Can't just use replace as it will replace things within anchors we already inserted
                    # Can't modify self.description outside of the link position - must maintain user formatting.
                    part1 = self.description[:position]
                    part2 = self.description[position + len(ce_title) :]
                    self.description = slug_href.join([part1, part2])
                    # start the next loop searching after the anchor we just inserted

    def list_slugs(self):
        ce_objects = CultureEvent.objects.all()
        ce_slugs = [i.slug for i in ce_objects]
        return ce_slugs

    def __str__(self):
        return str(self.title)


class Visit(models.Model):
    ce = models.ForeignKey("CultureEvent", on_delete=models.CASCADE)
    team_present = models.CharField(blank=True, max_length=60)
    nationals_present = models.CharField(blank=True, max_length=60)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.ce)


# provide file folders to save audio and pictures in using foreign keys
def picture_folder(instance, filename):
    return "/".join(["CultureEventFiles", str(instance.ce.id), "images", filename])


def audio_folder(instance, filename):
    return "/".join(["CultureEventFiles", str(instance.ce.id), "audio", filename])


class Picture(models.Model):
    ce = models.ForeignKey("CultureEvent", on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=picture_folder, blank=True)

    # blank=True is a fudge. Trying to display multiple models in a single form and it wont'
    # submit if there is validation. The view function makes sure blank entries aren't saved though

    def __str__(self):
        return "Picture for " + str(self.ce)

    def save(self):
        if self.picture:
            if tools.check_already_imported(self.picture):
                return None  # exit function, don't save anything
            self.picture = tools.compress_picture(self.picture, (1200, 1200))
        super(Picture, self).save()


class Text(models.Model):
    genres = [
        ("1", "Narrative"),
        ("2", "Hortatory"),
        ("3", "Procedural"),
        ("4", "Expository"),
        ("5", "Descriptive"),
    ]
    standard = [
        ("1", "Unchecked"),
        ("2", "Double checked by author"),
        ("3", "Checked by team mate"),
        ("4", "Approved by whole team"),
        ("5", "Valid for linguistic analysis"),
    ]
    ce = models.ForeignKey("CultureEvent", on_delete=models.PROTECT)
    text_title = models.CharField(max_length=50, blank=True)
    audio = models.FileField(upload_to=audio_folder, blank=True)
    phonetic_text = models.TextField(blank=True)
    phonetic_standard = models.CharField(
        choices=standard, max_length=30, default="1", blank=True
    )
    orthographic_text = models.TextField(blank=True)
    discourse_type = models.CharField(choices=genres, max_length=15, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=20, blank=True)
    speaker_plain_text = models.CharField(max_length=50, blank=True)
    speaker = models.CharField(max_length=80, blank=True)

    def save(self):
        if self.audio:
            if tools.check_already_imported(self.audio):
                # don't duplicate audio in uploads during tests
                self.audio.upload_to = "temp"  # todo duplicates still added
        # search for integers in speaker field and provide link to profile if found
        if self.speaker_plain_text:
            integers = re.findall(integer_regex, self.speaker_plain_text)
            self.speaker = bleach.clean(self.speaker_plain_text)
            for match in integers:
                try:
                    link = people.models.Person.objects.get(pk=match)
                    self.speaker = self.speaker.replace(
                        match,
                        '<a href="/clahub/people/' + match + '"> ' + link.name + "</a>",
                    )
                except ObjectDoesNotExist:
                    pass

        super(Text, self).save()

    def __str__(self):
        return str(self.text_title)


class Question(models.Model):
    def __init__(self, *args, **kwargs):
        # init method injects 'form-control' in to enable bootstrap styling
        super(Question, self).__init__(*args, **kwargs)
        self.original_answer = self.answer

    ce = models.ForeignKey("CultureEvent", on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=200, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    asked_by = models.CharField(max_length=30)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=20)
    answered_by = models.CharField(max_length=20)

    def __str__(self):
        return "Question about " + str(self.ce) + ": " + str(self.question)
