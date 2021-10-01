''' Example to generate a population of cells from input files'''
import json
import os
import neurots
from neurots import extract_input


def get_log_data(mtype, number_of_cells, params, output_path):
    '''Creates log and returns it.
       If output_path saves the data in json
    '''
    from neurots.version import VERSION as neurotsV
    from tmd.version import VERSION as tmdV
    import datetime
    import platform
    import getpass
    today = datetime.date.today()
    log_data = {'Date': '{} {} {}'.format(today.day, today.month, today.year),
                'NeuroTS version': neurotsV,
                'TMD version': tmdV,
                'Number of cells': number_of_cells,
                'Mtype': mtype,
                'OS': platform.version(),
                'Python': platform.python_version(),
                'Generated by' : getpass.getuser(),
                'Parameters': params}

    with open(os.path.join(output_path, 'Synthesis_log.json'), 'w') as F:
        json.dump(log_data, F, indent=2)


def create_population(input_distributions, input_parameters,
                      number_of_cells, output_path, output_name,
                      mtype=None, formats=None):
    '''Generates N - number_of_cells according to the provided input:
       - input distributions
       - input parameters
       Saves cells in the selected files formats (default: h5, swc, asc).
       in output_path with the name prefix output_name.
       Also saves a log file with information about the growth.
    '''
    get_log_data(mtype, number_of_cells, input_parameters, output_path=output_path)

    if formats is None:
        formats = ['swc', 'h5', 'asc']

    # Creates directories to save selected file formats
    for f in formats:
        if not os.path.isdir(output_path + f):
            os.mkdir(output_path + f)

    for i in range(number_of_cells):
        Ngrower = neurots.NeuronGrower(input_distributions=input_distributions,
                                   input_parameters=input_parameters)
        neuron = Ngrower.grow()
        Ngrower.diametrize()
        for f in formats:
            neuron.write(output_path + '/' + f + '/' + output_name + '_' + str(i+1) + '.' + f)
