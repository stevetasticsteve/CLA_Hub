from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator

import re

# TODO. -oogot, updated modified_by on POST, version history, synonoms

kovol_text_validator = RegexValidator(
    regex="^[ieauowtyplkhgdsbnm]+$",
    message="You must only use letters in the Kovol orthography",
    flags=re.IGNORECASE,
)
tok_pisin_validator = RegexValidator(
    regex="^[abdefghiklmnoprstuvwy ]+$",
    message="You must only use letters in the Tok Pisin orthography",
    flags=re.IGNORECASE,
)
no_symbols_validator = RegexValidator(
    regex="^[a-z 2]+$",
    message="You cannot put symbols here",
    flags=re.IGNORECASE,
)


class LexiconEntry(models.Model):
    "A base class other models can inherit from"
    # defintions
    eng = models.CharField(
        verbose_name="English",
        max_length=35,
        null=False,
        blank=False,
        validators=[no_symbols_validator],
    )
    tpi = models.CharField(
        verbose_name="Tok Pisin",
        max_length=25,
        null=False,
        blank=False,
        validators=[tok_pisin_validator],
    )
    comments = models.TextField(
        null=True,
        blank=True,
        help_text="extra comments or an extended definition information",
        max_length=250,
    )
    review = models.CharField(
        choices=(
            ("0", "No review"),
            ("1", "Review now"),
            ("2", "Review after literacy"),
        ),
        max_length=1,
        help_text="Should this word be marked for review?",
        default="0",
        null=False,
    )
    review_comments = models.TextField(
        blank=True,
        null=True,
    )
    review_user = models.CharField(max_length=10, editable=False, blank=True, null=True)
    review_time = models.DateField(editable=False, null=True)
    created = models.DateField(editable=False, auto_now_add=True)
    modified = models.DateField(editable=False, auto_now=True)
    modified_by = models.CharField(editable=False, blank=True, null=True, max_length=10)

    def save(self, *args, **kwargs):
        self.eng = self.eng.lower()
        self.tpi = self.tpi.lower()
        return super(LexiconEntry, self).save(*args, **kwargs)


class LexiconVerbEntry(LexiconEntry):
    """A Kovol verb and all it's conjugations. Inherited by Imengis and Matat."""

    verb_text_fields = [
        "past_1s",
        "past_2s",
        "past_3s",
        "past_1p",
        "past_2p",
        "past_3p",
        "present_1s",
        "present_2s",
        "present_3s",
        "present_1p",
        "present_2p",
        "present_3p",
        "future_1s",
        "future_2s",
        "future_3s",
        "future_1p",
        "future_2p",
        "future_3p",
        "sg_imp",
        "pl_imp",
        "enclitic_same_actor",
        "enclitic_1s",
        "enclitic_1p",
        "enclitic_2s",
        "enclitic_2p",
        "nominalizer",
    ]

    # past tense conjugations
    past_1s = models.CharField(
        verbose_name="1s past",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    past_1s_checked = models.BooleanField(default=False)
    past_2s = models.CharField(
        verbose_name="2s past",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    past_2s_checked = models.BooleanField(default=False)
    past_3s = models.CharField(
        verbose_name="3s past",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    past_3s_checked = models.BooleanField(default=False)
    past_1p = models.CharField(
        verbose_name="1p past",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    past_1p_checked = models.BooleanField(default=False)
    past_2p = models.CharField(
        verbose_name="2p past",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    past_2p_checked = models.BooleanField(default=False)
    past_3p = models.CharField(
        verbose_name="3p past",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    past_3p_checked = models.BooleanField(default=False)

    # present tense conjugations
    present_1s = models.CharField(
        verbose_name="1s present",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    present_1s_checked = models.BooleanField(default=False)
    present_2s = models.CharField(
        verbose_name="2s present",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    present_2s_checked = models.BooleanField(default=False)
    present_3s = models.CharField(
        verbose_name="3s present",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    present_3s_checked = models.BooleanField(default=False)
    present_1p = models.CharField(
        verbose_name="1p present",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    present_1p_checked = models.BooleanField(default=False)
    present_2p = models.CharField(
        verbose_name="2p present",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    present_2p_checked = models.BooleanField(default=False)
    present_3p = models.CharField(
        verbose_name="3p present",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    present_3p_checked = models.BooleanField(default=False)

    # future tense conjugations
    future_1s = models.CharField(
        verbose_name="1s future",
        null=True,
        blank=False,
        max_length=25,
        validators=[kovol_text_validator],
    )
    future_1s_checked = models.BooleanField(default=False)
    future_2s = models.CharField(
        verbose_name="2s future",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    future_2s_checked = models.BooleanField(default=False)
    future_3s = models.CharField(
        verbose_name="3s future",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    future_3s_checked = models.BooleanField(default=False)
    future_1p = models.CharField(
        verbose_name="1p future",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    future_1p_checked = models.BooleanField(default=False)
    future_2p = models.CharField(
        verbose_name="2p future",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    future_2p_checked = models.BooleanField(default=False)
    future_3p = models.CharField(
        verbose_name="3p future", null=True, blank=True, max_length=25
    )
    future_3p_checked = models.BooleanField(default=False)

    # imperative conjugations
    sg_imp = models.CharField(
        verbose_name="singular imperative",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    sg_imp_checked = models.BooleanField(default=False)
    pl_imp = models.CharField(
        verbose_name="plural imperative",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    pl_imp_checked = models.BooleanField(default=False)

    # enclitic conjugations
    enclitic_same_actor = models.CharField(
        verbose_name="same actor encltic",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    enclitic_same_actor_checked = models.BooleanField(default=False)
    enclitic_1s = models.CharField(
        verbose_name="1s encltic",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    enclitic_1s_checked = models.BooleanField(default=False)
    enclitic_1p = models.CharField(
        verbose_name="1p encltic",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    enclitic_1p_checked = models.BooleanField(default=False)
    enclitic_2s = models.CharField(
        verbose_name="2s/3s encltic",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    enclitic_2s_checked = models.BooleanField(default=False)
    enclitic_2p = models.CharField(
        verbose_name="2p/3p encltic",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    enclitic_2p_checked = models.BooleanField(default=False)

    # nominalizer
    nominalizer = models.CharField(
        verbose_name="nominalizer",
        null=True,
        blank=True,
        max_length=25,
        validators=[kovol_text_validator],
    )
    nominalizer_checked = models.BooleanField(default=False)

    pos = models.CharField(
        verbose_name="part of speach",
        null=False,
        blank=False,
        max_length=5,
        default="v",
        editable=False,
    )

    def save(self, *args, **kwargs):
        for text in self.verb_text_fields:
            value = getattr(self, text)
            setattr(self, text, value.lower())
        return super(LexiconVerbEntry, self).save(*args, **kwargs)

    def get_conjugations(self):
        return [getattr(self, t) for t in self.verb_text_fields]


#
# Models for storing verb info
#
class ImengisVerb(LexiconVerbEntry):
    """A Kovol verb and all it's conjugations."""

    def __str__(self):
        """The string repr is used to order alphabetetically."""
        return f"{self.future_1s}, {self.eng}"

    def get_absolute_url(self):
        return reverse("lexicon:verb-detail", args=[self.pk])


class VerbSpellingVariation(models.Model):
    """A linked entry to ImengisVerb that enables recording spelling variations."""

    verb = models.ForeignKey(ImengisVerb, on_delete=models.CASCADE)
    spelling_variation = models.CharField(
        verbose_name="spelling variation",
        max_length=25,
        blank=False,
        null=False,
        help_text="write the spelling variation here",
        validators=[kovol_text_validator],
    )
    conjugation = models.CharField(
        choices=(
            ("1sp", "1s past"),
            ("2sp", "2s past"),
            ("3sp", "3s past"),
            ("1pp", "1p past"),
            ("2pp", "2p past"),
            ("3pp", "3p past"),
            ("1spr", "1s present"),
            ("2spr", "2s present"),
            ("3spr", "3s present"),
            ("1ppr", "1p present"),
            ("2ppr", "2p present"),
            ("3ppr", "3p present"),
            ("1sf", "1s future"),
            ("2sf", "2s future"),
            ("3sf", "3s future"),
            ("1pf", "1p future"),
            ("2pf", "2p future"),
            ("3pf", "3p future"),
            ("simp", "singular imperative"),
            ("pimp", "plural imperative"),
            ("saen", "same actor enclitic"),
            ("1sen", "1s enclitic"),
            ("1pen", "1p enclitic"),
            ("2sen", "2s/3s enclitic"),
            ("2pen", "2p/3p enclitic"),
            ("nom", "nominalizer"),
        ),
        max_length=4,
        null=False,
        blank=False,
    )

    def get_absolute_url(self):
        return reverse("lexicon:verb-detail", args=[self.verb.pk])

    def __str__(self):
        return f"spelling variation for {self.conjugation} {self.verb}"


class VerbSense(models.Model):
    """A linked entry to Kovol verb that allows adding of different senses."""

    sense = models.CharField(
        verbose_name="Sense",
        help_text="The English for an additional sense to a verb",
        max_length=45,
        blank=True,
        null=False,
        validators=[no_symbols_validator],
    )
    verb = models.ForeignKey(ImengisVerb, on_delete=models.CASCADE)

    def __str__(self):
        return f"Additional sense for {self.verb}"

    def get_absolute_url(self):
        """Return the detail page if asked for a specific url for an entry."""
        return reverse("lexicon:verb-detail", args=[self.verb.pk])


class MatatVerb(LexiconVerbEntry):
    """Subclass the main Kovol verb to record a Matat dialect version."""

    imengis_verb = models.ForeignKey(
        ImengisVerb,
        verbose_name="Imengis verb",
        help_text="The original verb this entry is linked to",
        on_delete=models.CASCADE,
        related_name="matat",
    )

    def __str__(self):
        return f"{self.imengis_verb} matat version"

    def get_absolute_url(self):
        """Return the detail page if asked for a specific url for an entry."""
        return reverse("lexicon:verb-detail", args=[self.imengis_verb.pk])


#
# Word models
#

# TODO  Verb allowable prefixes
# models for storing word info
class KovolWord(LexiconEntry):
    kgu = models.CharField(
        verbose_name="Imengis",
        max_length=25,
        blank=False,
        null=False,
        unique=True,
        validators=[kovol_text_validator],
    )
    checked = models.BooleanField(default=False, blank=False, null=False)
    matat = models.CharField(
        verbose_name="Matat",
        max_length=25,
        blank=True,
        null=True,
        validators=[kovol_text_validator],
    )
    pos = models.CharField(
        verbose_name="part of speech",
        max_length=5,
        blank=True,
        null=True,
        choices=(
            ("n", "noun"),
            ("adj", "adjective"),
            ("adv", "adverb"),
            ("pn", "pronoun"),
        ),
    )

    def __str__(self):
        """The str repr is used to order alphabetically."""
        return self.kgu

    def save(self, *args, **kwargs):
        self.kgu = self.kgu.lower()
        return super(KovolWord, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the detail page if asked for a specific url for an entry."""
        return reverse("lexicon:word-detail", args=[self.pk])


class KovolWordSpellingVariation(models.Model):
    """A linked entry to KovolWord to track spelling variations."""

    word = models.ForeignKey(
        KovolWord, on_delete=models.CASCADE, related_name="spelling_variation"
    )
    spelling_variation = models.CharField(
        verbose_name="spelling variation",
        max_length=25,
        blank=False,
        null=False,
        help_text="write the spelling variation here",
        validators=[kovol_text_validator],
    )

    def get_absolute_url(self):
        """Return the detail page if asked for a specific url for an entry."""
        return reverse("lexicon:word-detail", args=[self.word.pk])


class KovolWordSense(models.Model):
    """A linked entry to KovolWord to track additional senses."""

    word = models.ForeignKey(KovolWord, on_delete=models.CASCADE, related_name="senses")
    sense = models.CharField(
        verbose_name="sense",
        max_length=25,
        blank=False,
        null=False,
        help_text="write the English for the additional sense here",
        validators=[no_symbols_validator],
    )

    def get_absolute_url(self):
        """Return the detail page if asked for a specific url for an entry."""
        return reverse("lexicon:word-detail", args=[self.word.pk])