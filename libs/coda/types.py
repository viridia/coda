'''Coda built-in types. This is actually filled in by the bootstrap module.'''

from coda.runtime.descdata import Type, TypeKind #@UnusedImport
from coda.runtime.descdata import BooleanType, IntegerType, FloatType, DoubleType, StringType, BytesType
from coda.runtime.descdata import ListType, SetType, MapType, CollectionType, ModifiedType #@UnusedImport
from coda.runtime.descdata import DeclType, StructType, EnumType #@UnusedImport

BOOL = BooleanType.defaultInstance()
I16 = IntegerType().setBits(16).freeze()
I32 = IntegerType().setBits(32).freeze()
I64 = IntegerType().setBits(64).freeze()
FLOAT = FloatType.defaultInstance()
DOUBLE = DoubleType.defaultInstance()
STRING = StringType.defaultInstance()
BYTES = BytesType.defaultInstance()
ERROR = Type.defaultInstance()

# Strip modifiers and get the base type
def unmodified(ty):
  while isinstance(ty, ModifiedType):
    ty = ty.getElementType()
  return ty
