import os
from app import create_app
from werkzeug.contrib.fixers import ProxyFix

application = create_app(os.environ.get("APP_CONFIGURATION"))
application.wsgi_app = ProxyFix(application.wsgi_app)

if __name__ == "__main__":
    application.run()