'''Test tns.generate.section code'''
import json
import os

import numpy as np
from nose.tools import assert_dict_equal
from numpy.testing import assert_array_almost_equal, assert_equal
from tns.generate.algorithms.common import TMDStop
from tns.morphmath import sample

from tns.generate.algorithms.tmdgrower import (TMDAlgo, TMDApicalAlgo, TMDGradientAlgo)
from tns.generate.section import SectionGrower, SectionGrowerPath
from tns.generate.tree import SectionParameters

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def _setup_test(Algo, Grower):
    with open(os.path.join(_PATH, 'dummy_distribution.json')) as f:
        distributions = json.load(f)['basal']

    with open(os.path.join(_PATH, 'dummy_params.json')) as f:
        parameters = json.load(f)['basal']
    parameters['bias_length'] = 0.5
    parameters['bias'] = 0.5
    parameters["has_apical_tuft"] = True

    np.random.seed(42)
    algo = Algo(distributions, parameters, [0, 0, 1])
    seg_len = sample.Distr(parameters["step_size"])

    section_parameters = SectionParameters(
        randomness=0.2,
        targeting=0.3,
        history=1.0 - 0.2 - 0.3,
        scale_prob=1.0)

    grower = Grower(parent=None,
                    children=None,
                    first_point=[1.1,0.,0.],
                    direction=[0.57735, 0.57735, 0.57735],
                    parameters=section_parameters,
                    process='major',
                    stop_criteria={'TMD': TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)},
                    step_size_distribution=seg_len,
                    pathlength=0.0)

    return algo, grower


def _assert_dict_or_array(dict1, dict2):
    assert_equal(set(dict1.keys()), set(dict2.keys()))
    for key in dict1.keys():
        if isinstance(dict1[key], np.ndarray):
            assert_array_almost_equal(dict1[key], dict2[key])
        elif isinstance(dict1[key], dict):
            _assert_dict_or_array(dict1[key], dict2[key])
        else:
            assert_equal(dict1[key], dict2[key], 'Error for key: %s' % key)


def test_TMDAlgo():
    algo, grower = _setup_test(TMDAlgo, SectionGrowerPath)

    stop, num_sec = algo.initialize()
    assert_dict_equal(stop, {"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)})
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(s1,
                          {'direction': [0., 0., 0.],
                           'process': 'major',
                           'first_point': [1.1, 0. , 0. ],
                           'stop': {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=0, term=159.798, ref=0.0)}})

    _assert_dict_or_array(s2,
                          {'direction': [0., 0., 0.],
                           'process': 'major',
                           'first_point': [1.1, 0. , 0. ],
                           'stop': {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=1, term=124.8796, ref=0.0)}})


def test_TMDApicalAlgo():
    algo, grower = _setup_test(TMDApicalAlgo, SectionGrowerPath)

    stop, num_sec = algo.initialize()
    expected_stop = {"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)}
    assert_dict_equal(stop, expected_stop)
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(s1,
                          {'direction': [0.57735, 0.57735, 0.57735],
                           'process': 'major',
                           'first_point': [1.1, 0. , 0. ],
                           'stop': {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=0, term=159.798, ref=0.0)}})

    _assert_dict_or_array(s2,
                          {'direction': np.array([0.20348076, 0.54109933, 0.81597003]),
                           'process': 'secondary',
                           'first_point': [1.1, 0. , 0. ],
                           'stop': {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=1, term=124.8796, ref=0.0)}})


def test_TMDGradientAlgo():
    algo, grower = _setup_test(TMDGradientAlgo, SectionGrowerPath)

    stop, num_sec = algo.initialize()
    expected_stop = {"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)}
    assert_dict_equal(stop, expected_stop)
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(s1,
                          {'direction': [0.57735, 0.57735, 0.57735],
                           'process': 'major',
                           'first_point': [1.1, 0. , 0. ],
                           'stop': {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=0, term=159.798, ref=0.0)}})

    _assert_dict_or_array(s2,
                          {'direction': np.array([0.400454, 0.573604, 0.714573]),
                           'process': 'major',
                           'first_point': [1.1, 0. , 0. ],
                           'stop': {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=1, term=124.8796, ref=0.0)}})
