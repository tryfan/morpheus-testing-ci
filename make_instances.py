from asyncio.windows_events import NULL
from pymorpheus import MorpheusClient
import os
import json
import time
from pprint import pprint
import yaml

# print(os.environ)
# Setup vars from env
# morpheusUrl = os.environ['morpheus_url']
morpheusUsername = os.environ['morpheus_user']
morpheusPassword = os.environ['morpheus_pass']
#Get URL from yaml file
with open('urlvar.yml', 'r') as v:
    urlVarYaml = yaml.load(v)
    morpheusUrl = urlVarYaml['morpheus_url']

# morpheusUrl = 'https://morph.tldtrash.xyz'
# morpheusUsername = 'admin'
# morpheusPassword = 'morphPass1@'

morpheus = MorpheusClient(morpheusUrl, username=morpheusUsername, password=morpheusPassword)

callCloudSync = morpheus.call("post", "/zones/1/refresh")
if not callCloudSync['success']:
    print("Cloud sync is not successful")

timeCheck = 0
waitForCloudSync = morpheus.call("get", "/zones/1")
if waitForCloudSync['zone']['lastUpdated'] is NULL:
    time.sleep(5)
    while waitForCloudSync['zone']['lastUpdated'] is NULL:
        timeCheck += 1
        if timeCheck == 12:
            break
        waitForCloudSync = morpheus.call("get", "/zones/1")

with open('centos1.json', 'r') as centosfile:
    centos1data = centosfile.read()
centos1 = json.loads(centos1data)

with open('ubuntu1.json', 'r') as ubuntufile:
    ubuntu1data = ubuntufile.read()
ubuntu1 = json.loads(ubuntu1data)

with open('win1.json', 'r') as winfile:
    win1data = winfile.read()
win1 = json.loads(win1data)

## stupid collection bug fix
viget = morpheus.call("get", "/virtual-images", options=[("name", "Windows 2019 AMI New")])
for vi in viget['virtualImages']:
    viid = vi['id']
viupdate = dict()
# viupdate['virtualImage']['osType']['id'] = viid
viupdate = dict( 
    virtualImage = dict(
        osType = dict(
            name = "windows server 2019"
        )
    )
)
time.sleep(1)
viupdateresult = morpheus.call("PUT", "/virtual-images/%s" % viid, jsonpayload=json.dumps(viupdate))
# print(viupdateresult)

spget_linux = morpheus.call("get", "/service-plans", options=[('code', 'amazon-t2.nano')])
spid_linux = spget_linux['servicePlans'][0]['id']
spget_win = morpheus.call("get", "/service-plans", options=[('code', 'amazon-t2.medium')])
spid_win = spget_win['servicePlans'][0]['id']
centos1['instance']['plan']['id'] = spid_linux
ubuntu1['instance']['plan']['id'] = spid_linux
win1['instance']['plan']['id'] = spid_win

# Get CentOS Layout
centitget = morpheus.call("get", "/instance-types", options=[('name', 'centos')])
for centit in centitget['instanceTypes']:
    if centit['code'] == "centos":
        for centitl in centit['instanceTypeLayouts']:
            if centitl['provisionTypeCode'] == "amazon":
                centitlid = centitl['id']
                break

centos1['instance']['layout']['id'] = centitlid
centos1['instance']['layout']['code'] = None
time.sleep(1)

# Get Ubuntu Layout
ubuntuitget = morpheus.call("get", "/instance-types", options=[('name', 'ubuntu')])
for ubuntuit in ubuntuitget['instanceTypes']:
    if ubuntuit['code'] == "ubuntu":
        for ubuntuitl in ubuntuit['instanceTypeLayouts']:
            if ubuntuitl['provisionTypeCode'] == "amazon":
                ubuntuitlid = ubuntuitl['id']
                break

ubuntu1['instance']['layout']['id'] = ubuntuitlid
ubuntu1['instance']['layout']['code'] = None
time.sleep(1)

# Get Windows Layout
winitget = morpheus.call("get", "/instance-types", options=[('name', 'newbuilds')])
for winit in winitget['instanceTypes']:
    if winit['code'] == "newbuilds":
        for winitl in winit['instanceTypeLayouts']:
            if winitl['name'] == "Win2019":
                winitlid = winitl['id']

win1['instance']['layout']['id'] = winitlid
time.sleep(1)

rpget = morpheus.call("get", "/zones/1/resource-pools")
for rp in rpget['resourcePools']:
    if rp['name'] == "morpheus_test_vpc":
        rpid = rp['id']
centos1['config']['resourcePoolId'] = rpid
ubuntu1['config']['resourcePoolId'] = rpid
win1['config']['resourcePoolId'] = rpid

time.sleep(1)
nwget = morpheus.call("get", "/networks")
for nw in nwget['networks']:
    if str(nw['name']).startswith("morpheus_test_vpc-public-us-east-1d"):
        nwid = nw['id']
centos1['networkInterfaces'][0]['network']['id'] = nwid
ubuntu1['networkInterfaces'][0]['network']['id'] = nwid
win1['networkInterfaces'][0]['network']['id'] = nwid

time.sleep(1)
sgget = morpheus.call("get", "/security-groups")
for sg in sgget['securityGroups']:
    if sg['name'] == "default":
        for loc in sg['locations']:
            if loc['zonePool']['name'] == "morpheus_test_vpc":
                sgid = loc['externalId']
centos1['securityGroups'][0]['id'] = sgid
ubuntu1['securityGroups'][0]['id'] = sgid
win1['securityGroups'][0]['id'] = sgid

# pprint(centos1)
# pprint(ubuntu1)

time.sleep(1)
centosresult = morpheus.call("post", "/instances", jsonpayload=json.dumps(centos1))
print(centosresult)
time.sleep(1)
ubunturesult = morpheus.call("post", "/instances", jsonpayload=json.dumps(ubuntu1))
print(ubunturesult)
time.sleep(1)
winresult = morpheus.call("post", "/instances", jsonpayload=json.dumps(win1))
print(winresult)

NotAllRunning = True

time.sleep(30)
while NotAllRunning:
    NotAllRunning = False
    getinstances = morpheus.call("get","/instances")
    for instance in getinstances['instances']:
        if instance['status'] != "running":
            NotAllRunning = True
    if NotAllRunning:
        time.sleep(10)

print("All instances up!")