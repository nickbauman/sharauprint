#!/usr/bin/python

import sys
from os.path import expanduser
from dirscan import Entry, DirScanner, safeRemove, processOptions
from subprocess import call

#TODO replace duplicated constants into a single dependency
SMB_SHARE_PATH = '/srv/sharauprint'

class PrintEntry(Entry):
  def onEntryAdded(self):
    print self.path
    if self.path.startswith("._"):
      return Entry.onEntryAdded(self)
    # lpr -o portrait -o media=Letter -o fit-to-page
    call(["lpr", "-o", "fit-to-page", self.path])
    return Entry.onEntryAdded(self)
 
d = DirScanner(directory        = SMB_SHARE_PATH,
               days             = 0.001,
               sudo             = True,
               depth            = 0,
               minimalScan      = True,
               onEntryPastLimit = safeRemove)

d.registerEntryClass(PrintEntry)
d.scanEntries()
