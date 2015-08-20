#!/usr/bin/env python
from http.cookies import  SimpleCookie
import os

def application(environ, start_response):

    ItsMe = False
    response_body = None
    files = os.path(os.environ['OPENSHIFT_REPO_DIR']+'/xml')

    if 'HTTP_COOKIE' in environ:
        rcookie = SimpleCookie(environ['HTTP_COOKIE'])
        if 'session' in rcookie and rcookie['session'].value == 'ItsMe':
            ItsMe = True

    if environ['PATH_INFO'] == '/' and ItsMe is True:
        response_body = ['<a href="/xml/{}" download>{}</a><br>'.format(f,f) for f in files]
        response_body = ''.join(response_body)
        ctype = 'text/html'
    elif environ['PATH_INFO'].startswith('/xml/') and '..' not in environ['PATH_INFO'] and environ['PATH_INFO'].split('/')[-1] in files and ItsMe is True:
        r = open(os.environ['OPENSHIFT_REPO_DIR'] + '/xml/' + environ['PATH_INFO'].split('/')[-1], 'r')
        response_body = r.read()
        r.close()
        ctypes = {'json': 'application/json', 'xml': 'application/xml'}
        ctype = ctypes[environ['PATH_INFO'].split('.')[-1]]
    else:
        response_body = '''¿login?'''
        ctype = 'text/html'

    # always It's OK, okeeeya
    status = '200 OK'

    # create a cookie object
    #cookie = SimpleCookie()
    #cookie['session'] = 'ElCaloret'
    #cookie['session']['max-age'] = '600'
    #cookieheaders = ('Set-Cookie', cookie['session'].OutputString())

    #response_headers = [cookieheaders, ('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body.encode('utf-8') ]

#
# Below for testing only
#
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    httpd.handle_request()
