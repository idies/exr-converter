from exrconverter import exr2fits, fits2exr
from exrconverter.pixeltype import PixelType

input_fits="frame-r-006793-3-0127.fits"; output_exr = "frame-r-006793-3-0127.exr";
pixel_format = PixelType.FLOAT16
input_exr = output_exr
output_fits = "new_fits.fits"

fits2exr.convert(input_fits, output_exr, PixelType.FLOAT16)
#fits2exr.convert(input_fits, output_exr)


exr2fits.convert(input_exr, output_fits, PixelType.FLOAT16)
#exr2fits.convert(input_exr, output_fits)