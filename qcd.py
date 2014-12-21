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


from os.path import expanduser, isfile
from os import getcwd
import anydbm
from optionparser import OptionParser, Command, Configuration
import sys

import tabularize

# Global configuration parameters
name = "qcd"
options = dict()
default_db_file = "~/." + name + "db"


# Wrappers for managing the database

def initialize_database (writeable = False):
    file = expanduser ( options["dbfile"].value )

    if not writeable and not isfile(file):
        print >> sys.stderr, "Database is empty! Try adding something!"
        sys.exit (1)

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

def syntaxError (info = ""):
    print >> sys.stderr, "Syntax error!" + info
    parser.usage ()
    sys.exit (2)



# Implementation of the commands

def add (args):
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

def save (args):
    if len (args) > 1:
        syntaxError ()

    args.append ( getcwd() )
    add (args)

def change (args):
    if len (args) != 2:
        syntaxError ()

    db = initialize_database (True)

    if not args[0] in db:
        print >> sys.stderr, args[0] + " does not exist in the database."
        close_database (db)
        sys.exit (1)

    db[args[0]] = args[1]

    close_database (db)

def move(args):
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

def delete (args):
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

def list (args):
    if len (args) != 0:
        syntaxError ()

    db = initialize_database ()
    tabularize.write (sorted (db.iteritems()), writeable = sys.stderr)
    close_database (db)


def get (args):
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
    options["dbfile"] = cmdParser.add ( Configuration ("f", "file", 
                                       "Specifies which database to use",
                                       default_db_file, syntax = "FILENAME") )
    # The commands
    options["help"] = cmdParser.add ( Command ("h", "help", 
                                       "Prints this helpful message", 
                                       lambda args:cmdParser.usage ()) )

    options["add"] = cmdParser.add( Command ("a", "add", 
                                     "Add a new entry into the database", 
                                     add, syntax = "[LABEL] PATH") )

    options["save"] = cmdParser.add( Command ("s", "save", 
                                      "Add current path into the database", 
                                      save, syntax = "[LABEL]") )

    options["move"] = cmdParser.add( Command ("m", "move", 
                                      "Rename an entry in the database", 
                                      move, syntax = "FROM TO") )

    options["change"] = cmdParser.add( Command ("c", "change", 
                                        "Changes the path of an entry in the database", 
                                        change, syntax = "LABEL NEW_PATH") )

    options["delete"] = cmdParser.add( Command ("d", "delete", 
                                        "Delete an entry from the database", 
                                        delete, syntax = "LABEL") )

    options["list"] = cmdParser.add( Command ("l", "list", 
                                      "List the entries in the database", 
                                      list) )

    options["retrieve"] = cmdParser.add( Command ("g", "get", 
                                          "Retrieve an entry from the database",
                                          get, True, syntax = "LABEL") )
    return cmdParser


# main
if ( __name__ == "__main__" ):
    # Create a Command Line Parser
    qcdCmdParser = createQcdCmdLineParser()

    # Parse it!
    qcdCmdParser.parse ()
    
