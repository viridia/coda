from abc import abstractmethod

class TypeMixin:
  '''Mixin class for all type.'''
  @abstractmethod
  def kind(self):
    'Return the kind of this type'
    return self.typeId()

  @abstractmethod
  def coerce(self, value):
    '''Coerce the input value into this type. Raises TypeError if the conversion
       is impossible.'''
    return super().coerce(value)

  @abstractmethod
  def key(self):
    'Return a unique key for this type'
    return super().key()

class BooleanTypeMixin:
  '''Mixin methods for boolean type.'''

  def getName(self):
    return 'bool'

  def key(self):
    return (self.typeId(),)

  def isAssignable(self, value):
    return value is True or value is False

class IntegerTypeMixin:
  '''Mixin methods for integer type.'''

  def getName(self):
    return 'i' + str(self.getBits())

  def key(self):
    return (self.typeId(), self.getBits())

  def isAssignable(self, value):
    return isinstance(value, (int, float))

class FloatTypeMixin:
  '''Mixin methods for float type.'''

  def getName(self):
    return 'float'

  def key(self):
    return (self.typeId(),)

  def isAssignable(self, value):
    return isinstance(value, (int, float))

class DoubleTypeMixin:
  '''Mixin methods for float type.'''

  def getName(self):
    return 'double'

  def key(self):
    return (self.typeId(),)

  def isAssignable(self, value):
    return isinstance(value, (int, float))

class StringTypeMixin:
  '''Mixin methods for string type.'''

  def getName(self):
    return 'string'

  def key(self):
    return (self.typeId(),)

  def isAssignable(self, value):
    return isinstance(value, str)

class BytesTypeMixin:
  '''Mixin methods for bytes type.'''

  def getName(self):
    return 'bytes'

  def key(self):
    return (self.typeId(),)

  def isAssignable(self, value):
    return isinstance(value, str) or isinstance(value, bytes)

class ListTypeMixin:
  '''Mixin methods for list types.'''

  def getName(self):
    return 'list[' + self.getElementType().getName() + ']'

  def __repr__(self):
    return 'list[' + repr(self.getElementType()) + ']'

  def isAssignable(self, value):
    return isinstance(value, (list, tuple))

  def key(self):
    assert self.getElementType()
    return (self.typeId(), self.getElementType().key())

class SetTypeMixin:
  '''Mixin methods for set types.'''

  def getName(self):
    return 'set[' + self.getElementType().getName() + ']'

  def isAssignable(self, value):
    return isinstance(value, (list, tuple, set, frozenset))

  def key(self):
    return (self.typeId(), self.getElementType().key())

class MapTypeMixin:
  '''Mixin methods for map types.'''

  def getName(self):
    return 'map[' + self.getKeyType().getName() + ', ' +\
        self.getValueType().getName() + ']'

  def key(self):
    return (self.typeId(), self.getKeyType().key(), self.getValueType().key())

  def isAssignable(self, value):
    return isinstance(value, dict)

class ModifiedTypeMixin:
  '''Mixin methods for modified types.'''

  def getName(self):
    s = self.getElementType().getName()
    if self.isShared():
      s = 'shared ' + s
    if self.isConst():
      s = 'const ' + s
    return s

  def key(self):
    return (self.typeId(), self.getElementType().key(), self.isShared(), self.isConst())

  def isAssignable(self, value):
    return self.getElementType().isAssignable(value)

class DeclTypeMixin:
  '''Mixin methods for declared types.'''

  def getFullName(self):
    'Returns the fully-qualified name of this declaration.'
    if self._enclosingType:
      return self._enclosingType.getFullName() + '.' + self._name
    else:
      return self._file.getPackage() + '.' + self._name

  def key(self):
    return (self.typeId(), self.getFullName())

  def __str__(self):
    return self.getFullName()
