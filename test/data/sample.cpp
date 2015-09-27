// ============================================================================
// Generated by codagen from sample.coda.coda. DO NOT EDIT!
// ============================================================================

#include "coda/types.h"
#include "coda/io/codec.h"
#include "sample.h"
#include "coda/runtime/descriptors_static.h"

namespace sample {

coda::descriptors::FieldOptions _options0 = coda::descriptors::freeze(coda::descriptors::FieldOptions().setFixed(true));
coda::descriptors::FileOptions _options1 = coda::descriptors::freeze(coda::descriptors::FileOptions().putPackage("python", "sample").putPackage("java", "sample").putPackage("cpp", "sample").putOuterClass("java", "Sample"));

// ============================================================================
// E
// ============================================================================

static coda::descriptors::EnumDescriptor::Value E_Value_E0("E0", E_E0);
static coda::descriptors::EnumDescriptor::Value E_Value_E1("E1", E_E1);
static coda::descriptors::EnumDescriptor::Value E_Value_E2("E2", E_E2);

static coda::descriptors::EnumDescriptor::Value* E_Values[] = {
  &E_Value_E0,
  &E_Value_E1,
  &E_Value_E2,
};

coda::descriptors::EnumDescriptor E_DESCRIPTOR(
    "E",
    coda::descriptors::EnumOptions::DEFAULT_INSTANCE,
    E_Values
);

// ============================================================================
// S1
// ============================================================================

coda::descriptors::FieldDescriptor S1::Field_scalarBoolean(
    "scalarBoolean", 1,
    coda::types::Boolean::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _scalarBoolean),
    S1::HAS_SCALAR_BOOLEAN);
coda::descriptors::FieldDescriptor S1::Field_scalarI16(
    "scalarI16", 2,
    coda::types::Integer16::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _scalarI16),
    S1::HAS_SCALAR_I16);
coda::descriptors::FieldDescriptor S1::Field_scalarI32(
    "scalarI32", 3,
    coda::types::Integer32::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _scalarI32),
    S1::HAS_SCALAR_I32);
coda::descriptors::FieldDescriptor S1::Field_scalarI64(
    "scalarI64", 4,
    coda::types::Integer32::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _scalarI64),
    S1::HAS_SCALAR_I64);
coda::descriptors::FieldDescriptor S1::Field_scalarFixedI16(
    "scalarFixedI16", 5,
    coda::types::Integer16::DESCRIPTOR,
    _options0,
    CODA_OFFSET_OF(S1, _scalarFixedI16),
    S1::HAS_SCALAR_FIXED_I16);
coda::descriptors::FieldDescriptor S1::Field_scalarFixedI32(
    "scalarFixedI32", 6,
    coda::types::Integer32::DESCRIPTOR,
    _options0,
    CODA_OFFSET_OF(S1, _scalarFixedI32),
    S1::HAS_SCALAR_FIXED_I32);
coda::descriptors::FieldDescriptor S1::Field_scalarFixedI64(
    "scalarFixedI64", 7,
    coda::types::Integer32::DESCRIPTOR,
    _options0,
    CODA_OFFSET_OF(S1, _scalarFixedI64),
    S1::HAS_SCALAR_FIXED_I64);
coda::descriptors::FieldDescriptor S1::Field_scalarFloat(
    "scalarFloat", 8,
    coda::types::Float::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _scalarFloat),
    S1::HAS_SCALAR_FLOAT);
coda::descriptors::FieldDescriptor S1::Field_scalarDouble(
    "scalarDouble", 9,
    coda::types::Double::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _scalarDouble),
    S1::HAS_SCALAR_DOUBLE);
coda::descriptors::FieldDescriptor S1::Field_scalarString(
    "scalarString", 10,
    coda::types::String::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _scalarString),
    S1::HAS_SCALAR_STRING);
coda::descriptors::FieldDescriptor S1::Field_scalarBytes(
    "scalarBytes", 11,
    coda::types::Bytes::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _scalarBytes),
    S1::HAS_SCALAR_BYTES);
coda::descriptors::FieldDescriptor S1::Field_scalarEnum(
    "scalarEnum", 12,
    E_DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _scalarEnum),
    S1::HAS_SCALAR_ENUM);
coda::descriptors::FieldDescriptor S1::Field_listBoolean(
    "listBoolean", 20,
    coda::types::List<coda::types::Boolean>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _listBoolean),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_listInt(
    "listInt", 21,
    coda::types::List<coda::types::Integer32>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _listInt),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_listFloat(
    "listFloat", 22,
    coda::types::List<coda::types::Float>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _listFloat),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_listString(
    "listString", 23,
    coda::types::List<coda::types::String >::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _listString),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_listEnum(
    "listEnum", 24,
    coda::types::List<coda::types::Enum<E_DESCRIPTOR>>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _listEnum),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_setInt(
    "setInt", 41,
    coda::types::Set<coda::types::Integer32>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _setInt),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_setString(
    "setString", 43,
    coda::types::Set<coda::types::String >::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _setString),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_setEnum(
    "setEnum", 44,
    coda::types::Set<coda::types::Enum<E_DESCRIPTOR>>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _setEnum),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_mapIntString(
    "mapIntString", 51,
    coda::types::Map<coda::types::Integer32, coda::types::String >::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _mapIntString),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_mapStringInt(
    "mapStringInt", 52,
    coda::types::Map<coda::types::String, coda::types::Integer32>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _mapStringInt),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_mapEnumStruct(
    "mapEnumStruct", 53,
    coda::types::Map<coda::types::Enum<E_DESCRIPTOR>, S1>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _mapEnumStruct),
    (size_t)-1);
coda::descriptors::FieldDescriptor S1::Field_unused(
    "unused", 100,
    coda::types::Integer32::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S1, _unused),
    S1::HAS_UNUSED);

coda::descriptors::FieldDescriptor* S1::Fields[] = {
  &S1::Field_scalarBoolean,
  &S1::Field_scalarI16,
  &S1::Field_scalarI32,
  &S1::Field_scalarI64,
  &S1::Field_scalarFixedI16,
  &S1::Field_scalarFixedI32,
  &S1::Field_scalarFixedI64,
  &S1::Field_scalarFloat,
  &S1::Field_scalarDouble,
  &S1::Field_scalarString,
  &S1::Field_scalarBytes,
  &S1::Field_scalarEnum,
  &S1::Field_listBoolean,
  &S1::Field_listInt,
  &S1::Field_listFloat,
  &S1::Field_listString,
  &S1::Field_listEnum,
  &S1::Field_setInt,
  &S1::Field_setString,
  &S1::Field_setEnum,
  &S1::Field_mapIntString,
  &S1::Field_mapStringInt,
  &S1::Field_mapEnumStruct,
  &S1::Field_unused,
};

const uint32_t S1::TYPE_ID = 0;

coda::descriptors::StructDescriptor S1::DESCRIPTOR(
  "S1",
  0,
  &S1::DEFAULT_INSTANCE,
  FILE,
  NULL,
  NULL,
  coda::descriptors::StructOptions::DEFAULT_INSTANCE,
  coda::descriptors::StaticArrayRef<coda::descriptors::StructDescriptor*>(),
  coda::descriptors::StaticArrayRef<coda::descriptors::EnumDescriptor*>(),
  S1::Fields,
  &coda::descriptors::StaticObjectBuilder<S1>::create,
  (coda::descriptors::PresenceGetter) &S1::isFieldPresent,
  (coda::descriptors::PresenceSetter) &S1::setFieldPresent
);

S1 S1::DEFAULT_INSTANCE;

bool S1::equals(const coda::runtime::Object* other) const {
  return other != NULL && descriptor() == other->descriptor() &&
        _scalarBoolean == ((S1*) other)->_scalarBoolean &&
        _scalarI16 == ((S1*) other)->_scalarI16 &&
        _scalarI32 == ((S1*) other)->_scalarI32 &&
        _scalarI64 == ((S1*) other)->_scalarI64 &&
        _scalarFixedI16 == ((S1*) other)->_scalarFixedI16 &&
        _scalarFixedI32 == ((S1*) other)->_scalarFixedI32 &&
        _scalarFixedI64 == ((S1*) other)->_scalarFixedI64 &&
        _scalarFloat == ((S1*) other)->_scalarFloat &&
        _scalarDouble == ((S1*) other)->_scalarDouble &&
        _scalarString == ((S1*) other)->_scalarString &&
        _scalarBytes == ((S1*) other)->_scalarBytes &&
        _scalarEnum == ((S1*) other)->_scalarEnum &&
        _listBoolean == ((S1*) other)->_listBoolean &&
        _listInt == ((S1*) other)->_listInt &&
        _listFloat == ((S1*) other)->_listFloat &&
        _listString == ((S1*) other)->_listString &&
        _listEnum == ((S1*) other)->_listEnum &&
        _setInt == ((S1*) other)->_setInt &&
        _setString == ((S1*) other)->_setString &&
        _setEnum == ((S1*) other)->_setEnum &&
        _mapIntString == ((S1*) other)->_mapIntString &&
        _mapStringInt == ((S1*) other)->_mapStringInt &&
        _mapEnumStruct == ((S1*) other)->_mapEnumStruct &&
        _unused == ((S1*) other)->_unused;
}

size_t S1::hashValue() const {
  size_t hash = coda::runtime::Object::hashValue();
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarBoolean));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarI16));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarI32));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarI64));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarFixedI16));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarFixedI32));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarFixedI64));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarFloat));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarDouble));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarString));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_scalarBytes));
  coda::runtime::hash_combine(hash, coda::runtime::EnumHash<E>()(_scalarEnum));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_listBoolean));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_listInt));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_listFloat));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_listString));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_listEnum));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_setInt));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_setString));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_setEnum));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_mapIntString));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_mapStringInt));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_mapEnumStruct));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_unused));
  return hash;
}

void S1::freezeImpl() {
  for (std::unordered_map<E, S1*, coda::runtime::EnumHash<E> >::const_iterator it = _mapEnumStruct.begin(), itEnd = _mapEnumStruct.end(); it != itEnd; ++it) {
    if (it->second->isMutable()) {
      it->second->freeze();
    }
  }
}

void S1::clear() {
  _scalarBoolean = false;
  _scalarI16 = 0;
  _scalarI32 = 0;
  _scalarI64 = 0;
  _scalarFixedI16 = 0;
  _scalarFixedI32 = 0;
  _scalarFixedI64 = 0;
  _scalarFloat = 0;
  _scalarDouble = 0;
  _scalarEnum = E_E0;
  _listBoolean.clear();
  _listInt.clear();
  _listFloat.clear();
  _listString.clear();
  _listEnum.clear();
  _setInt.clear();
  _setString.clear();
  _setEnum.clear();
  _mapIntString.clear();
  _mapStringInt.clear();
  _mapEnumStruct.clear();
  _unused = 0;
}

void S1::deleteRecursiveImpl(Object** queue) {
  for (std::unordered_map<E, S1*, coda::runtime::EnumHash<E> >::const_iterator it = _mapEnumStruct.begin(), itEnd = _mapEnumStruct.end(); it != itEnd; ++it) {
    if (it->second != &S1::DEFAULT_INSTANCE) {
      it->second->queueForDelete(queue);
    }
  }
}

void S1::endWrite(coda::io::Encoder* encoder) const {
  if (hasScalarBoolean()) {
    encoder->writeFieldHeader("scalarBoolean", 1);
    encoder->writeBoolean(_scalarBoolean);
  }
  if (hasScalarI16()) {
    encoder->writeFieldHeader("scalarI16", 2);
    encoder->writeInteger(_scalarI16);
  }
  if (hasScalarI32()) {
    encoder->writeFieldHeader("scalarI32", 3);
    encoder->writeInteger(_scalarI32);
  }
  if (hasScalarI64()) {
    encoder->writeFieldHeader("scalarI64", 4);
    encoder->writeInteger(_scalarI64);
  }
  if (hasScalarFixedI16()) {
    encoder->writeFieldHeader("scalarFixedI16", 5);
    encoder->writeFixed16(_scalarFixedI16);
  }
  if (hasScalarFixedI32()) {
    encoder->writeFieldHeader("scalarFixedI32", 6);
    encoder->writeFixed32(_scalarFixedI32);
  }
  if (hasScalarFixedI64()) {
    encoder->writeFieldHeader("scalarFixedI64", 7);
    encoder->writeFixed32(_scalarFixedI64);
  }
  if (hasScalarFloat()) {
    encoder->writeFieldHeader("scalarFloat", 8);
    encoder->writeFloat(_scalarFloat);
  }
  if (hasScalarDouble()) {
    encoder->writeFieldHeader("scalarDouble", 9);
    encoder->writeDouble(_scalarDouble);
  }
  if (hasScalarString()) {
    encoder->writeFieldHeader("scalarString", 10);
    encoder->writeString(_scalarString);
  }
  if (hasScalarBytes()) {
    encoder->writeFieldHeader("scalarBytes", 11);
    encoder->writeBytes(_scalarBytes);
  }
  if (hasScalarEnum()) {
    encoder->writeFieldHeader("scalarEnum", 12);
    encoder->writeInteger((int32_t) _scalarEnum);
  }
  if (!_listBoolean.empty()) {
    encoder->writeFieldHeader("listBoolean", 20);
    encoder->writeBeginList(coda::descriptors::TYPE_KIND_BOOL, _listBoolean.size());
    for (std::vector<bool>::const_iterator it = _listBoolean.begin(), itEnd = _listBoolean.end(); it != itEnd; ++it) {
      encoder->writeBoolean(*it);
    }
    encoder->writeEndList();
  }
  if (!_listInt.empty()) {
    encoder->writeFieldHeader("listInt", 21);
    encoder->writeBeginList(coda::descriptors::TYPE_KIND_INTEGER, _listInt.size());
    for (std::vector<int32_t>::const_iterator it = _listInt.begin(), itEnd = _listInt.end(); it != itEnd; ++it) {
      encoder->writeInteger(*it);
    }
    encoder->writeEndList();
  }
  if (!_listFloat.empty()) {
    encoder->writeFieldHeader("listFloat", 22);
    encoder->writeBeginList(coda::descriptors::TYPE_KIND_FLOAT, _listFloat.size());
    for (std::vector<float>::const_iterator it = _listFloat.begin(), itEnd = _listFloat.end(); it != itEnd; ++it) {
      encoder->writeFloat(*it);
    }
    encoder->writeEndList();
  }
  if (!_listString.empty()) {
    encoder->writeFieldHeader("listString", 23);
    encoder->writeBeginList(coda::descriptors::TYPE_KIND_STRING, _listString.size());
    for (std::vector<std::string>::const_iterator it = _listString.begin(), itEnd = _listString.end(); it != itEnd; ++it) {
      encoder->writeString(*it);
    }
    encoder->writeEndList();
  }
  if (!_listEnum.empty()) {
    encoder->writeFieldHeader("listEnum", 24);
    encoder->writeBeginList(coda::descriptors::TYPE_KIND_ENUM, _listEnum.size());
    for (std::vector<E>::const_iterator it = _listEnum.begin(), itEnd = _listEnum.end(); it != itEnd; ++it) {
      encoder->writeInteger((int32_t) *it);
    }
    encoder->writeEndList();
  }
  if (!_setInt.empty()) {
    encoder->writeFieldHeader("setInt", 41);
    encoder->writeBeginSet(coda::descriptors::TYPE_KIND_INTEGER, _setInt.size());
    for (std::unordered_set<int32_t>::const_iterator it = _setInt.begin(), itEnd = _setInt.end(); it != itEnd; ++it) {
      encoder->writeInteger(*it);
    }
    encoder->writeEndSet();
  }
  if (!_setString.empty()) {
    encoder->writeFieldHeader("setString", 43);
    encoder->writeBeginSet(coda::descriptors::TYPE_KIND_STRING, _setString.size());
    for (std::unordered_set<std::string>::const_iterator it = _setString.begin(), itEnd = _setString.end(); it != itEnd; ++it) {
      encoder->writeString(*it);
    }
    encoder->writeEndSet();
  }
  if (!_setEnum.empty()) {
    encoder->writeFieldHeader("setEnum", 44);
    encoder->writeBeginSet(coda::descriptors::TYPE_KIND_ENUM, _setEnum.size());
    for (std::unordered_set<E, coda::runtime::EnumHash<E> >::const_iterator it = _setEnum.begin(), itEnd = _setEnum.end(); it != itEnd; ++it) {
      encoder->writeInteger((int32_t) *it);
    }
    encoder->writeEndSet();
  }
  if (!_mapIntString.empty()) {
    encoder->writeFieldHeader("mapIntString", 51);
    encoder->writeBeginMap(coda::descriptors::TYPE_KIND_INTEGER, coda::descriptors::TYPE_KIND_STRING, _mapIntString.size());
    for (std::unordered_map<int32_t, std::string>::const_iterator it = _mapIntString.begin(), itEnd = _mapIntString.end(); it != itEnd; ++it) {
      encoder->writeInteger(it->first);
      encoder->writeString(it->second);
    }
    encoder->writeEndMap();
  }
  if (!_mapStringInt.empty()) {
    encoder->writeFieldHeader("mapStringInt", 52);
    encoder->writeBeginMap(coda::descriptors::TYPE_KIND_STRING, coda::descriptors::TYPE_KIND_INTEGER, _mapStringInt.size());
    for (std::unordered_map<std::string, int32_t>::const_iterator it = _mapStringInt.begin(), itEnd = _mapStringInt.end(); it != itEnd; ++it) {
      encoder->writeString(it->first);
      encoder->writeInteger(it->second);
    }
    encoder->writeEndMap();
  }
  if (!_mapEnumStruct.empty()) {
    encoder->writeFieldHeader("mapEnumStruct", 53);
    encoder->writeBeginMap(coda::descriptors::TYPE_KIND_ENUM, coda::descriptors::TYPE_KIND_STRUCT, _mapEnumStruct.size());
    for (std::unordered_map<E, S1*, coda::runtime::EnumHash<E> >::const_iterator it = _mapEnumStruct.begin(), itEnd = _mapEnumStruct.end(); it != itEnd; ++it) {
      encoder->writeInteger((int32_t) it->first);
      encoder->writeStruct(it->second, true);
    }
    encoder->writeEndMap();
  }
  if (hasUnused()) {
    encoder->writeFieldHeader("unused", 100);
    encoder->writeInteger(_unused);
  }
}

// ============================================================================
// S2
// ============================================================================

coda::descriptors::FieldDescriptor S2::Field_left(
    "left", 1,
    S1::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S2, _left),
    S2::HAS_LEFT);
coda::descriptors::FieldDescriptor S2::Field_right(
    "right", 2,
    S1::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S2, _right),
    S2::HAS_RIGHT);

coda::descriptors::FieldDescriptor* S2::Fields[] = {
  &S2::Field_left,
  &S2::Field_right,
};

const uint32_t S2::TYPE_ID = 1;

coda::descriptors::StructDescriptor S2::DESCRIPTOR(
  "S2",
  1,
  &S2::DEFAULT_INSTANCE,
  FILE,
  NULL,
  &S1::DESCRIPTOR,
  coda::descriptors::StructOptions::DEFAULT_INSTANCE,
  coda::descriptors::StaticArrayRef<coda::descriptors::StructDescriptor*>(),
  coda::descriptors::StaticArrayRef<coda::descriptors::EnumDescriptor*>(),
  S2::Fields,
  &coda::descriptors::StaticObjectBuilder<S2>::create,
  (coda::descriptors::PresenceGetter) &S2::isFieldPresent,
  (coda::descriptors::PresenceSetter) &S2::setFieldPresent
);

S2 S2::DEFAULT_INSTANCE;

S2::S2()
  : _left(&S1::DEFAULT_INSTANCE)
  , _right(&S1::DEFAULT_INSTANCE)
{
}

bool S2::equals(const coda::runtime::Object* other) const {
  return S1::equals(other) &&
        _left == ((S2*) other)->_left &&
        _right == ((S2*) other)->_right;
}

size_t S2::hashValue() const {
  size_t hash = S1::hashValue();
  coda::runtime::hash_combine(hash, coda::runtime::hash(_left));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_right));
  return hash;
}

void S2::freezeImpl() {
  S1::freezeImpl();
  if (_left->isMutable()) {
    _left->freeze();
  }
  if (_right->isMutable()) {
    _right->freeze();
  }
}

void S2::clear() {
  S1::clear();
  _left = &S1::DEFAULT_INSTANCE;
  _right = &S1::DEFAULT_INSTANCE;
}

void S2::deleteRecursiveImpl(Object** queue) {
  S1::deleteRecursiveImpl(queue);
  if (_left != &S1::DEFAULT_INSTANCE) {
    _left->queueForDelete(queue);
  }
  if (_right != &S1::DEFAULT_INSTANCE) {
    _right->queueForDelete(queue);
  }
}

void S2::beginWrite(coda::io::Encoder* encoder) const {
  S1::beginWrite(encoder);
  encoder->writeSubtypeHeader("S2", coda::descriptors::TYPE_KIND_BOOL);
}

void S2::endWrite(coda::io::Encoder* encoder) const {
  if (hasLeft()) {
    encoder->writeFieldHeader("left", 1);
    encoder->writeStruct(_left, true);
  }
  if (hasRight()) {
    encoder->writeFieldHeader("right", 2);
    encoder->writeStruct(_right, true);
  }
  encoder->writeEndSubtype();
  S1::endWrite(encoder);
}

// ============================================================================
// S3
// ============================================================================

coda::descriptors::FieldDescriptor S3::Field_sList(
    "sList", 1,
    coda::types::List<S1>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S3, _sList),
    (size_t)-1);
coda::descriptors::FieldDescriptor S3::Field_sSet(
    "sSet", 2,
    coda::types::Set<S1>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S3, _sSet),
    (size_t)-1);
coda::descriptors::FieldDescriptor S3::Field_sMap(
    "sMap", 3,
    coda::types::Map<coda::types::String, S1>::DESCRIPTOR,
    coda::descriptors::FieldOptions::DEFAULT_INSTANCE,
    CODA_OFFSET_OF(S3, _sMap),
    (size_t)-1);

coda::descriptors::FieldDescriptor* S3::Fields[] = {
  &S3::Field_sList,
  &S3::Field_sSet,
  &S3::Field_sMap,
};

const uint32_t S3::TYPE_ID = 2;

coda::descriptors::StructDescriptor S3::DESCRIPTOR(
  "S3",
  2,
  &S3::DEFAULT_INSTANCE,
  FILE,
  NULL,
  &S1::DESCRIPTOR,
  coda::descriptors::StructOptions::DEFAULT_INSTANCE,
  coda::descriptors::StaticArrayRef<coda::descriptors::StructDescriptor*>(),
  coda::descriptors::StaticArrayRef<coda::descriptors::EnumDescriptor*>(),
  S3::Fields,
  &coda::descriptors::StaticObjectBuilder<S3>::create,
  NULL, NULL
);

S3 S3::DEFAULT_INSTANCE;

bool S3::equals(const coda::runtime::Object* other) const {
  return S1::equals(other) &&
        _sList == ((S3*) other)->_sList &&
        _sSet == ((S3*) other)->_sSet &&
        _sMap == ((S3*) other)->_sMap;
}

size_t S3::hashValue() const {
  size_t hash = S1::hashValue();
  coda::runtime::hash_combine(hash, coda::runtime::hash(_sList));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_sSet));
  coda::runtime::hash_combine(hash, coda::runtime::hash(_sMap));
  return hash;
}

void S3::freezeImpl() {
  S1::freezeImpl();
  for (std::vector<S1*>::const_iterator it = _sList.begin(), itEnd = _sList.end(); it != itEnd; ++it) {
    if ((*it)->isMutable()) {
      (*it)->freeze();
    }
  }
  for (std::unordered_set<S1*>::const_iterator it = _sSet.begin(), itEnd = _sSet.end(); it != itEnd; ++it) {
    if ((*it)->isMutable()) {
      (*it)->freeze();
    }
  }
  for (std::unordered_map<std::string, S1*>::const_iterator it = _sMap.begin(), itEnd = _sMap.end(); it != itEnd; ++it) {
    if (it->second->isMutable()) {
      it->second->freeze();
    }
  }
}

void S3::clear() {
  S1::clear();
  _sList.clear();
  _sSet.clear();
  _sMap.clear();
}

void S3::deleteRecursiveImpl(Object** queue) {
  S1::deleteRecursiveImpl(queue);
  for (std::vector<S1*>::const_iterator it = _sList.begin(), itEnd = _sList.end(); it != itEnd; ++it) {
    if ((*it) != &S1::DEFAULT_INSTANCE) {
      (*it)->queueForDelete(queue);
    }
  }
  for (std::unordered_set<S1*>::const_iterator it = _sSet.begin(), itEnd = _sSet.end(); it != itEnd; ++it) {
    if ((*it) != &S1::DEFAULT_INSTANCE) {
      (*it)->queueForDelete(queue);
    }
  }
  for (std::unordered_map<std::string, S1*>::const_iterator it = _sMap.begin(), itEnd = _sMap.end(); it != itEnd; ++it) {
    if (it->second != &S1::DEFAULT_INSTANCE) {
      it->second->queueForDelete(queue);
    }
  }
}

void S3::beginWrite(coda::io::Encoder* encoder) const {
  S1::beginWrite(encoder);
  encoder->writeSubtypeHeader("S3", coda::descriptors::TYPE_KIND_INTEGER);
}

void S3::endWrite(coda::io::Encoder* encoder) const {
  if (!_sList.empty()) {
    encoder->writeFieldHeader("sList", 1);
    encoder->writeBeginList(coda::descriptors::TYPE_KIND_STRUCT, _sList.size());
    for (std::vector<S1*>::const_iterator it = _sList.begin(), itEnd = _sList.end(); it != itEnd; ++it) {
      encoder->writeStruct(*it, true);
    }
    encoder->writeEndList();
  }
  if (!_sSet.empty()) {
    encoder->writeFieldHeader("sSet", 2);
    encoder->writeBeginSet(coda::descriptors::TYPE_KIND_STRUCT, _sSet.size());
    for (std::unordered_set<S1*>::const_iterator it = _sSet.begin(), itEnd = _sSet.end(); it != itEnd; ++it) {
      encoder->writeStruct(*it, true);
    }
    encoder->writeEndSet();
  }
  if (!_sMap.empty()) {
    encoder->writeFieldHeader("sMap", 3);
    encoder->writeBeginMap(coda::descriptors::TYPE_KIND_STRING, coda::descriptors::TYPE_KIND_STRUCT, _sMap.size());
    for (std::unordered_map<std::string, S1*>::const_iterator it = _sMap.begin(), itEnd = _sMap.end(); it != itEnd; ++it) {
      encoder->writeString(it->first);
      encoder->writeStruct(it->second, true);
    }
    encoder->writeEndMap();
  }
  encoder->writeEndSubtype();
  S1::endWrite(encoder);
}

// ============================================================================
// FILE
// ============================================================================

static coda::descriptors::StructDescriptor* FILE_Structs[] = {
  &S1::DESCRIPTOR,
  &S2::DESCRIPTOR,
  &S3::DESCRIPTOR,
};

static coda::descriptors::EnumDescriptor* FILE_Enums[] = {
  &E_DESCRIPTOR,
};

coda::descriptors::StaticFileDescriptor FILE(
    "sample.coda",
    "sample",
    _options1,
    FILE_Structs,
    FILE_Enums
);

} // namespace sample
