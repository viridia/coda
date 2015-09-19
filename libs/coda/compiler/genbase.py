# Base classes for code generation.

from abc import abstractmethod, ABCMeta
import os
import collections
from coda import types
from coda.descriptors import FileOptions, StructOptions, FieldOptions, EnumOptions

def getScopedOption(optionMap, scope, defaultValue=None):
  '''@type fd: coda.descriptors.FileDescriptor
     Function to retrieve a scoped option from an option map.
  '''
  assert isinstance(optionMap, collections.Mapping)
  while True:
    value = optionMap.get(scope)
    if value is not None:
      return value
    if scope == '':
      return defaultValue
    dot = scope.rfind('.')
    if dot < -1:
      scope = ''
    else:
      scope = scope[:dot]

class FileOptionsSummary:
  '''Summary of common file options.'''
  def __init__(self):
    self.package = None
    self.multipleFiles = True
    self.outerClassName = None
    self.out = None

class UniqueOptionsTable:
  def __init__(self):
    self.optionHolders = set()

  def add(self, options):
    self.optionHolders.add(options)

class CodeGenerator(metaclass=ABCMeta):
  '''Base class for code generators.'''

  MUTABLE_TYPES = set([
      types.TypeKind.LIST,
      types.TypeKind.SET,
      types.TypeKind.MAP,
      types.TypeKind.STRUCT])

  def __init__(self, optionScope, options={}):
    self.optionScope = optionScope
    self.indentLevel = 0
    self.options = options

  def setOutputDir(self, outputDir):
    self.outputDir = self.headerOutputDir = outputDir

  def setHeaderOutputDir(self, outputDir):
    self.headerOutputDir = outputDir

  def run(self, fdList):
    '''Given a list of file descriptors, generate a class for each child
       descriptor.'''
    self.allFiles = fdList
    for fd in fdList:
      self._genModule(fd)

  def _genModule(self, fd):
    fileOptions = FileOptionsSummary()
    fileOptions.package = self.getScopedOption(fd.getOptions().getPackage())
    fileOptions.outerClassName = self.getScopedOption(fd.getOptions().getOuterClass())
    fileOptions.filepath = self.getScopedOption(fd.getOptions().getFilepath())
    if not fileOptions.package:
      fileOptions.package = self.formatPackage(fd.getPackage())
    self.genFilesForModule(fd, fileOptions)
    
  def getFileOutputDir(self):
    return self.outputDir

  def genFilesForModule(self, fd, fileOptions):
    '''Generate the output files for a given input file. The default behavior is to generate
       a single output source file for each input file, however generator classes can override
       this behavior.'''
    path = self.calcSourcePath(fd, fileOptions, None)
    path = os.path.join(self.getFileOutputDir(), path)
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
      os.makedirs(dirname)
    self.out = open(path, "w")
    print('Writing', path)
    try:
      self.writeFileContent(fd, fileOptions)
    finally:
      self.out.close()
      self.out = None

  def writeFileContent(self, fd, fileOptions):
    '''@type fd: coda.descriptors.FileDescriptor'''
    self.beginFile(fd, fileOptions)
    self.genHeader(fd)
    self.genImports(fd)
    self.beginDecls(fd)
    for enum in fd.getEnums():
      self.genEnum(fd, enum)
    for struct in fd.getStructs():
      self.genStruct(fd, struct)
    self.endFile(fd)

  def genStruct(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    self.beginStruct(fd, struct)
    self.indent()
    for section in self.getStructSectionOrder():
      section(fd, struct)
    self.unindent()
    self.endStruct(fd, struct)

  def getStructSectionOrder(self):
    '''Return the order in which definitions appear in the generated class.'''
    return (
      self.genStructMemberEnums,
      self.genStructMemberStructs,
      self.genStructFieldDecls,
      self.genStructMetadata,
      self.genStructConstructor,
      self.genStructStdMethods,
      self.genStructFieldAccessors,
      self.genStructMethods)

  def genStructMemberStructs(self, fd, struct):
    '''Generate definitions for member structs of this type.'''
    for st in struct.getStructs():
      self.genStruct(fd, st)

  def genStructMemberEnums(self, fd, struct):
    '''Generate definitions for member enums of this type.'''
    for en in struct.getEnums():
      self.genEnum(fd, en)

  def genStructFieldDecls(self, fd, struct):
    '''Generate definitions for member fields of this type.'''
    for field in struct.getFields():
      self.genFieldDeclaration(fd, struct, field)

  def genStructMetadata(self, fd, struct):
    '''Generate static metadata structures for this type.'''
    pass

  def genStructConstructor(self, fd, struct):
    '''Generate the constructor for this struct type.'''
    pass

  def genStructStdMethods(self, fd, struct):
    'Generate methods for equals, hash, mutability control, and serialization.'
    pass

  def genStructFieldAccessors(self, fd, struct):
    for field in struct.getFields():
      self.genFieldAccessors(fd, struct, field)

  def genStructMethods(self, fd, struct):
    for method in struct.getMethods():
      self.genMethod(fd, struct, method)

  def genEnum(self, fd, enum):
    '''@type fd: coda.descriptors.FileDescriptor
       @type enum: coda.descriptors.EnumType'''
    self.beginEnum(fd, enum)
    self.indent()
    self.unindent()
    self.endEnum(fd, enum)

  def getScopedOption(self, optionMap, defaultValue=None):
    '''@type fd: coda.descriptors.FileDescriptor'''
    return getScopedOption(optionMap, self.optionScope, defaultValue)

  def isFieldWriteable(self, field):
    '''Return true if the given field is writeable.'''
    return (not field.getOptions().isTransient()
      and not field.getOptions().isDeprecated()
      and not self.getScopedOption(field.getOptions().getIgnore()))

  def isFieldPresentable(self, field):
    '''Return true if the given field has a 'present' bit.'''
    return (not isinstance(field.getType(), types.CollectionType)
        and not self.getScopedOption(field.getOptions().getIgnore()))

  def getWriteableFields(self, struct):
    '''Return the list of fields that can be serialized.'''
    return [field for field in struct.getFields()
        if self.isFieldWriteable(field)]

  def getPresentableFields(self, struct):
    '''Return the list of fields that have 'present' bits. This excludes fields
       of collection type.'''
    return [field for field in struct.getFields()
        if self.isFieldPresentable(field)]

  def getTypesUsed(self, fd):
    '''@type fd: coda.descriptors.FileDescriptor'''
    usedTypes = {}

    def findTypes(struct):
      for field in struct.getFields():
        usedTypes[field.getType().key()] = field.getType()
      for st in struct.getStructs():
        findTypes(st)
      for ex in struct.getExtensions():
        usedTypes[ex.getType().key()] = ex.getType()
        usedTypes[ex.getExtends().key()] = ex.getExtends()

    for struct in fd.getStructs():
      findTypes(struct)
    for ex in fd.getExtensions():
      usedTypes[ex.getType().key()] = ex.getType()
      usedTypes[ex.getExtends().key()] = ex.getExtends()
    return usedTypes.values()

  def getFilePackage(self, fd):
    '''@type fd: coda.descriptors.FileDescriptor
       Return the package string for this file, in native form.'''
    package = self.getScopedOption(fd.getOptions().getPackage())
    if not package:
      return self.formatPackage(fd.getPackage())
    return package

  def getDeclPackage(self, decl):
    '''@type decl: coda.descriptors.DeclType
       Return the package string for this declaration, in native form.'''
    while decl.getEnclosingType():
      decl = decl.getEnclosingType()
    return self.getFilePackage(decl.getFile())

  def registerUniqueTypes(self, fd):
    '''Build a table that assigns an integer index to each unique type.'''
    typesUsed = self.getTypesUsed(fd)
    self._typeTable = []
    for ty in typesUsed:
      self._typeTable.append(ty)
    self._typeTable.sort(key=lambda t: t.key())
    self._typeIds = {}
    nextIndex = 0
    for ty in self._typeTable:
      self._typeIds[ty.key()] = nextIndex
      nextIndex += 1

  def getUniqueTypes(self):
    return self._typeTable

  def typeIdOf(self, ty):
    '''Get the index of a type registered with the types table.'''
    return self._typeIds[ty.key()]

  def registerUniqueOptions(self, fd):
    '''@type fd: coda.descriptors.FileDescriptor
       Build a table that assigns an integer index to each unique option holder.'''

    optionHolders = set()

    def findOptions(struct):
      if struct.getOptions() is not StructOptions.defaultInstance():
        optionHolders.add(struct.getOptions())
      for field in struct.getFields():
        if field.getOptions() is not FieldOptions.defaultInstance():
          optionHolders.add(field.getOptions())
      for st in struct.getStructs():
        findOptions(st)
      for enum in struct.getEnums():
        if enum.getOptions() is not EnumOptions.defaultInstance():
          optionHolders.add(enum.getOptions())

    if fd.getOptions() is not FileOptions.defaultInstance():
      optionHolders.add(fd.getOptions())
    for struct in fd.getStructs():
      findOptions(struct)
    for enum in fd.getEnums():
      if enum.getOptions() is not EnumOptions.defaultInstance():
        optionHolders.add(enum.getOptions())

    optionsUsed = sorted(
        [(self.formatOptions(opts), opts) for opts in optionHolders])
    self._optionsTable = []
    self._optionsIds = {}
    nextIndex = 0
    for _, opt in optionsUsed:
      self._optionsTable.append(opt)
      self._optionsIds[opt] = nextIndex
      nextIndex += 1

  def formatOptions(self, opts):
    pass

  def getUniqueOptions(self):
    return self._optionsTable

  def optionIdOf(self, opts):
    '''Get the index of an option holder registered with the types table.'''
    return self._optionsIds.get(opts, -1)

  def indent(self, levels=1):
    self.indentLevel += 2 * levels

  def unindent(self, levels=1):
    self.indentLevel -= 2 * levels

  def write(self, s):
    self.out.write(s)

  def writeIndent(self):
    if self.indentLevel:
      self.out.write(' ' * self.indentLevel)

  def writeLn(self, s=''):
    if s:
      self.writeIndent()
      self.out.write(s)
    self.out.write('\n')

  def writeFmt(self, fmt, *args, **kwargs):
    self.write(fmt.format(*args, **kwargs))

  def writeLnFmt(self, fmt, *args, **kwargs):
    self.writeLn(fmt.format(*args, **kwargs))

  def writeWrapped(self, items, separator=', ', end=''):
    '''Write out a list of items, with line breaks inserted so that line lengths
       do not exceed 80 columns. Takes the current indentation level into
       account.'''
    items = tuple(items)
    line = ''
    sep = ''
    for item in items:
      if line and len(line) + len(sep) + len(item) + self.indentLevel >= 80:
        line += sep
        self.writeIndent()
        self.write(line.strip() + '\n')
        line = ''
      else:
        line += sep
      line += item
      sep = separator
    self.writeIndent()
    self.write(line.strip() + end + '\n')

  @abstractmethod
  def calcSourcePath(self, fd, options, decl):
    '''@type fd: coda.descriptors.FileDescriptor
       @type options: FileOptionsSummary
       Method to calculate the file path to write a descriptor to.'''

  @abstractmethod
  def fileExtension(self):
    'Return the file extension for files created by this generator'

  @abstractmethod
  def formatPackage(self, packageName):
    'Convert the Coda package name from dot-separated into native form.'

  def beginFile(self, fd, fileOptions):
    'Called at the beginning of a new output source file.'

  def genHeader(self, fd):
    'Override to generate a banner at the top of the file.'

  def genImports(self, fd):
    'Override to generate import statements after the banner.'

  def beginDecls(self, fd):
    'Override to generate code after the imports but before the first decl.'

  def endFile(self, fd):
    'Override to generate code at the end of the file, after all decls.'

  @abstractmethod
  def beginStruct(self, fd, struct):
    'Override to generate code at the beginning of a struct decl.'

  def endStruct(self, fd, struct):
    'Override to generate code at the end of a struct decl.'

  @abstractmethod
  def beginEnum(self, fd, enum):
    'Override to generate code at the beginning of an enum decl.'

  def endEnum(self, fd, enum):
    'Override to generate code at the end of an enum decl.'

  def genFieldDeclaration(self, fd, struct, field):
    pass

  def genFieldAccessors(self, fd, struct, field):
    pass

  def genMethod(self, fd, struct, method):
    pass

class AbstractTypeTransform:
  'Provides a framework for operations on type expression'
  @abstractmethod
  def visitType(self, ty, *args):
    return ty

  def visitPrimitiveType(self, *args):
    return self.visitType(*args)

  def visitBooleanType(self, *args):
    return self.visitPrimitiveType(*args)

  def visitIntegerType(self, *args):
    return self.visitPrimitiveType(*args)

  def visitFloatingType(self, *args):
    return self.visitType(*args)

  def visitFloatType(self, *args):
    return self.visitFloatingType(*args)

  def visitDoubleType(self, *args):
    return self.visitFloatingType(*args)

  def visitStringType(self, *args):
    return self.visitPrimitiveType(*args)

  def visitBytesType(self, *args):
    return self.visitPrimitiveType(*args)

  def visitCollectionType(self, *args):
    return self.visitType(*args)

  def visitListType(self, *args):
    return self.visitCollectionType(*args)

  def visitSetType(self, *args):
    return self.visitCollectionType(*args)

  def visitMapType(self, *args):
    return self.visitCollectionType(*args)

  def visitDeclType(self, *args):
    return self.visitType(*args)

  def visitStructType(self, *args):
    return self.visitDeclType(*args)

  def visitEnumType(self, *args):
    return self.visitDeclType(*args)

  def visitModifiedType(self, *args):
    return self.visitType(*args)

  def __call__(self, ty, *args):
    return self.__dispatch[ty.typeId()](ty, *args)

  def __init__(self):
    kinds = types.TypeKind
    self.__dispatch = {
      kinds.BOOL: self.visitBooleanType,
      kinds.INTEGER: self.visitIntegerType,
      kinds.FLOAT: self.visitFloatType,
      kinds.DOUBLE: self.visitDoubleType,
      kinds.STRING: self.visitStringType,
      kinds.BYTES: self.visitBytesType,
      kinds.LIST: self.visitListType,
      kinds.SET: self.visitSetType,
      kinds.MAP: self.visitMapType,
      kinds.STRUCT: self.visitStructType,
      kinds.ENUM: self.visitEnumType,
      kinds.MODIFIED: self.visitModifiedType,
    }
