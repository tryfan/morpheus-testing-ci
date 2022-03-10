from pymorpheus import MorpheusClient
import os
import time
import yaml

#print(os.environ)
# Setup vars from env
# morpheusUrl = os.environ['morpheus_url']
morpheusUsername = os.environ['morpheus_user']
morpheusPassword = os.environ['morpheus_pass']
morpheusLicense = os.environ['morpheus_license']

#Get URL from yaml file
if 'morpheus_url' in os.environ:
    morpheusUrl = os.environ['morpheus_url']
else:
    with open('urlvar.yml', 'r') as v:
        urlVarYaml = yaml.load(v)
        morpheusUrl = urlVarYaml['morpheus_url']

morpheusAlive = False
while not morpheusAlive:
    try:
        morpheus = MorpheusClient(morpheusUrl, username=morpheusUsername, password=morpheusPassword, sslverify=False)
        result = morpheus.call("get","/ping")
        print(result)
        if result['success'] == True:
            morpheusAlive = True
    except:
        print("Checking...")
        time.sleep(4)
    
licenseJson = '{"license": "%s"}' % morpheusLicense
putLicense = morpheus.call("post", "/license", jsonpayload=licenseJson)
