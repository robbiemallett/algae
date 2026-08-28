# Light modelling code for Campbell et al. "An improved characterization of pan-Arctic sea ice algal production in the Arctic summer"

This repository contains the necessary code to calculate bottom-ice PAR intensity following the approach of Stroeve et al. (2024), making use of the code published alongside Heorton et al. (2025).

To reproduce our analysis you must run notebooks 1-10 in /code/ locally.

You will then probably need a server to run Python files in /server_code/: 1, 2, 3 &  `make_ssrd_netcdf.py'.

This will produce a netcdf of PAR for the different environments described in the manuscript.
