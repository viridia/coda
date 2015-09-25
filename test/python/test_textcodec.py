'''Unit tests for CODA text serialization'''
import io
import unittest
from coda import descriptors
from coda.io.textcodec import TextCodec
from coda.runtime.descdata import BoolValue

class TextCodecTest(unittest.TestCase):
  def dumpBuffer(self, buffer):
    for lineno, line in enumerate(buffer.getvalue().split('\n')):
      print('{0}: {1}'.format(lineno+1, line))
  
  def testEncodeDecodeBoolean(self):
    source = BoolValue()
    source.setValue(True)
    buffer = io.StringIO()
    encoder = TextCodec.createEncoder(buffer)
    source.encode(encoder)
    buffer.seek(0)
#     self.dumpBuffer(buffer)
    decoder = TextCodec.createDecoder(buffer)
    result = decoder.decode(BoolValue)
    self.assertIsInstance(result, BoolValue)
    self.assertTrue(result.isValue())
    self.assertTrue(result.hasValue())
    
  def testEncodeDecodeStructType(self):
    buffer = io.StringIO()
    encoder = TextCodec.createEncoder(buffer)
    descriptors.StructType.DESCRIPTOR.encode(encoder)
    buffer.seek(0)
#     self.dumpBuffer(buffer)
    decoder = TextCodec.createDecoder(buffer)
    st = decoder.decode(descriptors.StructType)
    self.assertIsInstance(st, descriptors.StructType)
    self.assertEqual(st.getFullName(), descriptors.StructType.DESCRIPTOR.getFullName())
