'''Unit tests for CODA binary serialization'''
import io
import unittest
from coda import descriptors
from coda.io.binarycodec import BinaryCodec
from coda.runtime.descdata import BoolValue

class BinaryCodecTest(unittest.TestCase):
  def setUp(self):
    self.buffer = io.BytesIO()
#     self.encoder = BinaryCodec.createEncoder(self.buffer)
    
  def testEncodeDecodeBoolean(self):
    source = BoolValue()
    source.setValue(True)
    encoder = BinaryCodec.createEncoder(self.buffer)
    source.encode(encoder)
    self.buffer.seek(0)
    decoder = BinaryCodec.createDecoder(self.buffer)
    result = decoder.decode(BoolValue)
    self.assertIsInstance(result, BoolValue)
    self.assertTrue(result.isValue())
    self.assertTrue(result.hasValue())
    
  def testEncodeDecodeStructType(self):
    encoder = BinaryCodec.createEncoder(self.buffer)
    descriptors.StructType.DESCRIPTOR.encode(encoder)
#     buffer.write('\n'.encode())
    self.buffer.seek(0)
#     print("Binary buffer length:", len(self.buffer.getvalue()))
    decoder = BinaryCodec.createDecoder(self.buffer)
    st = decoder.decode(descriptors.StructType)
    self.assertIsInstance(st, descriptors.StructType)
    self.assertEqual(st.getFullName(), descriptors.StructType.DESCRIPTOR.getFullName())
