import pygmt
import numpy as np
import os, glob
# import matplotlib.pyplot as plt
import pandas as pd
# import matplotlib
import yaml


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

def plot_stations(
    eventfile=params['specfem']['cmtFile'],
    stationfile=params['specfem']['stationFile'],
    res="i",
    plotRes = 300,
    outputfile = 'event_station_map.png',
    offset = 5
):
    ## read station file
    df_stns = pd.read_csv(stationfile, delimiter='\s+', names=['netsta', 'reg', 'lat', 'lon', 'depth', 'xx'], header=None)

    ## read event info
    df_event = pd.read_csv(eventfile, delimiter=':', names=['params', 'val'], skiprows=1, header=None)
    df_event.set_index('params', inplace=True)

    # print(df_stns.head())
    # print(df_event.head())
    # print(df_event.loc['latitude','val'])
    elat, elon = float(df_event.loc['latitude','val']), float(df_event.loc['longitude','val'])
    # print(df_stns['lat'].min(),elat)
    minlat, minlon = min(df_stns['lat'].min(),elat) - offset, min(df_stns['lon'].min(), elon) - offset
    maxlat, maxlon = max(df_stns['lat'].max(),elat) + offset, max(df_stns['lon'].max(), elon) + offset

    print(minlon, maxlon, minlat, maxlat)
    topo_data = '@earth_relief_30s' #30 arc second global relief (SRTM15+V2.1 @ 1.0 km)
    # make color pallets
    pygmt.makecpt(
        cmap='topo',
        series='-8000/8000/1000',
        continuous=True
    )

    fig = pygmt.Figure()

    #plot high res topography
    fig.grdimage(
        grid=topo_data,
        region=[minlon, maxlon, minlat, maxlat],
        projection='M6i',
        shading=True,
        frame=True
        )


    # fig.coast(
    #     land="white",
    #     water="lightblue",
    #     area_thresh=4000,
    #     shorelines="0.25p,black",
    # )
    fig.coast(
        area_thresh=4000,
        shorelines="0.25p,black",
        resolution=res
    )

    exponent = 16
    factor = 10**exponent
    
    m_rr = float(df_event.loc['Mrr','val'])/factor
    m_tt = float(df_event.loc['Mtt','val'])/factor
    m_pp = float(df_event.loc['Mpp','val'])/factor
    m_rt = float(df_event.loc['Mrt','val'])/factor
    m_rp = float(df_event.loc['Mrp','val'])/factor
    m_tp = float(df_event.loc['Mtp','val'])/factor

    # store focal mechanisms parameters in a dict
    focal_mechanism = dict(mrr=m_rr, mtt=m_tt, mff=m_pp, mrt=m_rt, mrf=m_rp, mtf=m_tp, exponent=exponent)
    fig.meca(focal_mechanism, scale="0.3i", longitude=elon, latitude=elat, depth=float(df_event.loc['depth','val']),G='red')
    
    fig.plot(
            x=df_stns['lon'].values,
            y=df_stns['lat'].values,
            style="i15p",
            color='blue',
            pen="black",
        )
    for lon, lat, stn in zip(df_stns['lon'].values, df_stns['lat'].values, df_stns['netsta'].values):
        fig.text(
                x=lon,
                y=lat,
                text=stn,
                offset="0p/-15p",
                fill="white",
                font="10p,Helvetica-Bold,black",
            )

    
    fig.savefig(outputfile, crop=True, dpi=plotRes)
    

if __name__=="__main__":
    plot_stations(
        eventfile=params['specfem']['cmtFile'],
        stationfile=params['specfem']['stationFile'],
        res="i",

        plotRes = 300,
        outputfile = 'event_station_map.png')
