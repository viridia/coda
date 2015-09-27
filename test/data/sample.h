// ============================================================================
// Generated by codagen from sample.coda.coda. DO NOT EDIT!
// ============================================================================

#ifndef SAMPLE
#define SAMPLE 1

#ifndef CODA_RUNTIME_OBJECT_H
  #include "coda/runtime/object.h"
#endif

#include <bitset>
#include <stdint.h>

namespace sample {

enum E {
  E_E0 = 0,
  E_E1 = 1,
  E_E2 = 2,
};
extern coda::descriptors::EnumDescriptor E_DESCRIPTOR;

// ============================================================================
// S1
// ============================================================================

class S1 : public coda::runtime::Object {
public:
  enum FieldPresentBits {
    HAS_SCALAR_BOOLEAN,
    HAS_SCALAR_I16,
    HAS_SCALAR_I32,
    HAS_SCALAR_I64,
    HAS_SCALAR_FIXED_I16,
    HAS_SCALAR_FIXED_I32,
    HAS_SCALAR_FIXED_I64,
    HAS_SCALAR_FLOAT,
    HAS_SCALAR_DOUBLE,
    HAS_SCALAR_STRING,
    HAS_SCALAR_BYTES,
    HAS_SCALAR_ENUM,
    HAS_UNUSED,
  };

  S1()
    : _scalarBoolean(false)
    , _scalarI16(0)
    , _scalarI32(0)
    , _scalarI64(0)
    , _scalarFixedI16(0)
    , _scalarFixedI32(0)
    , _scalarFixedI64(0)
    , _scalarFloat(0)
    , _scalarDouble(0)
    , _scalarEnum(E_E0)
    , _unused(0)
  {}

  S1(const S1& _src)
    : _scalarBoolean(_src._scalarBoolean)
    , _scalarI16(_src._scalarI16)
    , _scalarI32(_src._scalarI32)
    , _scalarI64(_src._scalarI64)
    , _scalarFixedI16(_src._scalarFixedI16)
    , _scalarFixedI32(_src._scalarFixedI32)
    , _scalarFixedI64(_src._scalarFixedI64)
    , _scalarFloat(_src._scalarFloat)
    , _scalarDouble(_src._scalarDouble)
    , _scalarString(_src._scalarString)
    , _scalarBytes(_src._scalarBytes)
    , _scalarEnum(_src._scalarEnum)
    , _listBoolean(_src._listBoolean)
    , _listInt(_src._listInt)
    , _listFloat(_src._listFloat)
    , _listString(_src._listString)
    , _listEnum(_src._listEnum)
    , _setInt(_src._setInt)
    , _setString(_src._setString)
    , _setEnum(_src._setEnum)
    , _mapIntString(_src._mapIntString)
    , _mapStringInt(_src._mapStringInt)
    , _mapEnumStruct(_src._mapEnumStruct)
    , _unused(_src._unused)
  {}

  coda::descriptors::StructDescriptor* descriptor() const {
    return &DESCRIPTOR;
  }

  coda::runtime::Object* clone() const {
    return new S1(*this);
  }

  bool equals(const coda::runtime::Object* other) const;
  size_t hashValue() const;
  void freezeImpl();
  void endWrite(coda::io::Encoder* encoder) const;

  bool hasScalarBoolean() const {
    return fieldsPresent.test(HAS_SCALAR_BOOLEAN);
  }

  bool isScalarBoolean() const {
    return _scalarBoolean;
  }

  S1& setScalarBoolean(bool scalarBoolean) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_BOOLEAN);
    _scalarBoolean = scalarBoolean;
    return *this;
  }

  S1& clearScalarBoolean() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_BOOLEAN);
    _scalarBoolean = false;
    return *this;
  }

  bool hasScalarI16() const {
    return fieldsPresent.test(HAS_SCALAR_I16);
  }

  int16_t getScalarI16() const {
    return _scalarI16;
  }

  S1& setScalarI16(int16_t scalarI16) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_I16);
    _scalarI16 = scalarI16;
    return *this;
  }

  S1& clearScalarI16() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_I16);
    _scalarI16 = 0;
    return *this;
  }

  bool hasScalarI32() const {
    return fieldsPresent.test(HAS_SCALAR_I32);
  }

  int32_t getScalarI32() const {
    return _scalarI32;
  }

  S1& setScalarI32(int32_t scalarI32) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_I32);
    _scalarI32 = scalarI32;
    return *this;
  }

  S1& clearScalarI32() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_I32);
    _scalarI32 = 0;
    return *this;
  }

  bool hasScalarI64() const {
    return fieldsPresent.test(HAS_SCALAR_I64);
  }

  int32_t getScalarI64() const {
    return _scalarI64;
  }

  S1& setScalarI64(int32_t scalarI64) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_I64);
    _scalarI64 = scalarI64;
    return *this;
  }

  S1& clearScalarI64() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_I64);
    _scalarI64 = 0;
    return *this;
  }

  bool hasScalarFixedI16() const {
    return fieldsPresent.test(HAS_SCALAR_FIXED_I16);
  }

  int16_t getScalarFixedI16() const {
    return _scalarFixedI16;
  }

  S1& setScalarFixedI16(int16_t scalarFixedI16) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_FIXED_I16);
    _scalarFixedI16 = scalarFixedI16;
    return *this;
  }

  S1& clearScalarFixedI16() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_FIXED_I16);
    _scalarFixedI16 = 0;
    return *this;
  }

  bool hasScalarFixedI32() const {
    return fieldsPresent.test(HAS_SCALAR_FIXED_I32);
  }

  int32_t getScalarFixedI32() const {
    return _scalarFixedI32;
  }

  S1& setScalarFixedI32(int32_t scalarFixedI32) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_FIXED_I32);
    _scalarFixedI32 = scalarFixedI32;
    return *this;
  }

  S1& clearScalarFixedI32() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_FIXED_I32);
    _scalarFixedI32 = 0;
    return *this;
  }

  bool hasScalarFixedI64() const {
    return fieldsPresent.test(HAS_SCALAR_FIXED_I64);
  }

  int32_t getScalarFixedI64() const {
    return _scalarFixedI64;
  }

  S1& setScalarFixedI64(int32_t scalarFixedI64) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_FIXED_I64);
    _scalarFixedI64 = scalarFixedI64;
    return *this;
  }

  S1& clearScalarFixedI64() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_FIXED_I64);
    _scalarFixedI64 = 0;
    return *this;
  }

  bool hasScalarFloat() const {
    return fieldsPresent.test(HAS_SCALAR_FLOAT);
  }

  float getScalarFloat() const {
    return _scalarFloat;
  }

  S1& setScalarFloat(float scalarFloat) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_FLOAT);
    _scalarFloat = scalarFloat;
    return *this;
  }

  S1& clearScalarFloat() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_FLOAT);
    _scalarFloat = 0;
    return *this;
  }

  bool hasScalarDouble() const {
    return fieldsPresent.test(HAS_SCALAR_DOUBLE);
  }

  double getScalarDouble() const {
    return _scalarDouble;
  }

  S1& setScalarDouble(double scalarDouble) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_DOUBLE);
    _scalarDouble = scalarDouble;
    return *this;
  }

  S1& clearScalarDouble() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_DOUBLE);
    _scalarDouble = 0;
    return *this;
  }

  bool hasScalarString() const {
    return fieldsPresent.test(HAS_SCALAR_STRING);
  }

  const std::string& getScalarString() const {
    return _scalarString;
  }

  S1& setScalarString(const std::string& scalarString) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_STRING);
    _scalarString = scalarString;
    return *this;
  }

  S1& clearScalarString() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_STRING);
    _scalarString.clear();
    return *this;
  }

  bool hasScalarBytes() const {
    return fieldsPresent.test(HAS_SCALAR_BYTES);
  }

  const std::string& getScalarBytes() const {
    return _scalarBytes;
  }

  S1& setScalarBytes(const std::string& scalarBytes) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_BYTES);
    _scalarBytes = scalarBytes;
    return *this;
  }

  S1& clearScalarBytes() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_BYTES);
    _scalarBytes.clear();
    return *this;
  }

  bool hasScalarEnum() const {
    return fieldsPresent.test(HAS_SCALAR_ENUM);
  }

  E getScalarEnum() const {
    return _scalarEnum;
  }

  S1& setScalarEnum(E scalarEnum) {
    checkMutable();
    fieldsPresent.set(HAS_SCALAR_ENUM);
    _scalarEnum = scalarEnum;
    return *this;
  }

  S1& clearScalarEnum() {
    checkMutable();
    fieldsPresent.reset(HAS_SCALAR_ENUM);
    _scalarEnum = E_E0;
    return *this;
  }

  const std::vector<bool>& getListBoolean() const {
    return _listBoolean;
  }

  std::vector<bool>& getMutableListBoolean() {
    checkMutable();
    return _listBoolean;
  }

  S1& setListBoolean(const std::vector<bool>& listBoolean) {
    checkMutable();
    _listBoolean = listBoolean;
    return *this;
  }

  S1& clearListBoolean() {
    checkMutable();
    _listBoolean.clear();
    return *this;
  }

  const std::vector<int32_t>& getListInt() const {
    return _listInt;
  }

  std::vector<int32_t>& getMutableListInt() {
    checkMutable();
    return _listInt;
  }

  S1& setListInt(const std::vector<int32_t>& listInt) {
    checkMutable();
    _listInt = listInt;
    return *this;
  }

  S1& clearListInt() {
    checkMutable();
    _listInt.clear();
    return *this;
  }

  const std::vector<float>& getListFloat() const {
    return _listFloat;
  }

  std::vector<float>& getMutableListFloat() {
    checkMutable();
    return _listFloat;
  }

  S1& setListFloat(const std::vector<float>& listFloat) {
    checkMutable();
    _listFloat = listFloat;
    return *this;
  }

  S1& clearListFloat() {
    checkMutable();
    _listFloat.clear();
    return *this;
  }

  const std::vector<std::string>& getListString() const {
    return _listString;
  }

  std::vector<std::string>& getMutableListString() {
    checkMutable();
    return _listString;
  }

  S1& setListString(const std::vector<std::string>& listString) {
    checkMutable();
    _listString = listString;
    return *this;
  }

  S1& clearListString() {
    checkMutable();
    _listString.clear();
    return *this;
  }

  const std::vector<E>& getListEnum() const {
    return _listEnum;
  }

  std::vector<E>& getMutableListEnum() {
    checkMutable();
    return _listEnum;
  }

  S1& setListEnum(const std::vector<E>& listEnum) {
    checkMutable();
    _listEnum = listEnum;
    return *this;
  }

  S1& clearListEnum() {
    checkMutable();
    _listEnum.clear();
    return *this;
  }

  const std::unordered_set<int32_t>& getSetInt() const {
    return _setInt;
  }

  std::unordered_set<int32_t>& getMutableSetInt() {
    checkMutable();
    return _setInt;
  }

  S1& setSetInt(const std::unordered_set<int32_t>& setInt) {
    checkMutable();
    _setInt = setInt;
    return *this;
  }

  S1& clearSetInt() {
    checkMutable();
    _setInt.clear();
    return *this;
  }

  const std::unordered_set<std::string>& getSetString() const {
    return _setString;
  }

  std::unordered_set<std::string>& getMutableSetString() {
    checkMutable();
    return _setString;
  }

  S1& setSetString(const std::unordered_set<std::string>& setString) {
    checkMutable();
    _setString = setString;
    return *this;
  }

  S1& clearSetString() {
    checkMutable();
    _setString.clear();
    return *this;
  }

  const std::unordered_set<E, coda::runtime::EnumHash<E> >& getSetEnum() const {
    return _setEnum;
  }

  std::unordered_set<E, coda::runtime::EnumHash<E> >& getMutableSetEnum() {
    checkMutable();
    return _setEnum;
  }

  S1& setSetEnum(const std::unordered_set<E, coda::runtime::EnumHash<E> >& setEnum) {
    checkMutable();
    _setEnum = setEnum;
    return *this;
  }

  S1& clearSetEnum() {
    checkMutable();
    _setEnum.clear();
    return *this;
  }

  const std::unordered_map<int32_t, std::string>& getMapIntString() const {
    return _mapIntString;
  }

  std::unordered_map<int32_t, std::string>& getMutableMapIntString() {
    checkMutable();
    return _mapIntString;
  }

  S1& putMapIntString(int32_t key, const std::string& value) {
    checkMutable();
    _mapIntString[key] = value;
    return *this;
  }

  S1& setMapIntString(const std::unordered_map<int32_t, std::string>& mapIntString) {
    checkMutable();
    _mapIntString = mapIntString;
    return *this;
  }

  S1& clearMapIntString() {
    checkMutable();
    _mapIntString.clear();
    return *this;
  }

  const std::unordered_map<std::string, int32_t>& getMapStringInt() const {
    return _mapStringInt;
  }

  std::unordered_map<std::string, int32_t>& getMutableMapStringInt() {
    checkMutable();
    return _mapStringInt;
  }

  S1& putMapStringInt(const std::string& key, int32_t value) {
    checkMutable();
    _mapStringInt[key] = value;
    return *this;
  }

  S1& setMapStringInt(const std::unordered_map<std::string, int32_t>& mapStringInt) {
    checkMutable();
    _mapStringInt = mapStringInt;
    return *this;
  }

  S1& clearMapStringInt() {
    checkMutable();
    _mapStringInt.clear();
    return *this;
  }

  const std::unordered_map<E, S1*, coda::runtime::EnumHash<E> >& getMapEnumStruct() const {
    return _mapEnumStruct;
  }

  std::unordered_map<E, S1*, coda::runtime::EnumHash<E> >& getMutableMapEnumStruct() {
    checkMutable();
    return _mapEnumStruct;
  }

  S1& putMapEnumStruct(E key, S1* value) {
    checkMutable();
    _mapEnumStruct[key] = value;
    return *this;
  }

  S1& setMapEnumStruct(const std::unordered_map<E, S1*, coda::runtime::EnumHash<E> >& mapEnumStruct) {
    checkMutable();
    _mapEnumStruct = mapEnumStruct;
    return *this;
  }

  S1& clearMapEnumStruct() {
    checkMutable();
    _mapEnumStruct.clear();
    return *this;
  }

  bool hasUnused() const {
    return fieldsPresent.test(HAS_UNUSED);
  }

  int32_t getUnused() const {
    return _unused;
  }

  S1& setUnused(int32_t unused) {
    checkMutable();
    fieldsPresent.set(HAS_UNUSED);
    _unused = unused;
    return *this;
  }

  S1& clearUnused() {
    checkMutable();
    fieldsPresent.reset(HAS_UNUSED);
    _unused = 0;
    return *this;
  }

  static coda::descriptors::StructDescriptor DESCRIPTOR;
  static S1 DEFAULT_INSTANCE;
  static const uint32_t TYPE_ID;

private:
  std::bitset<13> fieldsPresent;
  bool _scalarBoolean;
  int16_t _scalarI16;
  int32_t _scalarI32;
  int32_t _scalarI64;
  int16_t _scalarFixedI16;
  int32_t _scalarFixedI32;
  int32_t _scalarFixedI64;
  float _scalarFloat;
  double _scalarDouble;
  std::string _scalarString;
  std::string _scalarBytes;
  E _scalarEnum;
  std::vector<bool> _listBoolean;
  std::vector<int32_t> _listInt;
  std::vector<float> _listFloat;
  std::vector<std::string> _listString;
  std::vector<E> _listEnum;
  std::unordered_set<int32_t> _setInt;
  std::unordered_set<std::string> _setString;
  std::unordered_set<E, coda::runtime::EnumHash<E> > _setEnum;
  std::unordered_map<int32_t, std::string> _mapIntString;
  std::unordered_map<std::string, int32_t> _mapStringInt;
  std::unordered_map<E, S1*, coda::runtime::EnumHash<E> > _mapEnumStruct;
  int32_t _unused;

  bool isFieldPresent(size_t index) const {
    return fieldsPresent[index];
  }

  void setFieldPresent(size_t index, bool present) {
    fieldsPresent[index] = present;
  }

  static coda::descriptors::FieldDescriptor Field_scalarBoolean;
  static coda::descriptors::FieldDescriptor Field_scalarI16;
  static coda::descriptors::FieldDescriptor Field_scalarI32;
  static coda::descriptors::FieldDescriptor Field_scalarI64;
  static coda::descriptors::FieldDescriptor Field_scalarFixedI16;
  static coda::descriptors::FieldDescriptor Field_scalarFixedI32;
  static coda::descriptors::FieldDescriptor Field_scalarFixedI64;
  static coda::descriptors::FieldDescriptor Field_scalarFloat;
  static coda::descriptors::FieldDescriptor Field_scalarDouble;
  static coda::descriptors::FieldDescriptor Field_scalarString;
  static coda::descriptors::FieldDescriptor Field_scalarBytes;
  static coda::descriptors::FieldDescriptor Field_scalarEnum;
  static coda::descriptors::FieldDescriptor Field_listBoolean;
  static coda::descriptors::FieldDescriptor Field_listInt;
  static coda::descriptors::FieldDescriptor Field_listFloat;
  static coda::descriptors::FieldDescriptor Field_listString;
  static coda::descriptors::FieldDescriptor Field_listEnum;
  static coda::descriptors::FieldDescriptor Field_setInt;
  static coda::descriptors::FieldDescriptor Field_setString;
  static coda::descriptors::FieldDescriptor Field_setEnum;
  static coda::descriptors::FieldDescriptor Field_mapIntString;
  static coda::descriptors::FieldDescriptor Field_mapStringInt;
  static coda::descriptors::FieldDescriptor Field_mapEnumStruct;
  static coda::descriptors::FieldDescriptor Field_unused;
  static coda::descriptors::FieldDescriptor* Fields[];
};

// ============================================================================
// S2
// ============================================================================

class S2 : public S1 {
public:
  enum FieldPresentBits {
    HAS_LEFT,
    HAS_RIGHT,
  };

  S2();
  S2(const S2& _src)
    : S1(*this)
    , _left(_src._left)
    , _right(_src._right)
  {}

  coda::descriptors::StructDescriptor* descriptor() const {
    return &DESCRIPTOR;
  }

  coda::runtime::Object* clone() const {
    return new S2(*this);
  }

  bool equals(const coda::runtime::Object* other) const;
  size_t hashValue() const;
  void freezeImpl();
  void beginWrite(coda::io::Encoder* encoder) const;
  void endWrite(coda::io::Encoder* encoder) const;

  bool hasLeft() const {
    return fieldsPresent.test(HAS_LEFT);
  }

  const S1* getLeft() const {
    return _left;
  }

  S1* getMutableLeft() {
    checkMutable();
    fieldsPresent.set(HAS_LEFT);
    return _left;
  }

  S2& setLeft(S1* left) {
    checkMutable();
    fieldsPresent.set(HAS_LEFT);
    _left = left;
    return *this;
  }

  S2& clearLeft() {
    checkMutable();
    fieldsPresent.reset(HAS_LEFT);
    _left = NULL;
    return *this;
  }

  bool hasRight() const {
    return fieldsPresent.test(HAS_RIGHT);
  }

  const S1* getRight() const {
    return _right;
  }

  S1* getMutableRight() {
    checkMutable();
    fieldsPresent.set(HAS_RIGHT);
    return _right;
  }

  S2& setRight(S1* right) {
    checkMutable();
    fieldsPresent.set(HAS_RIGHT);
    _right = right;
    return *this;
  }

  S2& clearRight() {
    checkMutable();
    fieldsPresent.reset(HAS_RIGHT);
    _right = NULL;
    return *this;
  }

  static coda::descriptors::StructDescriptor DESCRIPTOR;
  static S2 DEFAULT_INSTANCE;
  static const uint32_t TYPE_ID;

private:
  std::bitset<2> fieldsPresent;
  S1* _left;
  S1* _right;

  bool isFieldPresent(size_t index) const {
    return fieldsPresent[index];
  }

  void setFieldPresent(size_t index, bool present) {
    fieldsPresent[index] = present;
  }

  static coda::descriptors::FieldDescriptor Field_left;
  static coda::descriptors::FieldDescriptor Field_right;
  static coda::descriptors::FieldDescriptor* Fields[];
};

// ============================================================================
// S3
// ============================================================================

class S3 : public S1 {
public:
  S3()
  {}

  S3(const S3& _src)
    : S1(*this)
    , _sList(_src._sList)
    , _sSet(_src._sSet)
    , _sMap(_src._sMap)
  {}

  coda::descriptors::StructDescriptor* descriptor() const {
    return &DESCRIPTOR;
  }

  coda::runtime::Object* clone() const {
    return new S3(*this);
  }

  bool equals(const coda::runtime::Object* other) const;
  size_t hashValue() const;
  void freezeImpl();
  void beginWrite(coda::io::Encoder* encoder) const;
  void endWrite(coda::io::Encoder* encoder) const;

  const std::vector<S1*>& getSList() const {
    return _sList;
  }

  std::vector<S1*>& getMutableSList() {
    checkMutable();
    return _sList;
  }

  S3& setSList(const std::vector<S1*>& sList) {
    checkMutable();
    _sList = sList;
    return *this;
  }

  S3& clearSList() {
    checkMutable();
    _sList.clear();
    return *this;
  }

  const std::unordered_set<S1*>& getSSet() const {
    return _sSet;
  }

  std::unordered_set<S1*>& getMutableSSet() {
    checkMutable();
    return _sSet;
  }

  S3& setSSet(const std::unordered_set<S1*>& sSet) {
    checkMutable();
    _sSet = sSet;
    return *this;
  }

  S3& clearSSet() {
    checkMutable();
    _sSet.clear();
    return *this;
  }

  const std::unordered_map<std::string, S1*>& getSMap() const {
    return _sMap;
  }

  std::unordered_map<std::string, S1*>& getMutableSMap() {
    checkMutable();
    return _sMap;
  }

  S3& putSMap(const std::string& key, S1* value) {
    checkMutable();
    _sMap[key] = value;
    return *this;
  }

  S3& setSMap(const std::unordered_map<std::string, S1*>& sMap) {
    checkMutable();
    _sMap = sMap;
    return *this;
  }

  S3& clearSMap() {
    checkMutable();
    _sMap.clear();
    return *this;
  }

  static coda::descriptors::StructDescriptor DESCRIPTOR;
  static S3 DEFAULT_INSTANCE;
  static const uint32_t TYPE_ID;

private:
  std::vector<S1*> _sList;
  std::unordered_set<S1*> _sSet;
  std::unordered_map<std::string, S1*> _sMap;

  static coda::descriptors::FieldDescriptor Field_sList;
  static coda::descriptors::FieldDescriptor Field_sSet;
  static coda::descriptors::FieldDescriptor Field_sMap;
  static coda::descriptors::FieldDescriptor* Fields[];
};

extern coda::descriptors::StaticFileDescriptor FILE;

} // namespace sample

#endif // SAMPLE
