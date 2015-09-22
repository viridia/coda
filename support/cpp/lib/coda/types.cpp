// ============================================================================
// Coda base types
// ============================================================================

#include "coda/types.h"
#include "coda/descriptors.h"

namespace coda {
namespace types {

using namespace coda::descriptors;

// ============================================================================
// Boolean type descriptor
// ============================================================================

Boolean Boolean::DESCRIPTOR;

Boolean::Boolean() {
  freeze();
  DEFAULT_INSTANCE.freeze();
}

// ============================================================================
// Integer16 type descriptor
// ============================================================================

Integer16 Integer16::DESCRIPTOR;

Integer16::Integer16() {
  setBits(16);
  freeze();
  DEFAULT_INSTANCE.freeze();
}

// ============================================================================
// Integer32 type descriptor
// ============================================================================

Integer32 Integer32::DESCRIPTOR;

Integer32::Integer32() {
  setBits(32);
  freeze();
  DEFAULT_INSTANCE.freeze();
}

// ============================================================================
// Integer64 type descriptor
// ============================================================================

Integer64 Integer64::DESCRIPTOR;

Integer64::Integer64() {
  setBits(64);
  freeze();
  DEFAULT_INSTANCE.freeze();
}

// ============================================================================
// Float type descriptor
// ============================================================================

Float Float::DESCRIPTOR;

Float::Float() {
  freeze();
  DEFAULT_INSTANCE.freeze();
}

// ============================================================================
// Double type descriptor
// ============================================================================

Double Double::DESCRIPTOR;

Double::Double() {
  freeze();
  DEFAULT_INSTANCE.freeze();
}

// ============================================================================
// String type descriptor
// ============================================================================

String String::DESCRIPTOR;

String::String() {
  freeze();
  DEFAULT_INSTANCE.freeze();
}

// ============================================================================
// Bytes type descriptor
// ============================================================================

Bytes Bytes::DESCRIPTOR;

Bytes::Bytes() {
  freeze();
  DEFAULT_INSTANCE.freeze();
}

}} // namespace
