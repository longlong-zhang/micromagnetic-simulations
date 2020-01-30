import os
import sys
import random
import numpy as np
import time


def run_mumax_script(filename: str):
    os.system('mumax3-cuda6.5 ./mumax_scripts/' + filename)


def get_meta_data(file_path: str):
    headers = {}
    with open(file_path) as f:
        for line in f:
            if line[0] != '#': break
            if ':' in line:
                key_value = line.split('# ')[1].split(':')
                key, value = key_value[0], key_value[1].split('\n')[0].strip()
                headers[key] = value
    return int(headers['xnodes']), int(headers['ynodes']), int(headers['znodes']), \
           float(headers['xstepsize']), float(headers['ystepsize']), float(headers['zstepsize'])


def initialise_gridspace(x0: [int], filename: str, x: int, y: int):
    configs = ['uniform(0, 0, 0)', 'uniform(0, 1, 0)', 'uniform(0, -1, 0)',
               'uniform(1, 0, 0)', 'uniform(-1, 0, 0)']
    empty_space = [i for i in range(1, x*y + 1, int(y/2))]
    with open('./boilerplate12x12.mx3') as f:
        with open('./mumax_scripts/' + filename, 'w') as f1:
            for line in f:
                f1.write(line)
            lines = ''
            # Exclude indices that are not part of the empty space
            for i in range(1, x*y+1):
                if i not in empty_space:
                    lines += 'm.SetRegion(' + str(i) + ', ' + configs[x0[i-1]] + ')\n'
                    # If the cell is initialised empty, set it as an actual empty cell
                    # with no magnetic saturation (as in vacuum)
                    if x0[i-1] == 0:
                        lines += 'Msat.SetRegion(' + str(i) + ', 0)\n'
                        lines += 'Aex.SetRegion(' + str(i) + ', 0)\n'
                        lines += 'Kc1.SetRegion(' + str(i) + ', 0)\n'
            lines += 'relax()\n'
            lines += 'saveas(m, "m_optimise")\n'
            lines += 'saveas(B_demag, "strayfield_optimise")\n'
            f1.write(lines)


def find_max_B(file_path: str):
    ovf_path = './mumax_scripts/' + file_path + '.out/' + 'strayfield_optimise.ovf'
    x, y, z, _, _, _ = get_meta_data(ovf_path)
    zslice = int(z / 2)
    yslice = int(y / 2)
    data = np.array(np.loadtxt(ovf_path))
    data_field = data.reshape(x, y, z, 3, order='F')
    u, v, w = data_field[:, :, :, 0], data_field[:, :, :, 1], data_field[:, :, :, 2]
    mag = (u * u + v * v + w * w) ** 0.5
    mag_slice = mag[:, yslice, zslice]
    return max(mag_slice)


def acceptance_probability(old, new, T):
    """
    If the new cost value is larger than the old one, accept the new cost
    value with 100% probability. If the new cost value is smaller than the old,
    accept the new cost value with a probability equal to exp[(new - old) / T]
    T gets smaller at every iteration, i.e. we accept bad cost values with
    lower probability
    """
    if new > old:
        a = 1
    else:
        a = np.exp((new - old) / T)
    return a


def simulated_annealing(x0, T, T_min, alpha, x: int, y: int):
    max_costs = []
    max_actions = []
    max_cost = 0.01
    empty_space = [i for i in range(1, x*y + 1, int(y/2))]
    while T > T_min:
        count = 0
        while(count < 100):
            filename = str(T).replace('.', '') + '_' + str(count) + '.mx3'
            initialise_gridspace(x0, filename, x, y)
            run_mumax_script(filename)
            while not os.path.exists('./mumax_scripts/' + filename.split('.')[0] + '.out'):
                time.sleep(5)
            cost_new = find_max_B(filename.split('.')[0])
            print('new cost: ' + str(cost_new))
            ep = acceptance_probability(max_cost, cost_new, T)
            if ep > random.random():
                max_cost = cost_new
                max_action = x0.copy()
                max_costs.append(max_cost)
                max_actions.append(max_action)
            while True:
                idx = random.choice([i for i in range(1, x*y+1)])
                if idx not in empty_space:
                    break
            x0[idx-1] = random.choice([0, 1, 2, 3, 4])
            count += 1
            print('max cost: ' + str(max_cost))
        np.save("sim_annealing/costs" + str(T), max_costs)
        np.save("sim_annealing/action" + str(T), max_actions)
        T = T * alpha


x = 12
y = 12
x0 = [0 for i in range(x*y)]
x0 = '0 0 3 2 2 1 0 3 1 0 4 3 0 2 2 1 2 0 0 4 1 0 2 2 0 2 0 0 2 4 0 3 3 0 1 0 0 0 1 1 3 3 0 2 2 3 3 4 0 3 4 1 4 1 0 1 1 3 0 2 0 4 0 0 3 0 0 3 2 3 2 2 0 4 2 3 0 2 0 2 4 2 1 3 0 4 1 3 1 3 0 3 0 1 0 3 0 2 2 0 4 3 0 3 2 3 1 2 0 1 4 0 0 4 0 4 2 0 4 1 0 1 4 2 0 2 0 3 4 0 1 1 0 1 2 0 0 1 0 2 3 3 3 1'
x0 = x0.split(' ')
x0 = [int(i) for i in x0]
print(x0)
print(len(x0))
T = 0.8 ** 42
T_min = 0.00001
alpha = 0.8
simulated_annealing(x0, T, T_min, alpha, x, y)
