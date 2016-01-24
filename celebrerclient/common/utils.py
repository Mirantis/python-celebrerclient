#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function

import os
import six
import sys

from oslo_log import log as logging
from oslo_utils import encodeutils
from oslo_utils import importutils

import prettytable

LOG = logging.getLogger(__name__)


# Decorator for cli-args
def arg(*args, **kwargs):
    def _decorator(func):
        # Because of the sematics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator


def pretty_choice_list(l):
    return ', '.join("'%s'" % i for i in l)


def print_list(objs, fields, formatters={}, order_by=None):
    pt = prettytable.PrettyTable([f for f in fields],
                                 caching=False, print_empty=False)
    pt.aligns = ['l' for f in fields]

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                field_name = field.lower().replace(' ', '_')
                data = getattr(o, field_name, '')
                if data is None:
                    data = ''
                row.append(data)
        pt.add_row(row)

    if order_by is None:
        order_by = fields[0]
    encoded = encodeutils.safe_encode(pt.get_string(sortby=order_by))
    if six.PY3:
        encoded = encoded.decode()
    print(encoded)


def _word_wrap(string, max_length=0):
    """wrap long strings to be no longer than max_length."""
    if max_length <= 0:
        return string
    return '\n'.join([string[i:i + max_length] for i in
                     range(0, len(string), max_length)])


def print_dict(d, wrap=0):
    """pretty table prints dictionaries.
    Wrap values to max_length wrap if wrap>0
    """
    pt = prettytable.PrettyTable(['Property', 'Value'],
                                 caching=False, print_empty=False)
    pt.aligns = ['l', 'l']
    for (prop, value) in six.iteritems(d):
        if value is None:
            value = ''
        value = _word_wrap(value, max_length=wrap)
        pt.add_row([prop, value])
    encoded = encodeutils.safe_encode(pt.get_string(sortby='Property'))
    if six.PY3:
        encoded = encoded.decode()
    print(encoded)


def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars
    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.
    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def import_versioned_module(version, submodule=None):
    module = 'celebrerclient.v%s' % version
    if submodule:
        module = '.'.join((module, submodule))
    return importutils.import_module(module)


def exit(msg=''):
    if msg:
        print(encodeutils.safe_encode(msg), file=sys.stderr)
    sys.exit(1)
