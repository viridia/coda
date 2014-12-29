from coda.compiler import genbase
from coda import types
import os

class TypeNameFormatter:
  def __init__(self, gen):
    self.gen = gen

  def __call__(self, struct, useActual=True):
    '''@type struct: coda.descriptors.StructType'''
    name = struct.getName()
    while struct.getEnclosingType():
      struct = struct.getEnclosingType()
      name = struct.getName() + '.' + name
    fd = struct.getFile()
    if fd and fd is not self.fd:
      package = self.gen.getFilePackage(fd)
      if package:
        name = package + '.' + name
        for fullname, localname in self.gen.localNames.items():
          if name.startswith(fullname):
            return localname + name[len(fullname):]
        return name
    return name

  def setFile(self, fd):
    self.fd = fd

class DefaultValueFormatter(genbase.AbstractTypeTransform):
  '''Transform a type expression into it's default value.'''

  def __init__(self, nameFormatter):
    super().__init__()
    self.nameFormatter = nameFormatter

  def visitType(self, ty, *args):
    raise AssertionError('Type not handled: ' + str(ty))

  def visitBooleanType(self, ty):
    return 'False'

  def visitIntegerType(self, ty):
    return '0'

  def visitFloatType(self, ty):
    return '0.0'

  def visitDoubleType(self, ty):
    return '0.0'

  def visitStringType(self, ty):
    return 'coda.runtime.Object.EMPTY_STRING'

  def visitBytesType(self, ty):
    return 'coda.runtime.Object.EMPTY_BYTES'

  def visitListType(self, ty):
    return 'coda.runtime.Object.EMPTY_LIST'

  def visitSetType(self, ty):
    return 'coda.runtime.Object.EMPTY_SET'

  def visitMapType(self, ty):
    return 'coda.runtime.Object.EMPTY_MAP'

  def visitStructType(self, ty):
    return self.nameFormatter(ty) + '.defaultInstance()'

  def visitEnumType(self, ty):
    # TODO: get first member
    return '0'

  def visitModifiedType(self, ty):
    return self(ty.getElementType())

class EmptyValueFormatter(DefaultValueFormatter):
  '''Transform a type expression into an empty, mutable value.'''

  def visitBytesType(self, ty):
    return 'buffer()'

  def visitListType(self, ty):
    return '[]'

  def visitSetType(self, ty):
    return 'set()'

  def visitMapType(self, ty):
    return '{}'

  def visitStructType(self, ty):
    return self.nameFormatter(ty) + '()'

class TypeDescriptorFormatter(genbase.AbstractTypeTransform):
  '''Transform a type expression into its source form.'''

  def __init__(self, nameFormatter):
    super().__init__()
    self.nameFormatter = nameFormatter

  def visitType(self, ty, *args):
    raise AssertionError('Type not handled: ' + str(ty))

  def visitBooleanType(self, ty):
    return 't.BOOL'

  def visitIntegerType(self, ty):
    return 't.I{0}'.format(ty.getBits())

  def visitFloatType(self, ty):
    return 't.FLOAT'

  def visitDoubleType(self, ty):
    return 't.DOUBLE'

  def visitStringType(self, ty):
    return 't.STRING'

  def visitBytesType(self, ty):
    return 't.BYTES'

  def visitListType(self, ty):
    return 't.ListType().setElementType({0})'.format(
        self(ty.getElementType()))

  def visitSetType(self, ty):
    return 't.SetType().setElementType({0})'.format(
        self(ty.getElementType()))

  def visitMapType(self, ty):
    return 't.MapType().setKeyType({0}).setValueType({1})'.format(
        self(ty.getKeyType()), self(ty.getValueType()))

  def visitStructType(self, ty):
    return self.nameFormatter(ty) + '.DESCRIPTOR'

  def visitEnumType(self, ty):
    return self.nameFormatter(ty) + '.DESCRIPTOR'

  def visitModifiedType(self, ty):
    s = 't.ModifiedType().setElementType({0})'.format(self(ty.getElementType()))
    if ty.isShared():
      s += '.setShared(True)'
    if ty.isConst():
      s += '.setConst(True)'
    return s

class ValueFormatter(genbase.AbstractTypeTransform):
  '''Transform a typed expression into its python representation.'''

  def visitType(self, ty, *args):
    raise AssertionError('Type not handled: ' + str(ty))

  def visitBooleanType(self, ty, value):
    return repr(value)

  def visitIntegerType(self, ty, value):
    return repr(value)

  def visitFloatType(self, ty, value):
    return repr(value)

  def visitDoubleType(self, ty, value):
    return repr(value)

  def visitStringType(self, ty, value):
    return repr(value)

  def visitBytesType(self, ty, value):
    return repr(value)

  def visitListType(self, ty, value):
    return '[' + ', '.join(self(ty.getElementType(), el) for el in value) + ']'

  def visitSetType(self, ty, value):
    assert False, 'Implement'

  def visitMapType(self, ty, value):
    return '{' + ', '.join(
        self(ty.getKeyType(), k) + ': ' +
        self(ty.getValueType(), value[k]) for k in sorted(value.keys())) + '}'

  def visitStructType(self, ty, value):
    return repr(value)

  def visitEnumType(self, ty, value):
    return repr(value)

class Python3Generator(genbase.CodeGenerator):
  '''Python3 code generator for CODA classes.'''

  RESERVED_WORDS = frozenset([
      # Reserved words
      'if', 'else', 'class', 'finally', 'try', 'while', 'for', 'except', 'is', 'in',
      'return', 'break', 'continue',
      # Built-in types and functions
      'vars', 'iter', 'type', 'id', 'range', 'tuple', 'super',
  ])

  def __init__(self, options):
    super().__init__('python.python3', options)
    self.formatTypeName = TypeNameFormatter(self)
    self.defaultValueForType = DefaultValueFormatter(self.formatTypeName)
    self.emptyValueForType = EmptyValueFormatter(self.formatTypeName)
    self.describeType = TypeDescriptorFormatter(self.formatTypeName)
    self.formatValue = ValueFormatter()
    if 'checkTypes' in options:
      self.checkTypes = options.checkTypes in ['True', 'true', 'yes', 1]
    else:
      self.checkTypes = False

  def calcSourcePath(self, fd, options, decl):
    '''@type fd: coda.descriptors.FileDescriptor
       @type options: FileOptions
       Method to calculate the file path to write a descriptor to.'''
    return self.calcSourcePathWithoutExtension(fd, options, decl) + '.py'

  def calcSourcePathWithoutExtension(self, fd, options, decl):
    '''@type fd: coda.descriptors.FileDescriptor
       @type options: FileOptions
       Method to calculate the file path to write a descriptor to.'''
    if options.filepath:
      path = options.filepath
    elif options.package:
      path = os.path.join(*options.package.split('.'))
    else:
      path = fd.getDirectory()

    if decl:
      # This is the case for each type being in its own file
      # FIXME: I don't think this will actually work
      path = os.path.join(path, fd.getName(), decl.getName())
    else:
      # This is the case where all types are in a single file
      pass
    return path

  def beginFile(self, fd, fileOptions):
    self.formatTypeName.setFile(fd)
    self.registerUniqueTypes(fd)
    self.registerUniqueOptions(fd)
    self.globalNamesUsed = set()
    self.localNames = {}
    self.package = self.getScopedOption(fd.getOptions().getPackage(), None)

  def genHeader(self, fd):
    self.writeLn('# ' + '=' * 77)
    self.writeLnFmt(
        '# Generated by codagen from {0}.coda. DO NOT EDIT!', fd.getName())
    self.writeLn('# ' + '=' * 77)
    self.writeLn()

  def genImports(self, fd):
    '''@type fd: coda.descriptors.FileDescriptor'''
    self.writeLn('import coda.runtime')
    firstImport = True
    for imp in fd.getImports():
      path = self.getScopedOption(imp.getPackage(), None)
      if path:
        if firstImport:
          self.writeLn('__lateImports__ = []')
          firstImport = False
        self.writeImport(path)
    for imp in self.getScopedOption(fd.getOptions().getImports(), ()):
      if firstImport:
        self.writeLn('__lateImports__ = []')
        firstImport = False
      self.writeImport(imp)
    self.writeLn()

  def writeImport(self, path):
    packageParts = self.package.split('.')
    importParts = path.split('.')
    commonPrefix = []
    while len(packageParts) > 0 and len(importParts) > 1 and packageParts[0] == importParts[0]:
      commonPrefix.append(packageParts[0])
      packageParts = packageParts[1:]
      importParts = importParts[1:]
    self.writeLn('try:')
    self.indent()
    if commonPrefix and importParts[0] not in self.globalNamesUsed and importParts[0] not in self.RESERVED_WORDS and len(importParts) < 2:
      self.globalNamesUsed.add(importParts[0])
      self.localNames['.'.join(commonPrefix + importParts[0:1])] = importParts[0]
      localName = '.'.join(importParts)
      self.writeLnFmt('from {0} import {1}', '.' * len(packageParts), '.'.join(importParts))
    else:
      self.writeLnFmt('import {0}', path)
      localName = path
    self.unindent()
    self.writeLn('except ImportError:')
    self.indent()
    self.writeLnFmt("__lateImports__.append(('{0}', '{1}'))", path, localName)
    self.unindent()

  def beginStruct(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    if not struct.getEnclosingType():
      self.writeLn('# ' + '=' * 77)
      self.writeLnFmt('# {0}', struct.getName())
      self.writeLn('# ' + '=' * 77)
      self.writeLn()
    if struct.getBaseType():
      baseType = self.formatTypeName(struct.getBaseType())
    else:
      baseType = 'coda.runtime.Object'
    mixinType = genbase.getScopedOption(
          struct.getOptions().getMixin(),
          self.optionScope)
    if mixinType:
      baseType += ', ' + mixinType
    self.writeLnFmt('class {0}({1}):', struct.getName(), baseType)
    self.indent()
    if struct.getFields():
      self.writeLn('__slots__ = [')
      self.indent()
      for field in struct.getFields():
        self.writeLnFmt('\'_{0}\',', field.getName())
      self.unindent()
      self.writeLn(']')
      self.writeLn()
    self.unindent()

  def genStructMetadata(self, fd, struct):
    # Table of inner structs
    if struct.getStructs():
      self.writeLn('__structs__ = (')
      self.indent()
      for st in struct.getStructs():
        self.writeLnFmt('{0},', st.getName())
      self.unindent()
      self.writeLn(')')
    else:
      self.writeLn('__structs__ = ()')

    # Table of inner enums
    if struct.getEnums():
      self.writeLn('__enums__ = (')
      self.indent()
      for en in struct.getEnums():
        self.writeLnFmt('{0},', en.getName())
      self.unindent()
      self.writeLn(')')
    else:
      self.writeLn('__enums__ = ()')

    # Table of field definitions
    if struct.getFields():
      self.writeLn('__fields__ = (')
      self.indent()
      for field in struct.getFields():
        self.writeLnFmt('(\'{0}\', {1}, {2}, {3}),',
            field.getName(),
            field.getId(),
            self.typeIdOf(field.getType()),
            self.optionIdOf(field.getOptions()))
      self.unindent()
      self.writeLn(')')
    else:
      self.writeLn('__fields__ = ()')

    if struct.getExtensions():
      self.writeLn('__extensions__ = (')
      self.indent()
      for ex in struct.getExtensions():
        self.writeLnFmt('(\'{0}\', {1}, {2}, {3}, {4}),',
            ex.getName(),
            ex.getId(),
            self.typeIdOf(ex.getType()),
            self.typeIdOf(ex.getExtends()),
            ex.getSourceLine())
      self.unindent()
      self.writeLn(')')
    else:
      self.writeLn('__extensions__ = ()')

    if struct.hasOptions():
      self.writeLnFmt('__optionsIndex__ = {0}', self.optionIdOf(struct.getOptions()))

    if struct.hasTypeId():
      self.writeLn('TYPE_ID = {0}'.format(struct.getTypeId()))
    else:
      self.writeLn('TYPE_ID = None')

    self.writeLn()

  def genStructConstructor(self, fd, struct):
    self.writeLn('def __init__(self):')
    self.indent()
    self.writeLn('super().__init__()')
    for field in struct.getFields():
      self.writeLnFmt('self._{0} = {1}', field.getName(),
          self.defaultValueOf(field))
    self.unindent()
    self.writeLn()

  def genStructStdMethods(self, fd, struct):
    self.genEqualsMethod(fd, struct)
    self.genHashMethod(fd, struct)
    self.genFreezeMethod(fd, struct)
    self.genWriteMethods(fd, struct)
    self.genMergeMethod(fd, struct)

  def genEqualsMethod(self, fd, struct):
    # Equality comparison
    if struct.getFields():
      self.writeLn('def _equalsImpl(self, other):')
      self.indent()
      if self.useCompareByReference(struct):
        self.writeLn('return self is other')
      else:
        self.writeIndent()
        self.write('return (super()._equalsImpl(other)')
        self.indent()
        for field in struct.getFields():
          self.write(' and\n')
          self.writeIndent()
          self.write('self._{0} == other._{0}'.format(field.getName()))
        self.unindent()
        self.write(')')
        self.writeLn()
      self.unindent()
      self.writeLn()

  def genHashMethod(self, fd, struct):
    # Hashing
    if struct.getOptions().hasReference():
      self.writeLn('def __hash__(self):')
      self.indent()
      self.writeLn('return hash(id(self))')
      self.unindent()
      self.writeLn()
    elif struct.getFields() and not self.useCompareByReference(struct):
      self.writeLn('def _hashImpl(self):')
      self.indent()
      self.writeIndent()
      self.write('return hash((super()._hashImpl()')
      self.indent()
      for field in struct.getFields():
        self.write(',\n')
        self.writeIndent()
        self.write('self._{0}'.format(field.getName()))
      self.write('))')
      self.unindent()
      self.writeLn()
      self.unindent()
      self.writeLn()

  def genFreezeMethod(self, fd, struct):
    # Freezing
    if struct.getFields():
      lines = []
      for field in struct.getFields():
        fname = field.getName()
        ftype = field.getType()
        shared = False
        if ftype.typeId() == types.TypeKind.MODIFIED:
          shared |= ftype.isShared()
          ftype = ftype.getElementType()
        shared |= self.isSharedType(ftype)
        fkind = ftype.typeId()
        if fkind == types.TypeKind.LIST:
          # Ooops, we forgot to freeze the objects referenced here.
          lines.append('if type(self._{0}) is not tuple:'.format(fname))
          lines.append('  self._{0} = tuple(self._{0})'.format(fname))
        elif fkind == types.TypeKind.SET:
          # Ooops, we forgot to freeze the objects referenced here.
          lines.append('if type(self._{0}) is not frozenset:'.format(fname))
          lines.append('  self._{0} = frozenset(self._{0})'.format(fname))
        elif fkind == types.TypeKind.MAP:
          # Ooops, we forgot to freeze the objects referenced here.
          lines.append(
              'if type(self._{0}) is not coda.runtime.FrozenDict:'.format(
                  fname))
          lines.append(
              '  self._{0} = coda.runtime.FrozenDict(self._{0})'.format(fname))
        elif fkind == types.TypeKind.STRUCT:
          if field.getOptions().isNullable() or shared:
            if not self.useCompareByReference(ftype):
              lines.append('if deep and self._{0} and self._{0}.isMutable():'.format(fname))
              lines.append('  self._{0}.freeze(deep)'.format(fname))
          else:
            lines.append('if deep and self._{0}.isMutable():'.format(fname))
            lines.append('  self._{0}.freeze(deep)'.format(fname))
      if lines:
        self.writeLn('def _freezeImpl(self, deep=True):')
        self.indent()
        self.writeLn('super()._freezeImpl(deep)')
        for line in lines:
          self.writeLn(line)
        self.unindent()
        self.writeLn()

  def genWriteMethods(self, fd, struct):
    # Serialization
    writeableFields = self.getWriteableFields(struct)
    if struct.hasTypeId() or writeableFields:
      self.writeLn('def _writeFields(self, encoder):')
      self.indent()
      if struct.hasTypeId():
        self.writeLnFmt('encoder.writeSubtypeHeader(\'{0}\', {1})',
            struct.getName(), struct.getTypeId())
      for field in writeableFields:
        fty = field.getType()
        if isinstance(fty, types.CollectionType):
          self.writeLnFmt('if len(self._{0}):', field.getName())
        else:
          self.writeLnFmt('if self.has{0}():', self.capitalize(field.getName()))
        self.indent()
        self.writeLnFmt(
            "encoder.writeFieldHeader('{0}', {1})",
            field.getName(), field.getId())
        self.genValueWrite('self._' + field.getName(), fty, field.getOptions())
        self.unindent()
      if struct.getBaseType():
        self.writeLn('super()._writeFields(encoder)')
      self.unindent()
      self.writeLn()

  def genValueWrite(self, var, fty, options):
    fkind = fty.typeId()
    fixedParam = ', True' if options.isFixed() else ''
    if fkind == types.TypeKind.BOOL:
      self.writeLnFmt("encoder.writeBoolean({0})", var)
    elif fkind == types.TypeKind.INTEGER:
      if options.isFixed():
        self.writeLnFmt("encoder.writeFixed{1}({0})", var, fty.getBits())
      else:
        self.writeLnFmt("encoder.writeInteger({0})", var)
    elif fkind == types.TypeKind.FLOAT:
        self.writeLnFmt("encoder.writeFloat({0})", var)
    elif fkind == types.TypeKind.DOUBLE:
        self.writeLnFmt("encoder.writeDouble({0})", var)
    elif fkind == types.TypeKind.STRING:
        self.writeLnFmt("encoder.writeString({0})", var)
    elif fkind == types.TypeKind.BYTES:
        self.writeLnFmt("encoder.writeBytes({0})", var)
    elif fkind == types.TypeKind.LIST:
      self.writeLnFmt(
          "encoder.writeBeginList({1}, len({0}){2})",
          var, types.unmodified(fty.getElementType()).typeId(), fixedParam)
      self.writeLnFmt("for val in {0}:", var)
      self.indent()
      self.genValueWrite('val', fty.getElementType(), options)
      self.unindent()
      self.writeLn("encoder.writeEndList()")
    elif fkind == types.TypeKind.SET:
      self.writeLnFmt(
          "encoder.writeBeginSet({1}, len({0}){2})",
          var, types.unmodified(fty.getElementType()).typeId(), fixedParam)
      self.writeLnFmt("for val in {0}:", var)
      self.indent()
      self.genValueWrite('val', fty.getElementType(), options)
      self.unindent()
      self.writeLn("encoder.writeEndSet()")
    elif fkind == types.TypeKind.MAP:
      self.writeLnFmt(
          "encoder.writeBeginMap({1}, {2}, len({0}))",
          var,
          types.unmodified(fty.getKeyType()).typeId(),
          types.unmodified(fty.getValueType()).typeId())
      self.writeLnFmt("for key, val in {0}.items():", var)
      self.indent()
      self.genValueWrite('key', fty.getKeyType(), options)
      self.genValueWrite('val', fty.getValueType(), options)
      self.unindent()
      self.writeLn("encoder.writeEndMap()")
    elif fkind == types.TypeKind.STRUCT:
      if self.isSharedType(fty):
        self.writeLnFmt("encoder.writeSharedStruct({0})", var)
      else:
        self.writeLnFmt("encoder.writeStruct({0})", var)
    elif fkind == types.TypeKind.ENUM:
      self.writeLnFmt("encoder.writeInteger({0})", var)
    elif fkind == types.TypeKind.MODIFIED:
      if fty.isShared():
        assert isinstance(fty.getElementType(), types.StructType)
        self.writeLnFmt("encoder.writeSharedStruct({0})", var)
      else:
        self.genValueWrite(var, fty.getElementType(), options)
    else:
      assert False, 'Illegal type kind: ' + str(fty)

  def genMergeMethod(self, fd, struct):
    if len(struct.getFields()) == 0:
      return
    self.writeLn('def merge(self, src):')
    self.indent()
    self.writeLnFmt('"""@return {0}"""', self.formatTypeName(struct))
    if struct.getBaseType():
      self.writeLn('super().merge(src)')
    for field in struct.getFields():
      fname = self.capitalize(field.getName())
      fty = field.getType()
      if isinstance(fty, types.ListType):
        self.writeLnFmt('self.getMutable{0}().extend(src.get{0}())', fname)
      elif isinstance(fty, types.SetType):
        self.writeLnFmt('self.getMutable{0}().update(src.get{0}())', fname)
      elif isinstance(fty, types.MapType):
        self.writeLnFmt('self.getMutable{0}().update(src.get{0}())', fname)
      else:
        self.writeLnFmt('if src.has{0}():', fname)
        self.indent()
        if isinstance(fty, types.BooleanType):
          self.writeLnFmt("self.set{0}(src.is{0}())", fname)
        else:
          self.writeLnFmt("self.set{0}(src.get{0}())", fname)
        self.unindent()
    self.writeLn('return self')
    self.unindent()
    self.writeLn()

  def genFieldAccessors(self, fd, struct, field):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    fty = field.getType()
    if self.isFieldPresentable(field):
      self.genFieldPresentGetter(fd, struct, field)
    self.genFieldGetter(fd, struct, field)
    if fty.typeId() in self.MUTABLE_TYPES or (
        fty.typeId() == types.TypeKind.MODIFIED and not fty.isConst()):
      self.genFieldMutableGetter(fd, struct, field)
    self.genFieldSetter(fd, struct, field)
    self.genFieldClear(fd, struct, field)

  def genFieldPresentGetter(self, fd, struct, field):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    self.writeLnFmt('def has{0}(self):', self.capitalize(field.getName()))
    self.indent()
    self.writeLnFmt('return self._isPresent(\'{0}\')', field.getName())
    self.unindent()
    self.writeLn()

  def genFieldGetter(self, fd, struct, field):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    if field.getType().typeId() == types.TypeKind.BOOL:
      self.writeLnFmt('def is{0}(self):', self.capitalize(field.getName()))
    else:
      self.writeLnFmt('def get{0}(self):', self.capitalize(field.getName()))
    self.indent()
    if field.getType().typeId() == types.TypeKind.STRUCT:
      self.writeLnFmt('"""@return {0}"""', self.formatTypeName(field.getType()))
    self.writeLnFmt('return self._{0}', field.getName())
    self.unindent()
    self.writeLn()

  def genFieldMutableGetter(self, fd, struct, field):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    self.writeLnFmt('def getMutable{0}(self):',
        self.capitalize(field.getName()))
    self.indent()
    if field.getType().typeId() == types.TypeKind.STRUCT:
      self.writeLnFmt('"""@return {0}"""', self.formatTypeName(field.getType()))
    self.writeLn('self.checkMutable()')
#    if field.getOptions().?? (nullable? shared?)
    defaultValue = self.defaultValueOf(field)
    emptyValue = self.emptyValueOf(field)
    ftype = field.getType()
    if ftype.typeId() == types.TypeKind.MODIFIED:
      ftype = ftype.getElementType()
    if ftype.typeId() == types.TypeKind.STRUCT:
      emptyValue = 'self._{0}.shallowCopy()'.format(field.getName())
      self.writeLnFmt('if self._{0} is {1} or not self._{0}.isMutable():',
          field.getName(), defaultValue)
    else:
      self.writeLnFmt('if self._{0} is {1}:', field.getName(), defaultValue)
    self.indent()
    if self.isFieldPresentable(field):
      self.writeLnFmt('self._setPresent(\'{0}\')', field.getName())
    self.writeLnFmt('self._{0} = {1}', field.getName(), emptyValue)
    self.unindent()
    self.writeLnFmt('return self._{0}', field.getName())
    self.unindent()
    self.writeLn()

  def genFieldSetter(self, fd, struct, field):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    varName = self.varName(field.getName())
    self.writeLnFmt('def set{0}(self, {1}):', self.capitalize(field.getName()), varName)
    self.indent()
    self.writeLnFmt('"""@return {0}"""', self.formatTypeName(struct))
    self.writeLn('self.checkMutable()')
    if self.checkTypes:
      self.genTypeCheck(field, varName)

    self.writeLnFmt('self._{0} = {1}', field.getName(), varName)
    if self.isFieldPresentable(field):
      self.writeLnFmt('self._setPresent(\'{0}\')', field.getName())
    self.writeLn('return self')
    self.unindent()
    self.writeLn()

  def genFieldClear(self, fd, struct, field):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    self.writeLnFmt('def clear{0}(self):',
        self.capitalize(field.getName()))
    self.indent()
    self.writeLnFmt('"""@return {0}"""', self.formatTypeName(struct))
    self.writeLn('self.checkMutable()')
    self.writeLnFmt('self._{0} = {1}',
        field.getName(), self.defaultValueOf(field))
    if self.isFieldPresentable(field):
      self.writeLnFmt('self._clearPresent(\'{0}\')', field.getName())
    self.writeLn('return self')
    self.unindent()
    self.writeLn()

  def genTypeCheck(self, field, varName):
    ftype = field.getType()
    fkind = ftype.typeId()

    if fkind == types.TypeKind.MODIFIED:
      ftype = ftype.getElementType()
      fkind = ftype.typeId()

    if fkind == types.TypeKind.BOOL:
      self.writeLnFmt("assert isinstance({0}, bool), type({0})", varName)
    elif fkind == types.TypeKind.INTEGER:
      self.writeLnFmt("assert isinstance({0}, int), type({0})", varName)
    elif fkind == types.TypeKind.FLOAT:
      self.writeLnFmt("assert isinstance({0}, float), type({0})", varName)
    elif fkind == types.TypeKind.DOUBLE:
      self.writeLnFmt("assert isinstance({0}, float), type({0})", varName)
    elif fkind == types.TypeKind.STRING:
      self.writeLnFmt("assert isinstance({0}, str), type({0})", varName)
    elif fkind == types.TypeKind.BYTES:
      self.writeLnFmt("assert isinstance({0}, (str, bytes)), type({0})", varName)
    elif fkind == types.TypeKind.LIST:
      self.writeLnFmt("assert isinstance({0}, (list, tuple)), type({0})", varName)
    elif fkind == types.TypeKind.SET:
      self.writeLnFmt("assert isinstance({0}, (set, frozenset)), type({0})", varName)
    elif fkind == types.TypeKind.MAP:
      self.writeLnFmt("assert isinstance({0}, dict), type({0})", varName)
    elif fkind == types.TypeKind.STRUCT:
      if field.getOptions().isNullable():
        self.writeLnFmt(
            "assert {0} is None or isinstance({0}, {1}), type({0})",
            varName, self.formatTypeName(ftype))
      else:
        self.writeLnFmt(
            "assert isinstance({0}, {1}), type({0})", varName, self.formatTypeName(ftype))
    elif fkind == types.TypeKind.ENUM:
      pass
    else:
      assert False, 'Illegal type kind: ' + str(ftype)

  def beginEnum(self, fd, enum):
    '''@type fd: coda.descriptors.FileDescriptor
       @type enum: coda.descriptors.EnumType'''
    self.writeLnFmt('class {0}:', enum.getName())
    self.indent()
    for value in enum.getValues():
      self.writeLnFmt('{0} = {1}', value.getName(), value.getValue())

    self.writeLn()
    self.writeLn('__values__ = (')
    self.indent()
    valueNames = ["'{0}'".format(value.getName()) for value in enum.getValues()]
    self.writeWrapped(valueNames, end=',')
    self.unindent()
    self.writeLn(')')
    self.unindent()

  def endEnum(self, fd, enum):
    self.writeLn()

  def endFile(self, fd):
    '@type fd: coda.descriptors.FileDescriptor'

#     if fd.getPackage() != 'coda.descriptors':
#       self.writeLn('import coda.descriptors')
#       self.writeLn()

    structNames = [self.formatTypeName(ty, False) for ty in fd.getStructs()]
    enumNames = [self.formatTypeName(ty, False) for ty in fd.getEnums()]

    self.writeIndent()
    self.writeFmt('FILE = coda.runtime.createFile(\'{0}\', \'{1}\', \'{2}\'',
        fd.getName(), fd.getDirectory(), fd.getPackage())
    self.indent()
    if structNames:
      self.write(',\n')
      self.writeLn('structs = (')
      self.indent()
      self.writeWrapped(structNames, end=',')
      self.unindent()
      self.writeIndent()
      self.write(')')

    if enumNames:
      self.write(',\n')
      self.writeLn('enums = (')
      self.indent()
      self.writeWrapped(enumNames, end=',')
      self.unindent()
      self.writeIndent()
      self.write(')')

    if self.getUniqueTypes():
      self.write(',\n')
      self.writeLn('types = lambda t:(')
      self.indent()
      uniqueTypes = self.getUniqueTypes()
      for ty in uniqueTypes:
        self.writeLnFmt('{0},', self.describeType(ty))
      self.unindent()
      self.writeIndent()
      self.write(')')

    # Table of all options
    if self.getUniqueOptions():
      self.write(',\n')
      self.writeIndent()
      self.write('options = lambda d:(')
      self.indent()
      sep = ''
      uniqueOptions = self.getUniqueOptions()
      for opts in uniqueOptions:
        self.write(sep + '\n')
        sep = ','
        self.writeIndent()
        self.write(self.formatOptions(opts))
      if len(uniqueOptions) == 1:
        self.write(',')
      self.unindent()
      self.writeLn()
      self.writeIndent()
      self.write(')')

    if fd.getImports():
      self.write(',\n')
      self.writeIndent()
      self.write('imports = {')
      self.indent()
      sep = ''
      for imp in fd.getImports():
        self.write(sep + '\n')
        sep = ','
        self.writeLnFmt("'{0}': {{", imp.getPath())
        self.indent()
        for lang, pkg in imp.getPackage().items():
          self.writeLnFmt("'{0}': '{1}',", lang, pkg)
        self.unindent()
        self.writeIndent()
        self.write('}')
      self.unindent()
      self.writeLn()
      self.writeIndent()
      self.write('}')

    if fd.getExtensions():
      self.write(',\n')
      self.writeLn('extensions = (')
      self.indent()
      for ex in fd.getExtensions():
        self.writeLnFmt('(\'{0}\', {1}, {2}, {3}, {4}),',
            ex.getName(),
            ex.getId(),
            self.typeIdOf(ex.getType()),
            self.typeIdOf(ex.getExtends()),
            ex.getSourceLine())
      self.unindent()
      self.writeIndent()
      self.write(')')

#       self.write(',\n')
#       self.writeLn('enums = (')
#       self.indent()
#       self.writeWrapped(enumNames, end=',')
#       self.unindent()
#       self.writeIndent()
#       self.write(')')


    if fd.hasOptions():
      self.write(', fileOptions={0}'.format(self.optionIdOf(fd.getOptions())))

    if fd.getPackage() == 'coda.descriptors':
      self.write(', descriptors=globals()')
    else:
      self.write(', module=globals()')

    self.unindent()
    self.writeLn(')')
    self.writeLn()

    self.writeLn('__all__ = [')
    symbols = ['\'{0}\''.format(ty) for ty in structNames + enumNames]
    self.indent()
    self.writeWrapped(symbols)
    self.unindent()
    self.writeLn(']')

  def useCompareByReference(self, struct):
    while True:
      if struct.getOptions().hasReference():
        return struct.getOptions().isReference()
      if struct.hasBaseType():
        struct = struct.getBaseType()
      else:
        return False

  def isSharedType(self, struct):
    if not isinstance(struct, types.StructType):
      return False
    while True:
      if struct.getOptions().hasShared():
        return struct.getOptions().isShared()
      if struct.hasBaseType():
        struct = struct.getBaseType()
      else:
        return False

  def defaultValueOf(self, field):
    if field.getOptions().isNullable():
      return 'None'
    else:
      return self.defaultValueForType(field.getType())

  def emptyValueOf(self, field):
    return self.emptyValueForType(field.getType())

  def formatOptions(self, opts):
    def setOptionValues(opts, struct):
      if struct.getBaseType():
        setOptionValues(opts, struct.getBaseType())
      for field in struct.getFields():
        if field.isPresent(opts):
          value = field.getValue(opts)
          result.append('set{0}({1})'.format(
              self.capitalize(field.getName()),
              self.formatValue(field.getType(), value)))

    result = []
    result.append('d.{0}()'.format(opts.descriptor().getName()))
    setOptionValues(opts, opts.descriptor())
    return '.'.join(result)

  def varName(self, name):
    if name in Python3Generator.RESERVED_WORDS or name in self.globalNamesUsed:
      return 'v_' + name
    else:
      return name

  @staticmethod
  def makeTuple(items):
    items = list(items)
    if len(items) == 1:
      return '(' + items[0] + ',)'
    else:
      return '(' + ', '.join(items) + ')'

  def capitalize(self, s):
    '@type s: string'
    return s[0].upper() + s[1:]

  def decapitalize(self, s):
    '@type s: string'
    return s[0].lower() + s[1:]

  def fileExtension(self):
    return '.py'

  def formatPackage(self, packageName):
    return packageName
