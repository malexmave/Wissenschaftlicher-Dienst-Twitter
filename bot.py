# encoding: utf-8
import feedparser
import re
import datetime
import twitter


def str2date(datestr):
    """Convert datestring from RSS to datetime object."""
    return datetime.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ')

# RegEx-Pattern to match format of RSS titles containing actual reports
# The pattern is WD [some number] - [some numbers]/[last 2 digits of year]
pat = re.compile('WD \d* - \d*/\d\d')

# Load RSS feed
feed = feedparser.parse('https://www.bundestag.de/blueprint/servlet/service/de/14110/asFeed/index.rss')

# Load cached date of last processed entry
with open('lastdate.txt', 'r') as fo:
    lastdate = str2date(fo.readline().strip())

# Prepare list of tweets to be sent
submit = []
for entry in feed.entries:
    # Check if entry is newer than last cached entry
    if str2date(entry.date) <= lastdate:
        # Entry is older or the same, break
        break

    # Fix broken formatting from RSS feed
    if entry.title.startswith(': '):
        entry.title = entry.title[2:]

    # Check if we have an actual report by the WD by matching the title
    match = pat.match(entry.title)
    if match is not None:
        # We have a report, fix the title formatting
        entry.title = entry.title[:match.end()] + ': ' + entry.title[match.end():]

    # Check the twitter length limit and shorten tweet, if necessary
    if len(entry.title) > 115:  # Twitter limit
        highestspace = entry.title.rfind(' ', 0, 112)
        entry.title = entry.title[:highestspace] + '...'
    else:
        entry.title = entry.title + "."

    # Create tweet and add it to list of tweets to be sent
    tweet = entry.title + " " + entry.link
    submit += [tweet]

if len(submit) > 0:
    # We have tweets to send
    # TODO: Add your own tokens here
    api = twitter.Api(consumer_key='CONSUMER_KEY',
                      consumer_secret='CONSUMER_SECRET',
                      access_token_key='ACCESS_TOKEN_KEY',
                      access_token_secret='ACCESS_TOKEN_SECRET')
    for tweet in submit:
        # Send each tweet
        # verify_status_length is False because version 3.2 of python-twitter
        # has a bug in the length verification code that causes it to fail
        # the tweets if they have a long URL in them.
        # Newer versions may have fixed this bug, but at the time of coding,
        # the version from pip was still bugged (official repos contain fix)
        status = api.PostUpdate(tweet, verify_status_length=False)

# Cache last processed entry date
with open('lastdate.txt', 'w') as fo:
    fo.write(str(feed.entries[0].date) + '\n')
