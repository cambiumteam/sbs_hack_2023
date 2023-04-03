import React, { useEffect, useState } from "react";
import "./App.css";
import Map from "./components/OlMap/Map";
import { Layers, TileLayer, VectorLayer } from "./components/OlMap/Layers";
import { Circle as CircleStyle, Fill, Stroke, Style } from "ol/style";
import { osm, vector } from "./components/OlMap/Source";
import { fromLonLat, get } from "ol/proj";
import GeoJSON from "ol/format/GeoJSON";
import { Controls, FullScreenControl } from "./components/OlMap/Controls";
import OLTileLayer from "ol/layer/Tile";
import WGLTileLayer from "ol/layer/WebGLTile";
window.WGLTileLayer = WGLTileLayer;
window.OLTileLayer = OLTileLayer;
import OLVectorLayer from "ol/layer/Vector";
window.OLVectorLayer = OLVectorLayer;

import mapConfig from "./config.json";

const geojsonObject = mapConfig.geojsonObject;
const geojsonObject2 = mapConfig.geojsonObject2;
const markersLonLat = [mapConfig.kansasCityLonLat, mapConfig.blueSpringsLonLat];

import GeoTIFF from "ol/source/GeoTIFF";
import { features } from "process";
// import Map from 'ol/Map.js';
// import TileLayer from 'ol/layer/WebGLTile.js';

const source = new GeoTIFF({
  sources: [
    {
      url: "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/36/Q/WD/2020/7/S2A_36QWD_20200701_0_L2A/TCI.tif",
    },
  ],
});

// const map = new Map({
//   target: 'map',
//   layers: [
//     new TileLayer({
//       source: source,
//     }),
//   ],
//   view: source.getView(),
// });

const styles = {
  MultiPolygon: new Style({
    stroke: new Stroke({
      color: "blue",
      width: 1,
    }),
    fill: new Fill({
      color: "rgba(0, 0, 255, 0.1)",
    }),
  }),
};
const MapDemo = (props: any) => {
  // const [center, setCenter] = useState([-94.9065, 38.9884]);
  const [center, setCenter] = useState([-58.54571135776393,-20.24371986163491]);
  const [zoom, setZoom] = useState(9);
  const [showLayer1, setShowLayer1] = useState(true);
  const [showLayer2, setShowLayer2] = useState(true);
  const [testOlSource, setTestOlSource] = useState<any>();
  const [map, setMap] = useState<any>();

  const [featuresLayerSource, setFeaturesLayerSource] = useState({
    features: [],
  });
  useEffect(() => {
    if (props?.features && props.features.features.length > 0) {
      console.log('hey', props.features);
      const obj = new GeoJSON().readFeatures(props.features, {
        featureProjection: get("EPSG:3857"),
      });
      console.log('my thing', obj, vector(obj))
      setFeaturesLayerSource({
        features: obj,
      });
    }
  }, [props.features]);

  useEffect(() => {
    const source: any = vector({ features: [], url: props.featureCollectionUrl })
    setTestOlSource(source);
    console.log('use effect is working', props.featureCollectionUrl);
    source.on('change', () => { 
      // window.olmap.getView().fit(source.getExtent());
      const fitOptions = {
        size: map.getSize(),
        padding: [20, 20, 20, 20],
        maxZoom: 20,
      };
      map.getView().fit(source.getExtent(), fitOptions);
    });
    
  }, [props.featureCollectionUrl])
  return (
    <div>
      <Map center={fromLonLat(center)} zoom={zoom} setMapObj={setMap}>
        {/* <Map> */}
        <Layers>
          <TileLayer source={osm()} zIndex={0} />
          
          {/* <VectorLayer
            source={vector(featuresLayerSource)}
            // source={vector({ url: 'https://web2.co2.storage/ipfs/QmVLNxPAMkCw3MDGzDPkffeJpKqHmsnQ5VLMhrSKfNhJMU/'})}
            style={styles.MultiPolygon}
            zIndex={10}
          /> */}
          {/* <VectorLayer
            source={vector({ url: props.featureCollectionUrl })}
            // source={vector({ url: 'https://web2.co2.storage/ipfs/QmVLNxPAMkCw3MDGzDPkffeJpKqHmsnQ5VLMhrSKfNhJMU/'})}
            style={styles.MultiPolygon}
            zIndex={10}
          /> */}
          <VectorLayer
            source={testOlSource}
            // source={vector({ url: 'https://web2.co2.storage/ipfs/QmVLNxPAMkCw3MDGzDPkffeJpKqHmsnQ5VLMhrSKfNhJMU/'})}
            style={styles.MultiPolygon}
            zIndex={10}
          />
          {/* <TileLayer
          source={source}
          zIndex={0}
        /> */}

          {/* {showLayer1 && (
            <VectorLayer
              source={vector({
                features: new GeoJSON().readFeatures(geojsonObject, {
                  featureProjection: get("EPSG:3857"),
                }),
              })}
              style={styles.MultiPolygon}
            />
          )}
          {showLayer2 && (
            <VectorLayer
              source={vector({
                features: new GeoJSON().readFeatures(geojsonObject2, {
                  featureProjection: get("EPSG:3857"),
                }),
              })}
              style={styles.MultiPolygon}
            />
          )} */}

          
        </Layers>
        <Controls>
          <FullScreenControl />
        </Controls>
      </Map>
      <div>
        <input
          type="checkbox"
          checked={showLayer1}
          onChange={(event) => setShowLayer1(event.target.checked)}
        />{" "}
        Johnson County
      </div>
      <div>
        <input
          type="checkbox"
          checked={showLayer2}
          onChange={(event) => setShowLayer2(event.target.checked)}
        />{" "}
        Wyandotte County
      </div>
    </div>
  );
};
export default MapDemo;
