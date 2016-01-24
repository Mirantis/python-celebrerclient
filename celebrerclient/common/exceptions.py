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
import sys


class BaseException(Exception):
    """An error occurred."""
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message or self.__class__.__doc__


class ClientException(Exception):
    """The base exception class for all exceptions this library raises.
    """
    pass


class InvalidEndpoint(BaseException):
    """The provided endpoint is invalid."""


class CommunicationError(BaseException):
    """Unable to communicate with server."""


class HTTPException(ClientException):
    """Base exception for all HTTP-derived exceptions."""
    code = 'N/A'

    def __init__(self, details=None):
        self.details = details or self.__class__.__name__

    def __str__(self):
        return "%s (HTTP %s)" % (self.details, self.code)


class Unauthorized(HTTPException):
    """DEPRECATED!"""
    code = 401


class CommandError(ClientException):
    """Error in CLI tool."""
    pass


class HTTPUnauthorized(Unauthorized):
    pass


_code_map = {}
for obj_name in dir(sys.modules[__name__]):
    if obj_name.startswith('HTTP'):
        obj = getattr(sys.modules[__name__], obj_name)
        _code_map[obj.code] = obj


def from_response(response):
    """Return an instance of an HTTPException based on httplib response."""
    cls = _code_map.get(response.status_code, HTTPException)
    body = response.content
    if body and response.headers['content-type'].\
       lower().startswith("application/json"):
        # Iterate over the nested objects and retreive the "message" attribute.
        messages = [obj.get('message') for obj in response.json().values()]
        # Join all of the messages together nicely and filter out any objects
        # that don't have a "message" attr.
        details = '\n'.join(i for i in messages if i is not None)
        return cls(details=details)
    elif body and \
            response.headers['content-type'].lower().startswith("text/html"):
        # Split the lines, strip whitespace and inline HTML from the response.
        details = [re.sub(r'<.+?>', '', i.strip())
                   for i in response.text.splitlines()]
        details = [i for i in details if i]
        # Remove duplicates from the list.
        details_seen = set()
        details_temp = []
        for i in details:
            if i not in details_seen:
                details_temp.append(i)
                details_seen.add(i)
        # Return joined string separated by colons.
        details = ': '.join(details_temp)
        return cls(details=details)
    elif body:
        details = body.replace('\n\n', '\n')
        return cls(details=details)

    return cls()
