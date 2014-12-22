#!/usr/bin/env python

# Small program for storing and retrieving paths from a database
# Copyright (C) 2014 Gustav Behm

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from optionparser import OptionParser, Command, Configuration
from os.path import expanduser, isfile
from whichdb import whichdb
from os import getcwd
from glob import glob
import anydbm
import sys
import re

import tabularize

# Global configuration parameters
name = "qcd"
qcdCmdParser = ()
defaultDbFile = "~/." + name + "db"
dbType = ""

# Wrappers for managing the database

def mapDbFileName( filename ):
    fileGlob = expanduser( filename ) + "*"
    for candidateFile in glob( fileGlob ):
        if re.match(".*\.qcddb(\.db)?", candidateFile):
            # If either ~/.qcddb or ~/.qcddb.db has already been created (i.e.
            # previous executions of qcd), then return it.
            return candidateFile
    return filename

def initialize_database (writeable = False):
    # Get the db file name where qcd info is/will_be stored
    file = mapDbFileName( qcdCmdParser.getOption("file").value ) 

    if not writeable and not isfile(file):
        print >> sys.stderr, "Database is empty! Try adding something!"
        sys.exit (1)

    # changing the global dbType variable, it will contain the infomration
    # retrieved from whichdb, which basically says which db implementation was
    # used to create the db file.
    global dbType 
    dbType = whichdb(file)

    # Open the db
    if writeable:
        return anydbm.open (file, 'c')
    else:
        return anydbm.open (file, 'r')

def close_database (db):
    db.close ()

# Helpers

def getAnonymousKey (db):
    i = 1;
    while True:
        if not str(i) in db:
            return str(i)
        i += 1

# Implementation of the commands

def add (syntaxError, args):
    if len (args) == 0 or len (args) > 2:
        syntaxError ()

    db = initialize_database (True)

    if len (args) == 2:
        key = args[0]
        db[key] = args[1]
    else:
        key = getAnonymousKey (db)
        db[key] = args[0]

    close_database (db)

def save (syntaxError, args):
    if len (args) > 1:
        syntaxError ()

    args.append ( getcwd() )
    add (args)

def change (syntaxError, args):
    if len (args) != 2:
        syntaxError ()

    db = initialize_database (True)

    if not args[0] in db:
        print >> sys.stderr, args[0] + " does not exist in the database."
        close_database (db)
        sys.exit (1)

    db[args[0]] = args[1]

    close_database (db)

def move(syntaxError, args):
    if len (args) != 2:
        syntaxError ()

    db = initialize_database (True)

    if not args[0] in db:
        print >> sys.stderr, args[0] + " does not exist in the database."
        close_database (db)
        sys.exit (1)

    if args[1] in db:
        print >> sys.stderr, args[1] + " already exist in the database."
        close_database (db)
        sys.exit (1)

    db[args[1]] = db[args[0]]

    del db[args[0]]

    close_database (db)

def delete (syntaxError, args):
    if len (args) != 1:
        syntaxError ()

    db = initialize_database (True)

    try:
        del db[args[0]]
    except:
        print >> sys.stderr, args[0] + " does not exist in the database."
        close_database (db)
        sys.exit (1)

    close_database (db)

def list (syntaxError, args):
    if len (args) != 0:
        syntaxError ()

    db = initialize_database ()

    if dbType == "dumbdb" or dbType == "bsddb185":
        tabularize.write (sorted ([(key, db[key]) for key in db.keys()]), writeable = sys.stderr)
    else:
        tabularize.write (sorted (db.iteritems()), writeable = sys.stderr)

    close_database (db)


def get (syntaxError, args):
    if len (args) != 1:
        syntaxError ()

    db = initialize_database ()

    try:
        print db[args[0]]
    except:
        print >> sys.stderr, args[0] + " does not exist in the database."
        close_database (db)
        sys.exit (1)

    close_database (db)


# Setting up qcd command line interface
def createQcdCmdLineParser():
    # The command line parser
    cmdParser = OptionParser (name)

    # The options
    cmdParser.addConfiguration("f", "file", "Specifies which database to use",
                                defaultDbFile, syntax = "FILENAME") 
    # The commands
    cmdParser.addCommand("h", "help", "Prints this helpful message", 
                          lambda _,args:cmdParser.usage ()) 

    cmdParser.addCommand("a", "add", "Add a new entry into the database", 
                          add, syntax = "[LABEL] PATH")

    cmdParser.addCommand("s", "save", "Add current path into the database", 
                          save, syntax = "[LABEL]")

    cmdParser.addCommand("m", "move", "Rename an entry in the database", 
                          move, syntax = "FROM TO")

    cmdParser.addCommand("c", "change", 
                         "Changes the path of an entry in the database", 
                          change, syntax = "LABEL NEW_PATH")

    cmdParser.addCommand("d", "delete", "Delete an entry from the database", 
                          delete, syntax = "LABEL") 

    cmdParser.addCommand("l", "list", "List the entries in the database", list)

    cmdParser.addCommand("g", "get", "Retrieve an entry from the database",
                          get, True, syntax = "LABEL")
    return cmdParser


# main
if ( __name__ == "__main__" ):
    # Create a Command Line Parser
    qcdCmdParser = createQcdCmdLineParser()

    # Parse it!
    qcdCmdParser.parse ()

