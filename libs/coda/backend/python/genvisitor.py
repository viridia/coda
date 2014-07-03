from . import gen
from coda import types

class Python3VisitorGenerator(gen.Python3Generator):
  def __init__(self, options):
    super().__init__(options)
    self.visitorNames = set(cls.strip() for cls in options.getOption('visitor').split(','))

  def calcSourcePath(self, fd, options, decl):
    '''@type fd: coda.descriptors.FileDescriptor
       @type options: FileOptions
       Method to calculate the file path to write a descriptor to.'''
    return self.calcSourcePathWithoutExtension(fd, options, decl) + 'visitor.py'

  def genFilesForModule(self, fd, options):
    # Override to only generate a visitor if it contains one of the requested classes
    self.baseClasses = []
    def collectVisitorRoots(prefix, structs):
      for st in structs:
        name = prefix + '.' + st.getName()
        if name in self.visitorNames:
          self.baseClasses.append(st)
        collectVisitorRoots(name, st.getStructs())

    collectVisitorRoots(fd.getPackage(), fd.getStructs())
    if self.baseClasses:
      super().genFilesForModule(fd, options)

  def genImports(self, fd):
    '''@type fd: coda.descriptors.FileDescriptor'''
    #self.writeLn('import coda.runtime')
    # Generate an import to the descriptor module
#     package = self.getScopedOption(fd.getOptions().getPackage(), None)
#     if package:
#       self.writeImport(package)
#     self.writeLn()

  def genEnum(self, fd, en):
    pass

  def genStruct(self, fd, struct):
    if struct in self.baseClasses:
      super().genStruct(fd, struct)

  def getStructSectionOrder(self):
    '''Return the order in which definitions appear in the generated class.'''
    return (
      self.genStructVisitorMethods,
      self.genStructVistorDispatcher)

  def beginStruct(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    # Attempt to locate all structs that inherit from this one
    self.subtypes = []
    def findInheritingStructs(structs):
      for st in structs:
        base = st.getBaseType()
        while base:
          if base == struct:
            self.subtypes.append(st)
            break
          base = base.getBaseType()
        findInheritingStructs(st.getStructs())

    for file in self.allFiles:
      findInheritingStructs(file.getStructs())

    self.genStructVisitorClassHeader(fd, struct)

  def genStructVisitorClassHeader(self, fd, struct):
    self.writeLn('# ' + '=' * 77)
    self.writeLnFmt('# {0}', self.visitorClassName(struct))
    self.writeLn('# ' + '=' * 77)
    self.writeLn()
    self.writeLnFmt('class {0}:', self.visitorClassName(struct))

  def genStructVisitorMethods(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    valueName = self.getValueName(struct)
    self.writeLnFmt('def {0}(self, {1}, *args):', self.getVisitorMethodName(struct), valueName)
    self.indent()
    for field in struct.getFields():
      if not field.getOptions().isNovisit():
        self.genVisitField(fd, struct, field, valueName)
    self.writeLnFmt('return {0}', valueName)
    self.unindent()
    self.writeLn()

    self.writeLnFmt('def visitUnknown{1}(self, {0}, *args):', valueName, struct.getName())
    self.indent()
    self.writeLnFmt("assert False, 'Unknown {0} type \\\'' + type({1}).__name__ + '\\\' with id: ' + str({1}.typeId())",
        struct.getName(), valueName)
    self.unindent()
    self.writeLn()

    for subtype in self.subtypes:
      self.genVisitMethod(fd, struct, subtype, valueName)

  def genVisitMethod(self, fd, struct, subtype, valueName):
    self.writeLnFmt('def {0}(self, {1}, *args):', self.getVisitorMethodName(subtype), valueName)
    self.indent()
    visitable = [field for field in subtype.getFields() if not field.getOptions().isNovisit()]
    for field in visitable:
      self.genVisitField(fd, struct, field, valueName)
    self.writeLnFmt('return self.{0}({1}, *args)',
        self.getVisitorMethodName(subtype.getBaseType()), valueName)
    self.unindent()
    self.writeLn()

  def genVisitField(self, fd, struct, field, valueName):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    fieldType = field.getType()
    fmtParams = {
        'struct': struct.getName(),
        'field': self.capitalize(field.getName()),
        'value': valueName
    }
    if fieldType.typeId() == types.TypeKind.MODIFIED:
      fieldType = fieldType.getElementType()
    if fieldType.typeId() == types.TypeKind.STRUCT and self.isSubType(fieldType, struct):
      if field.getOptions().isNullable():
        self.writeLnFmt('if {value}.has{field}() and {value}.get{field}():', **fmtParams)
      else:
        self.writeLnFmt('if {value}.has{field}():', **fmtParams)
      self.indent()
      self.writeLnFmt('self.traverse{struct}({value}.get{field}(), *args)', **fmtParams)
      self.unindent()
    elif fieldType.typeId() == types.TypeKind.LIST:
      if self.isSubType(fieldType.getElementType(), struct):
        self.writeLnFmt('for item in {value}.get{field}():', **fmtParams)
        self.indent()
        self.writeLnFmt('self.traverse{struct}(item, *args)', **fmtParams)
        self.unindent()
    elif fieldType.typeId() == types.TypeKind.SET:
      if self.isSubType(fieldType.getElementType(), struct):
        self.writeLnFmt('for item in {value}.get{field}():', **fmtParams)
        self.indent()
        self.writeLnFmt('self.traverse{struct}(item, *args)', **fmtParams)
        self.unindent()
    elif fieldType.typeId() == types.TypeKind.MAP:
      if self.isSubType(fieldType.getKeyType(), struct):
        self.writeLnFmt('for item in {value}.get{field}().keys():', **fmtParams)
        self.indent()
        self.writeLnFmt('self.traverse{struct}(item, *args)', **fmtParams)
        self.unindent()
      if self.isSubType(fieldType.getValueType(), struct):
        self.writeLnFmt('for item in {value}.get{field}().values():', **fmtParams)
        self.indent()
        self.writeLnFmt('self.traverse{struct}(item, *args)', **fmtParams)
        self.unindent()

  def genStructVistorDispatcher(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    self.writeLnFmt('def traverse{0}(self, value, *args):', struct.getName())
    self.indent()
    self.writeLnFmt(
        'result = self.__dispatch.get(value.typeId(), self.visitUnknown{0})(value, *args)',
        struct.getName())
    self.writeLnFmt('self.validate{0}Result(value, result)', struct.getName())
    self.writeLn('return result')
    self.unindent()
    self.writeLn()

    self.writeLnFmt('def traverse{0}List(self, valueList, *args):', struct.getName())
    self.indent()
    self.writeLnFmt(
        'return [self.traverse{0}(value, *args) for value in valueList]', struct.getName())
    self.unindent()
    self.writeLn()

    self.writeLnFmt('def validate{0}Result(self, value, result):', struct.getName())
    self.indent()
    self.writeLn('pass')
    self.unindent()
    self.writeLn()

    # Dispatch function (call operator)
    self.writeLnFmt('def __call__(self, value, *args):')
    self.indent()
    self.writeLnFmt(
        'return self.__dispatch.get(value.typeId(), self.visitUnknown{0})(value, *args)',
        struct.getName())
    self.unindent()
    self.writeLn()

    # Constructor - initializes dispatch table
    self.writeLnFmt('def __init__(self):')
    self.indent()
    self.writeLn('super().__init__()')
    self.writeLn('self.__dispatch = {')
    self.indent()
    self.writeLnFmt('{0}: self.{1},', struct.getTypeId(), self.getVisitorMethodName(struct))
    for subtype in self.subtypes:
      self.writeLnFmt('{0}: self.{1},', subtype.getTypeId(), self.getVisitorMethodName(subtype))
    self.unindent()
    self.writeLn('}')
    self.unindent()
    self.writeLn()

  def visitorClassName(self, struct):
    return struct.getName() + "Visitor"

  def endFile(self, fd):
    pass

  def isSubType(self, ty, base):
    if ty.typeId() == types.TypeKind.MODIFIED:
      ty = ty.getElementType()
    if ty.typeId() != types.TypeKind.STRUCT:
      return False
    while ty:
      if ty is base:
        return True;
      elif ty.hasBaseType():
        ty = ty.getBaseType()
      else:
        break
    return False

  def getVisitorMethodName(self, struct):
    name = struct.getName()
    while struct.getEnclosingType():
      struct = struct.getEnclosingType()
      name = struct.getName() + name
    return 'visit' + name

  def getValueName(self, struct):
    name = self.decapitalize(struct.getName())
    st = struct
    while name == struct.getName() or name == 'args' or\
          name == 'item' or name in self.RESERVED_WORDS:
      if st.getBaseType():
        st = st.getBaseType()
        name = self.decapitalize(struct.getBaseType().getName())
      else:
        return 'value'
    return name
