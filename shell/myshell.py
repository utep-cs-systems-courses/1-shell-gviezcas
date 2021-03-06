#! /usr/bin/env python3

import os, sys, re

os.environ['PS1'] = '<#> '
runProgram = 1
fdIn = 0
fdOut = 1
fdError = 2
currentDir = os.getcwd()

def execCommand(command):
    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir, command)
        try:
            os.execve(program, [command, ], os.environ)
        except FileNotFoundError:
            pass

while runProgram:
    os.write(fdOut, ("%s\n" % currentDir).encode())
    os.write(fdOut, os.environ['PS1'].encode())
    rc = os.fork()
    if rc: #parent
        status = os.wait()
        if status[1]:
            sys.exit(status[1])
        else:
            continue
    elif rc < 0:
        os.write(fdError, ("Fork failed, returning %d\n" % rc).encode())
        os.write(fdError, "Program terminated with exit code 1.")
        sys.exit(1)
    else: #child
        command = os.read(fdIn, 10000).decode().split()
        if len(command) == 0:
            os.write(fdOut, "Please enter a command.\n".encode())
            continue
        if len(command) == 1:
            if command[0].lower() == "exit":
                os.write(fdOut, "Exiting...\n".encode())
                sys.exit(1)
            else:
                execCommand(command[0])
                os.write("%s: Command not found.\n" % command[1]).encode()
                sys.exit(0)
        elif len(command) > 1:
            if command[0].lower() == "cd":
                if os.path.exists(command[1]):
                    os.chdir(command[1])
                    currentDir = os.getcwd()
                    continue
                else:
                    os.write(fdOut, ("Invalid path: %s\n" % command[1]).encode())
                    continue
            elif command[1] == ">":
                os.close(fdOut)
                os.open(command[2], os.O_CREAT | os.O_WRONLY)
                os.set_inheritable(1, True)
                execCommand(command[0]) 
                os.write(fdOut, ("%s: Command not found.\n" % command[0]).encode())
                sys.exit(0)
            elif command[1] == "|":
                pr, pw = os.pipe()
                for f in (pr, pw):
                    os.set_inheritable(f, True)
                secondFork = os.fork()
                if secondFork < 0:
                    os.write(fdOut, "Fork failed..")
                    sys.exit(1)
                elif secondFork: #second parent
                    os.wait()
                    os.close(fdIn)
                    os.dup2(pr, fdIn)
                    for fd in (pr, pw):
                        os.close(fd)
                    execCommand(command[2])
                    sys.exit(0)
                else: #second child
                    os.close(fdOut)
                    os.dup2(pw, fdOut)
                    for fd in (pr, pw):
                        os.close(fd)
                    execCommand(command[0])
                    sys.exit(0)
