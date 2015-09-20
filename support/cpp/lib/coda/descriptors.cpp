// ============================================================================
// Coda base types
// ============================================================================

#include "coda/runtime/object.h"
#include "coda/runtime/typeregistry.h"
#include "coda/descriptors.h"

#include <assert.h>

namespace coda {
namespace descriptors {

const std::string DeclTypeMixin::getFullName() const {
  const DeclType* self = static_cast<const DeclType*>(this);
  if (self->getEnclosingType()) {
    return self->getEnclosingType()->getFullName() + '.' + self->getName();
  } else if (!self->getFile()->getPackage().empty()){
    return self->getFile()->getPackage() + '.' + self->getName();
  } else {
    return self->getName();
  }
}

void FieldDescriptor::setBoolean(runtime::Object* instance, bool value) const {
  assert(getType()->typeId() == TYPE_KIND_BOOL);
  *reinterpret_cast<bool*>((uint8_t*)instance + fieldOffset) = value;
}

void FieldDescriptor::setInteger16(runtime::Object* instance, int16_t value) const {
  assert(getType()->typeId() == TYPE_KIND_INTEGER);
  assert(static_cast<const IntegerType*>(getType())->getBits() == 16);
  *reinterpret_cast<int16_t*>((uint8_t*)instance + fieldOffset) = value;
}

void FieldDescriptor::setInteger32(runtime::Object* instance, int32_t value) const {
  assert(getType()->typeId() == TYPE_KIND_INTEGER);
  assert(static_cast<const IntegerType*>(getType())->getBits() == 32);
  *reinterpret_cast<int32_t*>((uint8_t*)instance + fieldOffset) = value;
}

void FieldDescriptor::setInteger64(runtime::Object* instance, int64_t value) const {
  assert(getType()->typeId() == TYPE_KIND_INTEGER);
  assert(static_cast<const IntegerType*>(getType())->getBits() == 64);
  *reinterpret_cast<int64_t*>((uint8_t*)instance + fieldOffset) = value;
}

void FieldDescriptor::setFloat(runtime::Object* instance, float value) const {
  assert(getType()->typeId() == TYPE_KIND_FLOAT);
  *reinterpret_cast<float*>((uint8_t*)instance + fieldOffset) = value;
}

void FieldDescriptor::setDouble(runtime::Object* instance, double value) const {
  assert(getType()->typeId() == TYPE_KIND_DOUBLE);
  *reinterpret_cast<double*>((uint8_t*)instance + fieldOffset) = value;
}

void FieldDescriptor::setString(runtime::Object* instance, const std::string& value) const {
  assert(getType()->typeId() == TYPE_KIND_STRING);
  reinterpret_cast<std::string*>((uint8_t*)instance + fieldOffset)->assign(value);
}

void FieldDescriptor::setBytes(runtime::Object* instance, const std::string& value) const {
  assert(getType()->typeId() == TYPE_KIND_BYTES);
  reinterpret_cast<std::string*>((uint8_t*)instance + fieldOffset)->assign(value);
}

void FieldDescriptor::setObject(runtime::Object* instance, runtime::Object* value) const {
  assert(getType()->typeId() == TYPE_KIND_STRUCT);
  *reinterpret_cast<runtime::Object**>((uint8_t*)instance + fieldOffset) = value;
}

void FieldDescriptor::setList(runtime::Object* instance, void* begin, void* end) const {
  void* fieldAddr = reinterpret_cast<void*>((uint8_t*)instance + fieldOffset);
  switch (getType()->typeId()) {
    case TYPE_KIND_BOOL: {
      std::vector<bool>& field = *reinterpret_cast<std::vector<bool>*>(fieldAddr);
      field.assign((bool*) begin, (bool*) end);
      break;
    }

    case TYPE_KIND_INTEGER: {
      const IntegerType* intType = static_cast<const IntegerType*>(getType());
      if (intType->getBits() == 16) {
        std::vector<int16_t>& field = *reinterpret_cast<std::vector<int16_t>*>(fieldAddr);
        field.assign((int16_t*) begin, (int16_t*) end);
      } else if (intType->getBits() == 32) {
        std::vector<int32_t>& field = *reinterpret_cast<std::vector<int32_t>*>(fieldAddr);
        field.assign((int32_t*) begin, (int32_t*) end);
      } else if (intType->getBits() == 64) {
        std::vector<int64_t>& field = *reinterpret_cast<std::vector<int64_t>*>(fieldAddr);
        field.assign((int64_t*) begin, (int64_t*) end);
      }
      break;
    }

    case TYPE_KIND_FLOAT: {
      std::vector<float>& field = *reinterpret_cast<std::vector<float>*>(fieldAddr);
      field.assign((float*) begin, (float*) end);
      break;
    }

    case TYPE_KIND_DOUBLE: {
      std::vector<double>& field = *reinterpret_cast<std::vector<double>*>(fieldAddr);
      field.assign((double*) begin, (double*) end);
      break;
    }

    case TYPE_KIND_STRING: {
      std::vector<std::string>& field = *reinterpret_cast<std::vector<std::string>*>(fieldAddr);
      field.assign((std::string*) begin, (std::string*) end);
      break;
    }

    case TYPE_KIND_BYTES: {
      std::vector<std::string>& field = *reinterpret_cast<std::vector<std::string>*>(fieldAddr);
      field.assign((std::string*) begin, (std::string*) end);
      break;
    }

    case TYPE_KIND_LIST:
    case TYPE_KIND_SET:
    case TYPE_KIND_MAP: {
      assert(false && "Invalid liste element type");
//      std::vector<std::string>& field = *reinterpret_cast<std::vector<std::string>*>(fieldAddr);
//      field.assign((std::string*) begin, (std::string*) end);
      break;
    }
  }
}

void StructDescriptor::buildFieldMaps() {
  fieldByName.clear();
  fieldById.clear();
  const std::vector<StructType::Field*>& fields = getFields();
  for (std::vector<Field*>::const_iterator it = fields.begin(), itEnd = fields.end();
      it != itEnd; ++it) {
    FieldDescriptor* f = (FieldDescriptor*)*it;
    fieldByName[f->getName()] = f;
    fieldById[f->getId()] = f;
  }
}

const FieldDescriptor* StructDescriptor::getField(const std::string& fieldName) const {
  std::unordered_map<std::string, FieldDescriptor*>::const_iterator it =
      fieldByName.find(fieldName);
  if (it != fieldByName.end()) {
    return it->second;
  }
  return NULL;
}

const FieldDescriptor* StructDescriptor::getField(int32_t fieldId) const {
  std::unordered_map<int32_t, FieldDescriptor*>::const_iterator it = fieldById.find(fieldId);
  if (it != fieldById.end()) {
    return it->second;
  }
  return NULL;
}

void StructDescriptor::freezeLocal() {
  checkMutable();
  if (getOptions() != &StructOptions::DEFAULT_INSTANCE) {
    getMutableOptions()->setImmutable();
  }
  for (std::vector<StructType::Field*>::const_iterator it =
      getMutableFields().begin(), itEnd = getMutableFields().end(); it != itEnd; ++it) {
    (*it)->setImmutable();
  }
  for (std::vector<StructType*>::const_iterator it =
      getMutableStructs().begin(), itEnd = getMutableStructs().end(); it != itEnd; ++it) {
    ((StructDescriptor*)(*it))->freezeLocal();
  }
  for (std::vector<EnumType*>::const_iterator it =
      getMutableEnums().begin(), itEnd = getMutableEnums().end(); it != itEnd; ++it) {
    ((EnumDescriptor*)(*it))->freezeLocal();
  }
  defaultInstance->setImmutable();
  setImmutable();
//  for (std::vector<ExtensionField*>::const_iterator it = _extensions.begin(), itEnd = _extensions.end(); it != itEnd; ++it) {
//    (*it)->freeze();
//  }
}

void EnumDescriptor::freezeLocal() {
  checkMutable();
  if (getOptions() != &EnumOptions::DEFAULT_INSTANCE) {
    getMutableOptions()->setImmutable();
  }
  for (std::vector<EnumType::Value*>::const_iterator it =
      getMutableValues().begin(), itEnd = getMutableValues().end(); it != itEnd; ++it) {
    (*it)->setImmutable();
  }
  setImmutable();
}

StaticFileDescriptor::StaticFileDescriptor(
    const char* name,
    const char* package,
    FileOptions& options,
    StaticArrayRef<StructDescriptor*> structs,
    StaticArrayRef<EnumDescriptor*> enums) {
  setName(name);
  setPackage(package);
  setOptions(&options);
  getMutableStructs().assign(structs.begin(), structs.end());
  getMutableEnums().assign(enums.begin(), enums.end());
  freezeLocal();
  runtime::TypeRegistry::getInstance().addFile(this);
}

void StaticFileDescriptor::freezeLocal() {
  checkMutable();
  if (getOptions() != &FileOptions::DEFAULT_INSTANCE) {
    getMutableOptions()->setImmutable();
  }
  for (std::vector<StructType*>::const_iterator it =
      getMutableStructs().begin(), itEnd = getMutableStructs().end(); it != itEnd; ++it) {
    ((StructDescriptor*)(*it))->freezeLocal();
  }
  for (std::vector<EnumType*>::const_iterator it =
      getMutableEnums().begin(), itEnd = getMutableEnums().end(); it != itEnd; ++it) {
    ((EnumDescriptor*)(*it))->freezeLocal();
  }
//  for (std::vector<ExtensionField*>::const_iterator it = _extensions.begin(), itEnd = _extensions.end(); it != itEnd; ++it) {
//    (*it)->freeze();
//  }
  for (std::vector<FileDescriptor::Import*>::const_iterator it =
      getMutableImports().begin(), itEnd = getMutableImports().end(); it != itEnd; ++it) {
    (*it)->setImmutable();
  }
  setImmutable();
}

void describeType(const Type* type, std::string& out) {
  switch ((TypeKind) type->typeId()) {
    case TYPE_KIND_BOOL:
      out.append("bool");
      break;

    case TYPE_KIND_INTEGER: {
      const IntegerType* intType = static_cast<const IntegerType*>(type);
      if (intType->getBits() == 16) {
        out.append("i16");
      } else if (intType->getBits() == 32) {
        out.append("i32");
      } else if (intType->getBits() == 64) {
        out.append("i64");
      }
      break;
    }

    case TYPE_KIND_FLOAT: {
      out.append("float");
      break;
    }

    case TYPE_KIND_DOUBLE: {
      out.append("double");
      break;
    }

    case TYPE_KIND_STRING: {
      out.append("string");
      break;
    }

    case TYPE_KIND_BYTES: {
      out.append("bytes");
      break;
    }

    case TYPE_KIND_LIST: {
      const ListType* listType = static_cast<const ListType*>(type);
      out.append("list<");
      describeType(listType->getElementType(), out);
      out.append(">");
      break;
    }

    case TYPE_KIND_SET: {
      const SetType* setType = static_cast<const SetType*>(type);
      out.append("set<");
      describeType(setType->getElementType(), out);
      out.append(">");
      break;
    }

    case TYPE_KIND_MAP: {
      const MapType* mapType = static_cast<const MapType*>(type);
      out.append("map<");
      describeType(mapType->getKeyType(), out);
      out.append(", ");
      describeType(mapType->getValueType(), out);
      out.append(">");
      break;
    }

    case TYPE_KIND_STRUCT: {
      const StructDescriptor* structType = static_cast<const StructDescriptor*>(type);
      out.append(structType->getFullName());
      break;
    }

    case TYPE_KIND_ENUM: {
      const EnumDescriptor* enumType = static_cast<const EnumDescriptor*>(type);
      out.append(enumType->getFullName());
      break;
    }

    case TYPE_KIND_MODIFIED: {
      const ModifiedType* modifiedType = static_cast<const ModifiedType*>(type);
      if (modifiedType->isConst()) {
        out.append("const ");
      }
      if (modifiedType->isShared()) {
        out.append("shared ");
      }
      describeType(modifiedType->getElementType(), out);
      break;
    }

    default:
      assert(false && "Invalid type");
  }
}

}} // namespace
