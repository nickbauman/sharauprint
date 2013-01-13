#!/usr/bin/python

import apt_pkg, apt
from subprocess import call
import os

class InstallProgress(apt.progress.InstallProgress):

  def fork(self):
    pass # don't fork
  

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

def main():
  """Main."""
  print "Installing some packages you will need"
  pkgList = ["git", "cups", "python-cups", "samba", "avahi-daemon"]
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
 
  if not os.path.exists("airprint-generate"):
    # download and create airprint services
    print "Fetching airprint-generate." 
    call(["git", "clone", "https://github.com/tjfontaine/airprint-generate"])
  print "Generating airprint services."
  call(["python", "airprint-generate/airprint-generate.py"])
   
if __name__ == "__main__":
  main()

