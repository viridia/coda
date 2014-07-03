// ============================================================================
// Coda Type Registry
// ============================================================================

#ifndef CODA_RUNTIME_TYPEREGISTRY_H
#define CODA_RUNTIME_TYPEREGISTRY_H 1

#ifndef CODA_DESCRIPTORS_H
  #include "coda/descriptors.h"
#endif

namespace coda {
namespace runtime {

class TypeRegistry {
public:
  typedef std::unordered_map<int32_t, const coda::descriptors::StructType*> typeid_map;
  typedef std::unordered_map<const coda::descriptors::StructType*, typeid_map> subtype_map;
  typedef std::unordered_multimap<
      const coda::descriptors::StructType*, const coda::descriptors::ExtensionField*> extension_map;

  /** Register a type as being a subtype of a given base type. */
  TypeRegistry& addSubtype(const coda::descriptors::StructType* subtype);

  /** Retrieve a subtype of a base type by subtype ID. */
  const coda::descriptors::StructType* getSubtype(
      const coda::descriptors::StructType* base, int32_t typeId) const;

  /** Retrieve all subtype of a base type. */
  const typeid_map& getSubtypes(const coda::descriptors::StructType* base) const;

  /** Add all subtypes and extensions registered within a file. */
  TypeRegistry& addFile(const coda::descriptors::FileDescriptor* file);

  /** Singleton instance of default type registry. */
  static TypeRegistry &getInstance();

private:
  subtype_map subtypes;
  extension_map extensions;

  static typeid_map emptyTypeIdMap;

  void addStruct(const coda::descriptors::StructType* st);
};

}} // namespace

#endif /* CODA_RUNTIME_TYPEREGISTRY_H */
