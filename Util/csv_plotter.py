import numpy as np
import csv
import matplotlib.pyplot as plt
import time
import os


class CsvPlotter:
    def __init__(self):
        self.time_init = time.time()
        try:
            os.remove("data234.csv")
        except:
            pass
        self.file = open("data234.csv", 'w')


    def write(self, values):
        self.time = time.time() - self.time_init
        writer = csv.writer(self.file, dialect='excel')
        values += [self.time]
        writer.writerow(values)

if __name__ == '__main__':
    fig = plt.figure()
    data = np.genfromtxt('../data234.csv', delimiter=',', skip_header=10,
                         skip_footer=10, names=['x1', 'x2', 't'])
    ax1 = fig.add_subplot(111)
    ax1.plot(data['t'], data['x1'], color='r', label='kalman_speed')
    ax1.plot(data['t'], data['x2'], color='b', label='commanded_speed')
    ax1.set_title("Mains power stability")
    ax1.set_xlabel('time')
    ax1.set_ylabel('Mains voltage')

    leg = ax1.legend()

    plt.show()