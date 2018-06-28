#~ rss-reader-skill - A simple rss reader skill for mycroft.
#~ Copyright (C) 2018  backassward
#~ Github - https://github.com/backassward

#~ This program is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.

#~ This program is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.

#~ You should have received a copy of the GNU General Public License
#~ along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import shelve
from time import localtime
from feedparser import parse
from operator import attrgetter
from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_file_handler
from mycroft.util.log import LOG
from mycroft.audio import wait_while_speaking


class Database():
    FEED_DATA = join(dirname(__file__), 'feed-data')

    def __init__(self):
        self.db = shelve.open(self.FEED_DATA)

    def db_read(self, name):
        return self.db.get(name, localtime(0))

    def db_update(self, feeds):
        for feed in feeds:
            name = feed.get_instance('name')
            if (name in self.db
                    and self.db[name] > feed.get_instance('last_access')):
                continue
            self.db[name] = feed.get_instance('last_access')

    def db_close(self):
        self.db.close()


class Article():
    def __init__(self, entry):
        self.title = entry.title
        self.summary = self._html_cleanup(entry.summary)
        self.author = getattr(entry, 'author', 'Not available')
        self.link = entry.link
        self.date = entry.published_parsed

    def _html_cleanup(self, string):
        return re.sub('<[^<]+?>', '', string)

    def __eq__(self, other):
        return self.date == other.date

    def __lt__(self, other):
        return self.date < other.date

    def get_instance(self, instance):
        return getattr(self, instance)


class Feed():
    def __init__(self, name, url, last_access):
        self.name = name
        self.parsed = parse(url)
        self.last_access = last_access
        self.articles = []

        for entry in self.parsed['entries']:
            # If the article was published after the user's last access
            if entry.published_parsed > self.last_access:
                self.articles.append(Article(entry))

        self.articles.sort()

    def get_count(self):
        return len(self.articles)

    def get_article(self):
        return self.articles.pop(0)

    def get_instance(self, instance):
        return getattr(self, instance)

    def update_last_access(self, date):
        self.last_access = date


class RssReader(MycroftSkill):
    SETTINGS_NAMES = ['nameone', 'nametwo', 'namethree']
    SETTINGS_URLS = ['urlone', 'urltwo', 'urlthree']

    def __init__(self):
        MycroftSkill.__init__(self)
        self.db = None
        self.feeds = []
        self.config = []

    @intent_file_handler('check.feeds.intent')
    def handle_check_feeds_intent(self, message):
        self.db = Database()
        utter = message.data['utterance']

        self.get_config()
        assert self.config, 'self.config is empty'

        self.get_feeds(utter)
        assert self.feeds, 'self.feeds is empty'

        self.article_count()
        self.db.db_close()

    def get_config(self):
        names = [self.settings[name] for name in self.SETTINGS_NAMES]
        urls = [self.settings[url] for url in self.SETTINGS_URLS]

        # Stores only valid couples of feed names and URLs
        self.config = [[n, u] for n, u in zip(names, urls) if n and u]

        # Configuration consistency check (XOR gate)
        if [[n, u] for n, u in zip(names, urls) \
                if (not (n and u) and (n or u))]:
            LOG.warning('skill-rss-reader: skill config inconsistent')

    def get_feeds(self, utter):
        self.feeds = []
        for name, url in self.get_user_query(utter):
            last_access = getattr(self.db, 'db_read')(name)
            self.feeds.append(Feed(name, url, last_access))

    def get_user_query(self, utter):
        user_query = []
        for name, url in self.config:
            if name.lower() in utter.lower():
                user_query = [[name, url]]
                break
            user_query.append([name, url])
        return user_query

    def article_count(self):
        a = self.translate_namedvalues('new.article', delim=',')

        for feed in self.feeds:
            data = {
                'name': feed.get_instance('name'),
                'number': feed.get_count(),
                'article': a['singular'] if feed.get_count() == 1 else a['plural']
                }
            self.speak_dialog('feed.count', data)

    @intent_file_handler('read.feeds.intent')
    def handle_read_feeds_intent(self, message):
        self.db = Database()
        utter = message.data['utterance']

        self.get_config()
        assert self.config, 'self.conf is empty'

        self.get_feeds(utter)
        assert self.feeds, 'self.feeds is empty'

        self.read_feeds()
        self.db.db_update(self.feeds)
        self.db.db_close()

    def read_feeds(self):
        choice = self.translate_namedvalues('choice.options', delim=',')
        # Dictionary with allowed user commands. 
        # Keys are in the user's own language to match his/her utter.  
        options = {choice[key]:key for key in choice}

        for feed in self.feeds:
            if feed.get_count() == 0:
                # Make sure the user knows if there are no new articles
                self.article_count()
                continue

            self.speak_dialog('feed.read', 
                              {'name': feed.get_instance('name')})

            while (feed.get_count() != 0):
                article = feed.get_article()

                self.speak(article.get_instance('title'))

                if article.get_instance('date') > feed.get_instance('last_access'):
                    feed.update_last_access(article.get_instance('date'))

                while True:
                    wait_while_speaking()
                    utter = self.get_response('choice.prompt',
                                              on_fail='choice.error',
                                              num_retries=2)

                    if (not utter) or (choice['stop'] in utter):
                        return

                    if choice['next'] in utter:
                        break

                    for x in options:
                        if x in utter:
                            # User command fires up the desired method
                            getattr(self, options.get(x))(feed, article)
                            break
                    else:
                        self.invalid(feed, article)

    def author(self, feed, article):
        self.speak(article.get_instance('author'))

    def repeat(self, feed, article):
        self.speak(article.get_instance('title'))

    def summary(self, feed, article):
        self.speak(article.get_instance('summary'))

    def sync(self, feed, article):
        feed.update_last_access(localtime())

    def invalid(self, feed, article):
        LOG.debug('skill-rss-reader: the supplied utter is invalid')
        self.speak_dialog('choice.error')

    def email(self, feed, article):
        name = feed.get_instance('name')
        title = article.get_instance('title')
        link = article.get_instance('link')

        subject = ''.join([name, ' feed - ', title[:20], '...'])
        html = '''<p>From your <i>{0}</i> feed:</p>
                  <p><b>{1}</b><br>
                  <a href="{2}">{2}</a></p>'''
        body = html.format(name, title, link)

        self.send_email(subject, body)
        self.speak_dialog('feed.email')


def create_skill():
    return RssReader()
