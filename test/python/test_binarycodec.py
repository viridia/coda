'''Unit tests for CODA binary serialization'''
import io
import unittest
from coda import descriptors
from coda.io.binarycodec import BinaryCodec

class BinaryCodecTest(unittest.TestCase):
  def testEncodeDecode(self):
    buffer = io.BytesIO()
    encoder = BinaryCodec.createEncoder(buffer)
    descriptors.StructType.DESCRIPTOR.write(encoder)
    buffer.write('\n'.encode())
    buffer.seek(0)
#     print("Binary buffer length:", len(buffer.getvalue()))
#     decoder = BinaryCodec.createDecoder(buffer)
#     st = decoder.read(descriptors.StructType)
#     self.assertIsInstance(st, descriptors.StructType)
#     self.assertEqual(st.getFullName(), descriptors.StructType.DESCRIPTOR.getFullName())
