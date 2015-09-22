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
#include <utility>
#include <assert.h>

namespace coda {
namespace types {

/** Returns true if the given type kind can be represented as POD data which requires no
    construction or destruction step. */
inline bool isPodType(int32_t kind) {
  return (kind >= descriptors::TYPE_KIND_BOOL && kind <= descriptors::TYPE_KIND_DOUBLE) ||
      kind == descriptors::TYPE_KIND_STRUCT || kind == descriptors::TYPE_KIND_ENUM;
}

class Boolean : public coda::descriptors::BooleanType {
public:
  typedef bool cpp_type;

  Boolean();

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  static Boolean DESCRIPTOR;
};

class Integer16 : public coda::descriptors::IntegerType {
public:
  typedef int16_t cpp_type;

  Integer16();

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  static Integer16 DESCRIPTOR;
};

class Integer32 : public coda::descriptors::IntegerType {
public:
  typedef int32_t cpp_type;

  Integer32();

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  static Integer32 DESCRIPTOR;
};

class Integer64 : public coda::descriptors::IntegerType {
public:
  typedef int64_t cpp_type;

  Integer64();

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  static Integer64 DESCRIPTOR;
};

class Float : public coda::descriptors::FloatType {
public:
  typedef float cpp_type;

  Float();

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  static Float DESCRIPTOR;
};

class Double : public coda::descriptors::DoubleType {
public:
  typedef double cpp_type;

  Double();

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  static Double DESCRIPTOR;
};

class String : public coda::descriptors::StringType {
public:
  typedef std::string cpp_type;

  String();

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  static String DESCRIPTOR;
};

class Bytes : public coda::descriptors::BytesType {
public:
  typedef std::string cpp_type;

  Bytes();

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  static Bytes DESCRIPTOR;
};

class GenericList : public coda::descriptors::ListType {
public:
  virtual void* append(void* collection, void* element) const = 0;
};

template<class ElementType>
class List : public GenericList {
public:
  typedef typename ElementType::cpp_type element_type;
  typedef std::vector<element_type> cpp_type;

  List() {
    setElementType(&ElementType::DESCRIPTOR);
    freeze();
  }

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  void* append(void* collection, void* src) const {
    cpp_type* list = (cpp_type*) collection;
    list->push_back(std::move(*(element_type*)src));
    return &list->back();
  }

  static List DESCRIPTOR;
};

template<class ElementType>
List<ElementType> List<ElementType>::DESCRIPTOR;

class GenericSet : public coda::descriptors::SetType {
public:
  virtual void* insert(void* collection, void* element) const = 0;
};

template<class ElementType>
class Set : public GenericSet {
public:
  typedef typename ElementType::cpp_type element_type;
  typedef std::unordered_set<element_type> cpp_type;

  Set() {
    setElementType(&ElementType::DESCRIPTOR);
    freeze();
  }

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  void* insert(void* collection, void* src) const {
    ((cpp_type*)collection)->insert(std::move(*(element_type*)src));
    return NULL;
  }

  static Set DESCRIPTOR;
};

template<class ElementType>
Set<ElementType> Set<ElementType>::DESCRIPTOR;

class GenericMap : public coda::descriptors::MapType {
public:
  virtual void add(void* collection, void* key, void *value) const = 0;
};

template<class KeyType, class ValueType>
class Map : public GenericMap {
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

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  void add(void* collection, void* key, void *value) const {
    (*(cpp_type*)collection)[*(key_type*)key] = std::move(*(value_type*)value);
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

  void* makeTemp() const { return new cpp_type; }
  void freeTemp(void* ptr) const { delete (cpp_type*) ptr; }

  static Modified DESCRIPTOR;
};

template<class ElementType, bool Const, bool Shared>
Modified<ElementType, Const, Shared> Modified<ElementType, Const, Shared>::DESCRIPTOR;


}} // namespace

#endif // CODA_TYPES_H
