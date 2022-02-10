#! /usr/bin/env python3

import os, sys

PS1 = "<#>"
runProgram = 1
fdIn = 0
fdOut = 1
fdError = 2
currentDir = os.getcwd()

while runProgram:
    os.write(fdOut, PS1.encode())
    rc = os.fork()  
    if rc: #parent
        status = os.wait()
    elif rc < 0:
        os.write(fdError, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    else: #child
        env = {'ls':'list'}
        command = os.read(fdIn, 10000).split()
        if len(command) == 0:
            os.write(fdOut, "Please enter a command.\n".encode())
            continue
        os.execve("/bin/bash", command, os.environ)
