// ============================================================================
// Efficient polymorphic strings.
// ============================================================================

#ifndef CODA_RUNTIME_STRINGREF_H
#define CODA_RUNTIME_STRINGREF_H 1

namespace coda {
namespace runtime {

#include <stddef.h>

class StringRef {
public:
  typedef const char* iterator;
  typedef const char* const_iterator;

  /// Construct an empty StringRef.
  StringRef() : _data(NULL), _size(0) {}

  /** Construct a StringRef from a C string. */
  template <size_t Size>
  StringRef(const char (&array)[Size]) : _data(array), _size(Size - 1) {}

  /** Construct a StringRef from an STL string. */
  StringRef(const std::string& str) : _data(str.data()), _size(str.size()) {}

  /** Return the size of the string in bytes. */
  size_t size() const { return _size; }

  // Iterators

  iterator begin() const { return _data; }
  iterator end() const { return _data + _size; }

private:
  const char* _data;
  size_t _size;
};

}} // namespace

#endif // CODA_RUNTIME_STRINGREF_H
