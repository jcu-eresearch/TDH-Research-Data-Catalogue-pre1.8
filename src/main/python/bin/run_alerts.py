#!/usr/bin/env python

import sys, glob, os.path

sys.path.append(os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], "..")))
from jcu.tweak_rifcs import fix
from argparse import ArgumentParser
from jcu import config, response, log
from com.googlecode.fascinator.common import FascinatorHome

alerts = {}
execfile(os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], "..", "..", "config", "portal", "default", "redbox", "scripts", "hkjobs", "alerts.py")), globals(), alerts)
AlertsData = alerts["AlertsData"]


if __name__ == "__main__":

    argParse = ArgumentParser(description="Process the JCU RIF-CS imports")
    argParse.add_argument('-o','--output', dest='output', action='store',  help='The output location.')
    argParse.add_argument('-m','--rifcs-map-file', nargs=1, dest='rmap', action='store', default=None, help='The location of the rifcs map file.')
    argParse.add_argument('-x','--xml-map-file', nargs=1, dest='xmap', action='store', default=None, help='The location of the xml map file.')
    argParse.add_argument('-p','--redbox-path', dest='path', nargs=1, action='store',  help='The base path of the ReDBoX Install')
    args = argParse.parse_args()

    if args.path is not None and os.path.exists(args.path[0]):
        fascinator_home = os.path.join(args.path[0], "home")

        FascinatorHome.setPath(fascinator_home)
        import json
        system = open(os.path.join(fascinator_home, "system-config.json"))
        system_data = json.load(system)
        system.close()

        _config = config(fascinator_home, system_data)
        output = _config.getString(None, ["alerts", "path"])

        if args.rmap is not None:
            system_data["alerts"]["xmlMaps"]["rif"] = args.rmap[0]
        if args.xmap is not None:
            system_data["alerts"]["xmlMaps"]["xml"] = args.xmap[0]

        if args.output is not None:
            system_data['alerts']['path'] = args.output[0]

        #Imports may be due to the globals or locals in the alert import at top.
        import csv
        from com.googlecode.fascinator import HarvestClient
        from com.googlecode.fascinator.common import FascinatorHome
        from com.googlecode.fascinator.common import JsonObject
        from com.googlecode.fascinator.common import JsonSimple

        from java.io import File
        from java.io import FileInputStream
        from java.io import InputStreamReader
        from java.lang import Exception

        from org.dom4j import DocumentFactory
        from org.dom4j.io import SAXReader
        from org.json.simple import JSONArray
        from org.dom4j.xpath import DefaultNamespaceContext
        from org.dom4j.xpath import DefaultXPath
        from org.jaxen import SimpleNamespaceContext
        import csv
        import os
        import shutil
        import shutil
        import time
        alerts = AlertsData()
        alerts.__activate__({"log":log(), 'systemConfig': _config, 'response': response()})