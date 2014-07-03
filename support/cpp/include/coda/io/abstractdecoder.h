// ============================================================================
// Coda Abstract Decoder
// ============================================================================

#ifndef CODA_IO_ABSTRACTDECODER_H
#define CODA_IO_ABSTRACTDECODER_H 1

#ifndef CODA_IO_CODEC_H
  #include "coda/io/codec.h"
#endif

namespace coda {
namespace runtime {
class TypeRegistry;
}
namespace io {

/**
 * Abstract base class that provides common functionality for encoders.
 */
class AbstractDecoder : public Decoder {
public:
  AbstractDecoder(runtime::TypeRegistry * typeReg);

  Decoder& addExtern(runtime::Object* obj, int32_t index = -1);

protected:
  int32_t addShared(runtime::Object* obj);
  runtime::Object* getShared(int32_t index);

  int32_t getNextSharedId() {
    if (nextSharedId < 0) {
      throw EncodingError("Too many shared objects");
    }
    return nextSharedId++;
  }

  int32_t getNextExternId() {
    while (objectRefs.find(nextExternId) != objectRefs.end()) {
      --nextExternId;
    }
    if (nextExternId >= 0) {
      throw EncodingError("Too many extern objects");
    }
    return nextExternId;
  }

protected:
  /** Compute the address of a field within an object. */
  void* fieldAddress(const descriptors::FieldDescriptor* field, runtime::Object* instance) {
    return field->fieldAddress(instance);
  }

  /** Look up a subtype by ID. */
  const descriptors::StructDescriptor* getSubtype(
      const descriptors::StructType* base, int32_t typeId);

private:
  const runtime::TypeRegistry* typeRegistry;
  int32_t nextSharedId;
  int32_t nextExternId;
  std::unordered_map<int32_t, runtime::Object*> objectRefs;
};

}} // namespace

#endif // CODA_IO_ABSTRACTDECODER_H
