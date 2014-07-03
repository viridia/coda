# AST analysis

import os
import coda.compiler
from coda import descriptors
from coda import types
from coda.runtime.object import Object
from coda.runtime.typeregistry import TypeRegistry
from collections import defaultdict
from coda.runtime import typemixins

class GenericType(coda.types.Type):
  def __init__(self, typeCtor):
    self.__typeCtor = typeCtor
    self.__numArgs = len(typeCtor.DESCRIPTOR.getFields())

  def getNumArgs(self):
    return self.__numArgs

  def __call__(self, args):
    ty = self.__typeCtor()
    for field, value in zip(self.__typeCtor.DESCRIPTOR.getFields(), args):
      if value is not coda.types.ERROR:
        assert type(value) is not coda.types.Type
        field.setValue(ty, value)
    return ty

  def __str__(self):
    return str(self.__typeCtor)

TYPENAMES = {
  'bool': coda.types.BOOL,
  'i16': coda.types.I16,
  'i32': coda.types.I32,
  'i64': coda.types.I64,
  'float': coda.types.FLOAT,
  'double': coda.types.DOUBLE,
  'string': coda.types.STRING,
  'bytes': coda.types.BYTES,
  'list': GenericType(coda.types.ListType),
  'set': GenericType(coda.types.SetType),
  'map': GenericType(coda.types.MapType),
}

class FileScope(typemixins.DeclTypeMixin):
  '''Helper class used to represent the file-level lookup scope.'''
  def __init__(self, file):
    self._file = file

  def getFullName(self):
    return self._file.getPackage()

  def getFile(self):
    return self._file

class ALLOWED_TYPES:
  LIST_ELEMENT = frozenset([
    types.TypeKind.BOOL,
    types.TypeKind.INTEGER,
    types.TypeKind.FLOAT,
    types.TypeKind.DOUBLE,
    types.TypeKind.STRING,
    types.TypeKind.BYTES,
    types.TypeKind.LIST,
    types.TypeKind.SET,
    types.TypeKind.MAP,
    types.TypeKind.STRUCT,
    types.TypeKind.ENUM,
  ])
  SET_ELEMENT = frozenset([
    types.TypeKind.INTEGER,
    types.TypeKind.STRING,
    types.TypeKind.BYTES,
    types.TypeKind.STRUCT,
    types.TypeKind.ENUM,
  ])
  MAP_KEY = frozenset([
    types.TypeKind.INTEGER,
    types.TypeKind.STRING,
    types.TypeKind.BYTES,
    types.TypeKind.STRUCT,
    types.TypeKind.ENUM,
  ])
  MAP_VALUE = frozenset([
    types.TypeKind.BOOL,
    types.TypeKind.INTEGER,
    types.TypeKind.FLOAT,
    types.TypeKind.DOUBLE,
    types.TypeKind.STRING,
    types.TypeKind.BYTES,
    types.TypeKind.LIST,
    types.TypeKind.SET,
    types.TypeKind.MAP,
    types.TypeKind.STRUCT,
    types.TypeKind.ENUM,
  ])

class Analyzer:
  def __init__(self, errorReporter):
    self.errorReporter = errorReporter
    self.typenames = dict(TYPENAMES)
    self.visibleFiles = defaultdict(set)
    self.imports = {}
    self.types = {} # Dictionary of unique types
    self.filesToAnalyze = []
    self.structsToAnalyze = []
    self.enumsToAnalyze = []
    self.fieldsToAnalyze = []
    self.methodsToAnalyze = []
    self.extensionToAnalyze = []
    self.typeRegistry = TypeRegistry()

  def run(self, asts, importAsts):
    for fileAst in importAsts:
      fd = self.processFile(fileAst)
      self.filesToAnalyze.append((fileAst, fd))

    fdList = []
    for fileAst in asts:
      fd = self.processFile(fileAst)
      fdList.append(fd)
      self.filesToAnalyze.append((fileAst, fd))

    for fileAst, fd in self.filesToAnalyze:
      self.analyzeFile(fileAst, fd)

    for fileAst, fd in self.filesToAnalyze:
      self.computeVisibleFiles(fd)

    # Process the list again now that we've registered all types and extensions
    for structAst, struct in self.structsToAnalyze:
      self.analyzeStruct(structAst, struct)

    for enumAst, enum in self.enumsToAnalyze:
      self.analyzeEnum(enumAst, enum)

    for fieldAst, field, extends, scope in self.extensionToAnalyze:
      self.analyzeExtensionField(fieldAst, field, extends, scope)

    for fileAst, fd in self.filesToAnalyze:
      self.setFileOptions(fileAst, fd)

    for fileAst, fd in self.filesToAnalyze:
      self.setImportPackages(fd)

    for structAst, struct in self.structsToAnalyze:
      self.setStructOptions(structAst, struct)

    for fieldAst, field in self.fieldsToAnalyze:
      self.setFieldOptions(fieldAst, field)

    for methodAst, method in self.methodsToAnalyze:
      self.setMethodOptions(methodAst, method)

    return fdList

  def processFile(self, fileAst):
    assert isinstance(fileAst, coda.compiler.ast.File)
    dirname, filename = os.path.split(fileAst.path)
    fd = descriptors.FileDescriptor()
    fd.setName(filename).setDirectory(dirname).setPackage(fileAst.package)
    self.imports[fileAst.path] = fd

    # Check for invalid package name?

    # Analyze contents of fileAst
    nameprefix = '' if fd.getPackage() is None else fd.getPackage() + '.'

    for extensionAst in fileAst.extensions:
      extensions = self.defineExtension(extensionAst, fd, None)
      fd.getMutableExtensions().extend(extensions)
    for structAst in fileAst.structs:
      struct = self.defineStruct(nameprefix, structAst, fd, None)
      fd.getMutableStructs().append(struct)
    for enumAst in fileAst.enums:
      enum = self.defineEnum(nameprefix, enumAst, fd, None)
      fd.getMutableEnums().append(enum)

    return fd

  def defineStruct(self, prefix, ast, file, enclosingType):
    fullname = prefix + ast.name
    assert isinstance(ast, coda.compiler.ast.StructDef)
    struct = descriptors.StructDescriptor(None)
    struct.setName(ast.name).setFile(file)
    if enclosingType:
      struct.setEnclosingType(enclosingType)
    struct.setSourceLine(ast.location.lineno)

    if ast.extensionRange != (0, 0):
      minExt, maxExt = ast.extensionRange
      assert isinstance(minExt, int)
      assert isinstance(maxExt, int)
      if minExt > maxExt or minExt < 0 or maxExt > 2**32-1:
        self.errorReporter.errorAt(
            ast.typeId.location,
            'Invalid extension range: {0} .. {1}'.format(minExt, maxExt))
      else:
        struct.setMinExtension(minExt)
        struct.setMaxExtension(maxExt)

    self.defineTypeName(fullname, struct, ast.location)

    # Analyze contents of struct
    prefix = fullname + '.'
    for extensionAst in ast.extensions:
      extensions = self.defineExtension(extensionAst, file, struct)
      struct.getMutableExtensions().extend(extensions)
    for structAst in ast.structs:
      st = self.defineStruct(prefix, structAst, file, struct)
      struct.getMutableStructs().append(st)
    for enumAst in ast.enums:
      enum = self.defineEnum(prefix, enumAst, file, struct)
      struct.getMutableEnums().append(enum)
    self.structsToAnalyze.append((ast, struct))
    return struct

  def defineEnum(self, prefix, ast, file, enclosingType):
    fullname = prefix + ast.name
    assert isinstance(ast, coda.compiler.ast.EnumDef)
    desc = descriptors.EnumDescriptor()
    desc.setName(ast.name).setFile(file)
    if enclosingType:
      desc.setEnclosingType(enclosingType)
    desc.setSourceLine(ast.location.lineno)
    self.defineTypeName(fullname, desc, ast.location)
    self.enumsToAnalyze.append((ast, desc))

    nextIndex = 0
    for valueAst in ast.values:
      if valueAst.value is not None:
        nextIndex = valueAst.value.value
      self.defineEnumValue(valueAst, desc, nextIndex)
      nextIndex += 1
    return desc

  def defineExtension(self, ast, file, enclosingType):
    assert isinstance(ast, coda.compiler.ast.StructDef)
    scope = enclosingType
    if not scope:
      scope = FileScope(file)
    result = []
    for fieldAst in ast.fields:
      extField = descriptors.ExtensionField()
      extField.setFile(file)
      extField.setEnclosingType(enclosingType)
      extField.setSourceLine(ast.location.lineno)
      extField.setName(fieldAst.name)
      extField.setId(fieldAst.index)
      self.extensionToAnalyze.append((fieldAst, extField, ast.extends, scope))
      result.append(extField)
    return result

  def analyzeFile(self, fileAst, fd):
    for _, relPath in fileAst.imports:
      importPath = os.path.join(os.path.dirname(fileAst.path), relPath)
#       importFile = self.imports[importPath]
      imp = coda.descriptors.FileDescriptor.Import()
      imp.setPath(importPath)
#       imp.setPackage(importFile.getOptions().getPackage())
      fd.getMutableImports().append(imp)

  def setImportPackages(self, fd):
    for imp in fd.getImports():
      importPath = imp.getPath()
      importFile = self.imports[importPath]
      imp.setPackage(importFile.getOptions().getPackage())

  def computeVisibleFiles(self, fd):
    path = os.path.join(fd.getDirectory(), fd.getName())
    for imp in fd.getImports():
      importPath = imp.getPath()
      importFile = self.imports[importPath]
      self.visibleFiles[path].add(importPath)
      if importPath not in self.visibleFiles:
        visibleSet = self.visibleFiles[importPath]
        self.computeVisibleFiles(importFile)
        self.visibleFiles[path].update(visibleSet)

  def analyzeStruct(self, ast, struct):
    '''@type ast: coda.compiler.ast.StructDef
       @type struct: descriptors.StructType'''
    if ast.typeId is not None:
      if isinstance(ast.typeId, coda.compiler.ast.Ident):
        enum, _, value = ast.typeId.value.rpartition('.')
        if not enum:
          self.errorReporter.errorAt(
              ast.typeId.location,
              'Incorrect formatter for type ID: {0}'.format(ast.typeId))
          return
        enumTy = self.lookupTypeName(enum, struct, ast.typeId.location)
        if enumTy:
          if enumTy.typeId() != types.TypeKind.ENUM:
            self.errorReporter.errorAt(
                ast.typeId.location,
                'Type id is not a number \'{0}\''.format(ast.typeId))
            return
          enumVal = enumTy.getValue(value)
          if enumVal is None:
            self.errorReporter.errorAt(
                ast.typeId.location,
                'Unknown enumeration value \'{0}\''.format(ast.typeId))
            return
          assert enumVal.getValue() is not None
          struct.setTypeId(enumVal.getValue())
      else:
        struct.setTypeId(ast.typeId)
    if ast.baseType:
      assert struct.hasTypeId()
      assert struct.getTypeId() is not None
      baseType = self.getType(ast.baseType, struct)
      if baseType is types.ERROR:
        return baseType
      if baseType is not None and not isinstance(
          baseType, descriptors.StructType):
        self.errorReporter.errorAt(
            ast.baseType.location,
            'Base type \'{0}\' is not a struct'.format(ast.baseType.name))
        return baseType
      if not baseType.hasTypeId():
        self.errorReporter.errorAt(
            ast.baseType.location,
            'Base type \'{0}\' must declare a type id to be inheritable'.format(ast.baseType.name))
        return types.ERROR
      struct.setBaseType(baseType)
      extensibleBase = self.getExtensibleBase(baseType)
      while baseType.hasBaseType():
        baseType = baseType.getBaseType()
      typeForId = self.typeRegistry.getSubtype(baseType, struct.getTypeId())
      if typeForId:
        self.errorReporter.errorAt(
            ast.location,
            'Attempt to register type {0} with ID {1} but it is already used by {2}'.format(
                ast.name, struct.getTypeId(), typeForId.getName()))
        return types.ERROR
      else:
        self.typeRegistry.addSubtype(struct)

      if struct.hasMinExtension() and extensibleBase:
        self.errorReporter.errorAt(
            ast.location,
            'Struct {0} cannot override the extension range of base class {1}'.format(
                ast.name, extensibleBase.getName()))
        return types.ERROR

    for fieldAst in sorted(ast.fields, key = lambda fld: fld.index):
      self.defineField(fieldAst, struct)
    for methodAst in ast.methods:
      self.defineMethod(methodAst, struct)

  def analyzeExtensionField(self, ast, field, extends, scope):
    struct = self.getType(extends, scope)
    if not struct or struct is types.ERROR:
      return types.ERROR
    extensibleStruct = self.getExtensibleBase(struct)
    if not extensibleStruct:
      self.errorReporter.errorAt(
          ast.location,
          'No extension range defined for struct {0}.'.format(struct.getName()))
      return
    struct = extensibleStruct
    field.setExtends(struct)
    field.setType(self.getType(ast.fieldType, scope))

    if not struct.hasMinExtension():
      self.errorReporter.errorAt(
          ast.location,
          'No extension range defined for struct {0}.'.format(struct.getName()))
    elif ast.index < struct.getMinExtension() or ast.index > struct.getMaxExtension():
      self.errorReporter.errorAt(
          ast.location,
          'Extension ID {0} does not fall within the allowed extension range '
          'for struct {1}: {2}..{3}.'.format(
              ast.index, struct.getName(), struct.getMinExtension(), struct.getMaxExtension()))
    elif self.typeRegistry.getExtension(struct, ast.index):
      self.errorReporter.errorAt(
          ast.location,
          'Extension ID {0} for type {1} is already in use.'.format(
              ast.index, struct.getName()))
    else:
      self.typeRegistry.addExtension(field)

  def getExtensibleBase(self, struct):
    while True:
      if struct.hasMinExtension():
        return struct
      elif struct.hasBaseType():
        struct = struct.getBaseType()
      else:
        return None

  def defineField(self, ast, struct):
    '''@type ast: ast.StructDef.Field
       @type struct: descriptors.StructType'''
    struct.checkMutable()
    assert isinstance(ast, coda.compiler.ast.StructDef.Field)

    if struct.getFieldById(ast.index) is not None:
      assert ast.location
      self.errorReporter.errorAt(
          ast.location,
          'Field with index {0} already defined.'.format(ast.index))
      return

    if struct.getField(ast.name) is not None:
      self.errorReporter.errorAt(
          ast.location,
          'Field with name {0} already defined.'.format(ast.name))
      return

    if struct.hasMaxExtension():
      assert struct.hasMaxExtension()
      if ast.index >= struct.getMinExtension() and ast.index <= struct.getMaxExtension():
        self.errorReporter.errorAt(
            ast.location,
            'Field index {0} falls within the extension range.'.format(ast.index))

    struct.checkMutable()
    field = struct.defineField(
        ast.name,
        ast.index,
        self.getType(ast.fieldType, struct))
    self.fieldsToAnalyze.append((ast, field))

  def defineMethod(self, ast, struct):
    '''@type ast: ast.StructDef.Method
       @type struct: descriptors.StructType'''
    struct.checkMutable()
    assert isinstance(ast, coda.compiler.ast.StructDef.Method)

    if ast.index is not None and struct.getFieldById(ast.index) is not None:
      assert ast.location
      self.errorReporter.errorAt(
          ast.location,
          'Field with index {0} already defined'.format(ast.index))
      return

    if struct.getField(ast.name) is not None:
      self.errorReporter.errorAt(
          ast.location,
          'Field with name {0} already defined'.format(ast.name))
      return

    paramList = []
    for p in ast.params:
      paramType = self.getType(p.type, struct)
      param = descriptors.StructDescriptor.Param().setName(ast.name).setType(paramType)
      paramList.append(param)
    struct.checkMutable()
    method = struct.defineMethod(
        ast.name,
        ast.index,
        paramList,
        self.getType(ast.returnType, struct))
    self.methodsToAnalyze.append((ast, method))

  def analyzeEnum(self, ast, enum):
    '''@type ast: coda.compiler.ast.EnumDef
       @type enum: descriptors.EnumType'''

  def defineEnumValue(self, ast, enum, index):
    '''@type ast: ast.StructDef.Field
       @type struct: descriptors.StructType'''
    assert isinstance(ast, coda.compiler.ast.EnumDef.Value)

    if enum.getValue(ast.name) is not None:
      self.errorReporter.errorAt(
          ast.location,
          'Value with name {0} already defined'.format(ast.name))
      return

    value = descriptors.EnumType.Value()
    value.setName(ast.name)
    value.setValue(index)
#   field.setSourceLine(ast.location.lineno)
    enum.addValue(value)

  def setFileOptions(self, ast, fd):
    '''@type ast: coda.compiler.ast.File
       @type struct: descriptors.FileDescriptor'''
    if ast.options:
      optionHolder = fd.getMutableOptions()
      for option in ast.options:
        self.setOption(
            optionHolder, option, descriptors.FileOptions)
      optionHolder.freeze()

  def setStructOptions(self, ast, struct):
    '''@type ast: coda.compiler.ast.StructDef
       @type struct: descriptors.StructType'''
    if ast.options:
      optionHolder = struct.getMutableOptions()
      for option in ast.options:
        self.setOption(optionHolder, option, descriptors.StructOptions)
      optionHolder.freeze()
      if (struct.getOptions().isShared()
          and struct.hasBaseType()
          and not struct.getBaseType().getOptions().isShared()):
        self.errorReporter.errorAt(
            ast.location,
            'Type {0} cannot be a shared type, because it is a subtype of a non-shared type.'
            .format(struct.getName()))
      if (struct.getOptions().isReference()
          and struct.hasBaseType()
          and not struct.getBaseType().getOptions().isReference()):
        self.errorReporter.errorAt(
            ast.location,
            'Type {0} cannot be a reference type, because it is a subtype of a non-reference type.'
            .format(struct.getName()))

  def setFieldOptions(self, ast, field):
    '''@type ast: coda.compiler.ast.StructDef.Field
       @type field: descriptors.StructType.Field'''
    if ast.options:
      optionHolder = field.getMutableOptions()
      for option in ast.options:
        self.setOption(optionHolder, option, descriptors.FieldOptions)
      optionHolder.freeze()

  def setMethodOptions(self, ast, method):
    '''@type ast: coda.compiler.ast.StructDef.Method
       @type field: descriptors.StructType.Method'''
    if ast.options:
      optionHolder = method.getMutableOptions()
      for option in ast.options:
        self.setOption(optionHolder, option, descriptors.MethodOptions)
      optionHolder.freeze()

  def setOption(self, optionHolder, option, optionClass):
    field = optionHolder.descriptor().findField(option.name)
    if not field:
      bestWord = None
      bestDist = 5
      for field in optionHolder.descriptor().getFields():
        dist = levenshtein(field.getName(), option.name)
        if dist < bestDist:
          bestDist = dist
          bestWord = field.getName()
      if bestWord:
        self.errorReporter.errorAt(
            option.location,
            "Unknown option '{0}', did you mean '{1}'?".format(option.name, bestWord))
      else:
        self.errorReporter.errorAt(
            option.location, "Unknown option '{0}'".format(option.name))
    else:
      ftype = field.getType()
      if ftype.typeId() == types.TypeKind.MAP:
        keyType = ftype.getKeyType()
        if isinstance(keyType, types.CollectionType):
          self.errorReporter.errorAt(
              option.location,
              "Invalid key type for option '{0}:{1}'.".format(option.name, option.scope))
        valueType = ftype.getValueType()
        scopeMap = field.getMutableValue(optionHolder)
        if scopeMap is Object.EMPTY_MAP:
          scopeMap = {}
          field.setValue(optionHolder, scopeMap)
        if option.scope in scopeMap:
          self.errorReporter.errorAt(
              option.location,
              "Option '{0}:{1}' has already been set".format(option.name, option.scope))
        else:
          value = coerceValue(valueType, option.value)
          if option.scope is None:
            option.scope = ''
          scopeMap[option.scope] = value
      elif option.scope:
        self.errorReporter.errorAt(
            option.location, "Option '{0}' is not scoped".format(option.name))
      else:
        field.setValue(optionHolder, coerceValue(ftype, option.value))

  def getType(self, typeAst, scope):
    if isinstance(typeAst, coda.compiler.ast.TypeName):
      ty = self.lookupTypeName(typeAst.name, scope, typeAst.location)
      if ty is None:
        return types.ERROR
      if isinstance(ty, GenericType):
        self.errorReporter.errorAt(
            typeAst.location,
            'Missing type parameters for type \'{0}\''.format(typeAst))
      return ty
    elif isinstance(typeAst, coda.compiler.ast.ModifiedType):
      base = self.getType(typeAst.base, scope)
      if not base or base is types.ERROR:
        return types.ERROR
      if base.typeId() != types.TypeKind.STRUCT:
        self.errorReporter.errorAt(
            typeAst.location, 'Type modifiers can only be applied to struct types')
        return types.ERROR
      ty = types.ModifiedType()
      assert type(base) is not types.Type
      ty.setElementType(base)
      if typeAst.const:
        ty.setConst(True)
      if typeAst.shared:
        ty.setShared(True)
      return ty
    elif isinstance(typeAst, coda.compiler.ast.SpecializedType):
      args = []
      for argAst in typeAst.args:
        argType = self.getType(argAst, scope)
        if argType is None or argType is types.ERROR:
          return types.ERROR
        args.append(argType)

      assert isinstance(typeAst.base, coda.compiler.ast.TypeName)
      genericType = self.lookupTypeName(
          typeAst.base.name, scope, typeAst.base.location)
      if genericType is None or genericType is types.ERROR:
        return types.ERROR
      if not isinstance(genericType, GenericType):
        self.errorReporter.errorAt(
            typeAst.location,
            'Type \'{0}\' does not have type parameters'.format(
                typeAst.base.location))
        return types.ERROR
      if len(args) != genericType.getNumArgs():
        self.errorReporter.errorAt(
            typeAst.location,
            'Incorrect number of type parameters for \'{0}\': ' +
            'found {1}, expected {2}'.format(
                typeAst.base.name, len(args), genericType.getNumArgs()))
        return types.ERROR

      ty = genericType(args) #.freeze()
      if ty is types.ERROR:
        return ty
      elif ty.typeId() == types.TypeKind.LIST:
        elemType = self.stripModifiers(ty.getElementType())
        if elemType.typeId() not in ALLOWED_TYPES.LIST_ELEMENT:
          self.errorReporter.errorAt(typeAst.location,
              'Lists of type \'{0}\' are not permitted  '.format(ty.getElementType().getName()))
      elif ty.typeId() == types.TypeKind.SET:
        elemType = self.stripModifiers(ty.getElementType())
        if elemType.typeId() not in ALLOWED_TYPES.SET_ELEMENT:
          self.errorReporter.errorAt(typeAst.location,
              'Sets of type \'{0}\' are not permitted  '.format(ty.getElementType().getName()))
      elif ty.typeId() == types.TypeKind.MAP:
        keyType = self.stripModifiers(ty.getKeyType())
        valueType = self.stripModifiers(ty.getValueType())
        if keyType.typeId() not in ALLOWED_TYPES.MAP_KEY:
          self.errorReporter.errorAt(typeAst.location,
              'Map keys of type \'{0}\' are not permitted  '.format(ty.getElementType().getName()))
        elif valueType.typeId() not in ALLOWED_TYPES.MAP_VALUE:
          self.errorReporter.errorAt(typeAst.location,
              'Map values of type \'{0}\' are not permitted  '.format(
                  ty.getElementType().getName()))
      return self.types.setdefault(ty.key(), ty)
    else:
      self.errorReporter.errorAt(
          typeAst.location, 'Unknown type \'{0}\''.format(typeAst))
      return types.ERROR

  def stripModifiers(self, ty):
    while isinstance(ty, types.ModifiedType):
      ty = ty.getElementType()
    return ty

  def lookupTypeName(self, name, scope, location):
    '''Look up a type by name. Report an error and return None if the
       type name could not be found.
       @type name: string
       @type scope: typemixins.DeclTypeMixin'''
    ty = self.typenames.get(name)
    if ty is None and scope:
      prefix = scope.getFullName()
      while True:
        ty = self.typenames.get(prefix + '.' + name)
        if ty is not None: break
        dot = prefix.rfind('.')
        if dot < 0:
          break
        prefix = prefix[:dot]

    if ty is None:
      bestWord = None
      bestDist = 5
      for typename in self.typenames.keys():
        if typename.endswith('.' + name):
          bestWord = typename
          bestDist = 0
          break
        elif typename.endswith(name):
          bestWord = typename
          bestDist = 1
        else:
          dist = levenshtein(typename, name)
          if dist < bestDist:
            bestDist = dist
            bestWord = typename
      if bestWord:
        self.errorReporter.errorAt(
            location,
            'Unknown type \'{0}\', did you mean \'{1}\'?'.format(
                name, bestWord))
      else:
        self.errorReporter.errorAt(
            location, 'Unknown type \'{0}\''.format(name))
      return None
    if scope and isinstance(ty, types.DeclType):
      srcPath = self.getFilePathForType(scope)
      dstPath = self.getFilePathForType(ty)
      if dstPath != srcPath and dstPath not in self.visibleFiles[srcPath]:
        self.errorReporter.errorAt(
            location,
            'Type \'{0}\' is defined in file \'{1}\', which was not included by \'{2}\'.'.format(
                name, dstPath, srcPath))
    return ty

  def getFilePathForType(self, ty):
    if isinstance(ty, FileScope):
      file = ty.getFile()
      return os.path.join(file.getDirectory(), file.getName())
    if isinstance(ty, types.DeclType):
      topLevelType = ty
      while topLevelType.getEnclosingType() is not None:
        topLevelType = topLevelType.getEnclosingType()
      file = topLevelType.getFile()
      if file:
        return os.path.join(file.getDirectory(), file.getName())
    return None

  def defineTypeName(self, name, sym, location):
    assert location
    if name in self.typenames:
      self.errorReporter.errorAt(location,
          "Typename '{0}' already defined".format(name))
      return
    self.typenames[name] = sym

def coerceValue(toType, value):
  if toType.typeId() == types.TypeKind.BOOL:
    if isinstance(value, coda.compiler.ast.BooleanValue):
      return value.value
    raise TypeError('Cannot convert {0} to boolean'.format(value))
  elif toType.typeId() == types.TypeKind.INTEGER:
    if isinstance(value, coda.compiler.ast.IntegerValue):
      return value.value
    raise TypeError('Cannot convert {0} to int'.format(value))
  elif (toType.typeId() == types.TypeKind.FLOAT or
      toType.typeId() == types.TypeKind.DOUBLE):
    assert False, "Float constants not implemented"
#     if isinstance(value, coda.compiler.ast.FloatValue):
#       return value.value
#     raise TypeError('Cannot convert {0} to float'.format(value))
  elif toType.typeId() == types.TypeKind.STRING:
    if isinstance(value, coda.compiler.ast.StringValue):
      return value.value
    raise TypeError('Cannot convert {0} to string'.format(value))
  elif toType.typeId() == types.TypeKind.BYTES:
    assert False, "Bytes constants not implemented"
#     if type(value) == bytes:
#       return value
#     raise TypeError('Cannot convert {0} to bytes'.format(value))
  elif toType.typeId() == types.TypeKind.LIST:
    if isinstance(value, coda.compiler.ast.ListValue):
      return tuple([coerceValue(toType.getElementType(), el) for el in value.value])
    raise TypeError('Cannot convert {0} to list'.format(value))
  else:
    raise TypeError('Cannot convert {0} to {1}'.format(value, str(toType)))

def levenshtein(s1, s2):
  if len(s1) < len(s2):
    return levenshtein(s2, s1)

  # len(s1) >= len(s2)
  if len(s2) == 0:
    return len(s1)

  previous_row = range(len(s2) + 1)
  for i, c1 in enumerate(s1):
    current_row = [i + 1]
    for j, c2 in enumerate(s2):
      insertions = previous_row[j + 1] + 1
      # j+1 instead of j since previous_row and current_row are one character longer than s2
      deletions = current_row[j] + 1
      substitutions = previous_row[j] + (c1 != c2)
      current_row.append(min(insertions, deletions, substitutions))
    previous_row = current_row

  return previous_row[-1]
