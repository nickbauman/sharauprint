# sharauprint

### Print Automatically a file on a share

This project exists because my printer driver was no 
longer supported by my OS (driver support was dropped
from Snow Leapoard) but my printer was perfectly
usable. So I did this so I could continue to use my
printer. What I found was it was so much easier to
drag and drop a bunch of files I wanted printing than
to actually open them and print them from the app.

So I thought it was valuable anyway. And now nobody
has to have a driver for a particular printer: you
just need for Linux to support it and your OS to be
able to make PDF files you can drop on a share.

### Requirements
 
For this you will need a Linux box. I used a Raspberry Pi.
You will also need to install git, CUPS, Samba, Python, a 
supported driver for your printer under Linux.

The install.py program will attempt to automate this. It
is still a work in progress but it seems to work well for
me. Let me know if you find any bugs.

### Installation

Run sudo install.py with your printer turned on and 
connected to the Linux machine.

Here is what the installer does:

It configures Samba to create a share available to 
anyone on the network.  

It then creates crontab entry to a user 
who as read-write access to the share. This
runs the checkprint.py program once a minute looking
for print jobs in the share.

This is so you may print by placing PDF files on 
the share.

You might find other files print well, too. YMMV.

You should also see your printers available as
AirPrinters, too, so you can print from AirPrint
capable devices such as your cell phone or Mac.

### Acknowledgements

This software boldly uses Timothy J Fontaine 
(tjfontaine 
auf atxconsulting punkt com) fine airprint
generate program to generate AirPrint servers
automatically from CUPS printers as God intended.

I've shamelessly used John Wiegley's (johnw auf 
newartisans punkt com) directory scanning python code to
search for and housekeep directory state for new
files to print. It's seems pretty robust but once
in a while a file will get deleted and won't print.
I estimate this happens about 1% of the time (YMMV)
but it hasn't happened in while.

I've included John's code here as a zip file but I
added a ".remove" extension.

