import collections
import itertools
import math
import operator
from PIL import Image


def permutations(values):
    '''Return an iterator whose .next() method returns the next consecutive
    permutation using the passed in values.  INFINITE SERIES.

    Example:
        >>> p = permutations('a')
        >>> next(p)
        'a'
        >>> next(p)
        'aa'
        >>> next(p)
        'aaa'
        >>> p = permutations('ab')
        >>> next(p)
        'a'
        >>> next(p)
        'b'
        >>> next(p)
        'aa'
        >>> next(p)
        'ab'
        >>> next(p)
        'ba'
        >>> next(p)
        'bb'
        >>> next(p)
        'aaa'
    '''
    length = len(values)
    chars = [0]
    while True:
        # reverse chars for more "human" generation
        yield ''.join(values[c] for c in reversed(chars))
        for (i, x) in enumerate(chars):
            if x >= length-1:
                chars[i] = 0
            else:
                chars[i] += 1
                break
        else:
            # All characters were reset.  We need a bigger search space.
            chars.append(0)


def compressed_matrix(matrix):
    '''A specialized matrix that compresses adjoining identical cells together.
    Each element will contain (length, value)

    Example:
        >>> m = [[1, 2, 3],
        ...      [4, 4, 4],
        ...      [5, 5, 6]]
        >>> lm = compressed_matrix(m)
        >>> lm == [[(1, 1), (1, 2), (1, 3)],
                   [(3, 4)],
                   [(2, 5), (1, 6)]]
        True
    '''
    new_matrix = []
    for row in matrix:
        new_row = []
        length = 1
        value = row[0]
        for cell in row[1:]:
            if cell == value:
                length += 1
            else:
                new_row.append((length, value))
                length = 1
                value = cell
        new_row.append((length, value))
        new_matrix.append(new_row)
    return new_matrix


def values_sorted_by_frequency(matrix, key=lambda x:x, min=2):
    counter = collections.defaultdict(int)
    for row in matrix:
        for cell in row:
            counter[key(cell)] += 1

    return sorted((c for (c, count) in counter.items() if count >= min), key=operator.itemgetter(1), reverse=True)


class ImageTable(object):
    def __init__(self, image, c='image'):
        self.image = image
        self.pixels = self.image_to_matrix(image)
        self.c = c

    def image_to_matrix(self, image):
        pixels = image.load()
        matrix = []
        for y in range(image.size[1]):
            row = []
            for x in range(image.size[0]):
                row.append(pixels[x, y])
            matrix.append(row)
        return matrix

    @classmethod
    def from_file(cls, file, *args, **kwargs):
        return cls(Image.open(file).convert('RGB'), *args, **kwargs)

    @property
    def color_classes(self):
        if not hasattr(self, '_color_classes'):
            aliased_colors = values_sorted_by_frequency(self.pixels)
            classes = permutations('abcdefghijklmnopqrstuvwxyz')
            self._color_classes = dict((c, next(classes)) for c in aliased_colors)

        return self._color_classes

    def cellattr(self, cell):
        if cell in self.color_classes:
            return 'class="%s"' % self.color_classes[cell]
        else:
            return 'style="background:#%02x%02x%02x"' % cell

    def styles(self, fout):
        fout.write('''\
p.%(class)s{width:%(width)s;}\
p.%(class)s a{float:left;width:1px;height:1px;padding:0;margin:0}''' % {'class': self.c, 'width': self.image.size[0]})
        for (color, cls) in self.color_classes.items():
            fout.write('p.%s .%s{background:#%02x%02x%02x}' % ((self.c, cls) + color))

    def main(self, fout):
        fout.write('<p class="%s">' % self.c)
        for row in self.pixels:
            for cell in row:
                fout.write('<a %s/>' % self.cellattr(cell))
        fout.write('</p>')

    def html(self, fout):
        fout.write('<html><head><style>')
        self.styles(fout)
        fout.write('</style><body>')
        self.main(fout)
        fout.write('</body></html>')


from_file = ImageTable.from_file


if __name__ == '__main__':
    import sys
    it = ImageTable.from_file(sys.argv[1])
    it.html(sys.stdout)
