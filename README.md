# Light modelling code for Campbell et al. "An improved characterization of pan-Arctic sea ice algal production in the Arctic summer"

This repository contains the necessary code to calculate bottom-ice PAR intensity following the approach of Stroeve et al. (2024), making use of the code published alongside Heorton et al. (2025).

To reproduce our analysis you must run notebooks 1-10 in /code/ locally.

You will then probably need a server to run Python files in /server_code/: 1, 2, 3 &  `make_ssrd_netcdf.py'.

This will produce a netcdf of PAR for the different environments described in the manuscript.



Stroeve JC, Veyssiere G, Nab C, Light B, Perovich D, Laliberté J, Campbell K, Landy J, Mallett R, Barrett A, Liston GE. Mapping potential timing of ice algal blooms from satellite. Geophysical Research Letters. 2024 Apr 28;51(8):e2023GL106486.
Heorton, Harold DBS, Julienne C. Stroeve, and Gaëlle Veyssière. "Future under sea ice light availability and algal bloom timing from CMIP6 model simulations." Frontiers in Marine Science 12 (2025): 1642506.
