// ============================================================================
// Coda base types
// ============================================================================

#include "coda/runtime/object.h"
#include "coda/descriptors.h"

namespace coda {
namespace runtime {

IllegalMutationError::IllegalMutationError(const Object* object)
  : CodaError("Attempt to modify object of type '" + object->descriptor()->getName() + "'.") {
}

int32_t Object::typeId() const {
  return descriptor()->getTypeId();
}

bool Object::isInstanceOf(const descriptors::StructType* st) const {
  const descriptors::StructType* thisType = this->descriptor();
  while (thisType) {
    if (thisType == st) {
      return true;
    }
    thisType = thisType->getBaseType();
  }
  return false;
}

size_t Object::hashValue() const {
  return hash_pointer(descriptor());
}

void Object::checkMutable() const throw(IllegalMutationError) {
  if (!_mutable) {
    throw IllegalMutationError(this);
  }
}

void Object::freeze() {
  if (_mutable) {
    _mutable = false;
    freezeImpl();
  }
}

}} // namespace
