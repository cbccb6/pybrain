"""

Build a simple lstm network with peepholes:

    >>> n = buildSimpleLSTMNetwork(True)
    simpleLstmNet
      Modules:
        [<BiasUnit 'bias'>, <LinearLayer 'i'>, <LSTMLayer 'lstm'>, <LinearLayer 'o'>]
      Connections:
        [<FullConnection 'f2': 'bias' -> 'lstm'>, <FullConnection 'f1': 'i' -> 'lstm'>, <FullConnection 'r1': 'lstm' -> 'o'>]
      Recurrent Connections:
        [<FullConnection 'r1': 'lstm' -> 'lstm'>]        
        
Check its gradient:

    >>> from pybrain.tests import gradientCheck
    >>> gradientCheck(n)
    Perfect gradient
    True

Try writing it to an xml file, reread it and determine if it looks the same:
    
    >>> from pybrain.tests import xmlInvariance
    >>> xmlInvariance(n)
    Same representation
    Same function
    Same class
    
"""


__author__ = 'Tom Schaul, tom@idsia.ch'

from pybrain import Network, LinearLayer, FullConnection, LSTMLayer, BiasUnit
from pybrain.tests import runModuleTestSuite


def buildSimpleLSTMNetwork(peepholes = False):
    N = Network('simpleLstmNet')  
    i = LinearLayer(1, name = 'i')
    h = LSTMLayer(1, peepholes = peepholes, name = 'lstm')
    o = LinearLayer(1, name = 'o')
    b = BiasUnit('bias')
    N.addModule(b)
    N.addOutputModule(o)
    N.addInputModule(i)
    N.addModule(h)
    N.addConnection(FullConnection(i, h, name = 'f1'))
    N.addConnection(FullConnection(b, h, name = 'f2'))
    N.addRecurrentConnection(FullConnection(h, h, name = 'r1'))
    N.addConnection(FullConnection(h, o, name = 'r1'))
    N.sortModules()
    print N
    return N
        

if __name__ == "__main__":
    runModuleTestSuite(__import__('__main__'))
