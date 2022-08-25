# remitter: Automating Covert and Resilient C2 Infrastructure Deployments
Remitter is a web GUI built to automate deployments of covert C2 infrastructure. Remitter is designed to be extremely easy to configure for teams lacking domain-knowledge and includes many considerations for teams with high data-retention and -privacy requirements. Heavily inspired by @bluescreenofjeff's Read Team Infrastructure Wiki and @byt3bl33d3r's posts on modern C2 infrastructure (references below).

<img width="1367" alt="MaximalC2Infra" src="https://user-images.githubusercontent.com/55160090/185764594-2e958397-9cbe-48b2-88a1-b1110a8c5310.png">

## Rationale
The above system diagram shows the "maximal" C2 infrastructure that can be created with Remitter. Maximal, meaning meant to display the full capabilities and complexity of Remitter. Components can be removed as desired in configuration settings to reduce complexity, cost, and/or realism. Below contains the rationale for each component in the above system diagram. 

### Victim Network
Remitter is not an implant generation framework, though it is designed to be flexible to accomodate different types of implant traffic. In a maximal setup, many computers will be infected with several persistence methods. 

### Internet, Mesh Overlay VPN

#### Redirector Layer
Redirectors are simple devices that forward traffic downstream towards the attack infrastructure using IPTables. Their purpose is to conceal the location of the attack infrastructure from analysts and scanners monitoring inbound/outbound network traffic. If a redirector is discovered, it can easily be torn down (for instance) and replaced without compromising the entire operation.

In a maximal setup, each redirector would have it's own domain name and traffic/authentication profile. For example:
##### www[.]somedomain1[.]co
Redirector Type: Short Haul  
Protocol: HTTPS  
Traffic profile: profiles/gmail.profile  
Authentication type: UserAgent Password  

##### www[.]somedomain2[.]org  
Redirector Type: Long Haul  
Protocol: DNS  
Authentication: mTLS  

#### Laundry Layer
High-throughput layer for forwarding all traffic to protected operational network. The laundry layer is only necessary if conducting an internal assessment where there are concerns a member of the blue team will observe traffic from the protected network to/from a redirector. It is another internet-level layer to hide any direct communication to devices also being communicated with via implants.

### Protected Operational Network
Reference to the Vault 7 leaks. Victim should have no idea where this is. 

#### Fingerprint/Cover Server
If desired, unauthenticated requests can be forwarded to a cover server, where browser fingerprinting is performed. This allows us to reduce suspicion while also achieving a greater understanding of attack surface.

#### Credential Capture Server
Mobile devices visiting a redirector can be forwarded to a credential capture page. If credentials are entered, those can be forwarded to our attack infrastructure ("Intel").

#### Operations Management Center
Houses the C2 TeamServer as well as Remitter. 

## Design Considerations

### Stealth
The core attack infrastructure must remain hidden to the victim. If the blue team discovers *anything* infrastructure related, it must not compromise the operation. Thus, redirectors are used, laundry layers are possible, and C2 traffic is diverse.

### Operational Resilience
If a blue team operator blocks egress traffic to a redirector, we want to be able to rotate the blocked redirectors to maintain access. Additionally, all data captured during the operation should be backed-up. 

### Simplicity


## API Contract

```
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

    Domains:
        GET /api/v1/engagement/<id>/domain/all
        GET /api/v1/engagement/<id>/domain/<id>
        POST /api/v1/engagement/<id>/domain/<id>
        DELETE /api/v1/engagement/<id>/domain/all
        DELETE /api/v1/engagement/<id>/domain/<id>
    Properties:
        {
            "id": "string"
            "domain_name": "string"
            "registrar": "string"
            "assigned": Boolean
            "engagement_id": "string"
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
            "public_ip_address": "string"
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
            "public_ip_address": "string"
            "domain_name": "string"
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
            "public_ip_address": "string"
            "domain_name": "string"
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
            "public_ip_address": "string"
            "domain_name": "string"
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
            "public_ip_address": "string"
            "domain_name": "string"
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
            "common_name": "string"
            "engagement_id": "string"
        }
```

# References
https://byt3bl33d3r.substack.com/p/taking-the-pain-out-of-c2-infrastructure-3c4

https://slack.engineering/introducing-nebula-the-open-source-global-overlay-network-from-slack/

https://blog.inspired-sec.com/archive/2017/02/14/Mail-Server-Setup.html

https://github.com/bluscreenofjeff/Red-Team-Infrastructure-Wiki

https://github.com/Coalfire-Research/Red-Baron

https://bluescreenofjeff.com/2017-08-08-attack-infrastructure-log-aggregation-and-monitoring/

https://shogunlab.gitbook.io/building-c2-implants-in-cpp-a-primer/chapter-1-designing-a-c2-infrastructure

https://ditrizna.medium.com/design-and-setup-of-c2-traffic-redirectors-ec3c11bd227d

