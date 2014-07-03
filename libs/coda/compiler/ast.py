# Abstract syntax tree for CODA IDL

# ============================================================================
# Scopes
# ============================================================================

class DefScope:
  'Mixin class for descriptors which are also scopes.'
  def __init__(self):
    self.structs = []
    self.enums = []
    self.extensions = []
    self.fields = []
    self.methods = []

  def addMember(self, member):
    assert member is not None
    if isinstance(member, StructDef):
      if member.isExtension():
        self.extensions.append(member)
      else:
        self.structs.append(member)
    elif isinstance(member, EnumDef):
      self.enums.append(member)
    elif isinstance(member, StructDef.Field):
      self.fields.append(member)
    elif isinstance(member, StructDef.Method):
      self.methods.append(member)
    else:
      raise AssertionError('Invalid member: ' + str(member))

# ============================================================================
# Type descriptors
# ============================================================================

class Ident:
  '''An identifier.'''
  def __init__(self, location, value):
    self.location = location
    self.value = value

  def __str__(self):
    return self.value

class TypeName:
  '''A reference to a type name.'''
  def __init__(self, location, name):
    self.location = location
    self.name = name

  def __str__(self):
    return self.name

class SpecializedType:
  '''A generic type plus type arguments.'''
  def __init__(self, base, args):
    self.location = base.location
    self.base = base
    self.args = args

  def __str__(self):
    return '{0}[{1}]'.format(self.base, ', '.join(str(ty) for ty in self.args))

class ModifiedType:
  '''A const or shared type.'''
  def __init__(self, base):
    self.location = base.location
    self.base = base
    self.const = False
    self.shared = False

  def __str__(self):
    return ''.join([
        ('const ' if self.const else ''),
        ('shared ' if self.shared else ''),
        (str(self.base))])

class Param:
  '''A method parameter.'''
  def __init__(self, location, name, ty):
    self.name = name
    self.type = ty

  def __str__(self):
    return '{0}:{1}'.format(self.name, self.type)

class AbstractDef:
  '''A type defined that has a name.'''
  def __init__(self, location, name):
    self.location = location
    self.name = name
    self.options = []

  def __str__(self):
    return self.name

class StructDef(AbstractDef, DefScope):
  '''A structure type.'''
  class Field:
    def __init__(self, location, name, fieldType, index):
      self.location = location
      self.name = name
      self.fieldType = fieldType
      self.options = []
      self.index = index

  class Method:
    def __init__(self, location, name, params, returnType, index = -1):
      self.location = location
      self.name = name
      self.params = params
      self.returnType = returnType
      self.options = []
      self.index = index

  def __init__(self, location, name):
    super().__init__(location, name)
    DefScope.__init__(self)
    self.baseType = None # For subtypes
    self.extends = None # For extensions
    self.typeId = None
    self.extensionRange = (0, 0)

  def getOptions(self):
    return self.options

  def addOptions(self, optionList):
    for option in optionList:
      self.options.append(option)

  def getExtensionRange(self):
    return self.extensionRange

  def setExtensionRange(self, extRange):
    self.extensionRange = extRange

  def isExtension(self):
    return self.extends is not None

class EnumDef(AbstractDef):
  '''An enumeration type.'''
  class Value:
    def __init__(self, location, name, value):
      self.location = location
      self.name = name
      self.value = value

  def __init__(self, location, name):
    super().__init__(location, name)
    self.values = []

  def addValues(self, values):
    self.values += values

# ============================================================================
# Options
# ============================================================================

class Option:
  def __init__(self, location, name, scope, value):
    assert location is not None
    assert name is not None
    assert value is not None
    self.location = location
    self.scope = scope
    self.name = name
    self.value = value

  def __str__(self):
    if self.scope:
      return '{0}:{1} = {2}'.format(self.scope, self.name, self.value)
    else:
      return '{0} = {1}'.format(self.name, self.value)

# ============================================================================
# Values - used for both options and constants
# ============================================================================

class Value:
  def __init__(self, location):
    self.location = location

# Boolean value
class BooleanValue(Value):
  def __init__(self, location, value):
    super().__init__(location)
    self.value = value

  def __str__(self):
    return 'True' if self.value else 'False'

# Integer value
class IntegerValue(Value):
  def __init__(self, location, value):
    super().__init__(location)
    self.value = value

  def __str__(self):
    return str(self.value)

# String value
class StringValue(Value):
  def __init__(self, location, value):
    super().__init__(location)
    self.value = value

  def __str__(self):
    return repr(self.value)

# List value
class ListValue(Value):
  def __init__(self, location, value):
    super().__init__(location)
    self.value = value

  def __str__(self):
    return '[' + ', '.join(str(value) for value in self.value) + ']'

# ============================================================================
# File descriptor
# ============================================================================

class File(DefScope):
  '''Descriptor for a CODA IDL file.'''
  def __init__(self, path, package=None):
    super().__init__()
    self.path = path
    self.package = package
    self.imports = []
    self.options = []

  def getPackage(self):
    'The declared _package of this file'
    return self.package
