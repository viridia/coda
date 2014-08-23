'''Registry for extensions and subclasses.'''

class TypeRegistry:
  def __init__(self):
    self.__subtypes = {}
    self.__extensions = {}

  def addSubtype(self, subtype):
    '''Register a type as being a subtype of a given base type.'''
    assert subtype.getTypeId() is not None, subtype.getName()
    base = subtype.getBaseType()
    assert base is not None
    while base.getBaseType():
      base = base.getBaseType()
    try:
      subtypesForBase = self.__subtypes[id(base)]
    except KeyError:
      subtypesForBase = self.__subtypes[id(base)] = {}
    if subtype.getTypeId() in subtypesForBase:
      raise AssertionError(
          "Error registering type {0}: subtype ID {1} already registered".\
              formatter(subtype.getFullName(), subtype.getTypeId()))
    subtypesForBase[subtype.getTypeId()] = subtype
    return self

  def getSubtype(self, base, typeId):
    '''Retrieve a subtype of a base type by subtype ID.'''
    subtypesForBase = self.__subtypes.get(id(base))
    if subtypesForBase:
      return subtypesForBase.get(typeId)
    return None

  def getSubtypes(self, base):
    '''Retrieve all subtype of a base type.'''
    return self.__subtypes.get(id(base), {})

  def addFile(self, file):
    '''Add all subtypes and extensions registered within a file.'''
    def addStruct(struct):
      if struct.getBaseType() is not None:
        self.addSubtype(struct)
      for st in struct.getStructs():
        addStruct(st)
    for struct in file.getStructs():
      addStruct(struct)

  def getExtension(self, struct, fieldId):
    return self.__extensions.get(id(struct), {}).get(fieldId)

  def addExtension(self, extField):
    try:
      extensionsForStruct = self.__extensions[id(extField.getExtends())]
    except KeyError:
      extensionsForStruct = self.__subtypes[id(extField.getExtends())] = {}
    assert extField.getId() not in extensionsForStruct, \
        'Duplicate extension id for struct ' + extField.getExtends().getName()
    extensionsForStruct[extField.getId()] = extField

  INSTANCE = None

TypeRegistry.INSTANCE = TypeRegistry()
