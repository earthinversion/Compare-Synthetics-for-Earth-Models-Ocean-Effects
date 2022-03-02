"""
This Python 3 script plots synthetic waveforms from two runs for a single station.

Federico Munch - June, 2021
Modified Utpal Kumar, Oct 2021
"""

# Load python packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from obspy.taup import TauPyModel
import yaml
import glob, os
import pandas as pd

import logging
logger = logging.getLogger(__name__)

## Reads the parameters.yml file
def read_params(inp = "input_params.yml"):
    params = {}
    with open(inp, "r") as stream:
        try:
            params = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return params

params = read_params(inp = "input_params.yml")
# --------------------------------- Auxiliar functions ---------------------------


def spectra(data, sampling_rate):
    # Plot the spectra of a signal (in variable data).
    fourier_transform = np.fft.rfft(data, n=np.size(data) * 3)
    abs_fourier_transform = np.abs(fourier_transform)
    power_spectrum = np.square(abs_fourier_transform)
    frequency = np.linspace(0, sampling_rate/2, len(power_spectrum))
    return frequency, power_spectrum


def great_circle_distance(lat1, lon1, lat2, lon2):
    # Compute great circle distance between points (lat1,lon1) and (lat2,lon2)
    lat1_rad = lat1 * np.pi / 180.
    lat2_rad = lat2 * np.pi / 180.
    lon1_rad = lon1 * np.pi / 180.
    lon2_rad = lon2 * np.pi / 180.

    dlon = np.abs(lon1_rad - lon2_rad)
    arg = np.sin(lat1_rad) * np.sin(lat2_rad) +\
        np.cos(lat1_rad) * np.cos(lat2_rad) * np.cos(dlon)
    dist = np.arccos(arg)
    dist = dist * 180/np.pi
    return dist


def read_waveforms(simulation_type, path):
    # read synthetic waveforms
    if simulation_type == 'specfem':
        sem_wave = np.genfromtxt(
            path+stn['code'].decode('utf-8')+'.'+stn['net'].decode('utf-8')+'.MX'+cmpnt+'.sem.ascii')
    elif simulation_type == 'regsem':
        sem_wave = np.genfromtxt(path+station+'_'+cmpnt)
    elif simulation_type == 'dsm':
        sem_wave = np.genfromtxt(path+station+'_u'+cmpnt)
    elif simulation_type == 'nms':
        sem_wave = np.genfromtxt(path+"U"+cmpnt+'_'+station)

    return sem_wave


# ------------------------ input ------------------------------------------ #
# Do you want to plot time series of spectra? Options: 'time' and 'frequency'
# plot_in = 'frequency'
for plot_in in ['frequency', 'time']:

    # 3D runs
    # 1D run
    # Indicate path to synthetic files run #2 and label (for plotting):
    path1 = params['specfem']['outputLoc']
    label1 = params['specfem']['label']
    simulation_type1 = 'specfem'

    path2 = params['regsem']['outputLoc']
    label2 = params['regsem']['label']
    simulation_type2 = 'regsem'

    path3 = params['nms']['outputLoc']
    label3 = params['nms']['label']
    simulation_type3 = 'nms'

    path4 = params['regsem2']['outputLoc']
    label4 = params['regsem2']['label']
    simulation_type4 = 'regsem'

    path5 = params['specfem_poly']['outputLoc']
    label5 = params['specfem_poly']['label']
    simulation_type5 = 'specfem'

    path6 = params['specfem_no_ocean']['outputLoc']
    label6 = params['specfem_no_ocean']['label']
    simulation_type6 = 'specfem'

    path7 = params['specfem-ocean-elev-rec']['outputLoc']
    label7 = params['specfem-ocean-elev-rec']['label']
    simulation_type7 = 'specfem'

    path8 = params['specfem-etopo_0']['outputLoc']
    label8 = params['specfem-etopo_0']['label']
    simulation_type8 = 'specfem'

    path9 = params['specfem_rearth_6371']['outputLoc']
    label9 = params['specfem_rearth_6371']['label']
    simulation_type9 = 'specfem'

    # Event coordinates [in deg]
    eventdf = pd.read_csv(params['specfem']['cmtFile'], skiprows=1, delimiter=':', names=['params', 'values'], header=None)
    eventdf.set_index('params', inplace=True)
    # eventdf_inputs = [mi.strip() for mi in eventdf['params'].values]
    elon = float(str(eventdf.loc['longitude', 'values']).strip())
    elat = float(str(eventdf.loc['latitude', 'values']).strip())
    edep = float(str(eventdf.loc['depth', 'values']).strip())

    # path to specfem STATION file (for station coordinate information)
    specfem_STATION_file = params['specfem']['stationFile']

    # Station name (check file "STATIONS" to see the entire list of modelled stations):
    # station = 'FFC'
    #stnList = params['inputStations'] #['FFC', 'BBB', 'DWPF']
    stnList0 = glob.glob(os.path.join(path2,"*_Z"))
    
    stnList = [os.path.basename(stn).split("_")[0] for stn in stnList0]

    for station in stnList:
        # Time window for plotting the spectra [in sec]
        twin = [params['timeWindowSpectra']['min'], params['timeWindowSpectra']['max']]

        # make sure that the station name is correct
        assert np.any(station == np.array(stnList)),\
            print(" This plotting scripts only visualizes stations",",".join(stnList))


        # Time window to plot [limits for the plot in time]
        xmin = params['timeWindowTimeSeries']['min']
        xmax = params['timeWindowTimeSeries']['max']

        # Source time function shift [in seconds]
        tshift = params['sftshift']

        # compute travel times (and plot) travel times for the following phases:
        phase_list = np.array(params['phasesToCompute'])

        # ------------------------ main ------------------------------------------- #
        #print(" >> Plotting traces for "+station+" in "+plot_in+" domain")
        # start Taup
        model = TauPyModel(model=params['TauPModel'])

        # Load station list
        stations_list = np.loadtxt(specfem_STATION_file,
                                      dtype=[('code', 'S9'), ('net', 'S2'), ('lat', '<f8'), ('lon', '<f8'),('dum1', '<f8'), ('dum2', '<f8')], ndmin=1)
        

        # Plot traces for a receiver in station
        for stn in stations_list:
            if (stn['code'].decode('utf-8').split('.')[-1].replace('_', '') == station):
                
                # print(" >> Plotting traces for "+station+" in "+plot_in+" domain")
                # Compute epicentral distance
                dist = great_circle_distance(lat1=elat, lon1=elon,
                                             lat2=stn['lat'], lon2=stn['lon'])
                # Get traveltimes
                arrivals = model.get_travel_times(source_depth_in_km=edep,
                                                  distance_in_degree=dist)
                
                #print(f"dist: {dist}, arrivals: {len(arrivals)}")
                # Create figure frame
                if plot_in == 'time':
                    plt.figure(figsize=(14, 6))
                elif plot_in == 'frequency':
                    # plt.figure(figsize=(6,8))
                    plt.figure(figsize=(12, 8))

                # plot each component
                for cmpnt in ['Z', 'E', 'N']:
                    if cmpnt == 'Z':
                        plt.subplot(311)
                        plt.title(station + ' ($\\Delta: $' +
                                  "{:.2f}".format(dist)+')')
                    elif cmpnt == 'E':
                        plt.subplot(312)
                    elif cmpnt == 'N':
                        plt.subplot(313)
                        plt.xlabel('Time [s]')
                    plt.ylabel(cmpnt)

                    # read synthetics
                    ## specfem
                    sem_path1 = read_waveforms(simulation_type=simulation_type1,
                                               path=path1)
                    ## regsem_ocean
                    sem_path2 = read_waveforms(simulation_type=simulation_type2,
                                               path=path2)
                    ## nms
                    sem_path3 = read_waveforms(simulation_type=simulation_type3,
                                               path=path3)
                    ##regsem_noocean
                    sem_path4 = read_waveforms(simulation_type=simulation_type4,
                                               path=path4)
                    ##specfem_poly
                    sem_path5 = read_waveforms(simulation_type=simulation_type5,
                                               path=path5)
                    ##specfem_no_ocean
                    sem_path6 = read_waveforms(simulation_type=simulation_type6,
                                               path=path6)
                    ##specfem-ocean-elev-rec
                    sem_path7 = read_waveforms(simulation_type=simulation_type7,
                                               path=path7)
                    ##specfem-etopo_0
                    sem_path8 = read_waveforms(simulation_type=simulation_type8,
                                               path=path8)
                    ##specfem_rearth_6371
                    sem_path9 = read_waveforms(simulation_type=simulation_type9,
                                               path=path9)

                    if plot_in == 'time':
                        sem_path_dict = {}
                        # plot signals
                        if params['plot_toggles']['specfem']:
                            plt.plot(sem_path1[:, 0]-tshift,
                                    sem_path1[:, 1], label=label1, color=params['specfem']['color'], ls=params['specfem']['lineStyle'])
                            sem_path_dict['specPath'] = sem_path1
                            sem_path_dict['specLab'] = label1

                        if params['plot_toggles']['specfem_poly']:
                            plt.plot(sem_path5[:, 0]-tshift,
                                    sem_path5[:, 1], label=label5, color=params['specfem_poly']['color'], ls=params['specfem_poly']['lineStyle'])
                            sem_path_dict['specPath'] = sem_path5
                            sem_path_dict['specLab'] = label5

                        if params['plot_toggles']['specfem_no_ocean']:
                            plt.plot(sem_path6[:, 0]-tshift,
                                    sem_path6[:, 1], label=label6, color=params['specfem_no_ocean']['color'], ls=params['specfem_no_ocean']['lineStyle'])
                            sem_path_dict['specPath'] = sem_path6
                            sem_path_dict['specLab'] = label6

                        if params['plot_toggles']['specfem-ocean-elev-rec']:
                            plt.plot(sem_path7[:, 0]-tshift,
                                    sem_path7[:, 1], label=label7, color=params['specfem-ocean-elev-rec']['color'], ls=params['specfem-ocean-elev-rec']['lineStyle'])
                            sem_path_dict['specPath'] = sem_path7
                            sem_path_dict['specLab'] = label7

                        if params['plot_toggles']['specfem-etopo_0']:
                            plt.plot(sem_path8[:, 0]-tshift,
                                    sem_path8[:, 1], label=label8, color=params['specfem-etopo_0']['color'], ls=params['specfem-etopo_0']['lineStyle'])
                            sem_path_dict['specPath'] = sem_path8
                            sem_path_dict['specLab'] = label8

                        if params['plot_toggles']['specfem_rearth_6371']:
                            plt.plot(sem_path9[:, 0]-tshift,
                                    sem_path9[:, 1], label=label9, color=params['specfem_rearth_6371']['color'], ls=params['specfem_rearth_6371']['lineStyle'])
                            sem_path_dict['specPath'] = sem_path9
                            sem_path_dict['specLab'] = label9

                        if params['plot_toggles']['regsem']:
                            plt.plot(sem_path2[:, 0]-tshift,
                                    sem_path2[:, 1], label=label2, color=params['regsem']['color'], ls=params['regsem']['lineStyle'])
                            sem_path_dict['regPath'] = sem_path2
                            sem_path_dict['regLab'] = label2

                        if params['plot_toggles']['nms']:
                            plt.plot(sem_path3[:, 0]-tshift,
                                    sem_path3[:, 1], label=label3, color=params['nms']['color'], ls=params['nms']['lineStyle'])
                            sem_path_dict['nmsPath'] = sem_path3
                            sem_path_dict['nmsLab'] = label3
                        
                        # plt.plot(sem_path4[:, 0]-tshift,
                        #          sem_path4[:, 1], label=label4, color=params['regsem2']['color'], ls=params['regsem2']['lineStyle'])
                        if params['plot_toggles']['diff']:
                            diff_sem_path1 = sem_path_dict['specPath']
                            diff_sem_path2 = sem_path_dict['regPath']
                            # plot differences
                            if np.size(diff_sem_path1[:, 1]) == np.size(diff_sem_path2[:, 1]):
                                diff = (diff_sem_path1[:, 1] - diff_sem_path2[:, 1])
                            else:
                                resampled = np.interp(
                                    diff_sem_path1[:, 0], diff_sem_path2[:, 0], diff_sem_path2[:, 1])
                                diff = resampled - diff_sem_path1[:, 1]
                            if params['diffAmp'] != 1:
                                diffLabel = f"{params['diffAmp']} x Diff."
                            else:
                                diffLabel = f"Diff. [{sem_path_dict['regLab']} - {sem_path_dict['specLab']}]"

                            plt.plot(diff_sem_path1[:, 0]-tshift, diff*params['diffAmp'],
                                    'k', label=diffLabel, linewidth=1.)
                        # Set boundaries x-axis
                        plt.xlim([xmin, xmax])
                        plt.gca().yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e'))

                        for ar in arrivals:
                            if np.any(phase_list == ar.name) & (ar.time < 1800):
                                plt.vlines(x=ar.time, ymin=np.min(sem_path1[:, 1]),
                                           ymax=np.max(sem_path1[:, 1]), color='k', linestyle='--', alpha=0.5)
                                if cmpnt == 'N':
                                    plt.text(ar.time, np.min(
                                        sem_path1[:, 1]), s=ar.name)
                    elif plot_in == 'frequency':
                        dt = np.mean(np.diff(sem_path1[:, 0]))
                        # Find time window of interest
                        idx = np.where((sem_path1[:, 0] > twin[0]) & (
                            sem_path1[:, 0] <= twin[1]))[0]
                        freq, power_spectrum1 = spectra(
                            data=sem_path1[idx, 1], sampling_rate=1/dt)

                        if params['plot_toggles']['specfem']:
                            plt.plot(freq, power_spectrum1, color=params['specfem']['color'],
                                    label=label1, linewidth=1.5)

                        #specfem_poly
                        if params['plot_toggles']['specfem_poly']:
                            resampled_specfem_poly = np.interp(
                                sem_path1[:, 0], sem_path5[:, 0], sem_path5[:, 1])
                            freq_specfem_poly, power_spectrum2_specfem_poly = spectra(
                                data=resampled_specfem_poly[idx], sampling_rate=1/dt)
                            plt.plot(freq_specfem_poly, power_spectrum2_specfem_poly, color=params['specfem_poly']['color'],
                                    label=label5, linewidth=1.5)

                        #specfem_no_ocean
                        if params['plot_toggles']['specfem_no_ocean']:
                            resampled_specfem_noocean = np.interp(
                                sem_path1[:, 0], sem_path6[:, 0], sem_path6[:, 1])
                            freq_specfem_noocean, power_spectrum2_specfem_noocean = spectra(
                                data=resampled_specfem_noocean[idx], sampling_rate=1/dt)
                            plt.plot(freq_specfem_noocean, power_spectrum2_specfem_noocean, color=params['specfem_no_ocean']['color'],
                                    label=label6, linewidth=1.5)

                        #specfem-ocean-elev-rec
                        if params['plot_toggles']['specfem-ocean-elev-rec']:
                            resampled_specfem_ocean_elev_rec = np.interp(
                                sem_path1[:, 0], sem_path7[:, 0], sem_path7[:, 1])
                            freq_specfem_ocean_elev_rec, power_spectrum2_specfem_ocean_elev_rec = spectra(
                                data=resampled_specfem_ocean_elev_rec[idx], sampling_rate=1/dt)
                            plt.plot(freq_specfem_ocean_elev_rec, power_spectrum2_specfem_ocean_elev_rec, color=params['specfem-ocean-elev-rec']['color'],
                                    label=label7, linewidth=1.5)

                        #specfem-etopo_0
                        if params['plot_toggles']['specfem-etopo_0']:
                            resampled_specfem_etopo_0 = np.interp(
                                sem_path1[:, 0], sem_path8[:, 0], sem_path8[:, 1])
                            freq_specfem_etopo_0, power_spectrum2_specfem_etopo_0 = spectra(
                                data=resampled_specfem_etopo_0[idx], sampling_rate=1/dt)
                            plt.plot(freq_specfem_etopo_0, power_spectrum2_specfem_etopo_0, color=params['specfem-etopo_0']['color'],
                                    label=label8, linewidth=1.5)

                        #specfem_rearth_6371
                        if params['plot_toggles']['specfem_rearth_6371']:
                            resampled_specfem_rearth_6371 = np.interp(
                                sem_path1[:, 0], sem_path9[:, 0], sem_path9[:, 1])
                            freq_specfem_rearth_6371, power_spectrum2_specfem_rearth_6371 = spectra(
                                data=resampled_specfem_rearth_6371[idx], sampling_rate=1/dt)
                            plt.plot(freq_specfem_rearth_6371, power_spectrum2_specfem_rearth_6371, color=params['specfem_rearth_6371']['color'],
                                    label=label9, linewidth=1.5)

                        ## regsem_with ocean
                        if params['plot_toggles']['regsem']:
                            resampled = np.interp(
                                sem_path1[:, 0], sem_path2[:, 0], sem_path2[:, 1])
                            freq, power_spectrum2 = spectra(
                                data=resampled[idx], sampling_rate=1/dt)
                            plt.plot(freq, power_spectrum2, color=params['regsem']['color'],
                                    label=label2, linewidth=1.5)

                        #nms
                        if params['plot_toggles']['nms']:
                            resampled_nms = np.interp(
                                sem_path1[:, 0], sem_path3[:, 0], sem_path3[:, 1])
                            freq_nms, power_spectrum2_nms = spectra(
                                data=resampled_nms[idx], sampling_rate=1/dt)
                            plt.plot(freq_nms, power_spectrum2_nms, color=params['nms']['color'],
                                    label=label3, linewidth=1.5)


                        ## Plot difference
                        # plt.plot(freq, (power_spectrum1-power_spectrum2)*10, color='k',
                        #          label='10 x Diff.', linewidth=1.5)
                        # set boundaries x-axis
                        plt.xlim([0, 0.04])
                        plt.xlabel('Frequency [Hz]')
                        plt.ylabel('Power Spectra '+cmpnt)

                    # Plot legend
                    if cmpnt == 'N':
                        plt.legend(loc='lower right', ncol=1, fontsize=10)
                plt.tight_layout()
                outputFig = f"figures/{station}_{plot_in}.png"
                plt.savefig(outputFig, dpi=params['outputImageDPI'])
                print(f" >>>> Output figure is {outputFig}")
                plt.close()
        # plt.show()
