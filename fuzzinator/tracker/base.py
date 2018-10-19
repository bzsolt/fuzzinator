# Copyright (c) 2016-2018 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import json

from string import Formatter

from fuzzinator.config import config_get_callable


class MultitonMetaClass(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls._instances = dict()

    def __call__(cls, *args):
        key = tuple(args)
        instance = cls._instances.get(key, None)
        if instance is None:
            instance = super().__call__(*args)
            cls._instances[key] = instance
        return instance


class BaseTracker(object, metaclass=MultitonMetaClass):

    def __init__(self, template=None, title=None):
        self.template = template
        self.title_fmt = title

    @property
    def logged_in(self):
        return True

    def title(self, issue):
        issue = self.decode_issue(issue)
        return self.title_fmt.format(**dict((entry[1], issue.get(entry[1], '')) for entry in Formatter().parse(self.title_fmt))) if self.title_fmt else issue['id']

    def decode_issue(self, issue):
        def universal_newlines(src):
            if type(src) == bytes:
                src = src.decode('utf-8', errors='ignore')
            if type(src) == str:
                return '\n'.join(src.splitlines())
            return src
        return dict((x, universal_newlines(y)) for (x, y) in issue.items() if x != '_id')

    def format_issue(self, issue):
        issue = self.decode_issue(issue)
        if self.template:
            with open(self.template, 'r') as f:
                template = f.read()
                return template.format(**dict((entry[1], issue.get(entry[1], '')) for entry in Formatter().parse(template)))
        return json.dumps(issue, indent=4, sort_keys=True)

    def find_issue(self, issue):
        pass

    def report_issue(self, **kwargs):
        pass

    def issue_url(self, issue):
        return ''


def init_tracker(config, sut):
    return config_get_callable(config, 'sut.' + sut, 'tracker')[0] or BaseTracker()
