from constants import *
from flask import Flask

from endpoints.certificates import certificates
from endpoints.domains import domains
from endpoints.engagements import engagements
from endpoints.groups import groups
from endpoints.implants import implants
from endpoints.lighthouses import lighthouses
from endpoints.proxies import proxies
from endpoints.redirectors import redirectors


app = Flask(__name__)
api_version = "v1"
api_prefix = "/api/{version}".format(version=api_version)

app.register_blueprint(certificates, url_prefix=api_prefix+"/certificates")
app.register_blueprint(domains, url_prefix=api_prefix+"/domains")
app.register_blueprint(engagements, url_prefix=api_prefix+"/engagements")
app.register_blueprint(groups, url_prefix=api_prefix+"/groups")
app.register_blueprint(implants, url_prefix=api_prefix+"/implants")
app.register_blueprint(lighthouses, url_prefix=api_prefix+"/lighthouses")
app.register_blueprint(proxies, url_prefix=api_prefix+"/proxies")
app.register_blueprint(redirectors, url_prefix=api_prefix+"/redirectors")

@app.route("/")
def index():
    return "<h1>Remitter</h1>"


if __name__ == '__main__':
    print(logo)
    app.run(host="0.0.0.0", port=8080)
