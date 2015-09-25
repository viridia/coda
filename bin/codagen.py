#!/usr/bin/env python3
'''
codagen -- compiler and code generator for CODA

@author: talin
@copyright:  2014 Talin. All rights reserved.
@license: Apache License 2.0

@contact: viridia@gmail.com
'''

import sys
import os
import traceback
import importlib
import coda.compiler.errors
import coda.compiler.parser
import coda.compiler.analyzer

from optparse import OptionParser
from collections import defaultdict

__all__ = []
__version__ = 0.1

DEBUG = 1

def parseFile(parser, path):
  try:
    fh = open(path, 'r')
  except FileNotFoundError:
    sys.stderr.write("Error: file '{0}' not found.\n".format(path))
    sys.exit(-1)
  try:
    src = fh.read()
  finally:
    fh.close()
  return parser.parse(src, sourcePath=path)

class BackendOptions:
  def __init__(self):
    self.__used = False

  def parseOptions(self, options):
    for s in options.split(';'):
      key, value = s.split('=')
      if hasattr(self, key):
        raise Exception("Option key {0} was already set.".format(key))
      setattr(self, key, value)

  def setUsed(self):
    self.__used = True

  def wasUsed(self):
    return self.__used

  def getOption(self, key):
    return self.__dict__.get(key)

  def __contains__(self, key):
    return self.__dict__.__contains__(key)

def main(argv=None):
  '''Command line options.'''
  program_name = os.path.basename(sys.argv[0])
  program_version = "v0.1"

  program_version_string = '%%prog %s' % program_version
  program_usage = 'Usage: %prog [options] input_files...'
  program_longdesc = ''''''  # optional - further explanation about what the program does
  program_license = "Copyright 2014 Talin\n\
      Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"

  if argv is None:
    argv = sys.argv[1:]
  try:
    # setup option parser
    parser = OptionParser(
        version=program_version_string,
        epilog=program_longdesc,
        description=program_license,
        usage=program_usage)
    parser.add_option(
        "-o", "--out",
        dest="out",
        action='append',
        help="output directory for language LANG", metavar="LANG:DIR")
    parser.add_option(
        "--headerout",
        dest="headerout",
        action='append',
        help="header output directory for language LANG", metavar="LANG:DIR")
    parser.add_option(
        "--opt",
        dest="opt",
        action='append',
        help="Option for language LANG", metavar="LANG:OPT")
    parser.add_option(
        "-v", "--verbose",
        dest="verbose",
        action="store_true",
        help="print additional status information (not implemented)")
    parser.add_option(
        "--seperate_field_init",
        dest="sepeate_field_init",
        action="store_true",
        help="use a separate source file for field descriptors (internal only)")

    # process options
    (opts, args) = parser.parse_args(argv)

#     if opts.verbose:
#       print("verbosity level = %d" % opts.verbose)

    # Parsing Phase
    errors = coda.compiler.errors.ErrorReporter()
    asts = []
    imports = []
    files = {}
    parser = coda.compiler.parser.Parser(errors)
    for path in args:
      ast = parseFile(parser, path)
      if ast:
        asts.append(ast)
        files[path] = ast

    if not opts.out:
      sys.stderr.write(program_name + ": No output specified.\n")
      sys.exit(-1)
        
    def readImports(file):
      for public, relPath in file.imports:
        importPath = os.path.join(os.path.dirname(file.path), relPath)
        if importPath not in files:
          ast = parseFile(parser, importPath)
          if ast:
            files[importPath] = ast
            imports.append(ast)
            readImports(ast)

    for file in asts:
      readImports(file)

    # Check errors and exit
    if (errors.getErrorCount() > 0):
      sys.exit(-1)

    # Analysis phase
    fdList = coda.compiler.analyzer.Analyzer(errors).run(asts, imports)

    # Check errors and exit
    if (errors.getErrorCount() > 0):
      sys.exit(-1)

    # Code Generation phase
    backendOptionMap = defaultdict(BackendOptions)
    if opts.opt:
      for opt in opts.opt:
        lang, value = opt.split(':')
        backendOptionMap[lang].parseOptions(value)

    headerDirMap = {}
    if opts.headerout:
      for opt in opts.headerout:
        lang, value = opt.split(':')
        headerDirMap[lang] = value

    # Code Generation phase
    for out in opts.out:
      lang, _, dirpath = out.partition(':')
      if not dirpath:
        sys.stderr.write('Invalid output specification: ' + out)
        sys.exit(-1)
      if not os.path.isdir(dirpath):
        sys.stderr.write('Not a directory: ' + dirpath)
        sys.exit(-1)

      backendOpts = backendOptionMap.get(lang)
      if backendOpts:
        backendOpts.setUsed()
      else:
        backendOpts = BackendOptions()
      generators = importlib.import_module(
          'coda.backend.{0}'.format(lang)).createGenerators(backendOpts)
      for gen in generators:
        gen.setOutputDir(dirpath)
        if lang in headerDirMap:
          gen.setHeaderOutputDir(headerDirMap[lang])
        gen.run(fdList)

    for lang, backendOpts in backendOptionMap.items():
      if not backendOpts.wasUsed():
        raise Exception('Unused options: ' + lang)

    return 0

  except Exception as e:
    sys.stderr.write(program_name + ": " + repr(e) + "\n")
    traceback.print_exc()
    return 2

if __name__ == "__main__":
  sys.exit(main())
