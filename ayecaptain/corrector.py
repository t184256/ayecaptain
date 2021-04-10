import numpy as np
import scipy.ndimage


class Corrector:
    def __init__(self, size_x, size_y, sigma, correction_cap, save_each=100,
                 path='correction.npz'):
        self.path = path
        try:
            f = np.load(self.path)
            self.corr_x, self.corr_y = f['corr_x'], f['corr_y']
            assert self.corr_x.shape == (size_x * 2, size_y * 2)
            assert self.corr_y.shape == (size_x * 2, size_y * 2)
        except FileNotFoundError:
            print('Initializing new correction matrices!')
            self.corr_x = np.zeros((size_x * 2, size_y * 2))  # * 2 to mitigate
            self.corr_y = np.zeros((size_x * 2, size_y * 2))  # tail wrapping
        self.size_x, self.size_y, self.sigma = size_x, size_y, size_x * sigma
        self.x_fix_cap = self.size_x * correction_cap
        self.y_fix_cap = self.size_y * correction_cap
        self.save_each, self.learn_counter = save_each, 0

        print('Initializing correction kernel')
        self.b = np.zeros_like(self.corr_x)
        self.b[0, 0] = 1
        self.b = scipy.ndimage.gaussian_filter(self.b, self.sigma, mode='wrap')
        self.b /= np.max(self.b)
        print('Correction kernel inititialized')

    def bin_coord(self, x, y):
        i = np.clip(int((x + .5) * self.size_x), 0, self.size_x - 1)
        j = np.clip(int((y + .5) * self.size_y), 0, self.size_y - 1)
        return i, j

    def learn(self, x, y, x_fix, y_fix, weight):
        i, j = self.bin_coord(x, y)
        template = np.roll(self.b, (i, j), axis=(0, 1))
        x_fix, y_fix = min(x_fix, self.x_fix_cap), min(y_fix, self.y_fix_cap)
        self.corr_x += weight * x_fix * template
        self.corr_y += weight * y_fix * template
        self.learn_counter += 1
        if self.learn_counter % self.save_each == 0:
            np.savez(self.path, corr_x=self.corr_x, corr_y=self.corr_y)

    def correct(self, x, y):
        if x is None or y is None:
            return None, None
        i, j = self.bin_coord(x, y)
        return x + self.corr_x[i, j], y + self.corr_y[i, j]
