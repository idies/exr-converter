import numpy


class PixelType(object):
    FLOAT16 = numpy.float16
    FLOAT32 = numpy.float32
    FLOAT64 = numpy.float64
    INT8 = numpy.int8
    INT16 = numpy.int16
    INT32 = numpy.int32
    UINT16 = numpy.uint16

    @classmethod
    def has(cls, value):
        return hasattr(cls, value)
