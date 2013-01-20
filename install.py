#!/usr/bin/python

"""
Copyright (c) 2013 Nick Bauman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import apt_pkg, apt, re, mmap, sys

from subprocess import call
from tempfile import mkstemp
from shutil import move, copy
from os import remove, path, mkdir, close, chdir, getcwd

INST_PKG_LIST = ['python-pip', 'git', 'cups', 'python-cups', 'samba', 'avahi-daemon']
SMB_SHARE_PATH = '/srv/sharauprint'
SMB_CONF = '/etc/samba/smb.conf'
SMB_CONF_TMPL = 'templates/smb.conf.tmpl'
AVAHI_SVCS = '/etc/avahi/services/'
AIRPRINT_GEN_SCRIPT = '/airprint-generate/airprint-generate.py'
AVAHI_REPO = 'https://github.com/tjfontaine/airprint-generate'

class InstallProgressSync(apt.progress.base.InstallProgress):

  def fork(self):
    return False # don't fork
  
def found_in_file(fileName, pattern):
  with open(fileName) as f:
    s = mmap.mmap(f.fileno(), 0, mmap.ACCESS_READ)
    for line in s:
      if re.match(pattern):
        return True
  return False 

def token_inflate(file, pattern, subst, outfile, appendMode=False):
  fh, absPath = mkstemp()
  with open(absPath,'w') as tempFile: 
    with open(file) as readFile:
      for line in readFile:
        tempFile.write(line.replace(pattern, subst))
  close(fh)
  if appendMode:
    print "Appending smb config fragments"
    with open(outfile, 'a') as appendFile:
      with open(absPath) as tempFile:
        for line in tempFile:
          appendFile.write(line)
    remove(absPath)   
  else:
    print "Moving file to %s" % outfile 
    move(absPath, outfile)

def check_pkg_status(package):
  versions = package.version_list
  version = versions[0]
  for other_version in versions:
    if apt_pkg.version_compare(version.ver_str, other_version.ver_str)<0:
      version = other_version
   
  if package.current_ver:
    current = package.current_ver
    if apt_pkg.version_compare(current.ver_str, version.ver_str)<0:
      return "upgradable"
    else:
      return "current"
  else:
    return "uninstalled"

def find_package(cache=False, packageName=False):
  if(cache and packageName):
    for pkg in cache.packages:
      if pkg.name == packageName:
        return pkg	
    return False
    
def install_if_missing(cache=False, cacheManager=False, packageName=False):
  if(cache and cacheManager and packageName):
    pkg = find_package(cache, packageName)
    if pkg:
      status = check_pkg_status(pkg)
      if "uninstalled" == status or "upgradable" == status: 
        thePackage = cache[packageName]
        cacheManager.mark_install(thePackage, True)
        return True
      return False
    raise Exception("package '%s' does not exist on this platform" % packageName) 
  raise Exception("missing cache, cacheManager or packageName in call")

def aptget_deps():
  print "Installing %s packages via apt" % ", ".join(INST_PKG_LIST) 
  apt_pkg.init_config()
  apt_pkg.init_system()
  cache = apt_pkg.Cache()
  cacheManager = apt_pkg.DepCache(cache)
  installerate = lambda pkgName: install_if_missing(cache, cacheManager, pkgName)
  result = map(installerate, INST_PKG_LIST)

  if any(result):
    # install or update these packages
    fetchProgress = apt.progress.text.TextProgress()
    installProgress = InstallProgressSync()
    cacheManager.commit(fetchProgress, installProgress)
    print "Packages required to complete the installation have been installed. Please rerun the program."
    sys.exit()
  else:
    print "Packages already installed. Carrying on with installation."
  
def create_avahi_srvs():
  if not path.exists("airprint-generate"):
    print "Fetching airprint-generate." 
    call(["git", "clone", AVAHI_REPO])
  print "Generating airprint services."
  last_dir = getcwd()
  chdir(AVAHI_SVCS)
  call(["python", "".join([last_dir, AIRPRINT_GEN_SCRIPT])])
  chdir(last_dir)
  call(["service", "avahi-daemon", "restart"])

def create_print_share():
  print "Configuring Samba"
  if path.isdir(SMB_SHARE_PATH):
    print "Apparently %s already exists. Ensuring world-writable." % SMB_SHARE_PATH
    call(["chmod", "777", SMB_SHARE_PATH])
  else: 
    print "Creating SMB printer share in %s" % SMB_SHARE_PATH
    mkdir(SMB_SHARE_PATH, 0777)
    if path.isfile(SMB_CONF):
      print "Samba config found. Will add sharauprint if necessary." 
    if not found_in_file(SMB_CONF, '.*sharauprint.*'):
      print "Backing up existing samba config."
      copy(SMB_CONF, "".join([SMB_CONF,'.bak']))
      token_inflate(SMB_CONF_TMPL, '$SRV_PATH', SMB_SHARE_PATH, SMB_CONF, True)
      call(["service", "smbd", "restart"])
    else:
      print "It appears as though you've already configured a sharauprint share. Skipping."
def main():
  """Main."""
  aptget_deps()
  create_avahi_srvs() 
  create_print_share()
   
if __name__ == "__main__":
  main()

