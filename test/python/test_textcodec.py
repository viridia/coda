'''Unit tests for CODA text serialization'''
import io
import unittest
from coda import descriptors
from coda.io.textcodec import TextCodec

class TextCodecTest(unittest.TestCase):
  def testEncodeDecode(self):
    buffer = io.StringIO()
    encoder = TextCodec.createEncoder(buffer)
    descriptors.StructType.DESCRIPTOR.write(encoder)
#     buffer.write('\n')
    buffer.seek(0)
    print("Text buffer:", buffer.getvalue())
    decoder = TextCodec.createDecoder(buffer)
    st = decoder.read(descriptors.StructType)
    self.assertIsInstance(st, descriptors.StructType)
    self.assertEqual(st.getFullName(), descriptors.StructType.DESCRIPTOR.getFullName())
