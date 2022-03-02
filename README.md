## How to run?
1. Edit the [input_params.yml](input_params.yml)
1. Run the script [`check_traces_single_station.py`](check_traces_single_station.py)
    ```
    python check_traces_single_station.py
    ```

## Dependencies
1. Numpy
1. Matplotlib
1. Obspy
1. Pyyaml
1. Pandas

## Input parameters
Model: **Preliminary Earth Reference Model**, with the ocean layer of thickness 3 km
* Spherical Earth: ON
* Anisotropy: ON
* **Oceans: ON**
* Topography: ON
* Gravity: OFF
* Attenuation: OFF
* Ellipticity: OFF

## Input Event and Stations Locations
<hr>
<p align="center">
<img src="event_station_map.png" alt="Event-Stations Map" />
</p>
<p align="center"><b>Event-Stations Map</b></p>
<hr>

## Results
- Define the input models and the synthetics paths

<hr>
<p align="center">
<img src="figures/BBB_time.png" alt="BBB Time" />
</p>
<p align="center"><b>BBB Time</b></p>
<hr>

<p align="center">
<img src="figures/BBB_frequency.png" alt="BBB Frequency" />
</p>
<p align="center"><b>BBB Frequency</b></p>
<hr>