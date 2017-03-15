#!/usr/bin/env python
from subprocess import check_call as cc
from http.cookies import SimpleCookie
from urllib.parse import parse_qs
from time import localtime, strftime
from scripts.pls import getpls
from scripts.motocal import mcal
import os


def application(environ, start_response):
    ItsMe = False
    xiia = False
    auth = False
    vlc = False
    response_body = None
    path = os.path.normpath(environ['PATH_INFO'])
    files = sorted(os.listdir(os.environ['OPENSHIFT_DATA_DIR'] + 'xml'), key=lambda x: (x.split('.')[-1], x.lower()))
    shows = getpls(None).allpro
    redirect = None

#    print('\n'.join(['%s: %s' % (key, value) for key, value in sorted(environ.items()) if key == 'HTTP_REFERER' or key == 'REQUEST_URI' or key == 'PATH_INFO' or key == 'QUERY_STRING' or key == 'wsgi.input']))

    if 'HTTP_COOKIE' in environ:
        rcookie = SimpleCookie(environ['HTTP_COOKIE'])
        if 'session' in rcookie and rcookie['session'].value == 'ItsMe' or rcookie['session'].value == 'itsme':
            ItsMe = True
        elif 'session' in rcookie and rcookie['session'].value == 'malonso' and path == '/nextgp':
            ItsMe = True

    if 'HTTP_USER_AGENT' in environ:
        if 'Dalvik/1.4.0' in environ['HTTP_USER_AGENT'] or 'Lavf/56.15.102' in environ['HTTP_USER_AGENT']:
            xiia = True
            if 'HTTP_AUTHORIZATION' in environ:
                if environ['HTTP_AUTHORIZATION'].split(' ')[-1] == 'cGktdG9uOmVsY2Fsb3JldA==':
                    auth = True
        elif 'LibVL' in environ['HTTP_USER_AGENT']:
            xiia = True
            if 'HTTP_AUTHORIZATION' in environ:
                if environ['HTTP_AUTHORIZATION'].split(' ')[-1] == 'cGktdG9uOmVsY2Fsb3JldA==':
                    vlc = True

    if 'QUERY_STRING' in environ:
        if environ['QUERY_STRING'].startswith('redirect='):
            redirect = os.path.normpath(environ['QUERY_STRING'])

    if path == '/' and ItsMe is True:
        response_body = ['<tr><td style="text-align:left;"><a href="/xml/{}" download>{}</a></td><td style="text-align:right;">{} kB</td><td style="text-align:right;">{}</td></tr>'.format(f, f, round(os.stat(os.environ['OPENSHIFT_DATA_DIR'] + 'xml/' + f).st_size / 1024, 1), strftime('%-d/%m at %H:%M', localtime(os.stat(os.environ['OPENSHIFT_DATA_DIR'] + 'xml/' + f).st_mtime))) for f in files if not f.startswith('.')]
        response_body.append('''<tr><td style="text-align:center;padding-top:25px;"><button onclick="go('/daily');">Daily</button></td><td></td><td style="text-align:center;padding-top:25px;"><button onclick="go('/hourly');">Hourly</button></td></tr></table></center><script type="text/javascript">function changetext(text){over=document.querySelector("#over");document.querySelector("#result").textContent=text;setTimeout(function(){over.style.display="none";location.reload();},2e3);}function go(cual){document.querySelector("#over").style.display="block";var xmlhttp=new XMLHttpRequest();xmlhttp.open("GET",cual);xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4&&xmlhttp.status==200){changetext(xmlhttp.responseText);}else{changetext(xmlhttp.statusText+" "+xmlhttp.status);}};xmlhttp.send(null);}</script></body></html>''')
        response_body.insert(0, '<!DOCTYPE html><html><head><meta content="charset=UTF-8"/><title>pi-ton</title></head><style>td {padding: 3px;}</style><body><center><div id="over"style="display:none;position:fixed;top:0%;left:0%;width:100%;height:100%;background-color:black;-moz-opacity:0.8;opacity:.80;filter:alpha(opacity=80);"><p id="result"style="color:red;margin-top:20%;font-weight:bolder;font-size:25px;">...</p></div><table style="margin-top:8%;"><th>Archivo</th><th>Tamaño</th><th style="width:150px;text-align: right;">Fecha modif.</th>')
        response_body = ''.join(response_body)
        ctype = 'text/html; charset=UTF-8'
    elif path == '/login' and ItsMe is False:
        try:
            length = int(environ['CONTENT_LENGTH'])
            pwd = environ['wsgi.input'].read(length).decode().replace('session=', '')
            if pwd == 'ItsMe' or pwd == 'itsme' or pwd == 'malonso':
                cookie = SimpleCookie()
                cookie['session'] = pwd
                cookie['session']['path'] = '/'
                cookie['session']['max-age'] = '864000'
                cookieheaders = ('Set-Cookie', cookie['session'].OutputString())
                if pwd == 'malonso':
                    response_headers = [cookieheaders, ('Location', '/nextgp')]
                elif redirect is None or redirect == '/':
                    response_headers = [cookieheaders, ('Location', '/')]
                else:
                    response_headers = [cookieheaders, ('Location', '{}'.format(parse_qs(redirect)['redirect'][0]))]
                start_response('302 Found', response_headers)
                return ['1']
            raise Exception
        except:
            response_body = '''<!DOCTYPE html><html><head><meta content="charset=UTF-8"/><title>pi-ton</title></head><body><center><form action=""method="post"><input name="session"type="text"size="10"placeholder="And you are...?"style="margin-top:20%;text-align:center"autofocus required><input type="submit"value="Submit"style="display:none"></form></center></body></html>'''
            ctype = 'text/html; charset=UTF-8'
    elif path == '/nextgp' and ItsMe is True:
        response_body = mcal().nextgptext
        ctype = 'text/plain; charset=UTF-8'
    elif path == '/report' and ItsMe is True:
        try:
            length = int(environ['CONTENT_LENGTH'])
            w = open(os.environ['OPENSHIFT_LOG_DIR'] + 'report.log', 'a')
            w.write(environ['wsgi.input'].read(length).decode() + '\n')
            w.close()
            response_body = 'ok'
        except:
            r = open(os.environ['OPENSHIFT_LOG_DIR'] + 'report.log', 'r')
            response_body = ''.join(list(reversed(r.readlines())))
            r.close()
        ctype = 'text/plain; charset=UTF-8'
    elif path.startswith('/xml/') and path.split('/')[-1] in files and ItsMe is True:
        r = open(os.environ['OPENSHIFT_DATA_DIR'] + 'xml/' + path.split('/')[-1], 'r')
        response_body = r.read()
        r.close()
        ctypes = {'json': 'application/json; charset=UTF-8', 'xml': 'application/xml; charset=UTF-8'}
        ctype = ctypes[path.split('.')[-1]]
#    elif path == '/xml/lostoros.xml':
#        response_body = '''<!DOCTYPE html><html><head><title>404 Not Found</title></head><body bgcolor="white"><h1>404 Not Found</h1><p>The URL you requested could not be found.</p><hr><address>Apache/2.2.15 (Red Hat) Server at pi-ton.rhcloud.com Port 80</address></body></html>'''
#        response_headers = [('content-type', 'text/html; charset=UTF-8'), ('content-length', str(len(response_body.encode('utf8'))))]
#        start_response('404 Not Found', response_headers)
#        return [response_body.encode('utf8')]
#    elif path == '/xml/lostoros.xml':
#        r = open(os.environ['OPENSHIFT_DATA_DIR'] + 'xml/lostoros.xml', 'r')
#        response_body = r.read()
#        r.close()
#        ctype = 'application/xml; charset=UTF-8'
    elif path.startswith('/pls/') and path.endswith('.pls') and path.split('/')[-1].replace('.pls', '') in shows:
        if ItsMe is True:
            ctype = 'audio/x-scpls'
            response_body = getpls(path.split('/')[-1].replace('.pls', '')).joinedpls
        elif xiia is True:
            if auth is True:
                location = getpls(path.split('/')[-1].replace('.pls', '')).joinedpls.split('\n')[1].replace('File1=', '')
                start_response('302 Found', [('Location', location)])
                return ['1']
            elif vlc is True:
                response_body = getpls(path.split('/')[-1].replace('.pls', '')).joinedpls
                start_response('200 OK', [('Content-Type', 'audio/x-scpls')])
                return [response_body.encode()]
            else:
                response_body = '''<!DOCTYPE html><html><head><meta content="charset=UTF-8"/><title>pi-ton</title></head><body><center><form action="/login"method="post"><input name="session"type="text"size="10"placeholder="And you are...?"style="margin-top:20%;text-align:center"autofocus required><input type="submit"value="Submit"style="display:none"></form></center></body></html>'''
                response_headers = [('content-type', 'text/html; charset=UTF-8'), ('content-length', str(len(response_body.encode('utf8')))), ('WWW-Authenticate', 'Basic realm="pls@pi-ton"')]
                start_response('401 Unauthorized', response_headers)
                return [response_body.encode('utf8')]
        else:
            if redirect is None:
                start_response('302 Found', [('Location', '/')])
            else:
                start_response('302 Found', [('Location', '/login?redirect={}'.format(path))])
            return ['1']
    elif path.startswith('/pls/') and path.endswith('.txt') and path.split('/')[-1].replace('.txt', '') in shows:
        if ItsMe is True:
            ctype = 'text/plain; charset=UTF-8'
            response_body = getpls(path.split('/')[-1].replace('.txt', '')).joinedpls
        else:
            if redirect is None:
                start_response('302 Found', [('Location', '/')])
            else:
                start_response('302 Found', [('Location', '/login?redirect={}'.format(path))])
            return ['1']
    elif path == '/daily' or path == '/hourly' and ItsMe is True:
        sp = cc(['sh', './app-root/repo/.openshift/cron/{}/runner'.format(path.replace('/', '')), 'echo'])
        response_body = 'fail'
        if sp == 0:
            response_body = 'ok'
        ctype = 'text/plain; charset=UTF-8'
#    elif path == '/env':
#        response_body = '\n'.join(['%s: %s' % (key, value) for key, value in sorted(environ.items())])
#        ctype = 'text/plain'
#        response_body = ['%s: %s' % (key, value) for key, value in sorted(environ.items())]
#        response_body.append('SCRIPT_NAME: {}'.format(environ['SCRIPT_NAME']))
#        response_body = '\n'.join(response_body)
    elif path == '/logout':
        if 'HTTP_COOKIE' in environ:
            dcookie = SimpleCookie(environ['HTTP_COOKIE'])
            if 'session' in dcookie and dcookie['session'].value == 'ItsMe' or dcookie['session'].value == 'itsme' or dcookie['session'].value == 'malonso':
                dcookie['session']['expires'] = 'expires=Thu, 01 Jan 1970 00:00:00 GMT'
                cookieheaders = ('Set-Cookie', dcookie['session'].OutputString())
                response_headers = [cookieheaders, ('Location', '/login')]
                start_response('302 Found', response_headers)
                return ['1']
    else:
        if ItsMe is True:
            if redirect is None:
                start_response('302 Found', [('Location', '/')])
            else:
                start_response('302 Found', [('Location', '{}'.format(parse_qs(redirect)['redirect'][0]))])
            return ['1']
        if path == '/':
            start_response('302 Found', [('Location', '/login'.format(path))])
        else:
            start_response('302 Found', [('Location', '/login?redirect={}'.format(path))])
        return ['1']

    # always It's OK, okeeeya!?
    status = '200 OK'

    if ctype == 'audio/x-scpls':
        response_headers = [('Content-Type', ctype)]
        start_response(status, response_headers)
        return [response_body.encode()]
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
