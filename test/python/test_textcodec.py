'''Unit tests for CODA text serialization'''
import io
import unittest
from coda import descriptors
from coda.io.textcodec import TextCodec
from coda.runtime.descdata import BoolValue
import finddata

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
    
  def testDecodeSample(self):
    sample = finddata.sample
    
    stream = finddata.sampleTxt.open()
    decoder = TextCodec.createDecoder(stream)
    result = decoder.decode(sample.S2)

    # S2 object
    self.assertIsInstance(result, sample.S2)
    self.assertTrue(result.hasLeft())
    self.assertIsInstance(result.getLeft(), sample.S1)
    s1 = result.getLeft()

    # scalarBoolean
    self.assertTrue(s1.hasScalarBoolean())
    self.assertTrue(s1.isScalarBoolean())
    
    # scalarI16
    self.assertTrue(s1.hasScalarI16())
    self.assertEqual(11, s1.getScalarI16())
    
    # scalarI32
    self.assertTrue(s1.hasScalarI32())
    self.assertEqual(12, s1.getScalarI32())
    
    # scalarI64
    self.assertTrue(s1.hasScalarI64())
    self.assertEqual(13, s1.getScalarI64())
    
    # scalarFixedI16
    self.assertTrue(s1.hasScalarFixedI16())
    self.assertEqual(14, s1.getScalarFixedI16())
    
    # scalarFixedI32
    self.assertTrue(s1.hasScalarFixedI32())
    self.assertEqual(15, s1.getScalarFixedI32())
    
    # scalarFixedI64
    self.assertTrue(s1.hasScalarFixedI64())
    self.assertEqual(16, s1.getScalarFixedI64())
    
    # scalarFloat
    self.assertTrue(s1.hasScalarFloat())
    self.assertEqual(55.0, s1.getScalarFloat())
    
    # scalarDouble
    self.assertTrue(s1.hasScalarDouble())
    self.assertEqual(56.0, s1.getScalarDouble())
    
    # scalarString
    self.assertTrue(s1.hasScalarString())
    self.assertEqual("alpha\n\t", s1.getScalarString())
    
    # scalarBytes
    self.assertTrue(s1.hasScalarBytes())
    self.assertEqual(b"beta", s1.getScalarBytes())
    
    # scalarEnum
    self.assertTrue(s1.hasScalarEnum())
    self.assertEqual(sample.E.E1, s1.getScalarEnum())
    
    # Lists
    self.assertListEqual([True, False, True], s1.getListBoolean())
    self.assertListEqual([100, 101, 102], s1.getListInt())
    self.assertListEqual([110.0, 110.1, 110.2], s1.getListFloat())
    self.assertListEqual(['beta', 'delta\0', 'yin-yan: ☯'], s1.getListString())
    self.assertListEqual([sample.E.E1, sample.E.E2, sample.E.E1], s1.getListEnum())

    # Sets
    self.assertSetEqual({200, 201, 202}, s1.getSetInt())
    self.assertSetEqual({'gamma', '\'single-quoted\'', '\"double-quoted\"'}, s1.getSetString())
    self.assertSetEqual({sample.E.E1, sample.E.E2}, s1.getSetEnum())
    
    # Maps
    self.assertEqual(2, len(s1.getMapIntString()))
    self.assertEqual('three_oh_oh', s1.getMapIntString()[300])
    self.assertEqual('three_oh_one', s1.getMapIntString()[301])
    self.assertEqual(2, len(s1.getMapStringInt()))
    self.assertEqual(300, s1.getMapStringInt()['three_oh_oh'])
    self.assertEqual(301, s1.getMapStringInt()['three_oh_one'])
    self.assertEqual(2, len(s1.getMapEnumStruct()))
    self.assertIsInstance(s1.getMapEnumStruct()[sample.E.E1], sample.S1)
    self.assertIsInstance(s1.getMapEnumStruct()[sample.E.E2], sample.S2)
    
    # Unused
    self.assertFalse(s1.hasUnused())

    # S3 object
#   s2 = sample.S2()
#   s2.setLeft(s1)
#   
#   s3 = sample.S3()
# #   s3.getMutableSList().append(sample.S1())
# #   s3.getMutableSList().append(sample.S2())
#   s2.setRight(s3)
