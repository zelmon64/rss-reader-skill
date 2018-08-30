## Rss Reader
A simple RSS reader skill for [Mycroft](https://mycroft.ai/).

## Description
This skill is a simple tool to get updates from your favorite news sources.

the main features are: 
* manage your feed subscriptions from your [dashboard](https://home.mycroft.ai/), 
* ask Mycroft to check if new articles have been published, 
* ask Mycroft to read the titles and other information for you.

## Examples
 - "Check for new feeds"
 - "Check for new feeds from Mycroft blog"
 - "Read my new feeds"
 - "Read my new feeds from Mycroft blog"

## Commands (en-us)
* `repeat` repeats the title of the article
* `author` gets information about the author
* `summary` gets Mycroft to read the summary
* `content` gets Mycroft to read the ful content
* `email` emails to your INBOX a link to the article
* `next` reads the next article
* `synchronize` marks all the articles as _read_
* `stop` stops the skill execution

## Room for improvements
Contributions are welcome.

1. _read_feeds() method clean-up_

   The read_feeds() code needs a little clean up.
   I would like to leave all the object iteration logic in this function, and delegate single tasks to specialized class method.

2. _Work on the vocabulary_

   The vocabulary can be extended to improve user experience.
    
3. _Make feeds data persistent_

   Every time a new intent is registered, the skill makes new http requests to retrieve feed data. 
   I would like to optimize resources by making the feeds data persistent (in ram) for a reasonable amount of time.
   
4. _Add translations_   

   The skill currently works for English speaking users.
   This skill is designed to be as language independent as possible, by not hard-coding any English-centric structures and using tools such as Mycroft's translate_namedvalues().
     
## FAQ
1. _The emails I get from skill-rss-reader have some tracking code in the article URL._

   This can’t be avoided. Links are fetched _clean_ from your feeds, but the Mycroft method send_email() adds to them. Please, refer to Mycroft privacy policy for further information.

2. _The skill doesn’t work as it should._

   Please, feel free to open an _issue_ on GitHub. If this might be helpful, the skill logs warnings and errors in the Mycroft CLI. You can use a filter to highlight the relevant information by typing `:find 'rss-reader'`

## Thanks
[JamesPoole](https://github.com/JamesPoole/) from whose [podcast-skill](https://github.com/JamesPoole/podcast-skill) brilliant skill I inherited many ideas. 

## Credits
backassward


