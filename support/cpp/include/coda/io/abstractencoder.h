// ============================================================================
// Coda Abstract Encoder
// ============================================================================

#ifndef CODA_IO_ABSTRACTENCODER_H
#define CODA_IO_ABSTRACTENCODER_H 1

#ifndef CODA_IO_CODEC_H
  #include "coda/io/codec.h"
#endif

namespace coda {
namespace io {

/**
 * Abstract base class that provides common functionality for encoders.
 */
class AbstractEncoder : public Encoder {
public:
  AbstractEncoder() {
    nextSharedId = 1;
    nextExternId = -1;
  }

  Encoder& addExtern(const coda::runtime::Object* obj, int32_t index = -1);

protected:
  int32_t addShared(const coda::runtime::Object* obj);
  int32_t getSharedIndex(const coda::runtime::Object* obj);

  int32_t getNextSharedId() {
    if (nextSharedId < 0) {
      throw EncodingError("Too many shared objects");
    }
    return nextSharedId++;
  }

  int32_t getNextExternId() {
    while (idsInUse.find(nextExternId) != idsInUse.end()) {
      --nextExternId;
    }
    if (nextExternId >= 0) {
      throw EncodingError("Too many extern objects");
    }
    return nextExternId;
  }

private:
  int32_t nextSharedId;
  int32_t nextExternId;
  std::unordered_map<void*, int32_t> objectRefs;
  std::unordered_set<int32_t> idsInUse;
};

}} // namespace

#endif // CODA_IO_ABSTRACTENCODER_H
