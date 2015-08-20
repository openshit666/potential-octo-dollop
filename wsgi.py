#!/usr/bin/env python
from http.cookies import  SimpleCookie
import os

def application(environ, start_response):

    ctype = 'text/plain'
    if environ['PATH_INFO'] == '/health':
        response_body = "1"
    elif environ['PATH_INFO'] == '/env':
        response_body = ['%s: %s' % (key, value)
                    for key, value in sorted(environ.items())]
        response_body = '\n'.join(response_body)
    elif environ['PATH_INFO'] == '/asd':
        r = open(os.environ['OPENSHIFT_REPO_DIR']'/xml/dvdr-_-movies.xml', 'r')
        response_body = r.read()
        r.close()
        ctype = 'application/json'
    else:
        ctype = 'text/html'
        response_body = '''opensheit!'''

    status = '200 OK'

    # create a cookie object
    cookie = SimpleCookie()
    cookie['likes'] = "cheese"
    cookieheaders = ('Set-Cookie', cookie['likes'].OutputString())


    response_headers = [cookieheaders, ('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
    #
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
