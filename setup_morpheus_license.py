from pymorpheus import MorpheusClient
import os
import time

#print(os.environ)
# Setup vars from env
morpheusUrl = os.environ['morpheus_url']
morpheusUsername = os.environ['morpheus_user']
morpheusPassword = os.environ['morpheus_pass']
morpheusLicense = os.environ['morpheus_license']

morpheusAlive = False
while not morpheusAlive:
    try:
        morpheus = MorpheusClient(morpheusUrl, username=morpheusUsername, password=morpheusPassword)
        result = morpheus.call("get","/ping")
        print(result)
        if result['success'] == True:
            print("it is true")
            morpheusAlive = True
    except:
        print("Checking...")
        time.sleep(4)
    
licenseJson = '{"license": "%s"}' % morpheusLicense
putLicense = morpheus.call("post", "/license", jsonpayload=licenseJson)