#!/usr/bin/python
from ocbind import openconfig_bgp
import json
import pyangbind.lib.pybindJSON as pybindJSON

ocbgp = openconfig_bgp()

ocbgp.bgp.global_.config.as_ = 1 #Configures the rw bgp - > global - > config passes in the oc-inet:as-number

ocbgp.bgp.global_.config.router_id = "1.1.1.1" #Passes in the rw bgp - > global - > config - > router-id passes in the oc-yang:dotted-quad

ocbgp.bgp.neighbors.neighbor.add("10.12.0.2")

ocbgp.bgp.neighbors.neighbor["10.12.0.2"].config.neighbor_address = "10.12.0.2"
ocbgp.bgp.neighbors.neighbor["10.12.0.2"].config.peer_as = 10
ocbgp.bgp.neighbors.neighbor["10.12.0.2"].config.description = "Spine 1"

print(pybindJSON.dumps(ocbgp, mode="ietfww"))

json_data = pybindJSON.dumps(ocbgp, mode="ietf")

with open("../../../flask/static/demo.json", 'w') as f:
  f.write(json_data) 