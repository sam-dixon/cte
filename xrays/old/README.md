X-Ray Analysis
==============

These scripts help with analyzing the X-Ray data taken in 2004 for the red-channel SNIFS CCD.

The x-Rays used were from a Fe-55 source. The spectral lines that should be seen, in order of decreasing brightness, are (from Janesick Section 2.3.2):
```
- K alpha        : 1620 e-
- K beta         : 1778 e-
- K alpha escape : 1133 e-
- K beta escape  : 1291 e-
- Silicon        : 487  e-
```

A simple way of measuring the charge transfer efficiency of a CCD is to expose the chip to X-rays of a known energy. Each x-ray hit on the CCD results in a known amount of charge being generated in the event. By plotting the amount of charge seen in each object vs the row number, we can see if the amount of charge that is read out decreases with increasing distance to the amplifier (a sign that the charge is being trapped along the way).

### Dependencies
The x-ray analysis uses [SEP](https://github.com/kbarbary/sep) to subtract the background from the images and extract objects.

### Interactive script
`interact.py` extracts the objects from a given object and opens an IPython shell so that they may be manipulated.

##### Usage
`python interact.py frame amp`

`frame` is the three-digit number used to identify the exposure. No need to append extra zeros -- this is done automatically. If the frame is bad (i.e. no gain measurement was made) the program complains and exits.

`amp` specifies the amplifier. Expected values are 'a' or 'b'.

##### Process
The script uses SEP to subtract the background and determine the background RMS. Then, all objects more than 5 sigma above the background are extracted and stored in a structured array called `objs`. `objs` is then filtered to remove flags objects and objects with ellipticity above 0.2. Another structured array called `sing_pix` contains all of the single-pixel events.

The values stored in the structured arrays can be found in the [documentation for SEP](http://sep.readthedocs.org/en/v0.4.x/index.html).

### All frames analysis
`all_frames.py` analyzes all of the good frames (i.e. those with gain measurements) in a given amplifier.

##### Usage
`python all_frames.py amp`

##### Process
For every good frame in the data set, the gain is read from gain_tbl.txt to convert the units in the image array from ADU to electrons. Then SEP extracts all objects (without flags) that are more than 5 sigma above the background. The data is filtered so that only single-pixel events in the K-alpha line remain. A scatter plot of row number versus pixel count (in electrons) is made for these events. The scatter plot is then binned, and a line is fit to the binned points.

The script reports a preliminary CTI number, given by the negative log of percentage of charge lost across the CCD.