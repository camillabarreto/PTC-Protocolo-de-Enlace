#!/usr/bin/env python3

import poller
from poller import Callback


class Sublayer(poller.Callback):

    def __init__(self, fd, timeout):
        Callback.__init__(self, fd, timeout)
        self.lowerLayer = None
        self.upperLayer = None

    def connect(self, lower, upper):
        self.lowerLayer = lower
        self.upperLayer = upper

    def send(self):
        pass

    def receive(self):
        pass
