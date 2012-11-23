#!/usr/bin/env python

import sys, glob, os.path

sys.path.append(os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], "..")))
from jcu.tweak_rifcs import fix
from jcu import config, response, log
from argparse import ArgumentParser
from java.io import PrintWriter
from com.googlecode.fascinator.common import FascinatorHome

alerts = {}
execfile(os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], "..", "..", "config", "portal", "default", "redbox", "scripts", "hkjobs", "alerts.py")), globals(), alerts)
AlertsData = alerts["AlertsData"]

#class response:
#    def setStatus(self, status): pass
#
#    def getPrintWriter(self, mime): return PrintWriter()
#
#class config:
#    def __init__(self, home, data):
#        self.data = data
#        self.home = home
#    def getString(self, *args):
#        print args
#        if args[1] == 'redbox.version.string':
#            return "1.5.2.2"
#        d = self.data
#        for i in args[1]:
#            d = d[i]
#        if d is None:
#            return None
#        return d.replace("${fascinator.home}",self.home)
#        if args[1] == ["alerts", "path"]:
#            d = self.data
#            for i in args[1]:
#                d = d[i]
#            return d.replace("${fascinator.home}",self.home)
#        if args[1] == ["alerts", "xmlMaps", "xml"]:
#            return "rifXmlMap.json"
#        return None

#class log:
#    def error(self, *args):
#        print "[ERROR]", args
#
#    def info(self, *args):
#        print "[INFO ]", args
#
#    def debug(self, *args):
#        a = args[0]
#        b = args[1:]
#        print "[DEBUG]", a.format(*b)



if __name__ == "__main__":

    argParse = ArgumentParser(description="Process the JCU RIF-CS imports")
    argParse.add_argument('-i','--inplace', dest='inplace', action='store_true', default=False, help='Update the files in place')
    argParse.add_argument('-o','--output', dest='output', action='store',  help='The output location, mutually exclusive with the inplace option.')
    argParse.add_argument('-p','--redbox-path', dest='path', nargs=1, action='store',  help='The base path of the ReDBoX Install')
    argParse.add_argument('-a','--alert', dest='alerts', action='store_true', default=False, help='Post-process with ReDBoX alert script.')
    argParse.add_argument('-m','--rifcs-map-file', nargs=1, dest='rmap', action='store', default=None, help='The location of the rifcs map file.')
    argParse.add_argument('-x','--xml-map-file', nargs=1, dest='xmap', action='store', default=None, help='The location of the xml map file.')
    argParse.add_argument('file', nargs='+', help='The RIF-CS Files to process (globs accepted)')
    args = argParse.parse_args()

    if args.output is not None and args.inplace:
        print "Options --inplace and --output cannot be used at the same time."
        argParse.print_help()
        sys.exit(5)
    print args.path, args.file

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
            output = args.output[0]
        if args.inplace:
            output = None

        for fl in args.file:
            for _file in glob.glob(fl):
                print "Processing: ", _file
                fix(_file, args, output)

        if args.alerts:
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

