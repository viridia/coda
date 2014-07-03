// ============================================================================
// Coda Type Registry
// ============================================================================

#include "coda/runtime/typeregistry.h"
#include "coda/descriptors.h"

#include <assert.h>

namespace coda {
namespace runtime {

using namespace coda::descriptors;

TypeRegistry &TypeRegistry::getInstance() {
  static TypeRegistry instance;
  return instance;
}

TypeRegistry& TypeRegistry::addSubtype(const StructType* subtype) {
  assert(subtype->getTypeId() > 0);
  const StructType* base = subtype->getBaseType();
  assert(base != NULL);
  while (base->getBaseType() != NULL) {
    base = base->getBaseType();
  }
  subtype_map::iterator si = subtypes.find(base);
  if (si == subtypes.end()) {
    si = subtypes.insert(std::make_pair(base, typeid_map())).first;
  }
  typeid_map& subtypesForBase = si->second;
  typeid_map::iterator it = subtypesForBase.find(subtype->getTypeId());
  if (it != subtypesForBase.end()) {
    throw std::runtime_error(
        "Error registering type " + subtype->getFullName() + ": subtype ID already registered.");
  }
  subtypesForBase[subtype->getTypeId()] = subtype;
  assert(getSubtype(base, subtype->getTypeId()) == subtype);
  return *this;
}

const coda::descriptors::StructType* TypeRegistry::getSubtype(
    const StructType* base, int32_t typeId) const {
  assert(base->getBaseType() == NULL);
  subtype_map::const_iterator it = subtypes.find(base);
  if (it == subtypes.end()) {
    return NULL;
  }
  const typeid_map& typeIds = it->second;
  typeid_map::const_iterator ti = typeIds.find(typeId);
  if (ti == typeIds.end()) {
    return NULL;
  }
  return ti->second;
}

//const typeid_map& TypeRegistry::getSubtypes(const StructType* base) const {
//  return self.__subtypes.get(id(base), {})
//}

TypeRegistry& TypeRegistry::addFile(const FileDescriptor* file) {
  const std::vector<StructType*>& structs = file->getStructs();
  for (std::vector<StructType*>::const_iterator it = structs.begin(), itEnd = structs.end();
      it != itEnd; ++it) {
    addStruct(*it);
  }
  return *this;
}

void TypeRegistry::addStruct(const StructType* st) {
  if (st->getBaseType() != NULL) {
    addSubtype(st);
  }
  const std::vector<StructType*>& structs = st->getStructs();
  for (std::vector<StructType*>::const_iterator it = structs.begin(), itEnd = structs.end();
      it != itEnd; ++it) {
    addStruct(*it);
  }
}

}} // namespace
