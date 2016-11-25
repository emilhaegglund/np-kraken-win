# np-kraken-win
Script to run kraken in Windows using Docker and local basecalled MinION reads.  
Plot the result in a browser windows using Bokeh.  
Remember to insert the Myformatter code in bokeh.models.formatters.py to get the ticks to display Specie name.
To run kraken in a docker container, remember to increase the amount of RAM used by the virtual machine. 8Gb should do it.
Currently only for visualizing old runs.
Dockerfile based on: https://github.com/dkoslicki/CAMIKraken
