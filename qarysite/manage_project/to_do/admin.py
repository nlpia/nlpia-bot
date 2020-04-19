
#!/usr/bin/env python
from ncclient import manager 
host = "5.1.105.105" 
user = "moh@hrinsvpn"
pw = "123321"
port = 2022
with manager.connect_ssh(host=host, port=port,
username=user, look_for_keys=False,
password=pw,
allow_agent=False,
hostkey_verify=False) as m:
c = m.get_config(source='running').data_xml with open("%s.xml" % host, 'w') as f:
f.write(c)
