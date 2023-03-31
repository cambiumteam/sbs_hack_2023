with rio.Env():
    # rasters[[*rasters.keys()][0]]['B04']
    raster_name = rasters[[*rasters.keys()][0]]['B04']

    # Write an array as a raster band to a new 8-bit file. For
    # the new file's profile, we start with the profile of the source
    # profile = src.profile

    # And then change the band count to 1, set the
    # dtype to uint8, and specify LZW compression.
    # profile.update(
    #     dtype=rio.uint8,
    #     count=1,
    #     compress='lzw')

    # with rio.open('outputs/example.tif', 'w', **profile) as dst:
    with rio.open(, 'w', 
        driver="GTiff",
        height=raster_name[0].shape[0],
        width=raster_name[0].shape[1],
        count=1,
        dtype=raster_name[0].dtype,
        transform=raster_name[1],
        crs=raster_name[2],
        compress='lzw'
    ) as dst:
        dst.write(raster_name[0].astype(rio.uint8), 1)