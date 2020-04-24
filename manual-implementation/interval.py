import re


class Interval:

    def __init__(self, interval: str = None, quality: str = None, size: int = None):
        if interval:
            if not isinstance(interval, str):
                raise ValueError('Interval argument must be a string.')
            if not re.match(r'^[MmPA][0-8]$', interval):
                raise ValueError('Interval argument must match the regex ^[MmPA][0-8]$')
            self.quality = interval[0]
            self.size = int(interval[1])
        elif quality and size:
            self.quality = quality
            self.size = size
        else:
            raise ValueError('Must specify either interval string or quality and size')

    def __str__(self):
        return f'Interval({self.quality}{self.size})'

    def __repr__(self):
        return f'Interval({self.quality}{self.size})'
