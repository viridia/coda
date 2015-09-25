import coda.io
import coda.runtime
from coda.io.codec import EncodingError
from coda import types

class TextEncoder(coda.io.AbstractEncoder):
  class State:
    CLEAR = 0
    STRUCT = 1
    CONTAINER = 2
    MAP_KEY = 3
    MAP_VALUE = 4
    SUBTYPE = 5

  def __init__(self, stream):
    super().__init__()
    self.__indentLevel = 0
    self.__stream = stream
    self.__first = True
    self.__state = self.State.CLEAR
    self.__fieldHeader = False
    self.__states = []
    self.__inProgress = set()
    self.__maxDepth = 255
    self.__subtypeName = None
    self.__subtypeId = None

  def fileBegin(self):
    pass

  def fileEnd(self):
    if self.__state == self.State.SUBTYPE:
      self.__stream.write("}")
      self.__indentLevel -= 2
    self.__state = self.State.CLEAR

  def writeSubtypeHeader(self, name, sid):
    self.__subtypeName = name
    self.__subtypeId = sid
    # Always write the outermost subtype header.
    # Omit enclosed subtype headers which have no fields.
    if self.__state in (self.State.STRUCT, self.State.CLEAR):
      self.__beginSubtype()
    self.__state = self.State.SUBTYPE

  def writeFieldHeader(self, name, fid):
    assert not self.__fieldHeader
    assert self.__state in (self.State.CLEAR, self.State.STRUCT, self.State.SUBTYPE)
    # If this field is inside a subtype whose header has not yet been written, then
    # write the subtype header before writing the field.
    if self.__subtypeId is not None:
      self.__beginSubtype()
    if not self.__first:
      self.__stream.write('\n')
      self.__indent()
    elif self.__state != self.State.CLEAR:
      self.__stream.write('\n')
      self.__indent()
    self.__stream.write(name + ': ')
    self.__fieldHeader = True
    if self.__state == self.State.CLEAR:
      self.__state = self.State.STRUCT

  def writeBoolean(self, value):
    self.__beginValue()
    if value:
      self.__stream.write('true')
    else:
      self.__stream.write('false')
    return self

  def writeInteger(self, value):
    self.__beginValue()
    self.__stream.write(str(value))
    return self

  def writeFixed16(self, value):
    self.__beginValue()
    self.__stream.write(str(value))
    return self

  def writeFixed32(self, value):
    self.__beginValue()
    self.__stream.write(str(value))
    return self

  def writeFixed64(self, value):
    self.__beginValue()
    self.__stream.write(str(value))
    return self

  def writeFloat(self, value):
    self.__beginValue()
    self.__stream.write(str(value))
    return self

  def writeDouble(self, value):
    self.__beginValue()
    self.__stream.write(str(value))
    return self

  def writeString(self, value):
    self.__beginValue()
    self.__stream.write("'")
    self.__stream.write(value) # TODO: Escapes
    self.__stream.write("'")
    return self

  def writeBytes(self, value):
    self.__beginValue()
    self.__stream.write("<[")
    self.__stream.write("]>")
    return self

  def writeBeginList(self, elementKind, length, fixed=False):
    if len(self.__states) > self.__maxDepth:
      raise EncodingError('Maximum recursion depth exceeded')
    self.__states.append(self.__state)
    self.__beginValue()
    self.__stream.write("[")
    self.__indentLevel += 2
    self.__state = self.State.CONTAINER
    self.__first = True
    return self

  def writeEndList(self):
    self.__indentLevel -= 2
    if not self.__first:
      self.__stream.write('\n')
      self.__indent()
    self.__stream.write("]")
    self.__state = self.__states.pop()
    self.__first = False
    return self

  def writeBeginSet(self, elementKind, length, fixed=False):
    if len(self.__states) > self.__maxDepth:
      raise EncodingError('Maximum recursion depth exceeded')
    self.__states.append(self.__state)
    self.__beginValue()
    self.__stream.write("[")
    self.__indentLevel += 2
    self.__state = self.State.CONTAINER
    self.__first = True
    return self

  def writeEndSet(self):
    self.__indentLevel -= 2
    if not self.__first:
      self.__stream.write('\n')
      self.__indent()
    self.__stream.write("]")
    self.__state = self.__states.pop()
    self.__first = False
    return self

  def writeBeginMap(self, keyKind, valueKind, length):
    if len(self.__states) > self.__maxDepth:
      raise EncodingError('Maximum recursion depth exceeded')
    self.__states.append(self.__state)
    self.__beginValue()
    self.__stream.write("{")
    self.__indentLevel += 2
    self.__state = self.State.MAP_KEY
    self.__first = True
    return self

  def writeEndMap(self):
    self.__indentLevel -= 2
    if not self.__first:
      self.__stream.write('\n')
      self.__indent()
    self.__stream.write("}")
    self.__state = self.__states.pop()
    self.__first = False
    return self

  def writeStruct(self, value, shared=False):
    stackLen = len(self.__states)
    self.__beginValue()
    if value is None:
      self.__stream.write("null")
    else:
      if shared:
        index = self.addShared(value)
        if index is not None:
          self.__beginValue()
          self.__stream.write('%' + str(index))
          return self
      assert isinstance(value, coda.runtime.Object)
      sid = id(value)
      if sid in self.__inProgress:
        raise EncodingError('Already serializing object of type ' +
            value.descriptor().getFullName())
      self.__inProgress.add(sid)
      index = self.getShared(value)
      self.__writeBeginStruct()
      if index:
        self.__stream.write(" #{0}".format(index))
      value.writeFields(self)
      self.__writeEndStruct()
      self.__inProgress.remove(sid)
    assert stackLen == len(self.__states)
    return self

  def __writeBeginStruct(self):
    if len(self.__states) > self.__maxDepth:
      raise EncodingError('Maximum recursion depth exceeded')
    self.__states.append(self.__state)
    self.__stream.write("{")
    self.__indentLevel += 2
    self.__state = self.State.STRUCT
    self.__first = True
    return self

  def __writeEndStruct(self):
    assert self.__state in (self.State.STRUCT, self.State.SUBTYPE)
    self.__indentLevel -= 2
    if not self.__first:
      self.__stream.write('\n')
      self.__indent()
    if self.__state == self.State.SUBTYPE:
      self.__stream.write("}")
      self.__indentLevel -= 2
#       self.__indent()
    self.__stream.write("}")
    self.__state = self.__states.pop()
    self.__first = False
    self.__subtypeId = None
    return self

  def __indent(self):
    self.__stream.write(' ' * self.__indentLevel)

  def __beginSubtype(self):
    assert self.__state in (self.State.STRUCT, self.State.SUBTYPE, self.State.CLEAR)
    if self.__state == self.State.SUBTYPE:
      self.__stream.write("}")
      self.__indentLevel -= 2
    self.__beginValue()
    self.__stream.write("${0} ({1}): {{".format(self.__subtypeId, self.__subtypeName))
    self.__indentLevel += 2
    self.__first = True
    self.__state = self.State.SUBTYPE
    self.__subtypeId = None
    self.__subtypeName = None
    return self

  def __beginValue(self):
    if self.__fieldHeader:
      self.__fieldHeader = False
    elif self.__state != self.State.CLEAR:
      if self.__first:
        self.__stream.write('\n')
        self.__indent()
      elif self.__state == self.State.MAP_KEY:
        self.__stream.write(': ')
        self.__state = self.State.MAP_VALUE
      elif self.__state == self.State.MAP_VALUE:
        self.__stream.write('\n')
        self.__indent()
        self.__state = self.State.MAP_KEY
      else:
        self.__stream.write('\n')
        self.__indent()
    self.__first = False

class TextDecoder(coda.io.AbstractDecoder):
  class State:
    CLEAR = 0
    STRUCT = 1
    CONTAINER = 2
    MAP_KEY = 3
    MAP_VALUE = 4

  class Lexer:
    '''Lexer for objects serialized in text formatter.'''
    states = (
       ('sstring','exclusive'),
       ('dstring','exclusive'),
     )

    keywords = {
      # Named values
      'true': 'TRUE',
      'false': 'FALSE',
    }

    tokens = (
      'COLON',
      'COMMA',
      'DOT',
      'LBINARY',
      'RBINARY',
      'LBRACKET',
      'RBRACKET',
      'LBRACE',
      'RBRACE',
      'LPAREN',
      'RPAREN',
      'FLOATVAL',
      'INTVAL',
      'STRING',
      'ID',
      'OBJREF',
      'TYPEREF',
    ) + tuple(keywords.values())

    # Regular expression rules for simple tokens
    t_COLON = r':'
    t_COMMA = r','
    t_DOT = r'\.'
    t_LBINARY = r'<\['
    t_RBINARY = r'\]>'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    def t_FLOATVAL(self, t):
      r'\d+\.\d+'
      t.value = float(t.value)
      return t

    def t_INTVAL(self, t):
      r'\d+'
      t.value = int(t.value)
      return t

    def t_ID(self, t):
      r'[a-zA-Z_][a-zA-Z0-9_]*'
      t.type = TextDecoder.Lexer.keywords.get(t.value, 'ID')
      return t

    # Track line numbers
    def t_newline(self, t):
      r'\n+'
      self.lexer.lineno += len(t.value)

    # C or C++ comment (ignore)
    def t_comment(self, t):
      r'\#.*'

    # Ignore spaces and tabs
    t_ignore = ' \t'
    t_sstring_dstring_ignore = ''

    # Object and type references

    def t_OBJREF(self, t):
      r'%\d+'
      t.value = int(t.value[1:])
      return t

    def t_TYPEREF(self, t):
      r'\$\d+'
      t.value = int(t.value[1:])
      return t

    # Strings

    # Start a quoted string
    def t_quote(self, t):
      '\'|"'
      self.stringVal = []
      self.stringTok = t
      if t.value == '\'':
        self.lexer.begin('sstring')
      else:
        self.lexer.begin('dstring')

    # End of a string if it matches the correct quote type
    def t_sstring_STRING(self, t):
      r"'"
      self.lexer.begin('INITIAL')
      t.value = ''.join(self.stringVal)
      return t

    def t_dstring_STRING(self, t):
      r'"'
      self.lexer.begin('INITIAL')
      t.value = ''.join(self.stringVal)
      return t

    # Regular string characters
    def t_sstring_char(self, t):
      r'[^\\\']+'
      self.stringVal.append(t.value)

    def t_dstring_char(self, t):
      r'[^\\"]+'
      self.stringVal.append(t.value)

    # Escape sequences in strings
    def t_sstring_dstring_backslash(self, t):
      r'\\\\'
      self.stringVal.append('\\')

    def t_sstring_dstring_nl(self, t):
      r'\\n'
      self.stringVal.append('\n')

    def t_sstring_dstring_cr(self, t):
      r'\\r'
      self.stringVal.append('\r')

    def t_sstring_dstring_tab(self, t):
      r'\\t'
      self.stringVal.append('\t')

    # Error handling

    def t_error(self, t):
      self.errorAt(t, "Illegal character '%s'" % t.value[0])
      self.errorReporter.abort();
      # t.lexer.skip(1)

    def t_sstring_dstring_error(self, t):
      self.errorAt(t, "Illegal character '%s'" % t.value[0])
      self.errorReporter.abort();

    # Build the lexer
    def __init__(self, stream, **kwargs):
      import ply.lex as lex
      self.lexer = lex.lex(module=self, **kwargs)
      self.stringTok = None
      self.stringVal = []

    def token(self):
      return self.lexer.token()

    def input(self, strm):
      self.__stream = strm
      self.lexer.input(self.__stream.read())

    def error(self, msg):
      self.errorReporter.error(msg)

    def errorAt(self, token, msg):
      raise EncodingError('Unexpected token on line {0}:{1}'.format(
          token.lineno, repr(token.value)))

  tokens = Lexer.tokens

  def decode(self, cls):
    assert cls.DESCRIPTOR, 'Missing descriptor for class ' + cls.__name__
    self.__descriptor = self.__getBase(cls.DESCRIPTOR)
    return self.__readStructFields()

  def __readValue(self, expectedType, options):
    tt = self.__token.type
    if self.match('LBRACE'):
      if self.__token.type == 'ID' or self.__token.type == 'TYPEREF':
        return self.__readStructValue(expectedType, options)
      else:
        return self.__readMapValue(expectedType, options)
    elif self.match('LBRACKET'):
      # It's a list
      if expectedType.typeId() != types.TypeKind.LIST and\
         expectedType.typeId() != types.TypeKind.SET:
        self.fatal(self.__token.lineno,
            'Type error: Expecting {0}, got a list', str(expectedType))
      return self.__readListValue(expectedType, options)
    elif tt == 'INTVAL':
      if (expectedType.typeId() != types.TypeKind.INTEGER and
          expectedType.typeId() != types.TypeKind.FLOAT and
          expectedType.typeId() != types.TypeKind.DOUBLE):
        self.fatal(self.__token.lineno,
            'Type error: Expecting {0}, got a number', str(expectedType))
      result = self.__token.value
      self.next()
      return result
    elif tt == 'FLOATVAL':
      if (expectedType.typeId() != types.TypeKind.INTEGER and
          expectedType.typeId() != types.TypeKind.FLOAT and
          expectedType.typeId() != types.TypeKind.DOUBLE):
        self.fatal(self.__token.lineno,
            'Type error: Expecting {0}, got a number', str(expectedType))
      assert False, 'Implement floats'
    elif tt == 'TRUE' or tt == 'FALSE':
      if expectedType.typeId() != types.TypeKind.BOOL:
        self.fatal(self.__token.lineno,
            'Type error: Expecting {0}, got a boolean', str(expectedType))
      self.next()
      return tt == 'TRUE'
    elif tt == 'STRING':
      if expectedType.typeId() != types.TypeKind.STRING:
        self.fatal(self.__token.lineno,
            'Type error: Expecting {0}, got a string', str(expectedType))
      result = self.__token.value
      self.next()
      return result
    elif tt == 'OBJREF':
      index = self.__token.value
      lineno = self.__token.lineno
      try:
        value = self.getShared(index)
      except KeyError as e:
        self.fatal(lineno, 'Invalid shared object ID {0}', index)
        raise e
      assert value
      self.next()
      return value
    else:
      self.fatal(self.__token.lineno, 'Unexpected token {0}', tt)

  def __readStructValue(self, expectedType, options):
    shared = False
    if expectedType.typeId() == types.TypeKind.MODIFIED:
      shared = expectedType.isShared()
      expectedType = expectedType.getElementType()
    if expectedType.typeId() != types.TypeKind.STRUCT:
      self.fatal(self.__token.lineno,
          "Type error: expecting a value of type {0}, not a struct",
          expectedType)
    self.__states.append(self.__instance)
    self.__states.append(self.__descriptor)
    self.__states.append(self.__sharedField)
    self.__sharedField = shared
    self.__instance = None
    self.__descriptor = expectedType
    st = self.__readStructFields()
    assert self.__descriptor is expectedType
    self.__sharedField = self.__states.pop()
    self.__descriptor = self.__states.pop()
    self.__instance = self.__states.pop()
    if not self.match('RBRACE'):
      self.fatal(self.__token.lineno, "Expected '}' after struct")
    return st

  def __readMapValue(self, expectedType, options):
    if expectedType.typeId() != types.TypeKind.MAP:
      self.fatal(self.__token.lineno,
          'Type error: Expecting {0} got a map', str(expectedType))
    keyType = expectedType.getKeyType()
    valueType = expectedType.getValueType()
    result = {}
    while True:
      if self.__token == None:
        self.fatal(self.__token.lineno,
            'Premature end of stream while reading map')
      elif self.__token.type == 'RBRACE':
        break
      lineno = self.__token.lineno
      key = self.__readValue(keyType, options)
      if not self.match('COLON'):
        self.fatal(self.__token.lineno, 'Colon expected after map key')
      if self.__token == None:
        self.fatal(self.__token.lineno,
            'Premature end of stream while reading map')
      if not keyType.isAssignable(key):
        self.typeError(lineno, type(key), 'map key', keyType)
      lineno = self.__token.lineno
      value = self.__readValue(valueType, options)
      if not valueType.isAssignable(value):
        self.typeError(lineno, type(value), 'map value', valueType)
      result[key] = value
    if not self.match('RBRACE'):
      self.fatal(self.__token.lineno, "'}' expected after map")
    return result

  def __readListValue(self, expectedType, options):
    if (expectedType.typeId() != types.TypeKind.LIST and
        expectedType.typeId() != types.TypeKind.SET):
      self.fatal(self.__token.lineno,
          'Type error: Expecting {0} got a list', str(expectedType))
    elementType = expectedType.getElementType()
    result = []
    while True:
      if self.__token == None:
        self.fatal(self.__token.lineno,
            'Premature end of stream while reading list')
      elif self.__token.type == 'RBRACKET':
        break
      lineno = self.__token.lineno
      element = self.__readValue(elementType, options)
      if not elementType.isAssignable(element):
        self.typeError(lineno, type(element), 'list element', elementType)
      result.append(element)
    if not self.match('RBRACKET'):
      self.fatal(self.__token.lineno, "']' expected after list")
    return result

  def __readStructFields(self):
    while self.__token:
      tt = self.__token.type
      if tt == 'ID':
        fieldName = self.__token.value
        self.next()
        if not self.match('COLON'):
          self.fatal(self.__token.lineno, 'Missing colon after field name')
        if self.__instance is None:
          self.__instance = self.__descriptor.new()
          if self.__sharedField:
            self.addShared(self.__instance)
        field = self.__descriptor.getField(fieldName)
        if not field:
          self.fatal(self.__token.lineno, 'Unknown field \'{0}\' of type {1}',
              fieldName, self.__descriptor.getName())
        fieldType = field.getType();
        lineno = self.__token.lineno
        self.__sharedField = False
        value = self.__readValue(fieldType, field.getOptions())
        if value is None and not field.getOptions().isNullable():
          self.fatal(lineno, "Null value not allowed for field '{0}'",
              fieldName)
        elif not fieldType.isAssignable(value):
          self.typeError(lineno, type(value),
              "value of field '{0}:{1}'".format(
                  self.__instance.descriptor().getName(), fieldName), fieldType)
        field.setValue(self.__instance, value)
      elif tt == 'TYPEREF':
        typeid = self.__token.value
        self.next()
        if not self.match('LPAREN'):
          self.fatal(self.__token.lineno, "'(' expected")
        typename = self.matchId()
        if not typename:
          self.fatal(self.__token.lineno, "type name expected")
        if not self.match('RPAREN'):
          self.fatal(self.__token.lineno, "')' expected")
        if not self.match('COLON'):
          self.fatal(self.__token.lineno, "Missing colon after subtype name")
        if not self.match('LBRACE'):
          self.fatal(self.__token.lineno, "'{{' expected")
        base = self.__getBase(self.__descriptor)
        subtype = self.__typeRegistry.getSubtype(base, typeid)
        if subtype is not None:
          self.__states.append(self.__descriptor)
          self.__descriptor = subtype
        else:
          # TODO: Create the instance with the descriptor we know, and
          # Store subtype fields in extension field 0
          print('No subtype id {0} found for base type {1}'.format(typeid,
              self.__descriptor.getName()))
          self.pushState(None)
          assert False, 'Implement unknown subtypes'
        self.__readStructFields()
        if self.__instance is None:
          self.__instance = self.__descriptor.new()
          if self.__sharedField:
            self.addShared(self.__instance)
        assert self.__descriptor is subtype
        self.__descriptor = self.__states.pop()
        if not self.match('RBRACE'):
          self.fatal(self.__token.lineno, "'}}' expected after subtype")
#         if not self.match('COMMA'):
#           break
      elif tt == 'RBRACE':
        break
      else:
        if tt:
          self.fatal(self.__token.lineno, 'Unexpected token {0}', tt)
        else:
          self.fatal(self.__token.lineno, 'Unknown token {0}',
              repr(self.__token.value))
    if self.__instance is None:
      self.__instance = self.__descriptor.new()
      if self.__sharedField:
        self.addShared(self.__instance)
    return self.__instance

  def next(self):
    self.__token = self.__lexer.token()

  def match(self, tokenType):
    if self.__token and self.__token.type == tokenType:
      self.next()
      return True
    return False

  def matchId(self):
    if self.__token.type == 'ID':
      value = self.__token.value
      self.next()
      return value
    return None

  def typeError(self, lineno, valueType, valueName, toType):
    if isinstance(valueType, types.Type):
      valueType = valueType.getName()
    elif isinstance(valueType, type):
      valueType = valueType.__name__

    if isinstance(toType, types.Type):
      toType = toType.getName()

    self.fatal(lineno,
        "Type error: {0} should be '{1}', not '{2}'",
        valueName, toType, valueType)

  def fatal(self, line, msgFmt, *args):
    raise EncodingError('Error:{0}: {1}'.format(line, msgFmt.format(*args)))

  @staticmethod
  def __getBase(ty):
    if ty.typeId() == types.TypeKind.STRUCT:
      while ty.getBaseType() != None:
        ty = ty.getBaseType()
    return ty

  def __init__(self, stream, sourcePath, typeRegistry):
    super().__init__()
    if not typeRegistry:
      from coda.runtime.typeregistry import TypeRegistry
      typeRegistry = TypeRegistry.INSTANCE
    self.__stream = stream
    self.__state = self.State.CLEAR
    self.__states = []
    self.__sourcePath = sourcePath
    self.__typeRegistry = typeRegistry
    self.__descriptor = None
    self.__lexer = TextDecoder.Lexer(stream)
    self.__lexer.sourcePath = sourcePath
    self.__lexer.lexer.lineno = 1
    self.__lexer.input(stream)
    self.__instance = None
    self.__sharedField = False
    self.next()

class TextCodec:
  @staticmethod
  def createEncoder(outputStream):
    return TextEncoder(outputStream)

  @staticmethod
  def createDecoder(inputStream, sourcePath=None, typeRegistry=None):
    return TextDecoder(inputStream, sourcePath, typeRegistry)
