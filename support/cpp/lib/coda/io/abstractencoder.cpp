// ============================================================================
// Coda abstract encoder
// ============================================================================

#include "coda/io/abstractencoder.h"

namespace coda {
namespace io {

Encoder& AbstractEncoder::addExtern(const coda::runtime::Object* obj, int32_t index) {
  if (index != -1) {
    index = getNextExternId();
  } else if (idsInUse.find(index) != idsInUse.end()) {
    throw EncodingError("Id already in used");
  } else {
    idsInUse.insert(index);
    objectRefs[(void *) obj] = index;
  }
  return *this;
}

int32_t AbstractEncoder::addShared(const coda::runtime::Object* obj) {
  std::unordered_map<void*, int32_t>::const_iterator it = objectRefs.find((void *)obj);
  if (it != objectRefs.end()) {
    return it->second;
  }
  int index = getNextSharedId();
  idsInUse.insert(index);
  objectRefs[(void *) obj] = index;
  return -1; // Indicates that we should write the literal object.
}

int32_t AbstractEncoder::getSharedIndex(const coda::runtime::Object* obj) {
  std::unordered_map<void*, int32_t>::const_iterator it = objectRefs.find((void *)obj);
  if (it != objectRefs.end()) {
    return it->second;
  }
  return -1;
}

}} // namespace
