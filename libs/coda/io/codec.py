'''Base classes for CODA codecs.'''

from abc import ABCMeta, abstractmethod

class EncodingError(Exception):
  '''Base class for exceptions encountered during encoding or decoding.'''
  def __init__(self, msg):
    self.__msg = msg

  def msg(self):
    return self.__msg

class Encoder(metaclass=ABCMeta):
  '''Interface class for encoders.'''

  @abstractmethod
  def addExtern(self, obj, index=None):
    raise NotImplementedError()
    return self

  @abstractmethod
  def fileBegin(self):
    raise NotImplementedError()
    return self

  @abstractmethod
  def fileEnd(self):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeSubtypeHeader(self, name, sid):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeFieldHeader(self, name, fid):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeBoolean(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeInteger(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeFixed16(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeFixed32(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeFixed64(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeFloat(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeDouble(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeString(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeBytes(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeBeginList(self, elementKind, length, fixed=False):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeEndList(self):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeBeginSet(self, elementKind, length, fixed=False):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeEndSet(self):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeBeginMap(self, keyKind, valueKind, length):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeEndMap(self):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeStruct(self, value):
    raise NotImplementedError()
    return self

  @abstractmethod
  def writeSharedStruct(self, value):
    raise NotImplementedError()
    return self

class Decoder(metaclass=ABCMeta):
  @abstractmethod
  def decode(self, cls):
    raise NotImplementedError()
    pass

class AbstractEncoder(Encoder):
  '''Abstract base class for encoders.'''
  def __init__(self):
    self.__nextSharedId = 1
    self.__nextExternId = -1
    self.__objectRefs = {}
    self.__idsInUse = set()

  def getNextSharedId(self):
    '''Return the next unused shared object identifier.'''
    value = self.__nextSharedId
    assert value not in self.__idsInUse
    self.__nextSharedId += 1
    return value

  def getNextExternId(self):
    '''Return the next unused shared object identifier.'''
    while self.__nextSharedId in self.__idsInUse:
      self.__nextSharedId += 1
    value = self.__nextSharedId
    self.__nextSharedId += 1
    return value

  def addExtern(self, obj, index=None):
    '''Add an object to the externs table.'''
    if index is None:
      index = self.getNextExternId()
    elif index in self.__idsInUse:
      raise EncodingError('Extern index {0} is already in use', index)
    self.__idsInUse.add(index)
    self.__objectRefs[id(obj)] = index

  def addShared(self, obj):
    '''Add an object to the shared object table. If the object has already
       been added, it returns the table index of the existing entry;
       Otherwise, the object is added to the table and None is returned.'''
    sid = id(obj)
    if sid in self.__objectRefs:
      return self.__objectRefs[sid]
    else:
      index = self.getNextSharedId()
      self.__idsInUse.add(index)
      self.__objectRefs[sid] = index
      #print("Object {0}: {1}".format(index, obj.descriptor().getFullName()))
      return None

  def getShared(self, obj):
    '''Return the index of an object in the shared object table, or None if
       the object is not in the table.'''
    return self.__objectRefs.get(id(obj))

class AbstractDecoder(Decoder):
  '''Abstract base class for decoders.'''
  def __init__(self, typeRegistry=None):
    self.__nextSharedId = 1
    self.__nextExternId = -1
    self.__objectRefs = {}
    if typeRegistry:
      self.__typeRegistry = typeRegistry
    else:
      from coda.runtime import typeregistry
      self.__typeRegistry = typeregistry.TypeRegistry.INSTANCE

  def getNextExternId(self):
    '''Return the next unused shared object identifier.'''
    while self.__nextExterndId in self.__objectRefs:
      self.__nextExterndId -= 1
    value = self.__nextExterndId
    self.__nextExterndId -= 1
    return value

  def getNextSharedId(self):
    '''Return the next unused shared object identifier.'''
    value = self.__nextSharedId
    self.__nextSharedId += 1
    return value

  def addExtern(self, obj, index=None):
    '''Add an object to the externs table.'''
    if index is None:
      index = self.getNextExternId()
    elif index in self.__objectRefs:
      raise EncodingError('Extern index {0} is already in use', index)
    self.__objectRefs[id(obj)] = index
    return self

  def addShared(self, obj):
    '''Add an object to the shared object table..'''
    index = self.getNextSharedId()
    self.__objectRefs[index] = obj
    return index

  def getShared(self, index):
    '''Return the shared object with the given id.'''
    return self.__objectRefs[index]

  @staticmethod
  def isSubtype(self, st, base):
    while st:
      if st is base:
        return True
      st = st.getBaseType()
    return False
