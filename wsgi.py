#!/usr/bin/env python
from subprocess import check_call as cc
from http.cookies import  SimpleCookie
from time import localtime, strftime
import os

def application(environ, start_response):

    ItsMe = False
    response_body = None
    files = os.listdir(os.environ['OPENSHIFT_REPO_DIR']+'xml')
    files.remove('.gitkeep')

    if 'HTTP_COOKIE' in environ:
        rcookie = SimpleCookie(environ['HTTP_COOKIE'])
        if 'session' in rcookie and rcookie['session'].value == 'ItsMe':
            ItsMe = True

    if environ['PATH_INFO'] == '/' and ItsMe is True:
        response_body = ['<tr><td><a href="/xml/{}" download>{}</a></td><td>{} kB</td><td>{}</td></tr>'.format(f,f,round(os.stat(os.environ['OPENSHIFT_REPO_DIR']+'xml/'+f).st_size/1024, 1),strftime('%x at %X', localtime(os.stat(os.environ['OPENSHIFT_REPO_DIR']+'xml/'+f).st_mtime))) for f in files]
        response_body.append('''<tr><td><button onclick="go('/daily');">Daily</button></td><td></td><td><button onclick="go('/hourly');">Hourly</button></td></tr></table><center><script type="text/javascript">function changetext(text){over=document.querySelector("#over");document.querySelector("#result").textContent=text;over.style.display="block";setTimeout(function(){over.style.display="none";},2e3);}function go(cual){var xmlhttp=new XMLHttpRequest();xmlhttp.open("GET",cual);xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4&&xmlhttp.status==200)   {changetext(xmlhttp.responseText);}else{changetext(xmlhttp.statusText+" "+xmlhttp.status);}};xmlhttp.send(null);}</script></body></html>''')
        response_body.insert(0, '<!DOCTYPE html><html><head><meta content="charset=UTF-8"/><title>pi-ton</title></head><style>td {text-align:center}</style><body><center><div id="over"style="display:none;position:fixed;top:0%;left:0%;width:100%;height:100%;background-color:black;-moz-opacity:0.8;opacity:.80;filter:alpha(opacity=80);"><p id="result"style="color:red;margin-top:15%;margin-left:45%;"></p></div><table><th>Archivo</th><th>Tamaño</th><th>Fecha modif.</th>')
        response_body = ''.join(response_body)
        ctype = 'text/html; charset=UTF-8'
    elif environ['PATH_INFO'].startswith('/xml/') and '..' not in environ['PATH_INFO'] and environ['PATH_INFO'].split('/')[-1] in files and ItsMe is True:
        r = open(os.environ['OPENSHIFT_REPO_DIR'] + 'xml/' + environ['PATH_INFO'].split('/')[-1], 'r')
        response_body = r.read()
        r.close()
        ctypes = {'json': 'application/json; charset=UTF-8', 'xml': 'application/xml; charset=UTF-8'}
        ctype = ctypes[environ['PATH_INFO'].split('.')[-1]]
    elif environ['PATH_INFO'] == '/xml/lostoros.xml':
        r = open(os.environ['OPENSHIFT_REPO_DIR'] + 'xml/lostoros.xml', 'r')
        response_body = r.read()
        r.close()
        ctype = 'application/xml; charset=UTF-8'
    elif environ['PATH_INFO'] == '/daily' or environ['PATH_INFO'] == '/hourly' and ItsMe is True:
        sp = cc(['sh', './app-root/repo/.openshift/cron/{}/runner'.format(environ['PATH_INFO']), 'echo'])
        if sp == 0:
            response_body = 'ok'
        else:
            response_body = 'fail'
        ctype = 'text/html; charset=UTF-8'
    else:
        response_body = '''<!DOCTYPE html><html><head><meta content="charset=UTF-8"/><title>pi-ton</title></head><body><center><input type="text"size="10"placeholder="And you are...?"style="margin-top:20%;text-align:center"autofocus required></center><script type="text/javascript">document.querySelector("input").addEventListener("keypress",function(e){if(e.key=="Enter"){document.cookie="session="+document.querySelector("input").value+"; max-age=864000; path=/";location.reload();}});</script></body></html>'''
        ctype = 'text/html; charset=UTF-8'

    # always It's OK, okeeeya!?
    status = '200 OK'

    # create a cookie object
#    cookie = SimpleCookie()
#    cookie['session'] = 'ItsMe'
#    cookie['session']['path'] = "/"
#    cookie['session']['max-age'] = '864000'
#    cookieheaders = ('Set-Cookie', cookie['session'].OutputString())
#    response_headers = [cookieheaders, ('Content-Type', ctype), ('Content-Length', str(len(response_body)))]

    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body.encode('utf8'))))]
    start_response(status, response_headers)
    return [response_body.encode('utf8')]
#    return [response_body]

#
# Below for testing only
#
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    httpd.handle_request()
