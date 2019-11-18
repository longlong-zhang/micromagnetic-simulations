import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('ggplot')
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 16
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['figure.figsize'] = 8, 5
plt.rcParams.update({'figure.autolayout': True})
plt.rcParams['mathtext.default'] = 'regular'

def process_mumax_single_cobalt_vary_z():
    widths = [i for i in range(70, 85, 5)]
    for w in widths:
        df = pd.read_csv('./data/hysteresis/mumax/double/cobalt_x-600-70/y-70-100-' + str(w) + '.txt', delimiter="\t")
        x = df['B_exty (T)']
        y = df['my ()']
        y = y/max(y)
        plt.plot(x, y, label=str(w)+'nm')
        plt.legend()
    plt.savefig('y-cobalt-double-vary-width-w0-70.pdf', dpi=1000)

    # widths = [i for i in range(100, 110, 10)]
    # for w in widths:
    #     df = pd.read_csv('./data/hysteresis/mumax/double/cobalt_x-600-100/y-100-' + str(w) + '-100.txt', delimiter="\t")
    #     x = df['B_exty (T)']
    #     y = df['my ()']
    #     y = y/max(y)
    #     plt.plot(x, y, label=str(w)+'nm')
    #     # plt.xlim([-0.2, 0.2])
    #     plt.legend()
    plt.show()

process_mumax_single_cobalt_vary_z()
