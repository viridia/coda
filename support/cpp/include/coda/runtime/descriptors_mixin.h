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
  /** Allocate a temporary instance of this type. Used in deserialization. */
  virtual void* makeTemp() const { return NULL; };

  /** Free a previously allocated instance of this type. Used in deserialization. */
  virtual void freeTemp(void*) const {};

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
