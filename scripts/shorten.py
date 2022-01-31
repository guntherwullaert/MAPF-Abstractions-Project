#!/usr/bin/env python3.0

import os, sys

#remove last line from a text line in python
fd=open(sys.argv[1],"r")
d=fd.read()
fd.close()
m=d.split("\n")
s="\n".join(m[:-2])
fd=open(sys.argv[1],"w+")
for i in range(len(s)):    
    fd.write(s[i])
fd.close()