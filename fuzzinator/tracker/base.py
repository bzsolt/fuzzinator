# Copyright (c) 2016-2019 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.


class BaseTracker(object):

    def find_issue(self, issue):
        pass

    def report_issue(self, **kwargs):
        pass

    def issue_url(self, issue):
        return ''
