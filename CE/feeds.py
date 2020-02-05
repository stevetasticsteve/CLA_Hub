from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse

from CE.models import Text
from CLAHub.base_settings import BASE_DIR

import subprocess
import os

server_url = "http://192.168.0.151:8000/"
#todo server_url is hardcoded. Must get the host address some way


class iTunesFeed(Rss201rev2Feed):
    def rss_attributes(self):
        return {
            "version": self._version,
            "xmlns:atom": "http://www.w3.org/2005/Atom",
            'xmlns:itunes': u'http://www.itunes.com/dtds/podcast-1.0.dtd'
        }

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        handler.addQuickElement('itunes:subtitle', self.feed['subtitle'])
        handler.addQuickElement('itunes:author', self.feed['author_name'])
        handler.addQuickElement('itunes:summary', self.feed['description'])
        handler.addQuickElement('itunes:category',
                                self.feed['iTunes_category'])
        handler.addQuickElement('itunes:explicit',
                                self.feed['iTunes_explicit'])
        handler.startElement("itunes:owner", {})
        handler.addQuickElement('itunes:name', self.feed['iTunes_name'])
        handler.endElement("itunes:owner")
        handler.addQuickElement('itunes:image', self.feed['iTunes_image_url'])

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement(u'itunes:summary', item['summary'])
        handler.addQuickElement(u'itunes:duration', item['duration'])
        handler.addQuickElement(u'itunes:explicit', item['explicit'])


class PodcastFeed(Feed):
    title = "CLAHub"
    link = "https://github.com/stevetasticsteve/CLA_Hub"
    author_name = "CLAHub"
    author_link = "https://github.com/stevetasticsteve"
    categories = ["Language Learning"]
    feed_copyright = "Creative Commons Attribution 4.0 International"
    description = "CLAHub provides missionary teams with a collaborative tool for creating and maintaining" \
                  "a culture and language file. This podcast feed contains uploaded vernacular texts that are stored" \
                  "in the CLAHub database"

    iTunes_explicit = 'no'
    iTunes_name = "CLAHub"
    iTunes_image_url = server_url + "static/logo/CLAHub_podcast.jpeg"
    iTunes_summary = description
    feed_type = iTunesFeed

    def items(self):
        return Text.objects.order_by('-date_created').exclude(audio='')

    def item_title(self, item):
        return item.text_title

    def item_description(self, item):
        if item.orthographic_text:
            return item.orthographic_text
        elif item.phonetic_text:
            return item.phonetic_text
        else:
            return 'No description for this text'

    def item_link(self, item):
        return reverse('CE:view', args=str(item.ce.pk))

    def item_author_name(self, item):
        return "CLAHub"

    def item_pubdate(self, item):
        return item.date_created

    def feed_extra_kwargs(self, obj):
        return {
            'iTunes_name': self.iTunes_name,
            'iTunes_image_url': self.iTunes_image_url,
            'iTunes_explicit': self.iTunes_explicit,
            'iTunes_category': 'Language Learning',
            'iTunes_summary': self.iTunes_summary,
        }

    def item_extra_kwargs(self, item):
        return {
            'summary': item.text_title,
            'duration': self.duration,
            'explicit': 'no',
        }

    def item_enclosure_url(self, item):
        return server_url + 'uploads/' + str(item.audio)

    def item_enclosure_length(self, item):
        audio_path = os.path.join(BASE_DIR, 'uploads', str(item.audio))
        args = ("ffprobe", "-show_entries", "format=duration", "-i", audio_path)
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        duration_info = p.stdout.read()
        duration = str(duration_info)
        duration = duration.lstrip("b'[FORMAT]\\nduration=")
        duration = duration.rstrip("\\n[/FORMAT]\\n'")
        self.duration = duration.split('.')[0]
        return self.duration

    def item_enclosure_mime_type(self, item):
        return 'audio/mp3'
