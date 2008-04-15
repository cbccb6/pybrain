__author__ = 'Tom Schaul, tom@idsia.ch'

from network import Network
from pybrain.structure.connections.shared import MotherConnection, SharedFullConnection
from pybrain.utilities import iterCombinations

# TODO: class TunedSwipingNetwork: reduce the overhead of having many modules, 
#       by doing only sliced connections on large layers, and not sorting them

# TODO: special treatment for multi-dimensional lstm cells: identity connections on state buffers


class SwipingNetwork(Network):
    """ A network architecture that establishes shared connections between ModuleMeshes (of identical dimesnions)
    so that the behavior becomes equivalent to one unit (in+hidden+out components at the same coordinate) swiping
    over a multidimensional input space and producing a multidimensional output. """
    
    # if all dimensions should be considered symmetric, their weights are shared
    symmetricdimensions = True
    
    # dimesnions of the swiping grid
    dims = None
        
    def __init__(self, inmesh = None, hiddenmesh = None, outmesh = None, predefined = {}, **args):
        Network.__init__(self, **args)
        
        # determine the dimensions 
        if inmesh != None:
            self.setArgs(dims = inmesh.dims)            
        elif self.dims == None:
            raise Exception('No dimensions specified, or derivable')
            
        self.swipes = 2**len(self.dims)
                
        if inmesh != None:
            self._verifyDimensions(inmesh, hiddenmesh, outmesh)
            self._buildSwipingStructure(inmesh, hiddenmesh, outmesh, predefined)
            self.sortModules()
        
    def _verifyDimensions(self, inmesh, hiddenmesh, outmesh):    
        """ verify dimension matching between the meshes """
        assert self.dims == inmesh.dims
        assert outmesh.dims == self.dims
        assert tuple(hiddenmesh.dims[:-1]) == self.dims
        assert hiddenmesh.dims[-1] == self.swipes
        assert min(self.dims) > 1        
        
    def _buildSwipingStructure(self, inmesh, hiddenmesh, outmesh, predefined):
        """
        @param inmesh: a mesh of input units
        @param hiddenmesh: a mesh of hidden units
        @param outmesh: a mesh of output units
        @param predefined: dictionnary with predefined weights for (some of) the motherconnections
        """
        
        # add the modules
        for c in inmesh:
            self.addInputModule(c)
        for c in outmesh:
            self.addOutputModule(c)
        for c in hiddenmesh:
            self.addModule(c)
        
        # create the motherconnections if they are not provided
        if 'inconn' not in predefined:
            predefined['inconn'] = MotherConnection(inmesh.componentOutdim*hiddenmesh.componentIndim, name = 'inconn')
        if 'outconn' not in predefined:
            predefined['outconn'] = MotherConnection(outmesh.componentIndim*hiddenmesh.componentOutdim, name = 'outconn')
        if 'hconns' not in predefined:
            predefined['hconns'] = {}
            for s in range(len(self.dims)):
                if s > 0 and self.symmetricdimensions:
                    predefined['hconns'][s] = predefined['hconns'][0]
                else:
                    predefined['hconns'][s] = MotherConnection(hiddenmesh.componentIndim*hiddenmesh.componentOutdim, name = 'hconn'+str(s))
        
        # establish the connections        
        for unit in self._iterateOverUnits():
            for swipe in range(self.swipes):
                hunit = tuple(list(unit)+[swipe])
                self.addConnection(SharedFullConnection(predefined['inconn'], inmesh[unit], hiddenmesh[hunit]))
                self.addConnection(SharedFullConnection(predefined['outconn'], hiddenmesh[hunit], outmesh[unit]))
                for dim, maxval in enumerate(self.dims):
                    # one swiping connection along every dimension
                    hconn = predefined['hconns'][dim]
                    # determine where the swipe is coming from in this direction:
                    # swipe directions are towards higher coordinates on dim D if the swipe%(2**D) = 0
                    # and towards lower coordinates otherwise.
                    previousunit = list(hunit)
                    if (swipe/2**dim) % 2 == 0:
                        previousunit[dim] -= 1
                    else:
                        previousunit[dim] += 1
                        
                    previousunit = tuple(previousunit)
                    if previousunit[dim] >= 0 and previousunit[dim] < maxval:
                        self.addConnection(SharedFullConnection(hconn, hiddenmesh[previousunit], hiddenmesh[hunit]))                                
        
    def _iterateOverUnits(self):
        """ iterate over the coordinates defines by the ranges of self.dims. """
        return iterCombinations(self.dims)
        