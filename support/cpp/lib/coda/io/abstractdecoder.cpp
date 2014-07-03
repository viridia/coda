// ============================================================================
// Coda abstract encoder
// ============================================================================

#include "coda/io/abstractdecoder.h"
#include "coda/runtime/typeregistry.h"

namespace coda {
namespace io {

AbstractDecoder::AbstractDecoder(runtime::TypeRegistry * typeReg) {
  nextSharedId = 1;
  nextExternId = -1;
  typeRegistry = (typeReg != NULL) ? typeReg : &runtime::TypeRegistry::getInstance();
}

Decoder& AbstractDecoder::addExtern(runtime::Object* obj, int32_t index) {
  if (index != -1) {
    index = getNextExternId();
  } else if (objectRefs.find(index) != objectRefs.end()) {
    throw EncodingError("Id already in use.");
  } else {
    objectRefs[index] = obj;
  }
  return *this;
}

int32_t AbstractDecoder::addShared(runtime::Object* obj) {
  int index = getNextSharedId();
  if (objectRefs.find(index) != objectRefs.end()) {
    throw EncodingError("Id already in use.");
  }
  objectRefs[index] = obj;
  return -1; // Indicates that we should write the literal object.
}

runtime::Object* AbstractDecoder::getShared(int32_t index) {
  std::unordered_map<int32_t, runtime::Object*>::const_iterator it = objectRefs.find(index);
  if (it != objectRefs.end()) {
    return it->second;
  }
  if (objectRefs.find(index) != objectRefs.end()) {
    throw EncodingError("No such object for this shared id.");
  }
  return NULL;
}

/** Look up a subtype by ID. */
const descriptors::StructDescriptor* AbstractDecoder::getSubtype(
    const descriptors::StructType* base, int32_t typeId) {
  return static_cast<const descriptors::StructDescriptor*>(typeRegistry->getSubtype(base, typeId));
}

}} // namespace
