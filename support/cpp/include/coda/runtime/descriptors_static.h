// ============================================================================
// Static helpers for generated descriptors
// ============================================================================

#ifndef CODA_RUNTIME_DESCRIPTORS_STATIC_H
#define CODA_RUNTIME_DESCRIPTORS_STATIC_H 1

#ifndef CODA_RUNTIME_DESCRIPTORS_GENERATED
  #include "coda/runtime/descriptors_generated.h"
#endif

namespace coda {
namespace descriptors {

// ============================================================================
// Classes to assist with initialization
// ============================================================================

template<class T>
class StaticArrayRef {
public:
  typedef const T * iterator;
  typedef const T * const_iterator;

  /// Construct an empty StaticArrayRef.
  StaticArrayRef() : data(NULL), size(0) {}

  /** Construct a StaticArrayRef from a C array. */
  template <size_t Size>
  StaticArrayRef(const T (&array)[Size]) : data(array), size(Size) {}

  // Iterators

  iterator begin() const { return data; }
  iterator end() const { return data + size; }

private:
  T const * data;
  size_t size;
};

template<class T>
class StaticListBuilder {
public:
  StaticListBuilder() {}

  StaticListBuilder& add(const T& value) {
    data.push_back(value);
    return *this;
  }

  const std::vector<T>& build() const { return data; }

private:
  std::vector<T> data;
};

/** Helper class that helps create new instances. */
template<class T>
class StaticObjectBuilder {
public:
  static runtime::Object* create() {
    return new T();
  }

  static StaticObjectBuilder INSTANCE;

private:
  std::vector<T> data;
};

template<class T>
StaticObjectBuilder<T> StaticObjectBuilder<T>::INSTANCE;

// ============================================================================
// FileDescriptor
// ============================================================================

class StaticFileDescriptor : public FileDescriptor {
public:
  StaticFileDescriptor(
      const char* name,
      const char* package,
      FileOptions& options,
      StaticArrayRef<StructDescriptor*> structs,
      StaticArrayRef<EnumDescriptor*> enums);

private:
  void freezeLocal();
};

// ============================================================================
// Helper functions
// ============================================================================

template<class T>
inline T& freeze(T& obj) {
  obj.freeze();
  return obj;
}

}} // namespace

#endif // CODA_RUNTIME_DESCRIPTORS_STATIC_H
