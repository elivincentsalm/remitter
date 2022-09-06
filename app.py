from constants import *
from flask import Flask

from routes.domains import domains
from routes.engagements import engagements
from routes.groups import groups
from routes.redirectors import redirectors


app = Flask(__name__)
api_version = "v1"
api_prefix = "/api/{version}".format(version=api_version)

app.register_blueprint(domains, url_prefix=api_prefix+"/domains")
app.register_blueprint(engagements, url_prefix=api_prefix+"/engagements")
app.register_blueprint(groups, url_prefix=api_prefix+"/groups")
app.register_blueprint(redirectors, url_prefix=api_prefix+"/redirectors")

@app.route("/")
def index():
    return "<h1>Remitter</h1>"


if __name__ == '__main__':
    print(logo)
    app.run(host="0.0.0.0", port=8080)
