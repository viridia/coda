def createGenerators(options):
  from . import gen
  generators = (gen.Python3Generator(options),)
  if options.getOption('visitor'):
    from . import genvisitor
    generators = generators + (genvisitor.Python3VisitorGenerator(options),)
  if options.getOption('transform'):
    from . import gentransform
    generators = generators + (gentransform.Python3TransformGenerator(options),)
  return generators
