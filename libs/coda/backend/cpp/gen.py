__all__ = ['createGenerator']

from coda.compiler import genbase
from coda import types
import os
import re

from abc import abstractmethod

reUpperFirst = re.compile('(.)([A-Z][a-z]+)')
reUpperRest = re.compile('([a-z0-9])([A-Z])')

def toUpperUnderscore(s):
  s = reUpperFirst.sub(r'\1_\2', s)
  return reUpperRest.sub(r'\1_\2', s).upper()

def getQualName(decl):
  '''The qualified name of a type, including enclosing types but not including namespace. This
     should only be used to reference types that are defined in the current namespace.'''
  name = decl.getName()
  while decl.getEnclosingType():
    decl = decl.getEnclosingType()
    name = decl.getName() + '::' + name
  return name

def getEnclosingQualName(decl):
  '''The qualified name of the type enclosing a declaration, including enclosing types but not
     including namespace. This should only be used to reference types that are defined in the
     current namespace.'''
  name = ''
  while decl.getEnclosingType():
    decl = decl.getEnclosingType()
    name = decl.getName() + '::' + name
  return name

# Set of types that end with a right angle bracket '>'
HAVE_TYPE_ARGS = set([
    types.TypeKind.STRING,
    types.TypeKind.BYTES,
    types.TypeKind.LIST,
    types.TypeKind.SET,
    types.TypeKind.MAP,
    types.TypeKind.MODIFIED])

class TypeNameFormatter:
  '''Return the name of a type with sufficient qualifiers that
     it can be referred to from within the current namespace.'''
  def __init__(self, gen):
    self.gen = gen

  def __call__(self, struct, useActual=True):
    '''@type struct: coda.descriptors.StructType'''
    name = struct.getName()
    while struct.getEnclosingType():
      struct = struct.getEnclosingType()
      name = struct.getName() + '::' + name
    fd = struct.getFile()
    if fd and fd is not self.fd:
      package = self.gen.getFilePackage(fd)
      if package:
        return package + '::' + name
    return name

  def setFile(self, fd):
    self.fd = fd

class CppTypeFormatter(genbase.AbstractTypeTransform):
  '''Transform a type expression into it's C++ representation.'''

  def __init__(self, nameFormatter):
    super().__init__()
    self.nameFormatter = nameFormatter

  def visitType(self, ty, *args):
    raise AssertionError('Type not handled: ' + str(ty))

  def visitPrimitiveType(self, ty, const, ref):
    '@type ty: cina.types.AbstractType'
    return self.visitType(ty)

  def visitBooleanType(self, ty, const, ref):
    return 'bool'

  def visitIntegerType(self, ty, const, ref):
    return 'int{0}_t'.format(ty.getBits())

  def visitFloatType(self, ty, const, ref):
    return 'float'

  def visitDoubleType(self, ty, const, ref):
    return 'double'

  def visitStringType(self, ty, const, ref):
    return self.refType('std::string', const, ref)

  def visitBytesType(self, ty, const, ref):
    return self.refType('std::string', const, ref)

  def visitListType(self, ty, const, ref):
    return self.refType(
        'std::vector<{0}>'.format(self(ty.getElementType(), False, False)),
        const, ref)

  def visitSetType(self, ty, const, ref):
    return self.refType(
        'std::unordered_set<{0}>'.format(
            self(ty.getElementType(), False, False)),
        const, ref)

  def visitMapType(self, ty, const, ref):
    if ty.getValueType().typeId() in HAVE_TYPE_ARGS:
      return self.refType(
          'std::unordered_map<{0}, {1} >'.format(
              self(ty.getKeyType(), False, False),
              self(ty.getValueType(), False, False)),
              const, ref)
    return self.refType(
        'std::unordered_map<{0}, {1}>'.format(
            self(ty.getKeyType(), False, False),
            self(ty.getValueType(), False, False)),
            const, ref)

  def visitStructType(self, ty, const, ref):
    return self.pointerType(self.nameFormatter(ty), const)

  def visitEnumType(self, ty, const, ref):
    return self.nameFormatter(ty)

  def visitModifiedType(self, ty, const, ref):
    return self(ty.getElementType(), const or ty.isConst(), ref)

  def pointerType(self, name, const):
    if const:
      name = 'const ' + name
    return name + '*'

  def refType(self, name, const, ref):
    if const:
      name = 'const ' + name
    if ref:
      name += '&'
    return name

class TypeDescriptorFormatter(genbase.AbstractTypeTransform):
  '''Transform a type into a reference to that type's descriptor.'''

  def __init__(self, nameFormatter):
    super().__init__()
    self.nameFormatter = nameFormatter

  def visitType(self, ty, *args):
    raise AssertionError('Type not handled: ' + str(ty))

  def visitBooleanType(self, ty):
    return 'coda::types::Boolean'

  def visitIntegerType(self, ty):
    return 'coda::types::Integer{0}'.format(ty.getBits())

  def visitFloatType(self, ty):
    return 'coda::types::Float'

  def visitDoubleType(self, ty):
    return 'coda::types::Double'

  def visitStringType(self, ty):
    return 'coda::types::String'

  def visitBytesType(self, ty):
    return 'coda::types::Bytes'

  def visitListType(self, ty):
    if ty.getElementType().typeId() in HAVE_TYPE_ARGS:
      return 'coda::types::List<{0} >'.format(self(ty.getElementType()))
    return 'coda::types::List<{0}>'.format(self(ty.getElementType()))

  def visitSetType(self, ty):
    if ty.getElementType().typeId() in HAVE_TYPE_ARGS:
      return 'coda::types::Set<{0} >'.format(self(ty.getElementType()))
    return 'coda::types::Set<{0}>'.format(self(ty.getElementType()))

  def visitMapType(self, ty):
    if ty.getValueType().typeId() in HAVE_TYPE_ARGS:
      return 'coda::types::Map<{0}, {1} >'.format(self(ty.getKeyType()), self(ty.getValueType()))
    return 'coda::types::Map<{0}, {1}>'.format(self(ty.getKeyType()), self(ty.getValueType()))

  def visitStructType(self, ty):
    return self.nameFormatter(ty)

  def visitEnumType(self, ty):
    return self.nameFormatter(ty)

  def visitModifiedType(self, ty):
    return 'coda::types::Modified<{0}, {1}, {2}>'.format(
        self(ty.getElementType()),
        ('true' if ty.isConst() else 'false'),
        ('true' if ty.isShared() else 'false'))

class DefaultValueProducer(genbase.AbstractTypeTransform):
  '''Transform a type into it's default value.'''

  def visitType(self, ty, *args):
    raise AssertionError('Type not handled: ' + str(ty))

  def visitBooleanType(self, ty):
    return 'false'

  def visitIntegerType(self, ty):
    return '0'

  def visitFloatType(self, ty):
    return '0'

  def visitDoubleType(self, ty):
    return '0'

  def visitStringType(self, ty):
    return None

  def visitBytesType(self, ty):
    return None

  def visitListType(self, ty):
    return None

  def visitSetType(self, ty):
    return None

  def visitMapType(self, ty):
    return None

  def visitStructType(self, ty):
    return 'NULL'

  def visitEnumType(self, ty):
    # TODO: get first member
    return '0'

  def visitModifiedType(self, ty):
    return self(ty.getElementType())

class ValueFormatter(genbase.AbstractTypeTransform):
  '''Transform a typed expression into its C++ representation.'''

  def __init__(self, typeFormatter):
    super().__init__()
    self.formatType = typeFormatter

  def visitType(self, ty, *args):
    raise AssertionError('Type not handled: ' + str(ty))

  def visitBooleanType(self, ty, value):
    return 'true' if value else 'false'

  def visitIntegerType(self, ty, value):
    return repr(value)

  def visitFloatType(self, ty, value):
    return repr(value)

  def visitDoubleType(self, ty, value):
    return repr(value)

  def visitStringType(self, ty, value):
    # TODO: Escapes
    return '"' + value + '"'

  def visitBytesType(self, ty, value):
    return repr(value)

  def visitListType(self, ty, value):
    result = ['coda::descriptors::StaticListBuilder<{0}>()'.format(
        self.formatType(ty.getElementType(), False, False))]
    for el in value:
      result.append('add(' + self(ty.getElementType(), el) + ')')
    result.append('build()')
    return '.'.join(result)
#     return '[' + ', '.join(self(ty.getElementType(), el) for el in value) + ']'

  def visitSetType(self, ty, value):
    assert False, 'Not implemented: set constants'

  def visitMapType(self, ty, value):
    assert False, 'This should not be called'
#     return '{' + ', '.join(
#         self(ty.getKeyType(), k) + ': ' +
#         self(ty.getValueType(), value[k]) for k in sorted(value.keys())) + '}'

  def visitStructType(self, ty, value):
    return repr(value)

  def visitEnumType(self, ty, value):
    return repr(value)

class AbstractCppGenerator(genbase.CodeGenerator):
  '''C++ header file code generator for CODA classes.'''

  def __init__(self, optionScope, options):
    super().__init__(optionScope, options)
    self.formatTypeName = TypeNameFormatter(self)
    self.formatType = CppTypeFormatter(self.formatTypeName)
    self.defaultValueOf = DefaultValueProducer()
    self.describeType = TypeDescriptorFormatter(self.formatTypeName)
    self.formatValue = ValueFormatter(self.formatType)
    self.typeKinds = {}
    self.computeTypeKindValues()

  # TODO: Verify package name

  def beginFile(self, fd, fileOptions):
    self.formatTypeName.setFile(fd)
    self.fileOptions = fileOptions

  @abstractmethod
  def getPathPrefix(self):
    return None

  def calcSourcePath(self, fd, options, decl, extension=None):
    '''@type fd: coda.descriptors.FileDescriptor
       @type options: FileOptions
       Method to calculate the file path to write a descriptor to.'''
    if options.filepath:
      path = options.filepath
    elif options.package:
      path = os.path.join(*options.package.split('::'))
    else:
      path = fd.getDirectory()

    prefix = self.getPathPrefix()
    if prefix:
      path = os.path.join(prefix, path)

    if decl:
      # This is the case for each type being in its own file
      # FIXME: I don't think this will actually work
      path = os.path.join(path, fd.getName(), decl.getName())
    else:
      # This is the case where all types are in a single file
      pass
    if not extension:
      extension = self.fileExtension()
    return path + extension

  def calcHeaderPath(self, fd, options, decl):
    '''@type fd: coda.descriptors.FileDescriptor
       @type options: FileOptions
       Method to calculate the file path to write a descriptor to.'''
    if options.filepath:
      path = options.filepath
    elif options.package:
      path = os.path.join(*options.package.split('::'))
    else:
      path = fd.getDirectory()

    if decl:
      # This is the case for each type being in its own file
      # FIXME: I don't think this will actually work
      path = os.path.join(path, fd.getName(), decl.getName())
    else:
      # This is the case where all types are in a single file
      pass
    return path + '.h'

  def calcHeaderGuard(self, fd, options, decl):
    if options.filepath:
      parts = options.filepath.upper().split('/')
    elif options.package:
      parts = [name.upper() for name in options.package.split('::')]
    else:
      parts = []

    if decl:
      # This is the case for each type being in its own file
      # FIXME: I don't think this will actually work
      parts.append(decl.getName().upper())
    else:
      # This is the case where all types are in a single file
      pass

    return '_'.join(parts)

  RESERVED_WORDS = frozenset([
      'class', 'struct', 'extern', 'auto',
      'if', 'for', 'while', 'switch',
      'default',
      'void', 'int', 'unsigned', 'float', 'double', 'long', 'short', 'char',
      'bool', 'signed', 'const'
  ])

  def requiresOutOfLineConstructor(self, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    for field in struct.getFields():
      ftype = types.unmodified(field.getType())
      if (ftype.typeId() == types.TypeKind.STRUCT and not field.getOptions().isNullable()):
        return True
    return False

  @staticmethod
  def varName(name):
    if name in AbstractCppGenerator.RESERVED_WORDS:
      return 'v_' + name
    else:
      return name

  def writeBanner(self, msg, *args):
    self.writeLn('// ' + '=' * 76)
    self.writeLnFmt('// {0}', msg.format(*args))
    self.writeLn('// ' + '=' * 76)
    self.writeLn()

  def capitalize(self, s):
    '@type s: string'
    return s[0].upper() + s[1:]

  def formatPackage(self, packageName):
    return '::'.join(packageName.split('.'))

  def computeTypeKindValues(self):
    for value in types.TypeKind.DESCRIPTOR.getValues():
      self.typeKinds[value.getValue()] = value.getName()

  def formatTypeKind(self, kind):
    return 'coda::descriptors::TYPE_KIND_' + self.typeKinds[int(kind)]

class CppHeaderGenerator(AbstractCppGenerator):
  '''C++ header file code generator for CODA classes.'''

  def getPathPrefix(self):
    return self.options.getOption('prefix_h')

  def fileExtension(self):
    return '.h'

  def getFileOutputDir(self):
    return self.headerOutputDir

  def genHeader(self, fd):
    '''@type fd: coda.descriptors.FileDescriptor'''
    self.writeBanner('Generated by codagen from {0}.coda. DO NOT EDIT!',
        fd.getName())
    guard = self.calcHeaderGuard(fd, self.fileOptions, None)
    self.writeLnFmt('#ifndef {0}', guard)
    self.writeLnFmt('#define {0} 1', guard)
    self.writeLn()

  def genImports(self, fd):
    '''@type fd: coda.descriptors.FileDescriptor'''
    self.writeLn('#ifndef CODA_RUNTIME_OBJECT_H')
    self.writeLn('  #include "coda/runtime/object.h"')
    self.writeLn('#endif')
    self.writeLn()
    self.writeLn('#include <bitset>')
    self.writeLn('#include <stdint.h>')
    for imp in self.getScopedOption(fd.getOptions().getImports(), ()):
      self.writeLnFmt('#include "{0}"', imp)
    self.writeLn()
    for ns in self.fileOptions.package.split('::'):
      self.writeLnFmt('namespace {0} {{', ns)
    self.writeLn()

    # Compute the list of types that need to be forward-declared.
    forward = self.getForwardDeclarations(fd)
    if forward:
      self.writeLn('// Forward declarations')
      for ty in forward:
        self.writeLnFmt('class {0};', ty)
      self.writeLn()

  def beginStruct(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    self.writeBanner('{0}', struct.getName())
    if struct.getBaseType():
      baseType = struct.getBaseType().getName()
    else:
      baseType = 'coda::runtime::Object'
    mixinType = genbase.getScopedOption(
          struct.getOptions().getMixin(),
          self.optionScope)
    if mixinType:
      baseType += ', public ' + mixinType
    self.writeLnFmt('class {0} : public {1} {{', struct.getName(), baseType)
    self.writeLn('public:')
    presentable = self.getPresentableFields(struct)
    if presentable:
      self.indent()
      self.writeLn('enum FieldPresentBits {')
      self.indent()
      for field in presentable:
        self.writeLnFmt('HAS_{0},', toUpperUnderscore(field.getName()))
      self.unindent()
      self.writeLn('};')
      self.writeLn()
      self.unindent()

  def endStruct(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    if struct.getFields():
      self.writeLn()
    self.indent()
    self.writeLn('static coda::descriptors::StructDescriptor DESCRIPTOR;')
    self.writeLnFmt('static {0} DEFAULT_INSTANCE;', struct.getName())
    if struct.hasTypeId() and False:
      self.writeLn('static const uint32_t TYPE_ID = {0};'.format(struct.getTypeId()))
    else:
      self.writeLn('static const uint32_t TYPE_ID;')
    self.unindent()

    if struct.getFields():
      self.writeLn()
      self.writeLn('private:')
      self.indent()
      presentable = self.getPresentableFields(struct)
      if len(presentable) > 0:
        self.writeLnFmt('std::bitset<{0}> fieldsPresent;', len(presentable))
      for field in struct.getFields():
        self.writeLnFmt('{0} _{1};',
            self.formatType(field.getType(), False, False), field.getName())
      self.writeLn()
      for field in struct.getFields():
        self.writeLnFmt('static coda::descriptors::FieldDescriptor Field_{0};', field.getName())
      self.writeLn('static coda::descriptors::FieldDescriptor* Fields[];')
      self.unindent()

    self.writeLn('};')
    self.writeLn()

  def genStructConstructor(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    if self.requiresOutOfLineConstructor(struct):
      self.writeLnFmt('{0}();', struct.getName())
    else:
      self.writeLnFmt('{0}()', struct.getName())
      self.indent()
      delim = ':'
      for field in struct.getFields():
        value = self.defaultValueOf(field.getType())
        if value:
          self.writeLnFmt('{0} _{1}({2})', delim, field.getName(), value)
          delim = ','
      self.unindent()
      self.writeLn('{}')
      self.writeLn()

    self.writeLnFmt('{0}(const {0}& _src)', struct.getName())
    self.indent()
    delim = ':'
    if struct.getBaseType():
      self.writeLnFmt(': {0}(*this)', struct.getBaseType().getName())
      delim = ','
    for field in struct.getFields():
      self.writeLnFmt('{0} _{1}(_src._{1})', delim, field.getName())
      delim = ','
    self.unindent()
    self.writeLn('{}')

  def genStructStdMethods(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    self.writeLn()

    self.writeLn('coda::descriptors::StructDescriptor* descriptor() const {')
    self.indent()
    self.writeLn('return &DESCRIPTOR;')
    self.unindent()
    self.writeLn('}')
    self.writeLn()

    # New instance
#     self.writeLnFmt('static {0}* newInstance() {{', struct.getName())
#     self.indent()
#     self.writeLnFmt('return new {0}();', struct.getName())
#     self.unindent()
#     self.writeLn('}')
#     self.writeLn()

    # Clone method
    self.writeLn('coda::runtime::Object* clone() const {')
    self.indent()
    self.writeLnFmt('return new {0}(*this);', struct.getName())
    self.unindent()
    self.writeLn('}')
    self.writeLn()

    # Equality comparison
    if struct.getFields():
      self.writeLn('bool equals(const coda::runtime::Object* other) const;')

    # Hashing
    if struct.getFields():
      self.writeLn('size_t hashValue() const;')

    # Freezing
    if struct.getFields():
      self.writeLn('void freezeImpl();')

    # Serialization
    if struct.getBaseType():
      self.writeLn('void beginWrite(coda::io::Encoder* encoder) const;')

    if self.getWriteableFields(struct) or struct.getBaseType():
      self.writeLn('void endWrite(coda::io::Encoder* encoder) const;')

  def beginEnum(self, fd, enum):
    self.writeLnFmt('enum {0} {{', enum.getName())
    self.indent()
    prefix = toUpperUnderscore(enum.getName())
    for value in enum.getValues():
      self.writeLnFmt('{0}_{1} = {2},', prefix, value.getName(), value.getValue())
    self.unindent()
    self.writeLn('};')

  def endEnum(self, fd, enum):
    '''@type fd: coda.descriptors.FileDescriptor'''
    self.writeLn()

  def genFieldAccessors(self, fd, struct, field):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    fty = types.unmodified(field.getType())
    if self.isFieldPresentable(field):
      self.genFieldPresentGetter(fd, struct, field)
    self.genFieldGetter(fd, struct, field)
    if fty.typeId() in self.MUTABLE_TYPES:
      self.genFieldMutableGetter(fd, struct, field)
    if fty.typeId() == types.TypeKind.MAP:
      self.genFieldPutter(fd, struct, field)
    self.genFieldSetter(fd, struct, field)
    self.genFieldClear(fd, struct, field)

  def genFieldPresentGetter(self, fd, struct, field):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    self.writeLn()
    self.writeLnFmt('bool has{0}() const {{',
        self.capitalize(field.getName()))
    self.indent()
    self.writeLnFmt('return fieldsPresent.test(HAS_{0});',
        toUpperUnderscore(field.getName()))
    self.unindent()
    self.writeLn('}')

  def genFieldGetter(self, fd, struct, field):
    self.writeLn()
    if field.getType().typeId() == types.TypeKind.BOOL:
      self.writeLnFmt('bool is{0}() const {{', self.capitalize(field.getName()))
    else:
      self.writeLnFmt('{0} get{1}() const {{',
          self.formatType(field.getType(), True, True),
          self.capitalize(field.getName()))
    self.indent()
    self.writeLnFmt('return _{0};', field.getName())
    self.unindent()
    self.writeLn('}')

  def genFieldMutableGetter(self, fd, struct, field):
    self.writeLn()
    self.writeLnFmt('{0} getMutable{1}() {{',
        self.formatType(field.getType(), False, True),
        self.capitalize(field.getName()))
    self.indent()
    self.writeLn('checkMutable();')
    if self.isFieldPresentable(field):
      self.writeLnFmt('fieldsPresent.set(HAS_{0});',
          toUpperUnderscore(field.getName()))
    self.writeLnFmt('return _{0};', field.getName())
    self.unindent()
    self.writeLn('}')

  def genFieldSetter(self, fd, struct, field):
    name = self.varName(field.getName())
    ftype = types.unmodified(field.getType())
    self.writeLn()
    self.writeLnFmt('{0} set{1}({2} {3}) {{',
        struct.getName() + '&',
        self.capitalize(field.getName()),
        self.formatType(field.getType(), ftype.typeId() != types.TypeKind.STRUCT, True),
        name)
    self.indent()
    self.writeLn('checkMutable();')
    if self.isFieldPresentable(field):
      self.writeLnFmt('fieldsPresent.set(HAS_{0});',
          toUpperUnderscore(field.getName()))
    self.writeLnFmt('_{0} = {1};', field.getName(), name)
    self.writeLn('return *this;')
    self.unindent()
    self.writeLn('}')

  def genFieldPutter(self, fd, struct, field):
    ftype = types.unmodified(field.getType())
    self.writeLn()
    self.writeLnFmt('{0} put{1}({2} key, {3} value) {{',
        struct.getName() + '&',
        self.capitalize(field.getName()),
        self.formatType(field.getType().getKeyType(), True, True),
        self.formatType(field.getType().getValueType(),
            ftype.getValueType().typeId() != types.TypeKind.STRUCT, True))
    self.indent()
    self.writeLn('checkMutable();')
    if self.isFieldPresentable(field):
      self.writeLnFmt('fieldsPresent.set(HAS_{0});',
          toUpperUnderscore(field.getName()))
    self.writeLnFmt('_{0}[key] = value;', field.getName())
    self.writeLn('return *this;')
    self.unindent()
    self.writeLn('}')

  def genFieldClear(self, fd, struct, field):
    self.writeLn()
    self.writeLnFmt('{0} clear{1}() {{',
        struct.getName() + '&',
        self.capitalize(field.getName()))
    self.indent()
    self.writeLn('checkMutable();')
    value = self.defaultValueOf(field.getType())
    if self.isFieldPresentable(field):
      self.writeLnFmt('fieldsPresent.reset(HAS_{0});',
          toUpperUnderscore(field.getName()))
    if value:
      self.writeLnFmt('_{0} = {1};', field.getName(), value)
    else:
      self.writeLnFmt('_{0}.clear();', field.getName())
    self.writeLn('return *this;')
    self.unindent()
    self.writeLn('}')

  def genMethod(self, fd, struct, method):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type method: coda.descriptors.StructType.Method'''
    params = ['{0}:{1}'.format(p.getName(), self.formatType(p.getType(), True, True))
        for p in method.getParams()]
    self.writeLn()
    self.writeLnFmt('{0} {1}({2}){3};',
        self.formatType(method.getType().getReturnType(), True, False),
        method.getName(),
        ', '.join(params),
        ' const' if method.getOptions().isConst() else '')

  def endFile(self, fd):
    '@type fd: coda.descriptors.FileDescriptor'
    self.writeLn('extern coda::descriptors::StaticFileDescriptor FILE;')
    self.writeLn()
    for ns in self.fileOptions.package.split('::'):
      self.writeLnFmt('}} // namespace {0}', ns)
    self.writeLn()
    self.writeLnFmt('#endif // {0}',
        self.calcHeaderGuard(fd, self.fileOptions, None))
    self.writeLn()

  def getForwardDeclarations(self, fd):
    forward = set()
    defined = set()

    def checkDefined(ty):
      if ty.typeId() == types.TypeKind.STRUCT:
        while ty.getEnclosingType():
          ty = ty.getEnclosingType()
        if ty.getFile() == fd and id(ty) not in defined:
          forward.add(ty.getName())
      elif (ty.typeId() == types.TypeKind.LIST or
          ty.typeId() == types.TypeKind.SET):
        checkDefined(ty.getElementType())
      elif ty.typeId() == types.TypeKind.MAP:
        checkDefined(ty.getKeyType())
        checkDefined(ty.getValueType())
      elif ty.typeId() == types.TypeKind.MODIFIED:
        checkDefined(ty.getElementType())

    def findTypes(struct):
      defined.add(id(struct))
      for st in struct.getStructs():
        findTypes(st)
      for field in struct.getFields():
        checkDefined(field.getType())

    for st in fd.getStructs():
      findTypes(st)
    return sorted(forward)

class CppGenerator(AbstractCppGenerator):
  '''C++ source file code generator for CODA classes.'''

  def fileExtension(self):
    return '.cpp'

  def getPathPrefix(self):
    return self.options.getOption('prefix_cpp')

  def beginFile(self, fd, fileOptions):
    super().beginFile(fd, fileOptions)
    self.registerUniqueOptions(fd)

  def genHeader(self, fd):
    self.writeBanner('Generated by codagen from {0}.coda. DO NOT EDIT!',
        fd.getName())

  def genImports(self, fd):
    '''@type fd: coda.descriptors.FileDescriptor'''
    self.writeLn('#include "coda/types.h"')
    self.writeLn('#include "coda/io/codec.h"')
    self.writeLnFmt('#include "{0}"',
        self.calcHeaderPath(fd, self.fileOptions, None))
    for imp in self.getScopedOption(fd.getOptions().getImports(), ()):
      self.writeLnFmt('#include "{0}"', imp)
    self.writeLn('#include "coda/runtime/descriptors_static.h"')
    self.writeLn()

  def beginDecls(self, fd):
    '''@type fd: coda.descriptors.FileDescriptor'''
    for ns in self.fileOptions.package.split('::'):
      self.writeLnFmt('namespace {0} {{', ns)
    self.writeLn()

    # Table of all options
    if self.getUniqueOptions():
      index = 0
      for opts in self.getUniqueOptions():
        self.writeLnFmt('coda::descriptors::{0} _options{1} = {2};',
            opts.descriptor().getName(), index, self.formatOptions(opts))
        index += 1
      self.writeLn()

  def beginStruct(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    self.writeBanner('{0}', struct.getName())
    structQualName = getQualName(struct)

    # Table of field definitions
    if struct.getFields():
      for field in struct.getFields():
        self.writeLnFmt(
            'coda::descriptors::FieldDescriptor {0}::Field_{1}(',
            structQualName, field.getName())
        self.indent(2)
        self.writeLnFmt('"{0}", {1},', field.getName(), field.getId())
        self.writeLnFmt('{0}::DESCRIPTOR,', self.describeType(field.getType()))
        optionId = self.optionIdOf(field.getOptions())
        if optionId >= 0:
          self.writeLnFmt('_options{0},', optionId)
        else:
          self.writeLn('coda::descriptors::FieldOptions::DEFAULT_INSTANCE,')
        self.writeLnFmt('CODA_OFFSET_OF({0}, _{1}));', structQualName, field.getName())
        self.unindent(2)
      self.writeLn()

    if struct.getStructs():
      structArray = '{0}_Structs'.format(struct.getName())
      self.writeLnFmt(
          'static coda::descriptors::StructDescriptor* {0}_Structs[] = {{',
          struct.getName())
      self.indent()
      for st in struct.getStructs():
        self.writeLnFmt('&{0}::DESCRIPTOR,', getQualName(st))
      self.unindent()
      self.writeLn('};')
      self.writeLn()
    else:
      structArray = 'coda::descriptors::StaticArrayRef<coda::descriptors::StructDescriptor*>()'

    if struct.getEnums():
      enumArray = '{0}_Enums'.format(struct.getName())
      self.writeLnFmt(
          'static coda::descriptors::EnumDescriptor* {0}_Enums[] = {{',
          struct.getName())
      self.indent()
      for en in struct.getStructs():
        self.writeLnFmt('&{0}::DESCRIPTOR,', getQualName(en))
      self.unindent()
      self.writeLn('};')
      self.writeLn()
    else:
      enumArray = 'coda::descriptors::StaticArrayRef<coda::descriptors::EnumDescriptor*>()'

    if struct.getFields():
      fieldArray = '{0}::Fields'.format(struct.getName())
      self.writeLnFmt('coda::descriptors::FieldDescriptor* {0}::Fields[] = {{', structQualName)
      self.indent()
      for field in struct.getFields():
        self.writeLnFmt('&{0}::Field_{1},', getQualName(struct), field.getName())
      self.unindent()
      self.writeLn('};')
      self.writeLn()
    else:
      fieldArray = 'coda::descriptors::StaticArrayRef<coda::descriptors::FieldDescriptor*>()'

    self.writeLnFmt('const uint32_t {0}::TYPE_ID = {1};', getQualName(struct), struct.getTypeId())
    self.writeLn()

    self.writeLnFmt('coda::descriptors::StructDescriptor {0}::DESCRIPTOR(', getQualName(struct))
    self.indent()
    self.writeLnFmt('"{0}",', structQualName)
    self.writeLnFmt('{0},', struct.getTypeId())
    self.writeLnFmt('&{0}::DEFAULT_INSTANCE,', getQualName(struct))
    self.writeLn('FILE,')
    if struct.getEnclosingType():
      self.writeLnFmt('&{0}::DESCRIPTOR,', getQualName(struct.getEnclosingType()))
    else:
      self.writeLn('NULL,')
    if struct.getBaseType():
      self.writeLnFmt('&{0}::DESCRIPTOR,', getQualName(struct.getBaseType()))
    else:
      self.writeLn('NULL,')
    optionId = self.optionIdOf(struct.getOptions())
    if optionId >= 0:
      self.writeLnFmt('_options{0},', optionId)
    else:
      self.writeLn('coda::descriptors::StructOptions::DEFAULT_INSTANCE,')
    self.writeLn(structArray + ',')
    self.writeLn(enumArray + ',')
    self.writeLn(fieldArray + ',')
    self.writeLnFmt('&coda::descriptors::StaticObjectBuilder<{0}>::create', structQualName)
    self.unindent()
    self.writeLn(');')
    self.writeLn()
    self.unindent()

    self.writeLnFmt('{0} {0}::DEFAULT_INSTANCE;', getQualName(struct))
    self.writeLn()

  def endStruct(self, fd, struct):
    self.indent()

  def genStructConstructor(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    if self.requiresOutOfLineConstructor(struct):
      self.writeLnFmt('{0}::{1}()', getQualName(struct), struct.getName())
      self.indent()
      delim = ':'
      for field in struct.getFields():
        value = self.defaultValueOf(field.getType())
        if value:
          self.writeLnFmt('{0} _{1}({2})', delim, field.getName(), value)
          delim = ','
      self.unindent()
      self.writeLn('{')
      self.indent()
      self.unindent()
      self.writeLn('}')
      self.writeLn()

  def genStructStdMethods(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    structQualName = getQualName(struct)

    # Compute the name of the nearest ancestor class that has fields.
    base = struct.getBaseType()
    while base and not base.getFields():
      base = base.getBaseType()
    if base:
      baseName = self.formatTypeName(base)
    else:
      baseName = 'coda::runtime::Object'

    # Equality comparison
    if struct.getFields():
      self.writeLnFmt('bool {0}::equals(const coda::runtime::Object* other) const {{',
          structQualName)
      self.indent()
      self.writeIndent()
      self.write('return ')
      if struct.getBaseType():
        self.writeFmt('{0}::equals(other)',
            self.formatTypeName(struct.getBaseType()))
      else:
        self.write('other != NULL && descriptor() == other->descriptor()')
      self.indent()
      for field in struct.getFields():
        self.write(' &&\n')
        self.writeIndent()
        self.writeIndent()
        self.write('_{0} == (({1}*) other)->_{0}'.format(
            field.getName(), struct.getName()))
      self.write(';\n')
      self.unindent()
      self.unindent()
      self.writeLn('}')
      self.writeLn()

    # Hashing
    if struct.getFields():
      self.writeLnFmt('size_t {0}::hashValue() const {{', structQualName)
      self.indent()
      self.writeLnFmt('size_t hash = {0}::hashValue();', baseName)
      for field in struct.getFields():
        hashExpr = 'coda::runtime::hash(_{0})'.format(field.getName())
        self.writeLnFmt('coda::runtime::hash_combine(hash, {0});', hashExpr)
      self.writeLn('return hash;')
      self.unindent()
      self.writeLn('}')
      self.writeLn()

    # Freezing
    if struct.getFields():
      self.writeLnFmt('void {0}::freezeImpl() {{', structQualName)
      self.indent()
      if base:
        self.writeLnFmt('{0}::freezeImpl();', baseName)
      for field in struct.getFields():
        fname = field.getName()
        ftype = field.getType()
        self.genValueFreeze('_' + fname, ftype, field.getOptions())
      self.unindent()
      self.writeLn('}')
      self.writeLn()

    # Serialization
    if struct.getBaseType():
      self.writeLnFmt(
          'void {0}::beginWrite(coda::io::Encoder* encoder) const {{', structQualName)
      self.indent()
      if base:
        self.writeLnFmt('{0}::beginWrite(encoder);', baseName)
      self.writeLnFmt('encoder->writeBeginSubtype("{0}", {1});',
          struct.getName(), self.formatTypeKind(struct.getTypeId()))
      self.unindent()
      self.writeLn('}')
      self.writeLn()

    writeableFields = self.getWriteableFields(struct)
    if writeableFields or struct.getBaseType():
      self.writeLnFmt(
          'void {0}::endWrite(coda::io::Encoder* encoder) const {{', structQualName)
      self.indent()
      for field in writeableFields:
        fty = field.getType()
        if isinstance(fty, types.CollectionType):
          self.writeLnFmt('if (!_{0}.empty()) {{', field.getName())
        else:
          self.writeLnFmt('if (has{0}()) {{', self.capitalize(field.getName()))
        self.indent()
        self.writeLnFmt(
            'encoder->writeFieldHeader("{0}", {1});',
            field.getName(), field.getId())
        self.genValueWrite('_' + field.getName(), fty, field.getOptions())
        self.unindent()
        self.writeLn('}')
      if struct.getBaseType():
        self.writeLn('encoder->writeEndSubtype();')
        if base:
          self.writeLnFmt('{0}::endWrite(encoder);', baseName)
      self.unindent()
      self.writeLn('}')
      self.writeLn()

  def isFreezableType(self, ty):
    if ty.typeId() == types.TypeKind.STRUCT:
      return True
    elif ty.typeId() == types.TypeKind.LIST or ty.typeId() == types.TypeKind.SET:
      return self.isFreezableType(ty.getElementType())
    elif ty.typeId() == types.TypeKind.MODIFIED:
      return self.isFreezableType(ty.getElementType())
    elif ty.typeId() == types.TypeKind.MAP:
      return self.isFreezableType(ty.getKeyType()) or self.isFreezableType(ty.getValyeType())
    else:
      return False

  def genValueFreeze(self, var, ftype, options, level=0):
      fkind = ftype.typeId()
      iteratorName = 'it' if level == 0 else 'i' + str(level)
      if fkind == types.TypeKind.LIST:
        if self.isFreezableType(ftype.getElementType()):
          typeName = self.formatType(ftype, False, False)
          self.beginForLoop(typeName, var, iteratorName)
          self.genValueFreeze('(*' + iteratorName + ')', ftype.getElementType(), options, level + 1)
          self.endForLoop()
      elif fkind == types.TypeKind.SET:
        if self.isFreezableType(ftype.getElementType()):
          typeName = self.formatType(ftype, False, False)
          self.beginForLoop(typeName, var, iteratorName)
          self.genValueFreeze('(*' + iteratorName + ')', ftype.getElementType(), options, level + 1)
          self.endForLoop()
      elif fkind == types.TypeKind.MAP:
        if self.isFreezableType(ftype.getKeyType()) or self.isFreezableType(ftype.getValueType()):
          typeName = self.formatType(ftype, False, False)
          self.beginForLoop(typeName, var, iteratorName)
          if self.isFreezableType(ftype.getKeyType()):
            self.genValueFreeze(iteratorName + '->first', ftype.getKeyType(), options, level + 1)
          if self.isFreezableType(ftype.getValueType()):
            self.genValueFreeze(iteratorName + '->second', ftype.getValueType(), options, level + 1)
          self.endForLoop()
      elif fkind == types.TypeKind.MODIFIED:
        self.genValueFreeze(var, ftype.getElementType(), options, level)
      elif fkind == types.TypeKind.STRUCT:
        if options.isNullable():
          self.writeLnFmt('if ({0} && {0}->isMutable()) {{', var)
        else:
          self.writeLnFmt('if ({0}->isMutable()) {{', var)
        self.indent()
        self.writeLnFmt('{0}->freeze();', var)
        self.unindent()
        self.writeLn("}")

  def genValueWrite(self, var, fty, options, level=0):
    iteratorName = 'it' if level == 0 else 'i' + str(level)
    fkind = fty.typeId()
    fixedParam = ', true' if options.isFixed() else ''
    if fkind == types.TypeKind.BOOL:
      self.writeLnFmt("encoder->writeBoolean({0});", var)
    elif fkind == types.TypeKind.INTEGER:
      if options.isFixed():
        self.writeLnFmt("encoder->writeFixed{1}({0});", var, fty.getBits())
      else:
        self.writeLnFmt("encoder->writeInteger({0});", var)
    elif fkind == types.TypeKind.FLOAT:
        self.writeLnFmt("encoder->writeFloat({0});", var)
    elif fkind == types.TypeKind.DOUBLE:
        self.writeLnFmt("encoder->writeDouble({0});", var)
    elif fkind == types.TypeKind.STRING:
        self.writeLnFmt("encoder->writeString({0});", var)
    elif fkind == types.TypeKind.BYTES:
        self.writeLnFmt("encoder->writeBytes({0});", var)
    elif fkind == types.TypeKind.LIST:
      self.writeLnFmt(
          "encoder->writeBeginList({1}, {0}.size(){2});",
          var, self.formatTypeKind(fty.getElementType().typeId()), fixedParam)
      typeName = self.formatType(fty, False, False)
      self.beginForLoop(typeName, var, iteratorName)
      self.genValueWrite('*' + iteratorName, fty.getElementType(), options, level + 1)
      self.endForLoop()
      self.writeLn("encoder->writeEndList();")
    elif fkind == types.TypeKind.SET:
      self.writeLnFmt(
          "encoder->writeBeginSet({1}, {0}.size(){2});",
          var, self.formatTypeKind(fty.getElementType().typeId()), fixedParam)
      typeName = self.formatType(fty, False, False)
      self.beginForLoop(typeName, var, iteratorName)
      self.genValueWrite('*' + iteratorName, fty.getElementType(), options, level + 1)
      self.endForLoop()
      self.writeLn("encoder->writeEndSet();")
    elif fkind == types.TypeKind.MAP:
      self.writeLnFmt("encoder->writeBeginMap({1}, {2}, {0}.size());", var,
          self.formatTypeKind(fty.getKeyType().typeId()),
          self.formatTypeKind(fty.getValueType().typeId()))
      typeName = self.formatType(fty, False, False)
      self.beginForLoop(typeName, var, iteratorName)
      self.genValueWrite(iteratorName + '->first', fty.getKeyType(), options, level + 1)
      self.genValueWrite(iteratorName + '->second', fty.getValueType(), options, level + 1)
      self.endForLoop()
      self.writeLn("encoder->writeEndMap();")
    elif fkind == types.TypeKind.STRUCT:
      self.writeLnFmt("encoder->writeSharedStruct({0});", var)
    elif fkind == types.TypeKind.MODIFIED:
      if fty.isShared():
        assert isinstance(fty.getElementType(), types.StructType)
        self.writeLnFmt("encoder->writeSharedStruct({0});", var)
      else:
        self.genValueWrite(var, fty.getElementType(), options)
    else:
      assert False and 'Illegal type kind'

  def formatOptions(self, opts):
    def setOptionValues(opts, struct):
      if struct.getBaseType():
        setOptionValues(opts, struct.getBaseType())
      for field in struct.getFields():
        if field.isPresent(opts):
          value = field.getValue(opts)
          ftype = field.getType()
          if ftype.typeId() == types.TypeKind.LIST or ftype.typeId() == types.TypeKind.SET:
            for v in value:
              result.append('add{0}({1})'.format(
                  self.capitalize(field.getName()),
                  self.formatValue(ftype.getElementType(), v)))
          if ftype.typeId() == types.TypeKind.MAP:
            for k, v in value.items():
              result.append('put{0}({1}, {2})'.format(
                  self.capitalize(field.getName()),
                  self.formatValue(ftype.getKeyType(), k),
                  self.formatValue(ftype.getValueType(), v)))
          else:
            result.append('set{0}({1})'.format(
                self.capitalize(field.getName()),
                self.formatValue(ftype, value)))

    result = []
    result.append('coda::descriptors::{0}()'.format(opts.descriptor().getName()))
    setOptionValues(opts, opts.descriptor())
    return 'coda::descriptors::freeze(' + '.'.join(result) + ')'

  def beginEnum(self, fd, enum):
    self.writeBanner('{0}', enum.getName())
    if enum.getValues():
      enumPrefix = getQualName(enum).replace('::', '_')
      enumScope = getEnclosingQualName(enum)
      valueArray = '{0}_Values'.format(getQualName(enum))
      for val in enum.getValues():
        self.writeLnFmt(
            'static coda::descriptors::EnumDescriptor::Value {0}_Value_{1}("{1}", {2}{3}_{4});',
            enumPrefix, val.getName(), enumScope, toUpperUnderscore(enum.getName()), val.getName())
      self.writeLn()
      self.writeLnFmt('static coda::descriptors::EnumDescriptor::Value* {0}[] = {{', valueArray)
      self.indent()
      for val in enum.getValues():
        self.writeLnFmt('&{0}_Value_{1},', enumPrefix, val.getName())
      self.unindent()
      self.writeLn('};')
      self.writeLn()
    else:
      valueArray = 'coda::descriptors::StaticArrayRef<coda::descriptors::EnumDescriptor::Value*>()'

    self.writeLnFmt('coda::descriptors::EnumDescriptor {0}_DESCRIPTOR(', enum.getName())
    self.indent(2)
    self.writeLnFmt('"{0}",', enum.getName())
    optionId = self.optionIdOf(enum.getOptions())
    if optionId >= 0:
      self.writeLnFmt('_options{0},', optionId)
    else:
      self.writeLn('coda::descriptors::EnumOptions::DEFAULT_INSTANCE,')
    self.writeLnFmt('{0}', valueArray)

    self.unindent(2)
    self.writeLn(');')

  def endEnum(self, fd, enum):
    '''@type fd: coda.descriptors.FileDescriptor'''
    self.writeLn()

  def endFile(self, fd):
    '@type fd: coda.descriptors.FileDescriptor'

    self.writeBanner('FILE')

    if fd.getStructs():
      structArray = 'FILE_Structs'
      self.writeLn('static coda::descriptors::StructDescriptor* FILE_Structs[] = {')
      self.indent()
      for st in fd.getStructs():
        self.writeLnFmt('&{0}::DESCRIPTOR,', st.getName())
      self.unindent()
      self.writeLn('};')
      self.writeLn()
    else:
      structArray = 'coda::descriptors::StaticArrayRef<coda::descriptors::StructDescriptor*>()'

    if fd.getEnums():
      enumArray = 'FILE_Enums'
      self.writeLn('static coda::descriptors::EnumDescriptor* FILE_Enums[] = {')
      self.indent()
      for en in fd.getEnums():
        self.writeLnFmt('&{0}_DESCRIPTOR,', en.getName())
      self.unindent()
      self.writeLn('};')
      self.writeLn()
    else:
      enumArray = 'coda::descriptors::StaticArrayRef<coda::descriptors::EnumDescriptor*>()'

    self.writeLn('coda::descriptors::StaticFileDescriptor FILE(')
    self.indent(2)
    self.writeLnFmt('"{0}",', fd.getName())
    self.writeLnFmt('"{0}",', fd.getPackage())
    optionId = self.optionIdOf(fd.getOptions())
    if optionId >= 0:
      self.writeLnFmt('_options{0},', optionId)
    else:
      self.writeLn('coda::descriptors::FileOptions::DEFAULT_INSTANCE,')
    self.writeLnFmt('{0},', structArray)
    self.writeLnFmt('{0}', enumArray)
    self.unindent(2)
    self.writeLn(');')
    self.writeLn()
    for ns in self.fileOptions.package.split('::'):
      self.writeLnFmt('}} // namespace {0}', ns)

  def beginForLoop(self, typeName, varName, iteratorName):
    self.writeLnFmt(
        "for ({0}::const_iterator {2} = {1}.begin(), {2}End = {1}.end(); {2} != {2}End; ++{2}) {{",
        typeName, varName, iteratorName)
    self.indent()

  def endForLoop(self):
    self.unindent()
    self.writeLn("}")

def createGenerators(options):
  return (CppHeaderGenerator('cpp', options), CppGenerator('cpp', options))
