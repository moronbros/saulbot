#!/usr/bin/env python

import sys
from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor

from pymarkovchain import MarkovChain

CORPUS = 'corpus.txt'


def markov():
    """A simple markov function"""
    mc = MarkovChain("./tempchain")

    with open(CORPUS, 'r') as f:
        data = f.read()

    mc.generateDatabase(data)

    return mc.generateString()


class SaulBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        if not user:
            return
        if self.nickname in msg:
            self.msg(self.factory.channel, markov())


class SaulBotFactory(protocol.ClientFactory):
    protocol = SaulBot

    def __init__(self, channel='', nickname=''):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


if __name__ == "__main__":
    try:
        chan = sys.argv[1]
    except IndexError:
        print "Please specify a channel name."

    # Allow for testing of the generated quips.
    if chan == 'test':
        print markov()
        sys.exit()

    reactor.connectTCP('irc.catch22.org', 6667, SaulBotFactory('#' + chan,
                       'saulbot', 2, chattiness=0.15))

    reactor.run()