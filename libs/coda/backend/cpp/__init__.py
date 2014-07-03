def createGenerators(options):
  from . import gen
  return (gen.CppHeaderGenerator('cpp', options), gen.CppGenerator('cpp', options))
