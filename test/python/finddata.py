import pathlib
import importlib
import sys

__all__ = ['sample', 'sampleTxt', 'sampleBin']

this = pathlib.Path(__file__)
datadir = this.parent.parent / 'data'

loader = importlib.machinery.SourceFileLoader('sample', str(datadir / 'sample.py'))
sample = loader.load_module()
sampleTxt = datadir / 'sample.txt'
sampleBin = datadir / 'sample.bin'
