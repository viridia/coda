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

void Boolean::put(void* dst, void* src) const {
  *(bool*)dst = *(bool*)src;
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

void Integer16::put(void* dst, void* src) const {
  *(int16_t*)dst = *(int16_t*)src;
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

void Integer32::put(void* dst, void* src) const {
  *(int32_t*)dst = *(int32_t*)src;
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

void Integer64::put(void* dst, void* src) const {
  *(int64_t*)dst = *(int64_t*)src;
}

// ============================================================================
// Float type descriptor
// ============================================================================

Float Float::DESCRIPTOR;

Float::Float() {
  freeze();
  DEFAULT_INSTANCE.freeze();
}

void Float::put(void* dst, void* src) const {
  *(float*)dst = *(float*)src;
}

// ============================================================================
// Double type descriptor
// ============================================================================

Double Double::DESCRIPTOR;

Double::Double() {
  freeze();
  DEFAULT_INSTANCE.freeze();
}

void Double::put(void* dst, void* src) const {
  *(double*)dst = *(double*)src;
}

// ============================================================================
// String type descriptor
// ============================================================================

String String::DESCRIPTOR;

String::String() {
  freeze();
  DEFAULT_INSTANCE.freeze();
}

void String::put(void* dst, void* src) const {
  ((std::string*)dst)->swap(*(std::string*)src);
}

// ============================================================================
// Bytes type descriptor
// ============================================================================

Bytes Bytes::DESCRIPTOR;

Bytes::Bytes() {
  freeze();
  DEFAULT_INSTANCE.freeze();
}

void Bytes::put(void* dst, void* src) const {
  ((std::string*)dst)->swap(*(std::string*)src);
}

}} // namespace
