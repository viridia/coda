Coda: Compact Object Data Archive
=================================

Coda is an object serialization system inspired by Thrift, Protocol Buffers, and others. It aims to provide fast encoding and decoding of objects into compact serialized form, while allowing for rapid evolution of the object schemas.

Unlike Protocol Buffers and Thrift, which are intended primarily for interprocess communication, Coda is targeted at a different set of application domains, and its feature set reflects this. Specifically, Coda was built for storage and transformation of complex, heterogenous object graphs. Examples of such graphs could be 3D model formats for games, or Abstract Syntax Trees created within a compiler.

Some of Coda's features:

* Support for true subclassing and polymorphic fields.
* Support for shared object references - multiple fields can reference the same object.
* Support for automatic generation of visitor and transform classes, allowing for easy traversal and modification of object graphs.
* Pluggable codecs allow serialization in various formats.
* Highly-compact binary encoding format.
* Supports schema evolution, so older/newer object formats can be processed without losing information.
* Facilitiates interoperability between different programming languages.
* Language plugins are written in Python 3 and are fairly easy to write. Adding support for a new language involves subclassing `coda.compiler.genbase.CodeGenerator`.

(Note: Currently only the Python code generator is complete, although the C++ code generator is partly done.)
