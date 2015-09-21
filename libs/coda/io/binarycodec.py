import struct
import coda.io
import coda.runtime
from coda.io.codec import EncodingError
from coda import types

# =============================================================================
# Encoding for Data types
# =============================================================================

class DataType:
  END = 0       # End of a struct
  ZERO = 1      # Constant integer 0
  ONE = 2       # Constant integer 1
  VARINT = 3    # Variable-length integer
  FIXED16 = 4   # 16-bit fixed-width integer
  FIXED32 = 5   # 32-bit fixed-width integer
  FIXED64 = 6   # 64-bit fixed-width integer
  FLOAT = 7     # 32-bit float
  DOUBLE = 8    # 64-bit float
  BYTES = 9     # String or Bytes type (followed by length)
  LIST = 10     # List of items (followed by length)
  PLIST = 11    # List of fixed-width items (followed by format and length)
  MAP = 12      # Map of items (followed by length)
  STRUCT = 13   # Beginning of a struct
  SUBTYPE = 14  # Beginning of subtype data, field ID is actually subtype ID

  # Extended types - low bits must be 0
  SHARED_REF = 0x10   # Reference to a shared object (followed by object id). Used in maps/lists.

  MAXVAL = SUBTYPE

class DataFormat:
  BYTE = struct.Struct('!B')
  FIXED16 = struct.Struct('!H')
  FIXED32 = struct.Struct('!I')
  FIXED64 = struct.Struct('!Q')
  FLOAT = struct.Struct('!f')
  DOUBLE = struct.Struct('!d')

DTYPE_NAMES = {
  DataType.END: 'end',
  DataType.ZERO: 'zero',
  DataType.ONE: 'one',
  DataType.VARINT: 'int',
  DataType.FIXED16: 'int16',
  DataType.FIXED32: 'int32',
  DataType.FIXED64: 'int64',
  DataType.FLOAT: 'float',
  DataType.DOUBLE: 'double',
  DataType.BYTES: 'bytes',
  DataType.LIST: 'list',
  DataType.PLIST: 'plist',
  DataType.MAP: 'map',
  DataType.STRUCT: 'struct',
  DataType.SUBTYPE: 'subtype',
}

# =============================================================================
# BinaryEncoder
# =============================================================================

class BinaryEncoder(coda.io.AbstractEncoder):
  KIND_TO_DTYPE = {
      types.TypeKind.BOOL: DataType.ONE,
      types.TypeKind.INTEGER: DataType.VARINT,
      types.TypeKind.FLOAT: DataType.FLOAT,
      types.TypeKind.DOUBLE: DataType.DOUBLE,
      types.TypeKind.STRING: DataType.BYTES,
      types.TypeKind.BYTES: DataType.BYTES,
      types.TypeKind.LIST: DataType.LIST,
      types.TypeKind.SET: DataType.LIST,
      types.TypeKind.MAP: DataType.MAP,
      types.TypeKind.STRUCT: DataType.STRUCT,
  }

  class State:
    CLEAR = 0
    STRUCT = 1
    CONTAINER = 2
    MAP_KEY = 3
    MAP_VALUE = 4
    SUBTYPE = 5

  def __init__(self, stream):
    super().__init__()
    self.__stream = stream
    self.__subtypeId = None
    self.__fieldId = None
    self.__lastFieldId = 0
    self.__state = self.State.CLEAR
    self.__fieldHeader = False
    self.__inProgress = set()

  def fileBegin(self):
    self.__state = self.State.STRUCT

  def fileEnd(self):
    pass

  def writeSubtypeHeader(self, name, sid):
    assert self.__state in (self.State.STRUCT, self.State.SUBTYPE, self.State.CLEAR)
    self.__subtypeId = sid
    if self.__state == self.State.STRUCT:
      self.__beginSubtype()
    return self

  def writeFieldHeader(self, name, fid):
    assert self.__fieldId is None
    assert self.__state in (self.State.CLEAR, self.State.STRUCT, self.State.SUBTYPE), self.__state
    self.__fieldId = fid
    if self.__state == self.State.CLEAR:
      self.__state = self.State.STRUCT

  def writeBoolean(self, value):
    if self.__fieldId is not None:
      self.__beginValue(DataType.ONE if value else DataType.ZERO)
    else:
      if value:
        self.__writeUByte(1)
      else:
        self.__writeUByte(0)
    return self

  def writeInteger(self, value):
    self.__beginValue(DataType.VARINT)
    self.__writeVarInt(self.zigZagEncode(value))
    return self

  def writeFixed16(self, value):
    self.__beginValue(DataType.FIXED16)
    self.__stream.write(DataFormat.FIXED16.pack(value))
    return self

  def writeFixed32(self, value):
    self.__beginValue(DataType.FIXED32)
    self.__stream.write(DataFormat.FIXED32.pack(value))
    return self

  def writeFixed64(self, value):
    self.__beginValue(DataType.FIXED64)
    self.__stream.write(DataFormat.FIXED64.pack(value))
    return self

  def writeFloat(self, value):
    self.__beginValue(DataType.FLOAT)
    self.__stream.write(DataFormat.FLOAT.pack(value))
    return self

  def writeDouble(self, value):
    self.__beginValue(DataType.DOUBLE)
    self.__stream.write(DataFormat.DOUBLE.pack(value))
    return self

  def writeString(self, value):
    self.__beginValue(DataType.BYTES)
    self.__writeVarInt(len(value))
    self.__stream.write(value.encode())
    return self

  def writeBytes(self, value):
    self.__beginValue(DataType.BYTES)
    self.__writeVarInt(len(value))
    self.__stream.write(value)
    return self

  def writeBeginList(self, elementKind, length, fixed=False):
    if fixed:
      self.__beginValue(DataType.PLIST)
    else:
      self.__beginValue(DataType.LIST)
    self.__writeUByte(self.KIND_TO_DTYPE[elementKind])
    self.__writeVarInt(length)
    return self

  def writeEndList(self):
    return self

  writeBeginSet = writeBeginList
  writeEndSet = writeEndList

  def writeBeginMap(self, keyKind, valueKind, length):
    self.__beginValue(DataType.MAP)
    self.__writeUByte(
        (self.KIND_TO_DTYPE[keyKind] << 4) | self.KIND_TO_DTYPE[valueKind])
    self.__writeVarInt(length)
    return self

  writeEndMap = writeEndList

  def writeSharedStruct(self, value):
    if value is None:
      self.writeStruct(value)
    else:
      index = self.addShared(value)
      if index is not None:
        # OK so the problem here is when we're writing a list or a map, we have no
        # field ID. Now, normally we would expect a field ID of the struct.
        if self.__fieldId is None:
          self.__writeUByte(DataType.SHARED_REF)
        self.writeInteger(index)
      else:
        self.writeStruct(value)

  def writeStruct(self, value):
    if value is None:
      self.__beginValue(DataType.ZERO)
    else:
      assert isinstance(value, coda.runtime.Object), type(value)
      sid = id(value)
      if sid in self.__inProgress:
        raise EncodingError('Already serializing object of type ' +
            value.descriptor().getFullName())
      self.__inProgress.add(sid)
      savedState = self.__state
      self.__beginValue(DataType.STRUCT)
      savedFieldId = self.__lastFieldId
      self.__lastFieldId = 0
      self.__state = self.State.STRUCT
      value.writeFields(self)
      self.__writeUByte(DataType.END)
      self.__subtypeId = None
      self.__state = savedState
      self.__lastFieldId = savedFieldId
      self.__inProgress.remove(sid)
    return self

  def __beginSubtype(self):
    if self.__subtypeId > 0 and self.__subtypeId <= 15:
      self.__writeUByte((self.__subtypeId << 4) | DataType.SUBTYPE)
    else:
      self.__writeUByte(DataType.SUBTYPE)
      self.__writeVarInt(self.__subtypeId)
    self.__lastFieldId = 0
    self.__subtypeId = None
    self.__state = self.State.SUBTYPE

  def __beginValue(self, dataType):
    if self.__subtypeId is not None:
      self.__beginSubtype()
    if self.__fieldId is not None:
      assert self.__state in (self.State.CLEAR, self.State.STRUCT, self.State.SUBTYPE)
      assert dataType is not DataType.END
      delta = self.__fieldId - self.__lastFieldId
      if delta <= 0:
        print(self.__lastFieldId, self.__fieldId)
        raise EncodingError('Fields should be serialized in monotonically increasing order')
      if delta <= 15:
        self.__writeUByte((delta << 4) | dataType)
      else:
        self.__writeUByte(dataType)
        self.__writeVarInt(self.__fieldId)
      self.__lastFieldId = self.__fieldId
      self.__fieldId = None
    elif self.__state == self.State.MAP_KEY:
      self.__state = self.State.MAP_VALUE
    elif self.__state == self.State.MAP_VALUE:
      self.__state = self.State.MAP_KEY

  def __writeUByte(self, byte):
    self.__stream.write(bytes((byte,)))

  def __writeVarInt(self, i):
    assert i >= 0
    b = bytearray()
    while i > 0x7f:
      b.append((i & 0xff) | 0x80)
      i = i >> 7
    b.append(i)
    self.__stream.write(b)
    return self

  @staticmethod
  def zigZagEncode(value):
    # Note this version of ZZ works with Python bignums
    if value >= 0:
      return int(value) * 2
    else:
      return -1 - int(value) * 2

# =============================================================================
# BinaryDecoder
# =============================================================================

class BinaryDecoder(coda.io.AbstractDecoder):
  def __init__(self, stream, sourcePath, typeRegistry):
    super().__init__()
    if not typeRegistry:
      from coda.runtime.typeregistry import TypeRegistry
      typeRegistry = TypeRegistry.INSTANCE
    self.__stream = stream
    self.__states = []
    self.__sourcePath = sourcePath
    self.__typeRegistry = typeRegistry
    self.__descriptor = None
    self.__instance = None
    self.__fieldId = 0
    self.__subtypeId = 0
    self.__atEof = False
    self.__indentLevel = 0
    self.__readPos = self.__pos()
    self.__lastReadPos = self.__readPos
    self.__debug = False
    self.__debugPos = self.__readPos

  def setDebug(self, value):
    self.__debug = value

  def atEof(self):
    return self.__atEof

  def decode(self, cls):
    if self.__atEof is None:
      return None
    assert cls.DESCRIPTOR, 'Missing descriptor for class ' + cls.__name__
    return self.__readStructFields(cls.DESCRIPTOR, first=True)

  def __readValue(self, expectedType, actualType):
    expectedKind = expectedType.typeId()
    if expectedKind == types.TypeKind.MODIFIED:
      expectedKind = expectedType.getElementType().typeId()

    if actualType == DataType.STRUCT:
      if expectedKind != types.TypeKind.STRUCT:
        self.fatal(self.__lastReadPos,
            'Type error: Expecting {0}, got a list', expectedType.getName())
      return self.__readStructValue(expectedType)
    elif actualType == DataType.LIST:
      return self.__readListValue(expectedType, actualType)
    elif actualType == DataType.PLIST:
      # It's a packed list
      if expectedKind != types.TypeKind.LIST and\
         expectedKind != types.TypeKind.SET:
        self.fatal(self.__lastReadPos,
            'Type error: Expecting {0}, got a list', expectedType.getName())
      assert False, 'Packed list not implemented'
    elif actualType == DataType.MAP:
      return self.__readMapValue(expectedType)
    elif actualType in (DataType.ZERO, DataType.ONE, DataType.VARINT,
        DataType.FIXED16, DataType.FIXED32, DataType.FIXED64):
      if actualType == DataType.ZERO:
        value = 0
      elif actualType == DataType.ONE:
        value = 1
      elif actualType == DataType.VARINT:
        value = self.__readVarInt()
        value = self.zigZagDecode(value)
      elif actualType == DataType.FIXED16:
        value = DataFormat.FIXED16.unpack(self.__readBytes(2))
      elif actualType == DataType.FIXED32:
        value = DataFormat.FIXED16.unpack(self.__readBytes(4))
      elif actualType == DataType.FIXED64:
        value = DataFormat.FIXED16.unpack(self.__readBytes(8))
      else:
        assert False

      if expectedKind == types.TypeKind.INTEGER:
        return value
      elif expectedKind == types.TypeKind.BOOL:
        return bool(value)
      elif expectedKind == types.TypeKind.STRUCT:
        if actualType == DataType.ZERO:
          return None
        elif actualType == DataType.VARINT:
          return self.__getShared(value)
        # Fall through
      elif expectedKind == types.TypeKind.ENUM:
        return value
      elif expectedKind in (types.TypeKind.FLOAT, types.TypeKind.DOUBLE):
        return float(value)

      self.fatal(self.__lastReadPos,
          'Type error: Expecting {0}, got an integer', expectedType.getName())
    elif actualType in (DataType.FLOAT, DataType.DOUBLE):
      if actualType == DataType.FLOAT:
        value = DataFormat.FLOAT.unpack(self.__readBytes(4))
      else:
        value = DataFormat.DOUBLE.unpack(self.__readBytes(8))

      if expectedKind in (types.TypeKind.FLOAT, types.TypeKind.DOUBLE):
        return value

      self.fatal(self.__lastReadPos,
          'Type error: Expecting {0}, got a float', expectedType.getName())
    elif actualType == DataType.BYTES:
      length = self.__readVarInt()
      data = self.__readBytes(length)

      if expectedKind == types.TypeKind.STRING:
        return data.decode()
      elif expectedKind == types.TypeKind.BYTES:
        return data

      self.fatal(self.__lastReadPos,
          'Type error: Expecting {0}, got bytes', expectedType.getName())
    else:
      assert False, 'Invalid data type'

  def __readStructValue(self, expectedType):
    shared = False
    originalType = expectedType
    if expectedType.typeId() == types.TypeKind.MODIFIED:
      shared = expectedType.isShared()
      expectedType = expectedType.getElementType()
    else:
      shared = self.__isSharedType(expectedType)

    if expectedType.typeId() != types.TypeKind.STRUCT:
      self.fatal(self.__lastReadPos,
          "Type error: expecting a value of type {0}, not a struct",
          expectedType)

    self.__states.append((self.__instance, self.__descriptor, self.__fieldId))

    self.__instance = None
    self.__descriptor = expectedType

    if self.__debug:
      self.__debugf('begin struct: {0}', originalType.getName())
      self.__indentLevel += 1

    st = self.__readStructFields(expectedType, shared=shared)

    if self.__debug:
      self.__indentLevel -= 1
      self.__debugf('end struct: {0}', st.descriptor().getName())

    self.__instance, self.__descriptor, self.__fieldId = self.__states.pop()
    return st

  def __readMapValue(self, expectedType):
    if expectedType.typeId() != types.TypeKind.MAP:
      self.fatal(self.__lastReadPos,
          'Type error: Expecting {0}, got a map', expectedType.getName())

    keyType = expectedType.getKeyType()
    valueType = expectedType.getValueType()

    actualType = self.__readUByte()
    if actualType is None:
      self.fatal(self.__lastReadPos,
          'Premature end of stream while reading map in struct {0}', self.__descriptor.getName())
    actualKeyType = actualType >> 4
    actualValueType = actualType & 0x0f

    length = self.__readVarInt()
    result = {}
    if self.__debug:
      self.__debugf('begin {0} [{1}]', expectedType.getName(), length)
      self.__indentLevel += 1
    for _ in range(length):
      key = self.__readValue(keyType, actualKeyType)
      if not keyType.isAssignable(key):
        self.typeError(self.__lastReadPos, type(key), 'map key', keyType)
      value = self.__readValue(valueType, actualValueType)
      if not valueType.isAssignable(value):
        self.typeError(self.__lastReadPos, type(value), 'map value', valueType)
      result[key] = value

    if self.__debug:
      self.__indentLevel -= 1
      self.__debugf('end {0}', expectedType.getName())
    return result

  def __readListValue(self, expectedType, packed=False):
    if expectedType.typeId() != types.TypeKind.LIST and\
       expectedType.typeId() != types.TypeKind.SET:
      self.fatal(self.__lastReadPos,
          'Type error: Expecting {0}, got a list', expectedType.getName())

    elementType = expectedType.getElementType()
    actualElementType = self.__readUByte()
    if actualElementType is None:
      self.fatal(self.__lastReadPos,
          'Premature end of stream while reading list in struct {0}', self.__descriptor.getName())
    if actualElementType > DataType.MAXVAL:
      self.fatal(self.__lastReadPos, 'Invalid data type: 0x{0:x}', elementType)

    length = self.__readVarInt()
    result = []
    if self.__debug:
      self.__debugf('begin {0} [{1}]', expectedType.getName(), length)
      self.__indentLevel += 1
    for _ in range(length):
      element = self.__readValue(elementType, actualElementType)
      if not elementType.isAssignable(element):
        self.typeError(self.__lastReadPos, type(element), 'list element', elementType)
      result.append(element)

    if expectedType.typeId() == types.TypeKind.SET:
      result = set(result)

    if self.__debug:
      self.__indentLevel -= 1
      self.__debugf('end {0}', expectedType.getName())

    return result

  def __readStructFields(self, expectedType, first=False, shared=False):
    baseType = self.__getBase(expectedType)
    self.__descriptor = baseType
    self.__fieldId = 0
    while not self.__atEof:
      dataType = self.__readFieldHeader()
      if dataType is None:
        if first:
          return self.__instance
        else:
          self.fatal(self.__lastReadPos,
              'Unexpected end of file while reading struct: {0}', expectedType.getName())

      if dataType == DataType.END:
        break
      elif dataType == DataType.SHARED_REF:
        oid = self.zigZagDecode(self.__readVarInt())
        if self.__debug:
          self.__debugf('shared object: {0}', oid)
        return self.__getShared(oid)
      elif dataType == DataType.SUBTYPE:
#         base = self.__getBase(self.__descriptor)
        if self.__subtypeId == baseType.getTypeId():
          subtype = baseType
        else:
          subtype = self.__typeRegistry.getSubtype(baseType, self.__subtypeId)
        if subtype:
#           self.__states.append((self.__fieldId, self.__descriptor))
          expectedType = subtype
          self.__fieldId = 0
          if self.__debug:
            self.__debugf('subtype: {0}({1})',
                expectedType.getName(), self.__subtypeId)
        else:
          # TODO: Create the instance with the descriptor we know, and
          # Store subtype fields in extension field 0
          print('No subtype id {0} found for base type {1}(id:{2})'.format(self.__subtypeId,
              baseType.getName(), baseType.getTypeId()))
          print("All known subtypes of", baseType.getName())
          for k, v in self.__typeRegistry.getSubtypes(baseType).items():
            print("  {0} = {1}".format(k, v.getName()))
#           self.pushState((self.__fieldId, None))
          assert False, 'Implement unknown subtypes'
#         self.__readStructFields()
        if self.__instance is None:
          self.__instance = expectedType.new()
          if shared:
            index = self.addShared(self.__instance)
            if self.__debug:
              self.__debugf('+shared: {0}', index)
#         assert self.__descriptor is subtype
#         print('{0:04x} end subtype: {1}'.format(self.__lastReadPos, self.__descriptor.getName()))
#         self.__fieldId, self.__descriptor = self.__states.pop()
#         print('{0:04x} resuming: {1}'.format(self.__lastReadPos, self.__descriptor.getName()))
        self.__descriptor = subtype
      else:
        if self.__instance is None:
          self.__instance = expectedType.new()
          if shared:
            index = self.addShared(self.__instance)
            if self.__debug:
              self.__debugf('+shared: {0}', index)
        field = expectedType.getFieldById(self.__fieldId)
        if not field:
          self.fatal(self.__lastReadPos, 'Unknown field #{0} of type {1}',
              self.__fieldId, expectedType.getName())
        fieldType = field.getType();
        if self.__debug:
          self.__debugf('field: {0}.{1}(2) type:{3} data:{4}',
              expectedType.getName(), field.getName(), self.__fieldId,
              fieldType.getName(), DTYPE_NAMES[dataType])
        value = self.__readValue(fieldType, dataType)
        if value is None and not field.getOptions().isNullable():
          self.fatal(self.__lastReadPos, "Null value not allowed for field '{0}'", field.getName())
        elif not fieldType.isAssignable(value):
          self.typeError(self.__lastReadPos, type(value),
              "value of field '{0}:{1}'".format(
                  self.__instance.descriptor().getName(), field.getName()), fieldType)
        field.setValue(self.__instance, value)
    if self.__instance is None:
      self.__instance = expectedType.new()
      if shared:
        index = self.addShared(self.__instance)
        if self.__debug:
          self.__debugf('+shared: {0}', index)
    return self.__instance

  def __readFieldHeader(self):
    self.__lastReadPos = self.__readPos
    data = self.__stream.read(1)
    if len(data) == 0:
      self.__atEof = True
      return None
    self.__readPos += 1
    assert len(data) == 1
    byte = data[0]
    delta = byte >> 4
    dataType = byte & 0x0f
    if dataType > DataType.MAXVAL:
      self.fatal(self.__lastReadPos, 'Invalid data type: 0x{0:x}', byte)
#     if self.__debug:
#       self.__debugf('-- dataType: 0x{0:x}', byte)
    if dataType == DataType.SUBTYPE:
      if delta > 0:
        self.__subtypeId = delta
      else:
        self.__subtypeId = self.__readVarInt()
      if self.__debug:
        self.__debugf('-- subtype header: dataType:{0}, subtypeId:{1}',
            DTYPE_NAMES[dataType], self.__subtypeId)
    elif dataType == DataType.END:
      dataType = byte # For extended types
    elif dataType != DataType.END:
      if delta > 0:
        self.__fieldId += delta
      else:
        oid = self.__fieldId
        self.__fieldId = self.__readVarInt()
        odelta = self.__fieldId - oid
        if odelta > 0 and odelta < 15:
          self.fatal(self.__lastReadPos, 'Invalid field ID encoding: {0} -> {1}', oid, self.__fieldId)
      self.__subtypeId = 0
#       if self.__debug:
#         self.__debugf('-- field header: dataType:{0}, fieldId:{1}',
#             DTYPE_NAMES[dataType], self.__fieldId)
    self.__lastReadPos = self.__readPos
    if self.__debug:
      assert self.__pos() == self.__readPos, (self.__pos(), self.__readPos)
    return dataType

  def __readVarInt(self):
    result = 0
    shift = 0
    while True:
      data = self.__stream.read(1)
      if len(data) == 0:
        self.fatal(self.__lastReadPos,
            'Unexpected end of file while reading struct: {0}', self.__descriptor.getName())
      self.__readPos += 1
      b = data[0]
      assert b >= 0
      result = result + ((b & 0x7f) << shift)
      if b < 0x80:
        break
      shift += 7
#     if self.__debug:
#       self.__debugf('-- varint: {0}', result)
    return result

  def __readBytes(self, length):
    data = self.__stream.read(length)
    if len(data) < length:
      self.fatal(self.__lastReadPos,
          'Unexpected end of file while reading struct: {0}', self.__descriptor.getName())
    self.__readPos += length
    return data

  def __readUByte(self):
    data = self.__stream.read(1)
    if len(data) == 0:
      self.__atEof = True
      return None
    self.__readPos += 1
    return data[0]

  def __pos(self):
    return self.__stream.tell()

  def __getShared(self, index):
    try:
      return self.getShared(index)
    except KeyError:
      self.fatal(self.__lastReadPos,
          'Invalid shared object ID {0}, expecting type {1} (while reading struct {2}).',
          index, self.__descriptor.getName(), self.__descriptor.getName())

  def __isSharedType(self, ty):
    while True:
      if ty.getOptions().hasShared():
        return ty.getOptions().isShared()
      if ty.hasBaseType():
        ty = ty.getBaseType()
      else:
        return False

  def typeError(self, pos, actualType, valueName, toType):
    if isinstance(actualType, types.Type):
      actualType = actualType.getName()
    elif isinstance(actualType, type):
      actualType = actualType.__name__
    else:
      actualType = DTYPE_NAMES[actualType]

    if isinstance(toType, types.Type):
      toType = toType.getName()

    self.fatal(self.__lastReadPos,
        "Type error: {0} should be '{1}', not '{2}'",
        valueName, toType, actualType)

  def fatal(self, pos, msgFmt, *args):
    raise EncodingError('Error:{0:x}: {1}'.format(pos, msgFmt.format(*args)))

  def __debugf(self, msg, *args, **kwargs):
    data = b''
    if self.__debugPos < self.__readPos:
      self.__stream.seek(self.__debugPos)
      data = self.__stream.read(self.__readPos - self.__debugPos)
      assert self.__stream.tell() == self.__readPos

    dumpdata = []
    for i in range(0, len(data), 6):
      row = []
      for j in range(i, i + 6):
        if j < len(data):
          row.append('{0:02x}'.format(data[j]))
        else:
          row.append('  ')
      dumpdata.append(' '.join(row))
    if len(dumpdata) == 0:
      dumpdata.append(' ' * 17)

    print('{0:04x} {1}  {2}{3}'.format(
        self.__debugPos, dumpdata[0], '  ' * self.__indentLevel, msg.format(*args, **kwargs)))
    for row in dumpdata[1:]:
      self.__debugPos += 6
      print('{0:04x} {1}'.format(self.__debugPos, row))

    self.__debugPos = self.__readPos

  @staticmethod
  def __getBase(ty):
    if ty.typeId() == types.TypeKind.STRUCT:
      while ty.hasBaseType():
        ty = ty.getBaseType()
    return ty

  @staticmethod
  def zigZagDecode(value):
    # Note this version of ZZ works with Python bignums
    if value & 1:
      return (-1 - value) >> 1
    else:
      return value >> 1

# =============================================================================
# Factory for binary codecs
# =============================================================================

class BinaryCodec:
  @staticmethod
  def createEncoder(outputStream):
    return BinaryEncoder(outputStream)

  @staticmethod
  def createDecoder(inputStream, sourcePath=None, typeRegistry=None):
    return BinaryDecoder(inputStream, sourcePath, typeRegistry)
