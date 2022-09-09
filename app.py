from constants import *
from flask import Flask, render_template

from routes.domains import domains
from routes.engagements import engagements
from routes.groups import groups
from routes.redirectors import redirectors


app = Flask(__name__)
api_version = "v1"
api_prefix = "/api/{version}".format(version=api_version)

app.register_blueprint(redirectors, url_prefix=api_prefix+"/redirectors")

@app.route("/")
def index():
    return render_template("base.html")

if __name__ == '__main__':
    print(logo)
    app.run(host="0.0.0.0", port=8080)
