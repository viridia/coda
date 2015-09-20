/* ================================================================== *
 * Address classes unit test
 * ================================================================== */

#include "gtest/gtest.h"
#include "coda/descriptors.h"
#include "coda/types.h"

namespace coda {
using namespace coda::descriptors;

TEST(DescriptorTest, Value) {
  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRUCT, Value::DESCRIPTOR.TYPE_ID);
  EXPECT_EQ("Value", Value::DESCRIPTOR.getName());
}

TEST(DescriptorTest, Type) {
  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRUCT, Type::DESCRIPTOR.TYPE_ID);
  EXPECT_EQ("Type", Type::DESCRIPTOR.getName());
  EXPECT_FALSE(Type::DESCRIPTOR.isMutable());
}

TEST(DescriptorTest, BooleanType) {
  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRUCT, BooleanType::DESCRIPTOR.TYPE_ID);
  EXPECT_EQ("BooleanType", BooleanType::DESCRIPTOR.getName());
  EXPECT_EQ(coda::descriptors::TYPE_KIND_BOOL, BooleanType::DEFAULT_INSTANCE.typeId());
  EXPECT_EQ(&BooleanType::DESCRIPTOR, BooleanType::DESCRIPTOR.newInstance()->descriptor());
//  EXPECT_EQ(BooleanType::DESCRIPTOR, BooleanType::DESCRIPTOR);
  EXPECT_FALSE(BooleanType::DESCRIPTOR.isMutable());
  EXPECT_FALSE(coda::types::Boolean::DESCRIPTOR.isMutable());
  EXPECT_FALSE(BooleanType::DEFAULT_INSTANCE.isMutable());

  EXPECT_EQ(BooleanType::DESCRIPTOR.getBaseType(), &Type::DESCRIPTOR);

  EXPECT_TRUE(BooleanType::DEFAULT_INSTANCE.isInstanceOf(&BooleanType::DESCRIPTOR));
  EXPECT_TRUE(BooleanType::DEFAULT_INSTANCE.isInstanceOf(&Type::DESCRIPTOR));
  EXPECT_FALSE(BooleanType::DEFAULT_INSTANCE.isInstanceOf(&IntegerType::DESCRIPTOR));
}

TEST(DescriptorTest, IntegerType) {
  EXPECT_EQ(coda::descriptors::TYPE_KIND_INTEGER, coda::types::Integer16::DESCRIPTOR.typeId());
  EXPECT_EQ("IntegerType", coda::types::Integer16::DESCRIPTOR.descriptor()->getName());
  EXPECT_EQ(16, coda::types::Integer16::DESCRIPTOR.getBits());
  EXPECT_FALSE(coda::types::Integer16::DESCRIPTOR.isMutable());

  EXPECT_EQ(coda::descriptors::TYPE_KIND_INTEGER, coda::types::Integer32::DESCRIPTOR.typeId());
  EXPECT_EQ("IntegerType", coda::types::Integer32::DESCRIPTOR.descriptor()->getName());
  EXPECT_EQ(32, coda::types::Integer32::DESCRIPTOR.getBits());
  EXPECT_FALSE(coda::types::Integer32::DESCRIPTOR.isMutable());

  EXPECT_EQ(coda::descriptors::TYPE_KIND_INTEGER, coda::types::Integer64::DESCRIPTOR.typeId());
  EXPECT_EQ("IntegerType", coda::types::Integer64::DESCRIPTOR.descriptor()->getName());
  EXPECT_EQ(64, coda::types::Integer64::DESCRIPTOR.getBits());
  EXPECT_FALSE(coda::types::Integer64::DESCRIPTOR.isMutable());

  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRUCT, coda::descriptors::IntegerType::DESCRIPTOR.typeId());
  EXPECT_FALSE(coda::descriptors::IntegerType::DESCRIPTOR.isMutable());
  EXPECT_FALSE(coda::descriptors::IntegerType::DEFAULT_INSTANCE.isMutable());
}

TEST(DescriptorTest, FloatType) {
  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRUCT, FloatType::DESCRIPTOR.TYPE_ID);
  EXPECT_EQ("FloatType", FloatType::DESCRIPTOR.getName());
  EXPECT_EQ(coda::descriptors::TYPE_KIND_FLOAT, FloatType::DEFAULT_INSTANCE.typeId());
  EXPECT_EQ(&FloatType::DESCRIPTOR, FloatType::DESCRIPTOR.newInstance()->descriptor());
  EXPECT_FALSE(FloatType::DESCRIPTOR.isMutable());
  EXPECT_FALSE(FloatType::DEFAULT_INSTANCE.isMutable());
}

TEST(DescriptorTest, DoubleType) {
  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRUCT, DoubleType::DESCRIPTOR.TYPE_ID);
  EXPECT_EQ("DoubleType", DoubleType::DESCRIPTOR.getName());
  EXPECT_EQ(coda::descriptors::TYPE_KIND_DOUBLE, DoubleType::DEFAULT_INSTANCE.typeId());
  EXPECT_EQ(&DoubleType::DESCRIPTOR, DoubleType::DESCRIPTOR.newInstance()->descriptor());
  EXPECT_FALSE(DoubleType::DESCRIPTOR.isMutable());
  EXPECT_FALSE(DoubleType::DEFAULT_INSTANCE.isMutable());
}

TEST(DescriptorTest, StringType) {
  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRUCT, StringType::DESCRIPTOR.TYPE_ID);
  EXPECT_EQ("StringType", StringType::DESCRIPTOR.getName());
  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRING, StringType::DEFAULT_INSTANCE.typeId());
  EXPECT_EQ(&StringType::DESCRIPTOR, StringType::DESCRIPTOR.newInstance()->descriptor());
  EXPECT_FALSE(StringType::DESCRIPTOR.isMutable());
  EXPECT_FALSE(StringType::DEFAULT_INSTANCE.isMutable());
}

TEST(DescriptorTest, BytesType) {
  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRUCT, BytesType::DESCRIPTOR.TYPE_ID);
  EXPECT_EQ("BytesType", BytesType::DESCRIPTOR.getName());
  EXPECT_EQ(coda::descriptors::TYPE_KIND_BYTES, BytesType::DEFAULT_INSTANCE.typeId());
  EXPECT_EQ(&BytesType::DESCRIPTOR, BytesType::DESCRIPTOR.newInstance()->descriptor());
  EXPECT_FALSE(BytesType::DESCRIPTOR.isMutable());
  EXPECT_FALSE(BytesType::DEFAULT_INSTANCE.isMutable());
}

TEST(DescriptorTest, IntegerValueHashing) {
  IntegerValue value0;
  IntegerValue value1;
  IntegerValue value2;

  value0.setValue(0);
  value1.setValue(0);
  value2.setValue(7);

  EXPECT_EQ(0, value0.getValue());
  EXPECT_EQ(0, value1.getValue());
  EXPECT_EQ(7, value2.getValue());

  EXPECT_EQ(value0.hashValue(), value1.hashValue());
  EXPECT_NE(value0.hashValue(), value2.hashValue());

//  EXPECT_EQ(coda::descriptors::TYPE_KIND_STRUCT, BytesType::DESCRIPTOR.TYPE_ID);
//  EXPECT_EQ("BytesType", BytesType::DESCRIPTOR.getName());
//  EXPECT_EQ(coda::descriptors::TYPE_KIND_BYTES, BytesType::DEFAULT_INSTANCE.typeId());
//  EXPECT_EQ(&BytesType::DESCRIPTOR, BytesType::newInstance()->descriptor());
}

TEST(DescriptorTest, IntegerValueEquals) {
  IntegerValue value0;
  IntegerValue value1;
  IntegerValue value2;

  value0.setValue(0);
  value1.setValue(0);
  value2.setValue(7);

  EXPECT_EQ(value0, value0);
  EXPECT_EQ(value0, value1);
  EXPECT_FALSE(value0 == value2);
  EXPECT_TRUE(value0 != value2);
}

TEST(DescriptorTest, File) {
  EXPECT_EQ("descriptors.coda", coda::descriptors::FILE.getName());
  EXPECT_EQ("coda.descriptors", coda::descriptors::FILE.getPackage());
  EXPECT_EQ("coda::descriptors",
      coda::descriptors::FILE.getOptions()->getPackage().find("cpp")->second);
  EXPECT_EQ("coda.runtime.descdata",
      coda::descriptors::FILE.getOptions()->getPackage().find("python")->second);
  EXPECT_EQ("coda.descriptors",
      coda::descriptors::FILE.getOptions()->getPackage().find("java")->second);
  EXPECT_EQ(28, coda::descriptors::FILE.getStructs().size());
  EXPECT_EQ(1, coda::descriptors::FILE.getEnums().size());
}

TEST(DescriptorTest, FileOptions) {
  // Test the contents of the 'imports' option.
  EXPECT_EQ(1, coda::descriptors::FILE.getOptions()->getImports().size());
  std::unordered_map<std::string, std::vector<std::string> >::const_iterator it =
      coda::descriptors::FILE.getOptions()->getImports().find("cpp");
  EXPECT_NE(it, coda::descriptors::FILE.getOptions()->getImports().end());
  EXPECT_EQ(1, it->second.size());
  EXPECT_EQ("coda/runtime/descriptors_mixin.h", it->second.front());
}

TEST(DescriptorTest, StructOptions) {
  // Test the type of the 'mixin' option.
  const FieldDescriptor *mixinField = StructOptions::DESCRIPTOR.getField("mixin");
  ASSERT_TRUE(mixinField != NULL);
  EXPECT_TRUE(mixinField->getType()->typeId() == descriptors::TYPE_KIND_MAP);
  const descriptors::MapType* mapType =
      static_cast<const descriptors::MapType*>(mixinField->getType());
  ASSERT_TRUE(mapType->getKeyType() != NULL);
  ASSERT_TRUE(mapType->getValueType() != NULL);
}

}
