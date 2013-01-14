#!/usr/bin/python

import apt_pkg, apt, re

from subprocess import call
from tempfile import mkstemp
from shutil import move, copy
from os import remove, path, mkdir, close


pkgList = ["git", "cups", "python-cups", "samba", "avahi-daemon"]
smbShare = '/srv/sharauprint'

class InstallProgress(apt.progress.InstallProgress):

  def fork(self):
    pass # don't fork
  
def found_in_file(fileName, pattern):
  with open(fileName) as f:
    for line in f:
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
  versions = package.VersionList
  version = versions[0]
  for other_version in versions:
    if apt_pkg.VersionCompare(version.VerStr, other_version.VerStr)<0:
      version = other_version
   
  if package.CurrentVer:
    current = package.CurrentVer
    if apt_pkg.VersionCompare(current.VerStr, version.VerStr)<0:
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
  print "Installing %s packages via apt" % ", ".join(pkgList) 
  apt_pkg.init_config()
  apt_pkg.init_system()
  cache = apt_pkg.Cache()
  cacheManager = apt_pkg.DepCache(cache)
  installerate = lambda pkgName: install_if_missing(cache, cacheManager, pkgName)
  result = map(installerate, pkgList)

  if any(result):
    # install or update these packages
    fetchProgress = apt.progress.TextFetchProgress()
    #installProgress = apt.progress.InstallProgress()
    installProgress = InstallProgress()
    cacheManager.commit(fetchProgress, installProgress)
  else:
    print "Packages already installed"
  
def create_avahi_srvs():
  if not path.exists("airprint-generate"):
    print "Fetching airprint-generate." 
    call(["git", "clone", "https://github.com/tjfontaine/airprint-generate"])
  print "Generating airprint services."
  call(["python", "airprint-generate/airprint-generate.py"])

def create_print_share():
  print "Creating SMB printer share in %s" % smbShare
  try:
    with open(smbShare) as f:
      pass
    mkdir(smbShare, mode=0777)  
  except:
    print "Directory %s already exists! Making world writable" % smbShare 
    call(["chmod", "777", smbShare])
  try:
    with open('/etc/samba/smb.conf') as f:
      print "Samba config found. Will add sharauprint if necessary." 
    if not found_in_file('/etc/samba/smb.conf', '.*sharauprint.*'):
      print "Backing up existing samba config."
      copy('/etc/samba/smb.conf', '/etc/samba/smb.conf.sharauprint.bak')
      token_inflate("templates/smb.conf.tmpl", '$SRV_PATH', smbShare, '/etc/samba/smb.conf', True)
      call(["service", "smbd", "restart"])
    else:
      print "It appears as though you've already configured a sharauprint share. Skipping."
  except:
    print "This is truly a bug. Cannot find your samba installation"

def main():
  """Main."""
  aptget_deps()
  create_avahi_srvs() 
  create_print_share()
   
if __name__ == "__main__":
  main()

