from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import json
import logging
import os
import re
import ssl
import sys
import six
import requests

try:
  import gnmi_pb2
except ImportError:
  print('ERROR: Ensure you\'ve installed dependencies from requirements.txt\n'
        'eg, pip install -r requirements.txt')
import gnmi_pb2_grpc

target = '10.20.30.24'
port = '7000'
user = 'arista'
password = 'arista'
mode = 'set-update'

_RE_PATH_COMPONENT = re.compile(r'''
^
(?P<pname>[^[]+)  # gNMI path name
(\[(?P<key>\w+)   # gNMI path key
=
(?P<value>.*)    # gNMI path value
\])?$
''', re.VERBOSE)

def _path_names(xpath):
  """Parses the xpath names.
  This takes an input string and converts it to a list of gNMI Path names. Those
  are later turned into a gNMI Path Class object for use in the Get/SetRequests.
  Args:
    xpath: (str) xpath formatted path.
  Returns:
    list of gNMI path names.
  """
  if not xpath or xpath == '/':  # A blank xpath was provided at CLI.
    return []
  return xpath.strip().strip('/').split('/')  # Remove leading and trailing '/'.

_path_names('ddddd')

def _parse_path(p_names):
  """Parses a list of path names for path keys.
  Args:
    p_names: (list) of path elements, which may include keys.
  Returns:
    a gnmi_pb2.Path object representing gNMI path elements.
  Raises:
    XpathError: Unabled to parse the xpath provided.
  """
  gnmi_elems = []
  for word in p_names:
    word_search = _RE_PATH_COMPONENT.search(word)
    if not word_search:  # Invalid path specified.
      raise XpathError('xpath component parse error: %s' % word)
    if word_search.group('key') is not None:  # A path key was provided.
      tmp_key = {}
      for x in re.findall(r'\[([^]]*)\]', word):
        tmp_key[x.split("=")[0]] = x.split("=")[-1]
      gnmi_elems.append(gnmi_pb2.PathElem(name=word_search.group(
          'pname'), key=tmp_key))
    else:
      gnmi_elems.append(gnmi_pb2.PathElem(name=word, key={}))
  return gnmi_pb2.Path(elem=gnmi_elems)


#print(paths)

def _create_stub(target, port):
  channel = gnmi_pb2_grpc.grpc.insecure_channel(target + ':' + port)
  return gnmi_pb2_grpc.gNMIStub(channel)

def _format_type(json_value):
  """Helper to determine the Python type of the provided value from CLI.
  Args:
    json_value: (str) Value providing from CLI.
  Returns:
    json_value: The provided input coerced into proper Python Type.
  """
  if (json_value.startswith('-') and json_value[1:].isdigit()) or (
      json_value.isdigit()):
    return int(json_value)
  if (json_value.startswith('-') and json_value[1].isdigit()) or (
      json_value[0].isdigit()):
    return float(json_value)
  if json_value.capitalize() == 'True':
    return True
  if json_value.capitalize() == 'False':
    return False
  return json_value  # The value is a string.

def _get_val(json_value):
  """Get the gNMI val for path definition.
  Args:
    json_value: (str) JSON_IETF or file.
  Returns:
    gnmi_pb2.TypedValue()
  """
  val = gnmi_pb2.TypedValue()
  set_json = json.loads(six.moves.builtins.open(
      json_value, 'rb').read())
  val.json_ietf_val = json.dumps(set_json).encode()
  return val

def _get(stub, paths, username, password):
  if username:  # User/pass supplied for Authentication.
    return stub.Get(
        gnmi_pb2.GetRequest(path=[paths], encoding='JSON_IETF'),
        metadata=[('username', username), ('password', password)])
  return stub.Get(gnmi_pb2.GetRequest(path=[paths], encoding='JSON_IETF'))

def _set(stub, paths, set_type, username, password, json_value):
  """Create a gNMI SetRequest.
  Args:
    stub: (class) gNMI Stub used to build the secure channel.
    paths: gNMI Path
    set_type: (str) Type of gNMI SetRequest.
    username: (str) Username used when building the channel.
    password: (str) Password used when building the channel.
    json_value: (str) JSON_IETF or file.
  Returns:
    a gnmi_pb2.SetResponse object representing a gNMI SetResponse.
  """
  if json_value:  # Specifying ONLY a path is possible (eg delete).
    val = _get_val(json_value)
    path_val = gnmi_pb2.Update(path=paths, val=val,)

  kwargs = {}
  if username:
    kwargs = {'metadata': [('username', username), ('password', password)]}
  if set_type == 'delete':
    return stub.Set(gnmi_pb2.SetRequest(delete=[paths]), **kwargs)
  elif set_type == 'update':
    return stub.Set(gnmi_pb2.SetRequest(update=[path_val]), **kwargs)
  return stub.Set(gnmi_pb2.SetRequest(replace=[path_val]), **kwargs)

  kwargs = {}
  if username:
    kwargs = {'metadata': [('username', username), ('password', password)]}
  if set_type == 'delete':
    return stub.Set(gnmi_pb2.SetRequest(delete=[paths]), **kwargs)
  elif set_type == 'update':
    return stub.Set(gnmi_pb2.SetRequest(update=[path_val]), **kwargs)
  return stub.Set(gnmi_pb2.SetRequest(replace=[path_val]), **kwargs)

def path_from_string(path='/'):
    mypath = []

    for e in list_from_path(path):
        eName = e.split("[", 1)[0]
        eKeys = re.findall('\[(.*?)\]', e)
        dKeys = dict(x.split('=', 1) for x in eKeys)
        mypath.append(gnmi_pb2.PathElem(name=eName, key=dKeys))

    return gnmi_pb2.Path(elem=mypath)

def get_json():
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    api_call = 'http://127.0.0.1:5000/static/ceos1_bgp.json'
    result = requests.get(api_call, headers=headers, verify=False)
    return(result.text)
    #return(json.dumps(result.text).encode())

def main():
  stub = _create_stub(target, port)
  paths = _parse_path(_path_names('/network-instances/network-instance[name=default]/protocols/protocol[name=BGP][identifier=BGP]/bgp'))
  #metadata=[('username', username), ('password', password)]
  #paths = _parse_path(_path_names(xpath))
  #This prints out the entire elem path with the list broken up
  json_value = get_json()
  stub = _create_stub(target, port)
  #This is easy to understand it simply creates the connection
  if mode == 'get':
    response = _get(stub, paths, user, password)
    print(json.dumps(json.loads(response.notification[0].update[0].val.
                                 json_ietf_val), indent=2))
  elif mode == 'set-update':
    print('Performing SetRequest Update, encoding=JSON_IETF', ' to ', target,
          ' with the following gNMI Path\n', '-'*25, '\n', paths, json_value)
    response = _set(stub, paths, 'update', user, password, json_value)
    print('The SetRequest response is below\n' + '-'*25 + '\n', response)                            

if __name__ == '__main__':
  main()



