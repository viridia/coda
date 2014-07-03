'''Descriptor classes'''

from collections import OrderedDict

from coda.runtime.descdata import TypeKind, StructType, EnumType
from coda.runtime.descdata import FileOptions, StructOptions, EnumOptions, FieldOptions, MethodOptions #@UnusedImport
from coda.runtime.descdata import FileDescriptor, ExtensionField #@UnusedImport

# ============================================================================
# Declared Types
# ============================================================================

class StructDescriptor(StructType):
  class Field(StructType.Field):
    def isPresent(self, obj):
      return obj._isPresent(self.getName())

    def getValue(self, obj):
      return getattr(obj, '_' + self.getName())

    def getMutableValue(self, obj):
      obj.checkMutable()
      value = self.getValue(obj)
      kind = self.getType().typeId()
      if kind == TypeKind.LIST:
        if type(list) is tuple:
          value = list(value)
          self.setValue(obj, value)
      elif kind == TypeKind.SET:
        if type(list) is frozenset:
          value = set(value)
          self.setValue(obj, value)
      elif kind == TypeKind.MAP:
        if type(list) is not dict:
          value = dict(value)
          self.setValue(obj, value)
      return value

    def setValue(self, obj, value):
      obj._setPresent(self.getName())
      setattr(obj, '_' + self.getName(), value)

  '''Descriptor for a CODA structure type definition.'''
  def __init__(self, cls):
    super().__init__()
    self._membersByName = {}
    self._fieldsById = OrderedDict()
    self._methods = []
    self._class = cls

  def getFields(self):
    'Returns the list of field definitions for this struct, in order by ID'
    return self._fieldsById.values()

  def getAllFields(self):
    '''Returns the list of field definitions for this struct, including fields
       defined in base classes.'''
    if self.getBaseType():
      return tuple(self.getBaseType().getAllFields()) + tuple(self.getFields())
    else:
      return self.getFields()

  def getMethods(self):
    'Returns the list of method definitions for this struct, in order by ID'
    return self._methods

  def findField(self, fieldName):
    '''Look up a field definition by name, searching base types if needed.
       Returns null if no such field exists.'''
    structType = self
    while structType is not None:
      assert isinstance(structType, StructDescriptor)
      field = structType.getField(fieldName)
      if field:
        return field
      structType = structType.getBaseType()
    return None

  def getField(self, fieldName):
    '''Look up a field definition by name. Does not search base types.
       Returns null if no such field exists.'''
    return self._membersByName.get(fieldName)

  def getFieldById(self, index):
    '''Look up a field definition by numeric index. Does not search base types.
       Returns null if no such field exists.'''
    return self._fieldsById.get(index)

  def defineField(self, name, fid, ty, options=None):
    '''Define a new field, and return it.'''
    if not ty:
      return
    assert ty.typeId() is not None
    assert name not in self._membersByName
    assert id not in self._fieldsById
    self.checkMutable()
    field = StructDescriptor.Field()
    field.setName(name).setType(ty).setId(fid)
    if options:
      field.setOptions(options)
    self.getMutableFields().append(field)
    self._membersByName[name] = field
    self._fieldsById[fid] = field
    return field

  def defineMethod(self, name, fid, paramTypes, returnTy, options=None):
    '''Define a new field, and return it.'''
    assert returnTy.typeId() is not None
    assert name not in self._membersByName
    self.checkMutable()
    method = StructDescriptor.Method()
    method.setName(name).setReturnType(returnTy).setParams(paramTypes).setId(fid)
    if options:
      method.setOptions(options)
    self._membersByName[name] = method
    self._methods.append(method)
    return method

  def isSubtypeOf(self, superType):
    ty = self
    while True:
      if ty is superType:
        return True
      elif ty.hasBaseType():
        ty = ty.getBaseType()
      else:
        return False

  def getClass(self):
    return self._class

  def new(self):
    return self._class()

  def isAssignable(self, value):
    return isinstance(value, self._class)

  @staticmethod
  def forClass(cls, file):
    sd = StructDescriptor(cls)
    sd.setName(cls.__name__)
    sd.setFile(file)
    if hasattr(cls.__bases__[0], 'DESCRIPTOR'):
      assert isinstance(cls.__bases__[0].DESCRIPTOR, StructDescriptor)
      sd.setBaseType(cls.__bases__[0].DESCRIPTOR)
    return sd

# =============================================================================
# EnumType
# =============================================================================

class EnumDescriptor(EnumType):
  def __init__(self):
    super().__init__()
    self._valuesByName = OrderedDict()

  def getValue(self, name):
    '''Look up a value by name. Returns null if no such value exists.'''
    return self._valuesByName.get(name)

  def addValue(self, value):
    self.getMutableValues().append(value)
    self._valuesByName[value.getName()] = value

  def isAssignable(self, value):
    return isinstance(value, int)

  @staticmethod
  def forClass(cls, file):
    ed = EnumDescriptor()
    ed.setName(cls.__name__)
    ed.setFile(file)
    for name in cls.__values__:
      value = EnumType.Value()
      value.setName(name)
      value.setValue(getattr(cls, name))
      ed.addValue(value)
    return ed

# ============================================================================
# Initialization
# ============================================================================

import coda.runtime
coda.runtime.initModule(StructDescriptor, EnumDescriptor, coda.runtime.descdata)
