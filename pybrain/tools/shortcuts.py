__author__ = 'Tom Schaul and Thomas Rueckstiess'


import logging

from itertools import chain

from pybrain.structure.networks import Network
from pybrain.structure.modules import BiasUnit, SigmoidLayer, LinearLayer
from pybrain.structure.connections import FullConnection, IdentityConnection


class NetworkError(Exception): pass


def buildNetwork(*layers, **options):
    """ This helper function builds arbitrary deep networks, depending on 
        how many arguments are given. With 2 arguments, a simple flat network
        with linear input and (per default linear) output layer are created.
        More arguments add (per default sigmoid) hidden layers to the network.
        @param layers: list of numbers of neurons for each layer
        @param options: These values can be changed: 
            bias=True, hiddenclass=SigmoidLayer, outclass=LinearLayer, outputbias=True
    """
    # options
    opt = { 'bias':True, 'hiddenclass':SigmoidLayer, 'outclass':LinearLayer, 'outputbias':True }
    for key in options:
        if key not in ['bias', 'hiddenclass', 'outclass', 'outputbias']:
            raise NetworkError('buildNetwork unknown option: %s' % key)
        opt[key] = options[key]
    
    if len(layers) < 2:
        raise NetworkError('buildNetwork needs 2 arguments for input and output layers at least.')
    n = Network()
    # linear input layer
    n.addInputModule(LinearLayer(layers[0], name='in'))
    # output layer of type 'outclass'
    n.addOutputModule(opt['outclass'](layers[-1], name='out'))
    if opt['bias']:
        # add bias module and connection to out module, if desired
        n.addModule(BiasUnit(name = 'bias'))
        if opt['outputbias']:
            n.addConnection(FullConnection(n['bias'], n['out']))
    # arbitrary number of hidden layers of type 'hiddenclass'
    for i, num in enumerate(layers[1:-1]):
        layername = 'hidden%i' % i
        n.addModule(opt['hiddenclass'](num, name=layername))
        if opt['bias']:
            # also connect all the layers with the bias
            n.addConnection(FullConnection(n['bias'], n[layername]))
    # connections between hidden layers
    for i in range(len(layers)-3):
        n.addConnection(FullConnection(n['hidden%i' % i], n['hidden%i' % (i+1)]))
    # other connections
    if len(layers) == 2:
        # flat network, connection from in to out
        n.addConnection(FullConnection(n['in'], n['out']))
    else:
        # network with hidden layer(s), connections from in to first hidden and last hidden to out
        n.addConnection(FullConnection(n['in'], n['hidden0']))
        n.addConnection(FullConnection(n['hidden%i' % (len(layers)-3)], n['out']))
    n.sortModules()
    return n
    

def _buildNetwork(*layers, **options):
    """This is a helper function to create different kinds of networks.

    `layers` is a list of tuples. Each tuple can contain an arbitrary number of
    layers, each being connected to the next one with IdentityConnections. Due 
    to this, all layers have to have the same dimension. We call these tuples
    'parts.'
    
    Afterwards, the last layer of one tuple is connected to the first layer of 
    the following tuple by a FullConnection.
    
    If the keyword argument bias is given, BiasUnits are added additionally with
    every FullConnection. 

    Example:
    
        _buildNetwork(
            (LinearLayer(3),),
            (SigmoidLayer(4), GaussianLayer(4)),
            (SigmoidLayer(3),),
        )
    """
    bias = options['bias'] if 'bias' in options else False
    
    net = Network()
    layerParts = iter(layers)
    firstPart = iter(layerParts.next())
    firstLayer = firstPart.next()
    net.addInputModule(firstLayer)
    
    prevLayer = firstLayer
    
    for part in chain(firstPart, layerParts):
        new_part = True
        for layer in part:
            net.addModule(layer)
            # Pick class depending on wether we entered a new part
            if new_part:
                ConnectionClass = FullConnection
                if bias:
                    biasUnit = BiasUnit('BiasUnit for %s' % layer.name)
                    net.addModule(biasUnit)
                    net.addConnection(FullConnection(biasUnit, layer))
            else:
                ConnectionClass = IdentityConnection
            new_part = False
            conn = ConnectionClass(prevLayer, layer)
            net.addConnection(conn)
            prevLayer = layer
    net.addOutputModule(layer)
    net.sortModules()
    return net
    

def buildSimpleNetwork(innodes, hiddennodes, outnodes, bias = True, componentclass = SigmoidLayer):
    """ an ad-hoc construction of a 1-hidden-layer network """
    logging.warning("Deprecated: Use pybrain.shortcuts.buildNetwork instead")
    n = Network()
    n.addInputModule(LinearLayer(innodes, name = 'in'))
    if bias:
        n.addModule(BiasUnit(name = 'bias'))
    n.addModule(componentclass(hiddennodes, name = 'h'))
    n.addOutputModule(LinearLayer(outnodes, name = 'out'))
    n.addConnection(FullConnection(n['in'], n['h']))
    n.addConnection(FullConnection(n['h'], n['out']))
    if bias:
        n.addConnection(FullConnection(n['bias'], n['h']))
        n.addConnection(FullConnection(n['bias'], n['out']))
    n.sortModules()
    return n


def buildFlatNetwork(innodes, outnodes, bias = True):
    """ an ad-hoc construction of a 1-hidden-layer network """
    logging.warning("Deprecated: Use pybrain.shortcuts.buildNetwork instead")
    n = Network()
    n.addInputModule(LinearLayer(innodes, name = 'in'))
    if bias:
        n.addModule(BiasUnit(name = 'bias'))
    n.addOutputModule(LinearLayer(outnodes, name = 'out'))
    n.addConnection(FullConnection(n['in'], n['out']))
    if bias:
        n.addConnection(FullConnection(n['bias'], n['out']))
    n.sortModules()
    return n