#!/bin/bash

pip install pyang pyangbind

SDIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p $SDIR/yang

git clone https://github.com/openconfig/public $SDIR/yang/


PYBINDPLUGIN=`/usr/bin/env python3 -c 'import pyangbind; import os; print ("{}/plugin".format(os.path.dirname(pyangbind.__file__)))'`
pyang --plugindir $PYBINDPLUGIN -f pybind -p $SDIR/yang/ -o $SDIR/ocbind.py $SDIR/yang/release/models/bgp/openconfig-bgp.yang --ignore-errors
#pyang --plugindir $PYBINDPLUGIN -f pybind -p $SDIR/yang/ -o $SDIR/ocnet.py $SDIR/yang/release/models/network-instance/openconfig-network-instance.yang --ignore-errors

echo "Bindings successfully generated!"