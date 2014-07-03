'''Unit tests for CODA object class'''
from coda import descriptors
from coda import types
import unittest

# from unittest.mock import Mock

class DescriptorsTest(unittest.TestCase):
  def testFileOptions(self):
    options = descriptors.FileOptions()
    packageField = options.descriptor().getField('package')
    self.assertEquals(types.TypeKind.MAP, packageField.getType().typeId())

    file = options.descriptor().getFile()
    self.assertEqual('descriptors.coda', file.getName())
    self.assertEqual('coda.descriptors', file.getPackage())

  def testStructOptions(self):
    desc = types.BooleanType.DESCRIPTOR
    options = desc.getOptions()
    mixin = options.getMixin()
    self.assertEquals(
        'coda.runtime.typemixins.BooleanTypeMixin',
        mixin.get('python.python3'))

  def testFieldOptions(self):
    desc = types.StructType.DESCRIPTOR
    field = desc.getField('baseType')
    fieldOpts = field.getOptions()
    self.assertTrue(fieldOpts.isNullable())

  def testTypeIds(self):
    self.assertEqual(types.TypeKind.BOOL, types.BooleanType.defaultInstance().typeId())
    self.assertEqual(types.TypeKind.INTEGER, types.IntegerType.defaultInstance().typeId())
    self.assertEqual(types.TypeKind.STRING, types.StringType.defaultInstance().typeId())
