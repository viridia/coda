// ============================================================================
// Mixin classes for generated descriptors
// ============================================================================

#ifndef CODA_RUNTIME_DESCRIPTORS_MIXIN_H
#define CODA_RUNTIME_DESCRIPTORS_MIXIN_H 1

#include <stddef.h>

namespace coda {
namespace descriptors {

// ============================================================================
// Mixin classses for type. These handle data conversion.
// ============================================================================

/** Mixin class for Type. */
class TypeMixin {
public:
  /**
   * Given a destination address, copy the data from the source address to the destination.
   * This simply copies the data from the source address to the destination address.
   */
  virtual void put(void* dst, void* src) const {}

  /**
   * Given the address of a collection, copy the data from the source and add it to the collection.
   * For map types, this treats the data at the source address as a key, inserts it into the map,
   * and returns the address of the associated (now default-constucted) value.
   */
  virtual void* add(void* collection, void* src) const { return NULL; }

protected:
  virtual ~TypeMixin() {}
};

/** Mixin class for DeclType. */
class DeclTypeMixin {
public:
  const std::string getFullName() const;
};

}} // namespace

#endif // CODA_DESCRIPTORS_MIXIN_H
