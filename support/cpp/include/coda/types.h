// ============================================================================
// Coda base types
// ============================================================================

#ifndef CODA_TYPES_H
#define CODA_TYPES_H 1

#ifndef CODA_DESCRIPTORS_H
  #include "coda/descriptors.h"
#endif

#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <assert.h>

namespace coda {
namespace types {

class Boolean : public coda::descriptors::BooleanType {
public:
  typedef bool cpp_type;

  Boolean();
  void put(void* dst, void* src) const;

  static Boolean DESCRIPTOR;
};

class Integer16 : public coda::descriptors::IntegerType {
public:
  typedef int16_t cpp_type;

  Integer16();
  void put(void* dst, void* src) const;

  static Integer16 DESCRIPTOR;
};

class Integer32 : public coda::descriptors::IntegerType {
public:
  typedef int32_t cpp_type;

  Integer32();
  void put(void* dst, void* src) const;

  static Integer32 DESCRIPTOR;
};

class Integer64 : public coda::descriptors::IntegerType {
public:
  typedef int64_t cpp_type;

  Integer64();
  void put(void* dst, void* src) const;

  static Integer64 DESCRIPTOR;
};

class Float : public coda::descriptors::FloatType {
public:
  typedef float cpp_type;

  Float();
  void put(void* dst, void* src) const;

  static Float DESCRIPTOR;
};

class Double : public coda::descriptors::DoubleType {
public:
  typedef double cpp_type;

  Double();
  void put(void* dst, void* src) const;

  static Double DESCRIPTOR;
};

class String : public coda::descriptors::StringType {
public:
  typedef std::string cpp_type;

  String();
  void put(void* dst, void* src) const;

  static String DESCRIPTOR;
};

class Bytes : public coda::descriptors::BytesType {
public:
  typedef std::string cpp_type;

  Bytes();
  void put(void* dst, void* src) const;

  static Bytes DESCRIPTOR;
};

template<class ElementType>
class List : public coda::descriptors::ListType {
public:
  typedef typename ElementType::cpp_type element_type;
  typedef std::vector<element_type> cpp_type;

  List() {
    setElementType(&ElementType::DESCRIPTOR);
    freeze();
  }

  void put(void* dst, void* src) const {
    ((cpp_type*) dst)->swap(*(cpp_type*) src);
  }

  void* add(void* collection, void* src) const {
    cpp_type* list = (cpp_type*) collection;
    if (src == NULL) {
      list->push_back(element_type());
    } else {
      list->push_back(*(element_type*)src);
    }
    return &list->back();
  }

  static List DESCRIPTOR;
};

template<class ElementType>
List<ElementType> List<ElementType>::DESCRIPTOR;

template<class ElementType>
class Set : public coda::descriptors::SetType {
public:
  typedef typename ElementType::cpp_type element_type;
  typedef std::unordered_set<element_type> cpp_type;

  Set() {
    setElementType(&ElementType::DESCRIPTOR);
    freeze();
  }

  void put(void* dst, void* src) const {
    ((cpp_type*) dst)->swap(*(cpp_type*) src);
  }

  void* add(void* collection, void* src) const {
    ((cpp_type*)collection)->insert(*(element_type*)src);
    return NULL;
  }

  static Set DESCRIPTOR;
};

template<class ElementType>
Set<ElementType> Set<ElementType>::DESCRIPTOR;

template<class KeyType, class ValueType>
class Map : public coda::descriptors::MapType {
public:
  typedef typename KeyType::cpp_type key_type;
  typedef typename ValueType::cpp_type value_type;
  typedef std::unordered_map<key_type, value_type> cpp_type;

  Map() {
    setKeyType(&KeyType::DESCRIPTOR);
    setValueType(&ValueType::DESCRIPTOR);
    assert(getKeyType() != NULL);
    assert(getValueType() != NULL);
    freeze();
  }
  void* add(void* collection, void* src) const {
    return &(*(cpp_type*)collection)[*(key_type*)src];
  }

  static Map DESCRIPTOR;
};

template<class KeyType, class ValueType>
Map<KeyType, ValueType> Map<KeyType, ValueType>::DESCRIPTOR;

template<class ElementType, bool Const, bool Shared>
class Modified : public coda::descriptors::ModifiedType {
public:
  typedef typename ElementType::cpp_type element_type;
  typedef element_type cpp_type;

  Modified() {
    setElementType(&ElementType::DESCRIPTOR);
    setConst(Const);
    setShared(Shared);
    freeze();
  }

  void put(void* dst, void* src) const {
    getElementType()->put(dst, src);
  }

  void* add(void* collection, void* src) const {
    return getElementType()->add(collection, src);
  }

  static Modified DESCRIPTOR;
};

template<class ElementType, bool Const, bool Shared>
Modified<ElementType, Const, Shared> Modified<ElementType, Const, Shared>::DESCRIPTOR;


}} // namespace

#endif // CODA_TYPES_H
