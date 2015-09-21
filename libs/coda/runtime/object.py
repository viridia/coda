'''Base classes for CODA objects.'''

import copy
from .frozendict import FrozenDict

class ObjectMeta(type):
  '''Metaclass that creates (but does not initialize) a default instance
     for each class. The default instance will be initialized later by
     the bootstrap code - this avoids the problem with circular references.'''
  def __init__(self, name, bases, nmspc):
    super().__init__(name, bases, nmspc)
    self.__defaultInstance__ = self.__new__(self)

class Object(metaclass=ObjectMeta):
  __slots__ = ['__mutable', '__present']

  EMPTY_LIST = ()
  EMPTY_SET = frozenset()
  EMPTY_MAP = FrozenDict()
  EMPTY_STRING = ''
  EMPTY_BYTES = bytes()

  '''Base type for serializable objects.'''
  def __init__(self):
    super().__init__()
    self.__mutable = True
    self.__present = set()

  def __str__(self):
    return self._toStr(set())

  def _toStr(self, inProcess):
    if id(self) in inProcess:
      return 'self'
    inProcess.add(id(self))
    fieldValues = []
    for field in self.descriptor().getAllFields():
      if field.isPresent(self) and not field.getOptions().isNovisit():
        value = field.getValue(self)
        if isinstance(value, Object):
          value = value._toStr(inProcess)
        else:
          value = str(value)
        fieldValues.append('{0}: {1}'.format(field.getName(), value))
    inProcess.remove(id(self))
    return self.descriptor().getFullName() + ' {' + '; '.join(fieldValues) + '}'

  def __eq__(self, other):
    return self._equalsImpl(other)

  def __hash__(self):
    return self._hashImpl()

  def merge(self, src):
    '''Merge the fields of 'src' with this object.'''
    self.checkMutable()
    assert type(self) is type(src)

  def _equalsImpl(self, other):
    return type(self) is type(other)

  def _hashImpl(self):
    if self.__mutable:
      raise AssertionError('Only immutable values can be hashed. (type={0})'.format(type(self)))
    return hash(type(self))

  def _freezeImpl(self, deep):
    '''Make this object immutable.'''
    self.__mutable = False

  def _isPresent(self, fieldName):
    return fieldName in self.__present

  def _setPresent(self, fieldName):
    self.__present.add(fieldName)

  def _clearPresent(self, fieldName):
    self.__present.discard(fieldName)

  def _initFieldValues(self, init):
    for fieldName, value in init.items():
      setattr(self, '_' + fieldName, value)
      self._setPresent(fieldName)

  def _beginWrite(self, encoder):
    pass

  def _endWrite(self, encoder):
    pass

  def descriptor(self):
    'Return the descriptor for this instance'
    return self.__class__.DESCRIPTOR

  def typeId(self):
    return self.descriptor().getTypeId()

  @classmethod
  def defaultInstance(cls):
    '''Return the default instance for this object type.'''
    return cls.__defaultInstance__

  @classmethod
  def newInstance(cls, **initArgs):
    desc = cls.DESCRIPTOR
    result = cls()
    for fieldName, value in initArgs.items():
      field = desc.getField(fieldName)
      if not field:
        raise AssertionError('Class {0} has no field {1}'.format(
            desc.getName(), fieldName))
      setattr(result, '_' + fieldName, value)
      result._setPresent(fieldName)
    return result

  def freeze(self, deep=True):
    '''Make this object immutable.'''
    if self.__mutable:
      self.__mutable = False
      self._freezeImpl(deep)
    return self

  def isMutable(self):
    'Return true if this object is mutable.'
    return self.__mutable

  def checkMutable(self):
    'Asserts that this object is mutable.'
    assert self.__mutable

  def shallowCopy(self):
    '''Return a mutable, shallow copy of this object.'''
    result = copy.copy(self)
    result.__mutable = True
    result.__present = set(self.__present)
    return result

  def encode(self, encoder):
    encoder.fileBegin()
    self._writeFields(encoder)
    encoder.fileEnd()

  def writeFields(self, encoder):
    self._writeFields(encoder)

  def _writeFields(self, encoder):
    pass

  def readFrom(self, streamCodec):
    '''Read the fields of this object from a stream.'''
    pass

class ExtensibleObject(Object):
  '''Base type for serializable objects that have extensions.'''
  __slots__ = ['__extensions']
  def __init__(self):
    super().__init__()
    self._extensions = {}

  def getExtension(self, extensionId):
    'Return an extension associated with the given id.'
    return self._extensions.get(extensionId)

  def setExtension(self, extensionId, extensionField):
    self._extensions.set(extensionId, extensionField)
    return self
