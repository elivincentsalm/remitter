from flask import Flask

app = Flask(__name__)

@app.route("/")
def main():
        return "<p>Remitter</p>"

logo = """
                            ||    .     .                   
... ..    ....  .. .. ..   ...  .||.  .||.    ....  ... ..  
 ||' '' .|...||  || || ||   ||   ||    ||   .|...||  ||' '' 
 ||     ||       || || ||   ||   ||    ||   ||       ||     
.||.     '|...' .|| || ||. .||.  '|.'  '|.'  '|...' .||.    
"""

print(logo)
if __name__ == '__main__':
        app.run(host="0.0.0.0", port=8080)

'''
I'm just going to need to create a backend first, and then a front end. Front end can start as a CLI simply calling the backend. 

API Contract:

    Config Management:
    Events and Scripting:

    Engagements:
        GET /api/v1/engagement/all
        GET /api/v1/engagement/<id>
        POST /api/v1/engagement/<id>
        DELETE /api/v1/engagement/all
        DELETE /api/v1/engagement/<id>
    Properties:
        {
            "id": "string"
            "name": "string"
            "groups": []
            "implants": []
            "redirectors": []
            "laundry": []
            "proxies": []
            "certificates": []
        }

    Groups:
        GET /api/v1/engagement/<id>/group/all
        GET /api/v1/engagement/<id>/group/<id>
        POST /api/v1/engagement/<id>/group/<id>
        POST /api/v1/engagement/<id>/group/<id>/add/<id>
        DELETE /api/v1/engagement/<id>/group/all
        DELETE /api/v1/engagement/<id>/group/<id>
    Properties:
        {
            "id": "string"
            "name": "string"
            "members": []
            "engagement_id": "string"
        }

    Implants:
        GET /api/v1/engagement/<id>/implant/all
        GET /api/v1/engagement/<id>/implant/<id>
        POST /api/v1/engagement/<id>/implant/<id>
        DELETE /api/v1/engagement/<id>/implant/all
        DELETE /api/v1/engagement/<id>/implant/<id>
    Properties:
        {
            "id": "string"
            "name": "string"
            "profile": "string"
            "host": "string"
            "status": "string"
            "redirectors": []
            "engagement_id": "string"
        }

    Lighthouses:
        GET /api/v1/engagement/<id>/lighthouse/all
        GET /api/v1/engagement/<id>/lighthouse/<id>
        POST /api/v1/engagement/<id>/lighthouse/<id>
        DELETE /api/v1/engagement/<id>/lighthouse/all
        DELETE /api/v1/engagement/<id>/lighthouse/<id>
    Properties:
        {
            "id": "string"
            "name": "string"
            "profile": "string"
            "host": "string"
            "csp": "string"
            "status": "string"
            "engagement_id": "string"
        }

    Redirectors:
        GET /api/v1/engagement/<id>/redirector/all
        GET /api/v1/engagement/<id>/redirector/<id>
        POST /api/v1/engagement/<id>/redirector/<id>
        DELETE /api/v1/engagement/<id>/redirector/all
        DELETE /api/v1/engagement/<id>/redirector/<id>
    Properties:
        {
            "id": "string"
            "name": "string"
            "profile": "string"
            "host": "string"
            "csp": "string"
            "status": "string"
            "engagement_id": "string"
        }

    Laundry Layer:
        GET /api/v1/engagement/<id>/laundry/all
        GET /api/v1/engagement/<id>/laundry/<id>
        POST /api/v1/engagement/<id>/laundry/<id>
        DELETE /api/v1/engagement/<id>/laundry/all
        DELETE /api/v1/engagement/<id>/laundry/<id>
    Properties:
        {
            "id": "string"
            "name": "string"
            "profile": "string"
            "host": "string"
            "csp": "string"
            "status": "string"
            "engagement_id": "string"
        }

    Proxy Layer:
        GET /api/v1/engagement/<id>/proxy/all
        GET /api/v1/engagement/<id>/proxy/<id>
        POST /api/v1/engagement/<id>/proxy/<id>
        DELETE /api/v1/engagement/<id>/proxy/all
        DELETE /api/v1/engagement/<id>/proxy/<id>
    Properties:
        {
            "id": "string"
            "name": "string"
            "profile": "string"
            "host": "string"
            "status": "string"
            "engagement_id": "string"
        }

    Certificates:
        GET /api/v1/engagement/<id>/ca/<id>
        GET /api/v1/engagement/<id>/certificate/<id>
    Properties:
        {
            "id": "string"
            "name": "string"
            "type": "string"
            "belongs_to": []
            "engagement_id": "string"
        }
'''
