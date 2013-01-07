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
You will also need to install CUPS, Samba, Python, a 
supported driver for your printer under Linux.

### Installation

First, configure Samba to create a share available to 
anyone on the network.  

Hint: Use the samba.conf file as an example.

Then get your printer working with the CUPS system
you have installed. That isn't covered here. 

Finally you may add the crontab entry to a user 
who as read-write access to the share.

Now you may print by placing PDF files on the share.
You might find other files print well, too. YMMV.

### Acknowledgements

I've shamelessly used John Wiegley's (johnw auf 
newartisans.com) directory scanning python code to
search for and housekeep directory state for new
files to print. It's seems pretty robust but once
in a while a file will get deleted and won't print.
I estimate this happens about 1% of the time (YMMV)
but it hasn't happened in while.

I've included his code here as a zip file but I
added a ".remove" extension.

