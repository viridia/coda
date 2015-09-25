'''Classes to bootstrap a generated Coda module.'''

class Bootstrap:
  deferred = []
  #incomplete = []
  structDescriptorClass = None
  enumDescriptorClass = None
  descdata = None
  modules = {}

def createFile(name, path, package, structs=(), enums=(), extensions=(),
    options=(), fileOptions=None, types=(), imports={}, descriptors=None, module=None):
  # Bootstrap descriptors
  if descriptors:
    fileDescriptorClass = descriptors['FileDescriptor']
    extensionFieldClass = descriptors['ExtensionField']
  else:
    import coda.descriptors
    fileDescriptorClass = coda.descriptors.FileDescriptor
    extensionFieldClass = coda.descriptors.ExtensionField

  # Initialize struct default instances.
  def initStructDefaultInstances(classes):
    for cls in classes:
      cls.__defaultInstance__.__init__()
      initStructDefaultInstances(cls.__structs__)
  def freezeStructDefaultInstances(classes):
    for cls in classes:
      cls.__defaultInstance__.freeze(False)
      freezeStructDefaultInstances(cls.__structs__)

  file = fileDescriptorClass()
  file.setName(name)
  file.setDirectory(path)
  file.setPackage(package)

  # Function to initialize descriptors after modules have been imported
  def initDescriptors():
    def initDeferredModule(importModule, initFn):
      if importModule.get('__initializing__'):
        return
      moduleName = importModule['__name__']
      if 'FILE' not in importModule:
        return
      importFileDesc = importModule['FILE']
      if not importFileDesc.isMutable():
        return
      lateImports = importModule.get('__lateImports__', [])
      if not lateImports:
        return
      for importPath, localName in lateImports:
        mod = __import__(importPath, globals(), locals(), 'FILE')
        importModule[localName] = mod
      importModule['__initializing__'] = True
      initFn()
    def handleModuleDeps():
      for importMap in imports.values():
        importPath = importMap.get('python')
        if importPath and importPath in Bootstrap.modules:
          initDeferredModule(*Bootstrap.modules[importPath])
    def createEnumDescriptors(classes, enclosingType):
      for cls in classes:
        cls.DESCRIPTOR = Bootstrap.enumDescriptorClass.forClass(cls, file)
        if enclosingType:
          cls.DESCRIPTOR.setEnclosingType(enclosingType)
    def createStructDescriptors(classes, enclosingType):
      for cls in classes:
        cls.DESCRIPTOR = Bootstrap.structDescriptorClass.forClass(cls, file)
        if enclosingType:
          cls.DESCRIPTOR.setEnclosingType(enclosingType)
        if cls.TYPE_ID:
          cls.DESCRIPTOR.setTypeId(cls.TYPE_ID)
        createStructDescriptors(cls.__structs__, cls.DESCRIPTOR)
        createEnumDescriptors(cls.__enums__, cls.DESCRIPTOR)
        if cls.__structs__:
          cls.DESCRIPTOR.setStructs([st.DESCRIPTOR for st in cls.__structs__])
        if cls.__enums__:
          cls.DESCRIPTOR.setEnums([en.DESCRIPTOR for en in cls.__enums__])
    def createFieldDescriptors(classes):
      for cls in classes:
        struct = cls.DESCRIPTOR
        for name, fid, typeId, optIndex in cls.__fields__:
          field = struct.defineField(name, fid, typeTable[typeId])
          if optIndex >= 0:
            field.setOptions(optionsTable[optIndex])
        createExtensionFieldDescriptors(cls.__extensions__, struct)
        createFieldDescriptors(cls.__structs__)
    def createExtensionFieldDescriptors(fields, enclosingType):
      result = []
      for name, xid, ty, extends, sourceLine in fields:
        ex = extensionFieldClass()
        ex.setFile(file)
        ex.setName(name)
        ex.setId(xid)
        ex.setType(typeTable[ty])
        ex.setExtends(typeTable[extends])
        ex.setSourceLine(sourceLine)
        if enclosingType:
          ex.setEnclosingType(enclosingType)
        result.append(ex)
        typeregistry.TypeRegistry.INSTANCE.addExtension(ex)
      return result
    def setStructOptions(classes):
      for cls in classes:
        if '__optionsIndex__' in cls.__dict__:
          cls.DESCRIPTOR.setOptions(optionsTable[cls.__optionsIndex__])
        setStructOptions(cls.__structs__)
        setEnumOptions(cls.__enums__)
    def setEnumOptions(classes):
      for cls in classes:
        if '__optionsIndex__' in cls.__dict__:
          cls.DESCRIPTOR.setOptions(optionsTable[cls.__optionsIndex__])
    def freezeDescriptors(classes):
      for cls in classes:
        cls.DESCRIPTOR.freeze()
        if isinstance(cls.DESCRIPTOR, Bootstrap.structDescriptorClass):
          freezeDescriptors(cls.__structs__)
          freezeDescriptors(cls.__enums__)
    from . import typeregistry
    for importPath, packages in imports.items():
      imp = fileDescriptorClass.Import().setPath(importPath)
      for lang, pkg in packages.items():
        imp.getMutablePackage()[lang] = pkg
      file.getMutableImports().append(imp)
    initStructDefaultInstances(structs)
    freezeStructDefaultInstances(structs)
    createStructDescriptors(structs, None)
    createEnumDescriptors(enums, None)
    handleModuleDeps()
    import coda.types
    if types:
      typeTable = types(coda.types)
    else:
      typeTable = ()
    optionsTable = options(Bootstrap.descdata)
    for opts in optionsTable:
      opts.freeze()
    if fileOptions is not None:
      file.setOptions(optionsTable[fileOptions])
    setStructOptions(structs)
    setEnumOptions(enums)
    file.setStructs([st.DESCRIPTOR for st in structs])
    file.setEnums([en.DESCRIPTOR for en in enums])
    createFieldDescriptors(structs)
    createExtensionFieldDescriptors(extensions, None)
    freezeDescriptors(structs)
    freezeDescriptors(enums)
    file.freeze()
    typeregistry.TypeRegistry.INSTANCE.addFile(file)

  if module:
    moduleName = module['__name__']
    Bootstrap.modules[moduleName] = (module, initDescriptors)
    lateImports = module.get('__lateImports__', [])
  else:
    lateImports = []

  if Bootstrap.structDescriptorClass and not lateImports:
    initDescriptors()
  else:
    Bootstrap.deferred.append(initDescriptors)

  return file

def initModule(structDescriptorClass, enumDescriptorClass, descdata):
  if Bootstrap.structDescriptorClass:
    return
  Bootstrap.structDescriptorClass = structDescriptorClass
  Bootstrap.enumDescriptorClass = enumDescriptorClass
  Bootstrap.descdata = descdata

  for deferred in Bootstrap.deferred:
    deferred()
