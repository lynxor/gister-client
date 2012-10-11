#!/usr/bin/python

import json
import urllib
import subprocess
import os
from optparse import OptionParser
import shutil
from os.path import basename

parser = OptionParser()
parser.add_option("-l", "--list", action="store_true",
                  help="list all scripts")

parser.add_option("-s", "--search", dest="search", action="store", type="string",
                  help="search by keyword")

parser.add_option("-r", "--run", dest="run", action="store", type="string",
                  help="download and run directly (not stored locally)")

parser.add_option("-i", "--install", dest="install", action="store", type="string",
                  help="install the script locally( to ~/.gister )")
(options, args) = parser.parse_args()

def listscripts(scripts):
	for script in scripts:
		print "--- " + script["command"] + " ---\n " + script["description"] + "\n " + script["html_url"] + "\n"

def retrievejson(url):
	(filename, info) = urllib.urlretrieve(url)
	return json.JSONDecoder().decode( open(filename).read() ) 

def retrievescript(url):
	print "retrieving script..."
	(filename, info) = urllib.urlretrieve(url)
	print "done"
	return filename

def createcommand(scriptmeta, scriptfile):
	execute = scriptmeta["exec"]
	return execute.replace("$SCRIPT", scriptfile) + " " + " ".join(args[1:])

def ensuredir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

gisterdir = os.getenv("HOME") + "/.gister/"
ensuredir(gisterdir)
gister_host = "http://localhost:8087"

if options.list:
	scripts = retrievejson(gister_host + "/scripts/json")["scripts"]
	print "All available commands: \n"
	listscripts(scripts)
	
elif options.search != None:
	scripts = retrievejson(gister_host + "/scripts/search/json/" + options.search)["scripts"]
	print "Search results: \n"
	listscripts(scripts)

elif options.run:
	scriptmeta = retrievejson(gister_host + "/script/json/command/" + options.run)["script"]
	scriptfile = retrievescript(scriptmeta["url"])
	bashcmd = createcommand(scriptmeta, scriptfile)
	# print bashcmd
	process = subprocess.Popen(bashcmd.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print output

elif options.install != None:

	installdir = gisterdir + options.install +"_files/"
	ensuredir(installdir)

	scriptmeta = retrievejson(gister_host + "/script/json/command/" + options.install)["script"]
	scriptfile = retrievescript(scriptmeta["url"])
	print "installing ..."
	

	shutil.copy(scriptfile, installdir)
	bashcmd = createcommand(scriptmeta, installdir + basename(scriptfile))

	runscript = open(gisterdir + options.install, 'w')
	runscript.write(bashcmd)
	runscript.close()

	os.chmod(gisterdir + options.install, 0775)
	print "Done"

else:
	parser.error("No arguments")





	


	