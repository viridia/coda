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

#ifndef LLVM_ADT_HASHING_H
  #include "llvm/adt/hashing.h"
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
  virtual llvm::hash_code hashValue() const = 0;
};

///** Construct a hash value from a pointer. */
//template<class T>
//inline std::size_t hash_pointer(T* value) {
//  static const std::size_t shift = (std::size_t)log2(1 + sizeof(T));
//  return reinterpret_cast<std::size_t>(value) >> shift;
//}

/** Hash function helpers. */

//template<class T>
//inline std::size_t hash(const llvm::ArrayRef<T>& value) {
//  std::size_t result = 1;
//  for (typename std::vector<T>::const_iterator it = value.begin(), itEnd = value.end(); it != itEnd; ++it) {
//    hash_combine(result, hash(*it));
//  }
//  return result;
//}

//template<class T>
//inline llvm::hash_code hash_code(const llvm::DenseSet<T>& value) {
//  std::size_t result = 2;
//  for (typename std::unordered_set<T>::const_iterator it = value.begin(), itEnd = value.end(); it != itEnd; ++it) {
//    hash_combine(result, hash(*it));
//  }
//  return result;
//}
//
//template<class K, class V>
//inline llvm::hash_code hash(const llvm::DenseMap<K, V>& value) {
//  std::size_t result = 2;
//  for (typename std::unordered_map<K, V>::const_iterator it = value.begin(), itEnd = value.end(); it != itEnd; ++it) {
//    hash_combine(result, hash(it->first));
//    hash_combine(result, hash(it->second));
//  }
//  return result;
//}

inline llvm::hash_code hash(const Hashable* value) {
  return value ? value->hashValue() : llvm::hash_value(NULL);
}

}} // namespace

#endif /* CODA_HASHING_H */
