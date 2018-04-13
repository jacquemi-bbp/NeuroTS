'''
TNS class : Grower object that contains the grower functionality.
'''
import numpy as np
from tns.morphmath import sample
import diametrizer

from morphio.mut import Morphology
from tns.generate.soma import SomaGrower

bifurcation_methods = ['symmetric', 'bio_oriented', 'directional', 'bio_smoothed', ]


class NeuronGrower(object):
    """
    A Grower object is a container for a Neuron, encoded in the (groups, points)
    structure, a set of input distributions that store the data consumed by the algorithms
    and the user-selected parameters. The name of the neuron defines the filename
    in which the generated neuron can be saved in.
    """

    def __init__(self, input_parameters, input_distributions, name='Neuron'):
        """TNS NeuronGrower
        neuron: Obj neuron where groups and points are stored
        input_parameters: the user-defined parameters
        input_distributions: distributions extracted from biological data
        """
        self.neuron = Morphology()

        self.input_parameters = input_parameters
        self.input_distributions = input_distributions

        # A list of trees with the corresponding orientations
        # and initial points on the soma surface will be initialized.
        self.active_neurites = set()

    def next(self):
        '''Call the "next" method of each neurite grower'''
        for grower in self.active_neurites.copy():
            if grower.end():
                self.active_neurites.remove(grower)
            else:
                grower.next()

    def grow(self):
        """Generates a neuron according to the input_parameters
        and the input_distributions. The neuron consists of a soma
        and a list of trees encoded in the h5 format as a set of points
        and groups.

        Returns the grown neuron
        """
        self._grow_soma(interpolation=None)
        while self.active_neurites:
            self.next()
        return self.neuron

    def diametrize(self):
        """Corrects the diameters of the neuron saved in the Grower.
        The neuron can either be loaded from a file by calling G.neuron.load(filename)
        or it can be generate by calling the G.grow() method.
        The Grower should be initialized with a distribution
        that includes a diameter_model.
        To extract a diameter model from a file, call extract_input.diameter_distributions(file)
        """

        model = self.input_distributions['diameter_model']
        diametrizer.correct_diameters(self.neuron, model=model)

    # Functions not intended to be accessible by the user

    def _convert_orientation2points(self, orientation, n_trees, distr):
        '''Checks the type of orientation input and returns the soma points generated by the
        corresponding selection. Currently accepted orientations include the following options:
        list of 3D points: select the orientation externally
        None: creates a list of orientations according to the biological distributions.
        'from_space': generates orientations depending on spatial input (not implemented yet).
        '''

        if type(orientation) is list:  # Gets major orientations externally
            if len(orientation) >= n_trees:
                pts = self.soma.add_points_from_orientations(orientation[:n_trees])
            else:
                raise ValueError('Not enough orientation points!')
        elif orientation is None:  # Samples from trunk_angles
            trunk_angles = sample.trunk_angles(distr, n_trees)
            trunk_z = sample.azimuth_angles(distr, n_trees)
            pts = self.soma.add_points_from_trunk_angles(trunk_angles, trunk_z)
        elif orientation == 'from_space':
            raise ValueError('Not implemented yet!')
        else:
            raise ValueError('Input orientation format is not correct!')
        return pts

    def _grow_trunks(self):
        """Generates the initial points of each tree, which depend on the selectedS
        tree types and the soma surface. All the trees start growing from the surface
        of the soma. The outgrowth direction is either specified in the input parameters,
        as parameters['type']['orientation'] or it is randomly chosen according to the
        biological distribution of trunks on the soma surface if 'orientation' is None.
        """
        from tree import TreeGrower

        for type_of_tree in self.input_parameters['grow_types']:

            # Easier to access distributions
            params = self.input_parameters[type_of_tree]
            distr = self.input_distributions[type_of_tree]

            # Sample the number of trees depending on the tree type
            n_trees = sample.n_neurites(distr["num_trees"])
            orientation = params['orientation']
            # Clean up orientation options in converting function
            points = self._convert_orientation2points(orientation, n_trees, distr)

            # Iterate over all initial points on the soma and create new trees
            # with a direction and initial_point
            for p in points:
                tree_direction = self.soma.orientation_from_point(p)
                self.active_neurites.add(TreeGrower(self.neuron,
                                                    initial_direction=tree_direction,
                                                    initial_point=p,
                                                    parameters=params,
                                                    distributions=distr))

    def _grow_soma(self, interpolation=None):
        """Generates a soma based on the input_distributions. The coordinates
        of the soma contour are retrieved from the trunks.
        """
        self.soma = SomaGrower(initial_point=self.input_parameters["origin"],
                               radius=sample.soma_size(self.input_distributions))

        self._grow_trunks()

        self.neuron.soma.points = self.soma.generate_neuron_soma_points3D(
            interpolation=interpolation).tolist()
        self.neuron.soma.diameters = [0] * len(self.neuron.soma.points)
