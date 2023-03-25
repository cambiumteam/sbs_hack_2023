from typing import Union

from fastapi import FastAPI
from pydantic_geojson import PolygonModel
import server.utils as utils
from shapely.geometry import shape
import shapely.geometry
import utm


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/process")
async def process(polygon: PolygonModel):
    boundary = shape(polygon)
    bbox = utils.get_bbox(boundary)
    bbox_padded = utils.get_bbox(boundary, padding=1e-3)
    boundary_utm = utils.reproject_shape(
        boundary, 
        src_crs=rio.crs.CRS.from_string('EPSG:4326'),
        dst_crs=greenest_crs
    )
    greenest, greenest_tf, greenest_crs = await sentinel2.get_ndvi_summary_by_bbox_async(
        bbox_padded, 
        dates = '2021-07-05/2021-07-15',
        masked_ratio_threshold=0.3,
    )
    
    # bbox_utm = boundary_utm.bounds
    # bbox_padded_utm = utils.get_bbox(
    #     shapely.geometry.box(
    #         *utm.from_latlon(*reversed(bbox_padded[0:2]))[0:2],
    #         *utm.from_latlon(*reversed(bbox_padded[2:4]))[0:2],
    #     )
    # )




