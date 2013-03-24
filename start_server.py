import os
import os.path
import imp
from werkzeug.serving import run_simple
from optparse import OptionParser


def startServer(options):
    app_root = os.getcwd()

    if os.environ.get('WERKZEUG_RUN_MAIN', False):
        os.environ['HTTP_HOST'] = '%s:%d' % (options.host, options.port)
        app = imp.load_source('index_wsgi', 'index_wsgi.py')
        application = app.application
    else:
        application = 1

    statics = {
        '/static': os.path.join(app_root,  'static'),
        '/favicon.ico': os.path.join(app_root,  'static/img/favicon.ico'),
    }

    files = ['index_wsgi.py']

    try:
        run_simple(
            options.host, options.port, application,
            use_reloader=True,
            use_debugger=True,
            extra_files=files,
            static_files=statics,
            threaded=True)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--port", type="int", dest="port", default="8080",
                      help="Which port to listen")
    parser.add_option("--host", dest="host", default="localhost",
                      help="Which host to listen")
    (options, args) = parser.parse_args()

    startServer(options)
