from osgeo import gdal
import numpy as np
import os

def embed_geo_data(fname: str, tif_path: os.PathLike, geo_data: np.ndarray):
    """
    Embeds geographical data from a NumPy array into a new georeferenced TIF file.

    Args:
        fname (str):            Name of the output TIF file.
        tif_path (os.PathLike): Path to the original TIF file.
        geo_data (np.ndarray):  NumPy array containing geographical data with the 
                                same spatial dimensions as the original TIF file.
    """

    # Open the original TIF file
    with gdal.Open(tif_path, gdal.GA_ReadOnly) as src_ds:
        # Get information from the original file
        driver = gdal.GetDriverByName('GTiff')
        geotransform = src_ds.GetGeoTransform()
        projection = src_ds.GetProjection()
        cols, rows = src_ds.RasterXSize, src_ds.RasterYSize

    # Create a new TIF file with the same dimensions and projection
    if not fname.endswith('.tif'):
        fname += '.tif'
    out_ds = driver.Create(f"{tif_path[:-4]}_geo.tif", cols, rows, 1, gdal.GDT_Float32)

    # Set geotransform and projection for the new file
    out_ds.SetGeoTransform(geotransform)
    out_ds.SetProjection(projection)

    # Write the geographical data to the new file
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(geo_data)

    # Flush data to disk and close the file
    out_band.FlushCache()
    out_ds = None

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