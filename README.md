# exr-converter
This python package converts EXR images into several file formats, back and forth.

### Requirements
1.  OpenEXR C++ library. 

    Source code located in https://github.com/openexr/openexr
    
    There are several options for installing it:

    * Directly in linux or mac:    

      Ubuntu: `sudo apt-get install libopenexr-dev openexr`
      
      Mac: `sudo port install openexr`

       Check out https://excamera.com/sphinx/articles-openexr.html

    * Using Conda:

       `conda install -c conda-forge openexr`
          
       For more options, see https://anaconda.org/conda-forge/openexr
  
2. OpenEXR python bindings.

    Install them by running: 
    
    `pip install openexr`

    Source code located in https://github.com/jamesbowman/openexrpython 
    
    Note that if you installed the OpenEXR C++ library with `conda`, you might need to 
    clone and manually install this repo, since you might need to modify the base paths in `include_dirs` and `library_dirs` (defined in https://github.com/jamesbowman/openexrpython/blob/master/setup.py) to match the library base paths in your Anaconda installation.

### Installation 
1. Clone the repository:
 
    `git clone https://github.com/idies/exr-converter`

2. Enter the `./exr-converter` directory and run

    `python setup.py install`

3. Make sure all python packages listed in `requirements.txt` are already installed locally.

    `pip install -r requirements.txt`
    
### Example Code
   Located in `./examples`
