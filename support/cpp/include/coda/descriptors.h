// ============================================================================
// Coda Descriptors
// ============================================================================

#ifndef CODA_DESCRIPTORS_H
#define CODA_DESCRIPTORS_H 1

#ifndef CODA_RUNTIME_OBJECT_H
  #include "coda/runtime/object.h"
#endif

#ifndef CODA_RUNTIME_DESCRIPTORS_GENERATED
  #include "coda/runtime/descriptors_generated.h"
#endif

#ifndef CODA_RUNTIME_DESCRIPTORS_STATIC
  #include "coda/runtime/descriptors_static.h"
#endif

namespace coda {
namespace io {
class AbstractDecoder;
}
namespace descriptors {

class EnumDescriptor;

// Macro for computing field offsets
#define CODA_OFFSET_OF(ty, fld) ((size_t)&((ty*)0)->fld)

// ============================================================================
// FieldDecriptor
// ============================================================================

class FieldDescriptor : public StructType::Field {
public:
  friend class coda::io::AbstractDecoder;

  FieldDescriptor(const char* name, int32_t id, Type& type, FieldOptions& options, size_t offset) {
    setName(name);
    setType(&type);
    setId(id);
    setOptions(&options);
    fieldOffset = offset;
  }

  // Interface for setting scalar and object values
  void setBoolean(runtime::Object* instance, bool value) const;
  void setInteger16(runtime::Object* instance, int16_t value) const;
  void setInteger32(runtime::Object* instance, int32_t value) const;
  void setInteger64(runtime::Object* instance, int64_t value) const;
  void setFloat(runtime::Object* instance, float value) const;
  void setDouble(runtime::Object* instance, double value) const;
  void setString(runtime::Object* instance, const std::string& value) const;
  void setBytes(runtime::Object* instance, const std::string& value) const;
  void setObject(runtime::Object* instance, runtime::Object* value) const;

  // Interface for setting lists and sets. The begin and end pointers will be cast to iterators
  // of the appropriate type.
  void setList(runtime::Object* instance, void* begin, void* end) const;

private:
  void* fieldAddress(runtime::Object* instance) const {
    return (void*) ((uint8_t*)instance + fieldOffset);
  }

  size_t fieldOffset;
};

// ============================================================================
// StructDescriptor
// ============================================================================

class StructDescriptor : public StructType {
public:
  StructDescriptor() : defaultInstance(NULL), create(NULL) {}

  StructDescriptor(
      const char* name,
      uint32_t typeId,
      runtime::Object* staticDefaultInstance,
      FileDescriptor& file,
      StructDescriptor* enclosingType,
      StructDescriptor* baseType,
      StructOptions& options,
      StaticArrayRef<StructDescriptor*> structs,
      StaticArrayRef<EnumDescriptor*> enums,
      StaticArrayRef<FieldDescriptor*> fields,
      runtime::Object* (*createFn)())
    : defaultInstance(staticDefaultInstance)
    , create(createFn)
  {
    setName(name);
    setTypeId((uint32_t) typeId);
    setFile(&file);
    setEnclosingType(enclosingType);
    setBaseType(baseType);
    setOptions(&options);
    getMutableStructs().assign(structs.begin(), structs.end());
    getMutableEnums().assign(enums.begin(), enums.end());
    getMutableFields().assign(fields.begin(), fields.end());
    buildFieldMaps();
  }

  /** Lookup a field by name. Only looks at fields defined in this type, not inherited fields. */
  const FieldDescriptor* getField(const std::string& fieldName) const;

  /** Lookup a field by id. Only looks at fields defined in this type, not inherited fields. */
  const FieldDescriptor* getField(int32_t fieldId) const;

  /** The default instance for a struct type. */
  const runtime::Object* getDefaultInstance() const { return defaultInstance; }

  runtime::Object* newInstance() const {
    return (*create)();
  }

  void* makeTemp() const { return new (runtime::Object*); }
  void freeTemp(void* ptr) const { delete (runtime::Object**) ptr; }

private:
  friend class coda::descriptors::StaticFileDescriptor;

  runtime::Object* defaultInstance;
  runtime::Object* (*create)();

  // Only freeze objects known to be defined in the same file.
  void freezeLocal();

  void buildFieldMaps();

  std::unordered_map<std::string, FieldDescriptor*> fieldByName;
  std::unordered_map<int32_t, FieldDescriptor*> fieldById;
};

// ============================================================================
// EnumDescriptor
// ============================================================================

class EnumDescriptor : public EnumType {
public:
  typedef int32_t cpp_type;

  class Value : public EnumType::Value {
  public:
    Value(const char* name, int32_t value) {
      setName(name);
      setValue(value);
    }
  };

  EnumDescriptor() {}

  EnumDescriptor(
      const char* name,
      EnumOptions& options,
      StaticArrayRef<Value*> values) {
    setName(name);
    setOptions(&options);
    getMutableValues().assign(values.begin(), values.end());
  }

  void* makeTemp() const { return new int32_t; }
  void freeTemp(void* ptr) const { delete (int32_t*) ptr; }

private:
  friend class coda::descriptors::StructDescriptor;
  friend class coda::descriptors::StaticFileDescriptor;

  // Only freeze objects known to be defined in the same file.
  void freezeLocal();
};

// ============================================================================
// Helper methods for type-testing and casting.
// ============================================================================

/**
 * Returns true if the object is non-null and an instance of type T.
 * Usage: if (isa<SomeType>(obj)) { ... }
 */
template<class T>
inline bool isa(coda::runtime::Object* obj) {
  return obj != NULL && obj->isInstanceOf(&T::DESCRIPTOR);
}

/**
 * Returns true if the object is either null or an instance of type T.
 * Usage: if (isa_or_null<SomeType>(obj)) { ... }
 */
template<class T>
inline bool isa_or_null(coda::runtime::Object* obj) {
  return obj == NULL || obj->isInstanceOf(&T::DESCRIPTOR);
}

/**
 * Dynamic cast operator that works with type descriptors.
 * Usage: SomeType* value = dyn_cast<SomeType>(obj);
 */
template<class T>
inline T* dyn_cast(coda::runtime::Object* obj) {
  return isa<T>(obj) ? static_cast<T*>(obj) : NULL;
}

template<class T>
inline const T* dyn_cast(const coda::runtime::Object* obj) {
  return isa<T>(obj) ? static_cast<const T*>(obj) : NULL;
}

// ============================================================================
// Helper methods for reporting type errors.
// ============================================================================

void describeType(const coda::descriptors::Type* type, std::string& out);

}} // namespace

#endif // CODA_DESCRIPTORS_H
