"""Official REST lifecycle adapter; creation fails closed on broken deadline support.

runpod/runpodctl#330 removed timers that the service ignored. No client-side
timeout is represented as a service-enforced spending limit.
"""
import json
import os
import urllib.request
import urllib.error
from .common import ContractError, identifier, parser, redact

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise ContractError("Refusing authenticated API redirect")

class RunpodProvider:
    def __init__(self, transport=None):
        self.transport=transport

    def request(self,method,path):
        token=os.environ.get("RUNPOD_API_KEY")
        if not token: raise ContractError("RUNPOD_API_KEY must be provided through environment")
        request=urllib.request.Request("https://rest.runpod.io/v1"+path,method=method,headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"})
        try:
            if self.transport: return self.transport(request)
            with urllib.request.build_opener(NoRedirect).open(request,timeout=30) as response:
                body=response.read(4*1024*1024)
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            raise ContractError(f"RunPod HTTP failure {exc.code}; response body suppressed") from None
        except urllib.error.URLError:
            raise ContractError("RunPod connection failed; do not retry creation without reconciliation") from None

    def create(self,manifest):
        raise ContractError("LIVE_RUNPOD_BLOCKED: upstream deadline fields are not enforced (runpodctl#330). No Pod was created. A reviewed provider deadline implementation and worker-image/artifact-transfer integration are required before live spending can be enabled.")

    def status(self,pid):
        identifier(pid)
        data=self.request("GET","/pods/"+pid)
        return {"id":data["id"],"name":data["name"],"status":str(data.get("desiredStatus","unknown")).lower()}

    def stop(self,pid):
        identifier(pid); return self.request("POST","/pods/"+pid+"/stop")

    def delete(self,pid):
        identifier(pid); return self.request("DELETE","/pods/"+pid)

    def collect(self,pid,manifest,out):
        raise ContractError("Live artifact transport is not configured; preserve the exact Pod and use declared checksum-verified recovery")

def main():
    p=parser("Inspect provider capabilities without contacting RunPod")
    p.add_argument("action",choices=["capabilities"])
    p.parse_args()
    return {"provider":"official RunPod REST v1","live_creation":False,"deadline_guarantee":False,"mock_lifecycle":True,"reason":"runpodctl#330 removed nonfunctional deadline flags; no cloud calls made"}
