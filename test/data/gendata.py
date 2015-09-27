#!/usr/bin/env python3
'''
gendata -- generate sample data for CODA unit tests.

@author: talin
@copyright:  2015 Talin. All rights reserved.
@license: Apache License 2.0

@contact: viridia@gmail.com
'''

import sys
import os
import pathlib
import io
import traceback
from coda.io.textcodec import TextCodec
from coda.io.binarycodec import BinaryCodec
import sample

from optparse import OptionParser

__all__ = []
__version__ = 0.1

def createSample():
  s1 = sample.S1()
  s1.setScalarBoolean(True)
  s1.setScalarI16(11);
  s1.setScalarI32(12);
  s1.setScalarI64(13);
  s1.setScalarFixedI16(14);
  s1.setScalarFixedI32(15);
  s1.setScalarFixedI64(16);
  s1.setScalarFloat(55.0);
  s1.setScalarDouble(56.0);
  s1.setScalarString("alpha\n\t");
  s1.setScalarBytes(b"beta");
  s1.setScalarEnum(sample.E.E1);

  s1.getMutableListBoolean().append(True)
  s1.getMutableListBoolean().append(False)
  s1.getMutableListBoolean().append(True)

  s1.getMutableListInt().append(100)
  s1.getMutableListInt().append(101)
  s1.getMutableListInt().append(102)

  s1.getMutableListFloat().append(110.0)
  s1.getMutableListFloat().append(110.1)
  s1.getMutableListFloat().append(110.2)

  s1.getMutableListString().append('beta')
  s1.getMutableListString().append('delta\0')
  s1.getMutableListString().append('yin-yan: ☯')

  s1.getMutableListEnum().append(sample.E.E1)
  s1.getMutableListEnum().append(sample.E.E2)
  s1.getMutableListEnum().append(sample.E.E1)

  s1.getMutableSetInt().add(200)
  s1.getMutableSetInt().add(201)
  s1.getMutableSetInt().add(202)

  s1.getMutableSetString().add('gamma')
  s1.getMutableSetString().add('\'single-quoted\'')
  s1.getMutableSetString().add('\"double-quoted\"')

  s1.getMutableSetEnum().add(sample.E.E1)
  s1.getMutableSetEnum().add(sample.E.E2)
  s1.getMutableSetEnum().add(sample.E.E1)
  
  s1.getMutableMapIntString()[300] = 'three_oh_oh'
  s1.getMutableMapIntString()[301] = 'three_oh_one'
  
  s1.getMutableMapStringInt()['three_oh_oh'] = 300
  s1.getMutableMapStringInt()['three_oh_one'] = 301
  
  s1.getMutableMapEnumStruct()[sample.E.E1] = sample.S1()
  s1.getMutableMapEnumStruct()[sample.E.E2] = sample.S2()

  s2 = sample.S2()
  s2.setLeft(s1)
  
  s3 = sample.S3()
  s3.getMutableSList().append(sample.S1())
  s3.getMutableSList().append(sample.S2())
  s2.setRight(s3)
  return s2

# struct S2(S1) = 1 {
#   left: S1 = 1;
#   right: S1 = 2;
# }
# 
# struct S3(S1) = 2 {
#   sList : list[S1] = 1;
#   sSet : set[S1] = 2;
#   sMap : map[string, S1] = 3;
# }

def main(argv=None):
  '''Command line options.'''
  program_name = os.path.basename(sys.argv[0])
  program_version = "v0.1"

  program_version_string = '%%prog %s' % program_version
  program_usage = 'Usage: %prog [options] input_files...'
  program_longdesc = ''''''  # optional - further explanation about what the program does
  program_license = "Copyright 2015 Talin\n\
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

    # process options
    (opts, args) = parser.parse_args(argv)
    
    s = createSample()

    if not opts.out:
      sys.stderr.write(program_name + ": No output specified.\n")
      sys.exit(-1)
        
    for out in opts.out:
      format, _, filepath = out.partition(':')
      if not filepath:
        sys.stderr.write('Invalid output specification: ' + out)
        sys.exit(-1)
      filepath = pathlib.Path(filepath)
      if format == 'text':
        stream = filepath.open('w')
        encoder = TextCodec.createEncoder(stream)
        s.encode(encoder)
        stream.close()
      elif format == 'bin':
        stream = filepath.open('wb')
        encoder = BinaryCodec.createEncoder(stream)
        s.encode(encoder)
        stream.close()
      else:
        sys.stderr.write('Invalid output format: ' + format)
        sys.exit(-1)

    return 0

  except Exception as e:
    sys.stderr.write(program_name + ": " + repr(e) + "\n")
    traceback.print_exc()
    return 2

if __name__ == "__main__":
  sys.exit(main())
