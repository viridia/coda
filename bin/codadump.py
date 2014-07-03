#!/usr/bin/env python3
'''
codadump -- prints out contents of encoded Coda files

@author: talin
@copyright:  2014 Talin. All rights reserved.
@license: Apache License 2.0

@contact: viridia@gmail.com
'''

import sys
import os
import traceback
import coda.io.binarycodec
import spark.spc.spc # Need to make this a param

import argparse
from optparse import OptionParser
from coda.io import binarycodec, textcodec

__all__ = []
__version__ = 0.1

DEBUG = 1

def main(argv=None):
  '''Command line options.'''
  try:
    # setup option parser
    argParser = argparse.ArgumentParser(
        description="""Coda Dump: Print contents of a binary-encoded Coda file.\n
                       Copyright (c) 2014 Talin.\n
                       Licensed under the Apache License 2.0:\n
                           http://www.apache.org/licenses/LICENSE-2.0""")
    argParser.add_argument(
        "input", action="append", help="input files", metavar="FILE")
    argParser.add_argument("-s", "--skip",
        action="store", help="number if initial bytes to skip", metavar="NUM")
    argParser.add_argument("--debug",
        action="store_true", help="dump debugging information from input stream")

    # process options
    args = argParser.parse_args(argv)

    # Parsing Phase
    for path in args.input:
      try:
        fh = open(path, 'rb')
        if args.skip:
          fh.read(int(args.skip))
        codec = binarycodec.BinaryCodec.createDecoder(fh, path)
        if args.debug:
          codec.setDebug(True)
        obj = codec.read(spark.spc.spc.Module)
        codec = textcodec.TextCodec.createEncoder(sys.stdout)
        codec.writeStruct(obj)
      except FileNotFoundError:
        sys.stderr.write("Error: file '{0}' not found.\n".format(path))
        sys.exit(-1)
      try:
        src = fh.read()
      finally:
        fh.close()

    return 0

  except Exception as e:
    sys.stderr.write(program_name + ": " + repr(e) + "\n")
    traceback.print_exc()
    return 2

if __name__ == "__main__":
  sys.exit(main())
