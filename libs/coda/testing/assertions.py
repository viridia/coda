import coda.types
import coda.runtime

class Assertions:
  'Mixin class for unit tests that provides friendly assertions for comparing CODA objects.'

  SCALARS = frozenset([
      coda.types.TypeKind.BOOL,
      coda.types.TypeKind.INTEGER,
      coda.types.TypeKind.FLOAT,
      coda.types.TypeKind.DOUBLE,
      coda.types.TypeKind.STRING,
      coda.types.TypeKind.BYTES,
      coda.types.TypeKind.ENUM,
  ])

  def assertCodaObjectsEqual(self, expected, actual, excludeTypes=(), excludedFields=set()):
    '''@type expected: coda.runtime.Object
       @type actual: coda.runtime.Object
       Compares two CODA objects for equality, and fails if they are different, with a failure
       message that describes the differences between the two objects.'''

    # Track the set of objects already checked for equality so we don't get into a loop.
    checked = set()

    def describeType(cls):
      if cls.__module__ == 'builtins':
        return cls.__qualname__
      else:
        return cls.__module__ + '.' + cls.__qualname__

    # TODO: Refactor this into an assertion helper class.
    # TODO: Create a method that prints a short summary of a value.
    def assertObjectsEqual(expected, actual, prefix=''):
      if isinstance(expected, excludeTypes) or isinstance(actual, excludeTypes):
        return
      if expected is None and actual is not None:
        self.fail("Expected '{0}' to not be None.".format(prefix))
      if expected is not None and actual is None:
        self.fail("Expected '{0}' to be None.".format(prefix))
      if expected.typeId() != actual.typeId():
        self.fail("Expected '{0}' to be type {1}, was {2}.".format(
            prefix,
            expected.descriptor().getFullName(),
            actual.descriptor().getFullName()))
      descriptor = expected.descriptor()  # @type method: coda.descriptors.StructDescriptor
      while descriptor:
        for field in descriptor.getFields():
          if field.getName() in excludedFields:
            continue
          fieldName = prefix + '.' + field.getName() if prefix else field.getName()
          if field.isPresent(expected) != field.isPresent(actual):
            if field.isPresent(expected):
              self.fail("Expected '{0}' to be present, but was absent.".format(fieldName))
            else:
              actualValue = field.getValue(actual)
              self.fail("Expected '{0}' to be absent, but was present (value is type '{1}')."
                  .format(fieldName, describeType(type(actualValue))))
          elif field.isPresent(expected):
            assertValuesEqual(
                field.getType(),
                field.getValue(expected),
                field.getValue(actual),
                fieldName)
        descriptor = descriptor.getBaseType()

    def assertValuesEqual(codaType, expected, actual, fieldName):
      fieldKind = codaType.typeId()
      if fieldKind == coda.types.TypeKind.MODIFIED:
        fieldKind = codaType.getElementType().typeId()
      if fieldKind in Assertions.SCALARS:
        if expected != actual:
          self.fail("Expected '{0}' to be '{1}', was '{2}'.".format(
              fieldName, expected, actual))
      elif fieldKind == coda.types.TypeKind.LIST:
        if len(expected) != len(actual):
          self.fail("Expected '{0}' to be length {1}, was {2}.".format(
              fieldName, len(expected), len(actual)))
        else:
          for i in range(0, len(expected)):
            assertValuesEqual(
                codaType.getElementType(),
                expected[i],
                actual[i],
                '{0}[{1}]'.format(fieldName, i))
      elif fieldKind == coda.types.TypeKind.SET:
        if len(expected) != len(actual):
          self.fail("Expected '{0}' to be length {1}, was {2}.".format(
              fieldName, len(expected), len(actual)))
        else:
          for value in expected.difference(actual):
            assert False, 'Implement ' + value
          for value in actual.difference(expected):
            assert False, 'Implement ' + value
      elif fieldKind == coda.types.TypeKind.MAP:
        if len(expected) != len(actual):
          self.fail("Expected {0} to be length {1}, was {2}.".format(
              fieldName, len(expected), len(actual)))
        else:
          assert False, 'Implement'
      elif fieldKind == coda.types.TypeKind.STRUCT:
        if not isinstance(actual, coda.runtime.Object):
          self.fail("Expected value of '{0}' to be an object, was {1}.".format(
              fieldName, describeType(type(actual))))
        elif id(actual) not in checked:
          checked.add(id(actual))
          assertObjectsEqual(expected, actual, fieldName)

    assertObjectsEqual(expected, actual)
