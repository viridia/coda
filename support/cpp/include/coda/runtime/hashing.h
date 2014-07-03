// ============================================================================
// Coda Object
// ============================================================================

#ifndef CODA_RUNTIME_HASHING_H
#define CODA_RUNTIME_HASHING_H 1

#ifndef CODA_CONFIG_H
  #include "coda/config.h"
#endif

#if CODA_HAVE_FUNCTIONAL
  #include <functional>
#endif

#if CODA_HAVE_MATH_H
  #include <math.h>
#endif

#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace coda {
namespace runtime {

/** Interface for hashable objects. */
class Hashable {
public:
  virtual ~Hashable() {}
  virtual std::size_t hashValue() const = 0;
};

/** Combine two hash vaues. */
inline void hash_combine(std::size_t& lhs, std::size_t rhs) {
  lhs ^= rhs + 0x9e3779b9 + (lhs<<6) + (lhs>>2);
}

/** Construct a hash value from a pointer. */
template<class T>
inline std::size_t hash_pointer(T* value) {
  static const std::size_t shift = (std::size_t)log2(1 + sizeof(T));
  return reinterpret_cast<std::size_t>(value) >> shift;
}

/** Hash function helpers. */

inline std::size_t hash(bool value) {
  return std::hash<bool>()(value);
}

inline std::size_t hash(int16_t value) {
  return std::hash<int16_t>()(value);
}

inline std::size_t hash(int32_t value) {
  return std::hash<int32_t>()(value);
}

inline std::size_t hash(int64_t value) {
  return std::hash<int64_t>()(value);
}

inline std::size_t hash(float value) {
  return std::hash<float>()(value);
}

inline std::size_t hash(double value) {
  return std::hash<double>()(value);
}

inline std::size_t hash(const std::string& value) {
  return std::hash<std::string>()(value);
}

template<class T>
inline std::size_t hash(const std::vector<T>& value) {
  std::size_t result = 1;
  for (typename std::vector<T>::const_iterator it = value.begin(), itEnd = value.end(); it != itEnd; ++it) {
    hash_combine(result, hash(*it));
  }
  return result;
}

template<class T>
inline std::size_t hash(const std::unordered_set<T>& value) {
  std::size_t result = 2;
  for (typename std::unordered_set<T>::const_iterator it = value.begin(), itEnd = value.end(); it != itEnd; ++it) {
    hash_combine(result, hash(*it));
  }
  return result;
}

template<class K, class V>
inline std::size_t hash(const std::unordered_map<K, V>& value) {
  std::size_t result = 2;
  for (typename std::unordered_map<K, V>::const_iterator it = value.begin(), itEnd = value.end(); it != itEnd; ++it) {
    hash_combine(result, hash(it->first));
    hash_combine(result, hash(it->second));
  }
  return result;
}

inline std::size_t hash(const Hashable* value) {
  return value ? value->hashValue() : (size_t) -1;
}

}} // namespace

#endif /* CODA_HASHING_H */
