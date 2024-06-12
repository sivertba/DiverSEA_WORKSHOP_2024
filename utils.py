import numpy as np
from osgeo import gdal
from osgeo import osr
from pathlib import Path

from hypso.georeference.reference import generate_geotiff

def embed_geo_data(fname: str, satObj, geo_data: np.ndarray) -> None:
    """
    Generate RGB GeoTiff image

    :param satObj: Hypso satellite object.
    :param overwrite: If true, overwrite the previously generated RGB GeoTiff image

    :return: No return
    """


    # GeoTiff Output ------------------------------------------------------------------------
    top_folder_name = satObj.info["top_folder_name"]
    geotiff_folder_path = Path(top_folder_name, "geotiff")
    output_path_rgba_tif = Path(geotiff_folder_path, fname)

    # Select data for RGB GeoTiff --------------------------------------------------------
    geo_data = np.nan_to_num(geo_data)
    cube_data = np.repeat(geo_data[:, :, np.newaxis], 3, axis=2)

    # Get Geometric Information----------------------------------------------------------------
    grid_dims, geotransform, destination_epsg, grid_data_all_bands, _ = generate_geotiff(satObj, [0,1,2],
                                                                                                    cube_data)

    # Geotiff Objects ------------------------------------------------------------------------------------------
    # some Geotiff reference info:
    # https://gis.stackexchange.com/questions/380607/how-to-geo-reference-a-tif-image-knowing-corner-coordinates
    # https://gis.stackexchange.com/questions/275125/expressing-raster-rotation-with-gdal-geotransform-python

    dst_ds_alpha_channel = gdal.GetDriverByName('GTiff').Create(
        str(output_path_rgba_tif), grid_dims[0], grid_dims[1], 1, gdal.GDT_Float32)

    dst_ds_alpha_channel.SetGeoTransform(geotransform)  # specify coords
    srs = osr.SpatialReference()  # establish encoding
    srs.ImportFromEPSG(destination_epsg)
    dst_ds_alpha_channel.SetProjection(
        srs.ExportToWkt())  # export coords to file
    
    data = grid_data_all_bands[:, :, 1]
    dst_ds_alpha_channel.GetRasterBand(1).WriteArray(data)
    dst_ds_alpha_channel.FlushCache()  # write to disk

def check4files():
    import requests
    from bs4 import BeautifulSoup
    import os

    secretUrl = "https://folk.ntnu.no/sivertba/diversea/"

    response = requests.get(secretUrl)
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup.prettify())

    # Get all files
    files = []
    for link in soup.find_all('a'):
        if '.' in link.get('href'): # only get files
            files.append(link.get('href'))
    print(files)
    # check if the files are in the cwd and if not, download them
    for f in files:
        if not os.path.exists(os.path.join(os.getcwd(), f)):
            print(f"Downloading {f}")
            url = secretUrl + f
            r = requests
            r = requests.get(url, allow_redirects=True)
            open(f, 'wb').write(r.content)
        else:
            print(f"{f} already exists in the current directory")