'''Unit tests for CODA object class'''
from coda import descriptors
import unittest

class ObjectTest(unittest.TestCase):
  def testEq(self):
    v1 = descriptors.FieldOptions().setDeprecated(True)
    v2 = descriptors.FieldOptions().setDeprecated(True)
    v3 = descriptors.FieldOptions().setDeprecated(False)
    v4 = descriptors.FieldOptions()

    self.assertEqual(v1, v2)
    self.assertNotEqual(v1, v3)
    self.assertNotEqual(v1, v4)

  def testHash(self):
    v1 = descriptors.FieldOptions().setDeprecated(True).freeze()
    v2 = descriptors.FieldOptions().setDeprecated(True).freeze()
    v3 = descriptors.FieldOptions().setDeprecated(False).freeze()
    v4 = descriptors.FieldOptions().freeze()

    self.assertEqual(hash(v1), hash(v2))
    self.assertNotEqual(hash(v1), hash(v3))
    self.assertNotEqual(hash(v1), hash(v4))
