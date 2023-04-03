import GeoTIFF from "ol/source/GeoTIFF";
import OlMap from "ol/Map";
import TileLayer from "ol/layer/WebGLTile";
import React, { useRef, useState, useEffect } from "react";
import OLVectorLayer from "ol/layer/Vector";
import { Vector as VectorSource } from 'ol/source';
import { Style, Stroke, Fill } from 'ol/style';
import OlView from 'ol/View';


const source = new GeoTIFF({
  sources: [
    {
      url: "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/36/Q/WD/2020/7/S2A_36QWD_20200701_0_L2A/TCI.tif",
    },
  ],
});

const styles = {
  'MultiPolygon': new Style({
    stroke: new Stroke({
      color: 'blue',
      width: 1,
    }),
    fill: new Fill({
      color: 'rgba(0, 0, 255, 0.1)',
    }),
  }),
};

// const map = new OlMap({
//   target: "map",
//   layers: [
//     new TileLayer({
//       source: source,
//       // styles
//     }),
//   ],
//   view: source.getView(),
// });

const MyMap = (props: any) => {
  const mapRef = useRef<HTMLDivElement>();
  const [map, setMap] = useState<OlMap>();

  // on component mount
  useEffect(() => {
    const options = {
      // view: new OlView({ zoom, center }),
      view: source.getView(),
      // view: new OlView({ 
      //   zoom: 9, 
      //   center: [-58.54571135776393,-20.24371986163491]
      // }),
      layers: [
        new TileLayer({
          source: source,
        })
      ],
      controls: [],
      overlays: [],
    };
    const mapObject = new OlMap(options);
    mapObject.setTarget(mapRef.current);
    setMap(mapObject);
    return () => mapObject.setTarget(undefined);
  }, []);

  // // handle features
  // useEffect(() => {
  //   if (!map) return;
  //   if (props?.features && props.features.features.length > 0) {
  //     const source = new VectorSource(props.features.features);
  //     const vectorLayer = new OLVectorLayer({
  //       source,
  //       style: styles.MultiPolygon,
  //     });
  //     map.addLayer(vectorLayer);
  //     // vectorLayer.setZIndex(zIndex);
  //     vectorLayer.setZIndex(100);
  //     return () => {
  //       if (map) {
  //         map.removeLayer(vectorLayer);
  //       }
  //     };
  //   }
  // }, [props.features]);
  // // zoom change handler
  // useEffect(() => {
  //   if (!map) return;
  //   map.getView().setZoom(zoom);
  // }, [zoom]);
  // // center change handler
  // useEffect(() => {
  //   if (!map) return;
  //   map.getView().setCenter(center);
  // }, [center]);
  return (
    // <MapContext.Provider value={{ map }}>
      <div ref={mapRef} className="ol-map">
      </div>
    // </MapContext.Provider>
  );
};
export default MyMap;
