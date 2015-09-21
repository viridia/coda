'''Unit tests for CODA object class'''
import unittest
from coda import types, descriptors

class TextCodecTest(unittest.TestCase):
  def testBooleanType(self):
    ty = types.BooleanType.defaultInstance()
    self.assertTrue(ty.isAssignable(True))
    self.assertTrue(ty.isAssignable(False))
    self.assertFalse(ty.isAssignable(1))
    self.assertFalse(ty.isAssignable([]))

  def testIntegerType(self):
    ty = types.IntegerType.defaultInstance()
    self.assertTrue(ty.isAssignable(1))
    self.assertTrue(ty.isAssignable(1.0))
    self.assertFalse(ty.isAssignable([]))

  def testMapType(self):
    ty = types.MapType()\
        .setKeyType(types.StringType.defaultInstance())\
        .setValueType(types.StringType.defaultInstance())
    self.assertFalse(ty.isAssignable(1))
    self.assertFalse(ty.isAssignable(1.0))
    self.assertFalse(ty.isAssignable([]))
    self.assertTrue(ty.isAssignable({}))

  def testStructType(self):
    self.assertEquals("StructType", descriptors.StructType.DESCRIPTOR.getName())
    newStruct = descriptors.StructType.newInstance()
    self.assertIsInstance(newStruct, descriptors.StructType)
