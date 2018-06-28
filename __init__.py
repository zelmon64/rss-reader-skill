from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler


class RssReader(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('reader.rss.intent')
    def handle_reader_rss(self, message):
        article = ''
        name = ''
        number = ''

        self.speak_dialog('reader.rss', data={
            'name': name,
            'number': number,
            'article': article
        })


def create_skill():
    return RssReader()

