// ============================================================================
// Coda Encoders and Decoders
// ============================================================================

#ifndef CODA_IO_CODEC_H
#define CODA_IO_CODEC_H 1

#ifndef CODA_DESCRIPTORS_H
  #include "coda/descriptors.h"
#endif

namespace coda {
namespace io {

/**
 * Exception thrown by encoders and decoders.
 */
class EncodingError : public std::runtime_error {
public:
  EncodingError(const std::string& what_arg) : std::runtime_error(what_arg) {}
};

/**
 * Interface definition for CODA stream encoder.
 */
class Encoder {
public:
  virtual Encoder& addExtern(const coda::runtime::Object* obj, int32_t index = -1) = 0;

  /** Write out a field header. This should be called immediately before writing the data
      for the field. */
  virtual Encoder& writeFieldHeader(const char* name, int32_t fieldId) = 0;
  virtual Encoder& writeFieldHeader(const std::string& name, int32_t fieldId) = 0;

  /** Write a boolean value to the stream. */
  virtual Encoder& writeBoolean(bool value) = 0;

  /** Write an integer value to the stream. */
  virtual Encoder& writeInteger(int32_t value) = 0;
  virtual Encoder& writeInteger(int64_t value) = 0;

  /** Write a fixed-length integer value to the stream. */
  virtual Encoder& writeFixed16(int16_t value) = 0;
  virtual Encoder& writeFixed32(int32_t value) = 0;
  virtual Encoder& writeFixed64(int64_t value) = 0;

  /** Write a float value to the stream. */
  virtual Encoder& writeFloat(float value) = 0;

  /** Write a double-precision float value to the stream. */
  virtual Encoder& writeDouble(double value) = 0;

  /** Write a string value to the stream. */
  virtual Encoder& writeString(const std::string& value) = 0;

  /** Write a bytes value to the stream. */
  virtual Encoder& writeBytes(const std::string& value) = 0;

  /** Start a list value. */
  virtual Encoder& writeBeginList(
      coda::descriptors::TypeKind elementKind, size_t length, bool fixed = false) = 0;

  /** Finish a list value. */
  virtual Encoder& writeEndList() = 0;

  /** Start a set value. */
  virtual Encoder& writeBeginSet(
      coda::descriptors::TypeKind elementKind, size_t length, bool fixed = false) = 0;

  /** End a set value. */
  virtual Encoder& writeEndSet() = 0;

  /** Start a map value. */
  virtual Encoder& writeBeginMap(
      coda::descriptors::TypeKind keyKind,
      coda::descriptors::TypeKind valueKind,
      size_t length) = 0;

  /** End a map value. */
  virtual Encoder& writeEndMap() = 0;

  /** Write a struct value to the stream. */
  virtual Encoder& writeStruct(const coda::runtime::Object* value) = 0;

  /** Write a shared struct value to the stream. */
  virtual Encoder& writeSharedStruct(const coda::runtime::Object* value) = 0;

  /** Start a subtype record. */
  virtual Encoder& writeBeginSubtype(const std::string& name, int32_t subtypeId) = 0;

  /** Finish a subtype record. */
  virtual Encoder& writeEndSubtype() = 0;

protected:
  Encoder() {}
  virtual ~Encoder() {}
};

/**
 * Interface definition for CODA stream decoder.
 */
class Decoder {
public:

  template<class T>
  T* decode() {
    return static_cast<T*>(readObject(&T::DESCRIPTOR));
  }

  virtual runtime::Object* readObject(const coda::descriptors::StructDescriptor* descriptor) = 0;

protected:
  Decoder() {}
  virtual ~Decoder() {}
};

}} // namespace

#endif // CODA_IO_CODEC_H
