from . import genvisitor
from coda import types

class Python3TransformGenerator(genvisitor.Python3VisitorGenerator):
  def __init__(self, options):
    super().__init__(options)
    self.visitorNames = set(cls.strip() for cls in options.getOption('transform').split(','))

  def genStruct(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    self.mutating = True
    super().genStruct(fd, struct)

    self.mutating = False
    super().genStruct(fd, struct)

  def calcSourcePath(self, fd, options, decl):
    '''@type fd: coda.descriptors.FileDescriptor
       @type options: FileOptions
       Method to calculate the file path to write a descriptor to.'''
    return self.calcSourcePathWithoutExtension(fd, options, decl) + 'transform.py'

  def genStructVisitorClassHeader(self, fd, struct):
    self.writeLn('# ' + '=' * 77)
    self.writeLnFmt('# {0}', self.visitorClassName(struct))
    self.writeLn('# ' + '=' * 77)
    self.writeLn()
    if self.mutating:
      self.writeLnFmt('class {0}Transform:', struct.getName())
    else:
      self.writeLnFmt('class {0}NonMutatingTransform({0}Transform):', struct.getName())

  def genStructVisitorMethods(self, fd, struct):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType'''
    if self.mutating:
      super().genStructVisitorMethods(fd, struct)
    else:
      valueName = self.getValueName(struct)
      for subtype in self.subtypes:
        self.genVisitMethod(fd, struct, subtype, valueName)

      self.writeLn('@staticmethod')
      self.writeLn('def _copyOnChange(oldValue, newValue):')
      self.indent()
      self.writeLn('if oldValue is newValue:')
      self.indent()
      self.writeLn('return oldValue.shallowCopy()')
      self.unindent()
      self.writeLn('return newValue')
      self.unindent()
      self.writeLn()

  def genStructVistorDispatcher(self, fd, struct):
    if self.mutating:
      super().genStructVistorDispatcher(fd, struct)

  def genVisitMethod(self, fd, struct, subtype, valueName):
    visitable = [field for field in subtype.getFields()
        if not field.getOptions().isNovisit() and self.isTransformableField(struct, field)]
    if not self.mutating and len(visitable) == 0:
      return
    self.writeLnFmt('def {0}(self, {1}, *args):', self.getVisitorMethodName(subtype), valueName)
    self.indent()
    fmtParams = {
        'struct': struct.getName(),
        'value': valueName,
        'newValue': 'new' + self.capitalize(valueName),
        'superName': self.getVisitorMethodName(subtype.getBaseType())
    }
    visitable = [field for field in subtype.getFields()
        if not field.getOptions().isNovisit() and self.isTransformableField(struct, field)]
    if self.mutating:
      for field in visitable:
        self.genVisitField(fd, struct, field, valueName)
      self.writeLnFmt('return self.{superName}({value}, *args)', **fmtParams)
    else:
      self.writeLnFmt('{newValue} = self.{superName}({value}, *args)', **fmtParams)
      for field in visitable:
        self.genVisitFieldNonMutating(fd, struct, field, valueName)
      self.writeLnFmt('return {newValue}', **fmtParams)
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
      self.writeLnFmt('{value}.set{field}(self.traverse{struct}({value}.get{field}(), *args))',
          **fmtParams)
      self.unindent()
    elif fieldType.typeId() == types.TypeKind.LIST:
      if self.isSubType(fieldType.getElementType(), struct):
        self.writeLnFmt('if len({value}.get{field}()) > 0:', **fmtParams)
        self.indent()
        self.writeLnFmt(
            '{value}.set{field}([self.traverse{struct}(item, *args) for item in {value}.get{field}()])',
            **fmtParams)
        self.unindent()
    elif fieldType.typeId() == types.TypeKind.SET:
      if self.isSubType(fieldType.getElementType(), struct):
        self.writeLnFmt('if len({value}.get{field}()) > 0:', **fmtParams)
        self.indent()
        self.writeLnFmt(
            '{value}.set{field}(set(self.traverse{struct}(item, *args) for item in {value}.get{field}()))',
            **fmtParams)
        self.unindent()
    elif fieldType.typeId() == types.TypeKind.MAP:
      visitKeys = self.isSubType(fieldType.getKeyType(), struct)
      visitValues = self.isSubType(fieldType.getValueType(), struct)
      if visitKeys or visitValues:
        self.writeLnFmt('if len({value}.get{field}()) > 0:', **fmtParams)
      if visitKeys and visitValues:
        self.indent()
        self.writeLn('newMap = {}')
        self.writeLnFmt('for k, v in {value}.get{field}().items():', **fmtParams)
        self.indent()
        self.writeLnFmt(
            'newMap[self.traverse{struct}(k, *args)] = self.traverse{struct}(v, *args)', **fmtParams)
        self.unindent()
        self.writeLnFmt('{value}.set{field}(newMap)', **fmtParams)
        self.unindent()
      elif visitKeys:
        self.indent()
        self.writeLn('newMap = {}')
        self.writeLnFmt('for k, v in {value}.get{field}().items():', **fmtParams)
        self.indent()
        self.writeLnFmt('newMap[self.traverse{struct}(k, *args)] = v', **fmtParams)
        self.unindent()
        self.writeLnFmt('{value}.set{field}(newMap)', **fmtParams)
        self.unindent()
      elif visitValues:
        self.indent()
        self.writeLn('newMap = {}')
        self.writeLnFmt('for k, v in {value}.get{field}().items():', **fmtParams)
        self.indent()
        self.writeLnFmt('newMap[k] = self.traverse{struct}(v, *args)', **fmtParams)
        self.unindent()
        self.writeLnFmt('{value}.set{field}(newMap)', **fmtParams)
        self.unindent()

  def genVisitFieldNonMutating(self, fd, struct, field, valueName):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    fieldType = field.getType()
    fmtParams = {
        'struct': struct.getName(),
        'field': self.capitalize(field.getName()),
        'value': valueName,
        'newValue': 'new' + self.capitalize(valueName)
    }
    if fieldType.typeId() == types.TypeKind.MODIFIED:
      fieldType = fieldType.getElementType()
    if fieldType.typeId() == types.TypeKind.STRUCT and self.isSubType(fieldType, struct):
      if field.getOptions().isNullable():
        self.writeLnFmt('if {value}.has{field}() and {value}.get{field}():', **fmtParams)
      else:
        self.writeLnFmt('if {value}.has{field}():', **fmtParams)
      self.indent()
      self.writeLnFmt('fieldVal = self.traverse{struct}({value}.get{field}(), *args)', **fmtParams)
      self.writeLnFmt('if fieldVal is not {value}.get{field}():', **fmtParams)
      self.indent()
      self.writeLnFmt('{newValue} = self._copyOnChange({value}, {newValue})', **fmtParams)
      self.writeLnFmt('{newValue}.set{field}(fieldVal)',
          **fmtParams)
      self.unindent()
      self.unindent()
    elif fieldType.typeId() == types.TypeKind.LIST:
      if self.isSubType(fieldType.getElementType(), struct):
        self.writeLnFmt('if len({value}.get{field}()) > 0:', **fmtParams)
        self.indent()
        self.writeLn('newList = []')
        self.writeLn('fieldChanged = False')
        self.writeLnFmt('for item in {value}.get{field}():', **fmtParams)
        self.indent()
        self.writeLnFmt('newItem = self.traverse{struct}(item, *args)', **fmtParams)
        self.writeLn('newList.append(newItem)')
        self.writeLn('if newItem is not item:')
        self.indent()
        self.writeLn('fieldChanged = True')
        self.unindent()
        self.unindent()
        self.writeLn('if fieldChanged:')
        self.indent()
        self.writeLnFmt('{newValue} = self._copyOnChange({value}, {newValue})', **fmtParams)
        self.writeLnFmt('{newValue}.set{field}(newList)', **fmtParams)
        self.unindent()
        self.unindent()
    elif fieldType.typeId() == types.TypeKind.SET:
      if self.isSubType(fieldType.getElementType(), struct):
        self.writeLnFmt('if len({value}.get{field}()) > 0:', **fmtParams)
        self.indent()
        self.writeLn('newSet = set()')
        self.writeLn('fieldChanged = False')
        self.writeLnFmt('for item in {value}.get{field}():', **fmtParams)
        self.indent()
        self.writeLnFmt('newItem = self.traverse{struct}(item, *args)', **fmtParams)
        self.writeLn('newSet.append(newItem)')
        self.writeLn('if newItem is not item:')
        self.indent()
        self.writeLn('fieldChanged = True')
        self.unindent()
        self.unindent()
        self.writeLn('if fieldChanged:')
        self.indent()
        self.writeLnFmt('{newValue} = self._copyOnChange({value}, {newValue})', **fmtParams)
        self.writeLnFmt('{newValue}.set{field}(newSet)', **fmtParams)
        self.unindent()
        self.unindent()
    elif fieldType.typeId() == types.TypeKind.MAP:
      visitKeys = self.isSubType(fieldType.getKeyType(), struct)
      visitValues = self.isSubType(fieldType.getValueType(), struct)
      if not visitKeys and not visitValues:
        return
      self.writeLnFmt('if len({value}.get{field}()) > 0:', **fmtParams)
      self.indent()
      self.writeLn('newMap = {}')
      self.writeLn('fieldChanged = False')
      self.writeLnFmt('for k, v in {value}.get{field}().items():', **fmtParams)
      self.indent()
      if visitKeys:
        self.writeLnFmt('kNew = self.traverse{struct}(k)', **fmtParams)
        self.writeLn('if kNew is not k:')
        self.indent()
        self.writeLn('fieldChanged = True')
        self.unindent()
      if visitValues:
        self.writeLnFmt('vNew = self.traverse{struct}(v)', **fmtParams)
        self.writeLn('if vNew is not v:')
        self.indent()
        self.writeLn('fieldChanged = True')
        self.unindent()
      self.writeLn('newMap[k] = v')
      self.unindent()
      self.unindent()

  def visitorClassName(self, struct):
    if self.mutating:
      return struct.getName() + "Transform"
    else:
      return struct.getName() + "NonMutatingTransform"

  def isTransformableField(self, struct, field):
    '''@type fd: coda.descriptors.FileDescriptor
       @type struct: coda.descriptors.StructType
       @type field: coda.descriptors.StructType.Field'''
    fieldType = field.getType()
    if fieldType.typeId() == types.TypeKind.MODIFIED:
      fieldType = fieldType.getElementType()
    if fieldType.typeId() == types.TypeKind.STRUCT and self.isSubType(fieldType, struct):
      return True
    elif fieldType.typeId() == types.TypeKind.LIST:
      if self.isSubType(fieldType.getElementType(), struct):
        return True
    elif fieldType.typeId() == types.TypeKind.SET:
      if self.isSubType(fieldType.getElementType(), struct):
        return True
    elif fieldType.typeId() == types.TypeKind.MAP:
      visitKeys = self.isSubType(fieldType.getKeyType(), struct)
      visitValues = self.isSubType(fieldType.getValueType(), struct)
      return visitKeys or visitValues
