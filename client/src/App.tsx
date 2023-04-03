import React, { useState } from "react";
// import { ChakraProvider, Input, Text } from "@chakra-ui/react";
import Map, { Source, Layer } from "react-map-gl";
import maplibregl from "maplibre-gl";
import OlMap from "./components/OlMap/Map";

import MapDemo from "./MapDemo";
import MyMap from "./components/MyMap/MyMap";
import FeaturesForm from "./components/FeaturesForm/FeaturesForm";
import ProjectTable from "./components/ProjectTable/ProjectTable";
import ProcessButton from "./components/ProcessButton/ProcessButton";

const RASTER_SOURCE_OPTIONS = {
  // "type": "raster",
  // "tiles": [
  //   "https://someurl.com/512/{z}/{x}/{y}",
  // ],
  // "tileSize": 512
  type: "raster",
  url: "https://web2.co2.storage/ipfs/QmPEc9bjbhHJ1keQao7zLRjkQ2Su2wvm2FnDg6r9U4g5fA/outputs/ndvi-summary.tif",
};

import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";

import "maplibre-gl/dist/maplibre-gl.css";
import "./App.css";

import {
  isMapboxURL,
  transformMapboxUrl,
} from "maplibregl-mapbox-request-transformer";

const transformRequest = (url: string, resourceType: string) => {
  if (isMapboxURL(url)) {
    return transformMapboxUrl(
      url,
      resourceType,
      import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
    );
  }

  // Do any other transforms you want
  return { url };
};

function App() {
  // const [featuresUrl, setFeaturesUrl] = useState('');
  const [features, setFeatures] = useState({features: []});

  const fc1 = {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        geometry: {
          type: "Polygon",
          coordinates: [
            [
              [-58.5561865842015, -20.36540048286432, 0],
              [-58.55526742406304, -20.30851569194789, 0],
              [-58.54695763386918, -20.30843241687653, 0],
              [-58.54700421612423, -20.28946635616567, 0],
              [-58.54571135776393, -20.24371986163491, 0],
              [-58.5451852883676, -20.22508773190468, 0],
              [-58.57764828935018, -20.22510833481063, 0],
              [-58.57745434077569, -20.31790983963656, 0],
              [-58.58308693145964, -20.31791258467039, 0],
              [-58.58299153302925, -20.36509026642087, 0],
              [-58.5561865842015, -20.36540048286432, 0],
            ],
          ],
        },
        properties: {},
      },
    ],
  };
  // console.log(import.meta.env)
  // console.log(process.env)
  const [fcUrl, setFcUrl] = useState('');

  const handleTestFeaturesUrl = () => {
    setFcUrl('https://web2.co2.storage/ipfs/QmVLNxPAMkCw3MDGzDPkffeJpKqHmsnQ5VLMhrSKfNhJMU/');
  }
  return (
    // <ChakraProvider>
      <div className="App">
        {/* <FeaturesForm setFeatures={setFeatures} /> */}
        {/* <OlMap/> */}
        {/* <MyMap features={features} /> */}
        <ProjectTable setFcUrl={setFcUrl} />
        <button onClick={handleTestFeaturesUrl}>test features url</button>
        {/* <MapDemo features={features} /> */}
        <MapDemo featureCollectionUrl={fcUrl} />
        <ProcessButton featureCollectionUrl={fcUrl} />
        {/* <Map mapLib={maplibregl} 
          initialViewState={{
            longitude: 16.62662018,
            latitude: 49.2125578,
            zoom: 14
          }}
          mapStyle='mapbox://styles/mapbox/satellite-streets-v11'
          transformRequest={transformRequest}
          style={{width: "500px", height: "500px"}}
        >
          <Source 
            id="source_id" 
            type="image" 
            url="https://web2.co2.storage/ipfs/QmPEc9bjbhHJ1keQao7zLRjkQ2Su2wvm2FnDg6r9U4g5fA/outputs/ndvi-summary.tif"
            // tileJsonSource={RASTER_SOURCE_OPTIONS} 
            
          />
          <Layer type="raster" id="layer_id" source="source_id" />
  
        </Map> */}

        {/* <div>
          <a href="https://vitejs.dev" target="_blank"  rel="noreferrer" >
            <img src={viteLogo} className="logo" alt="Vite logo" />
          </a>
          <a href="https://reactjs.org" target="_blank"  rel="noreferrer" >
            <img src={reactLogo} className="logo react" alt="React logo" />
          </a>
        </div>
        <h1>Vite + React</h1>
        <div className="card">
          <button onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button>
          <p>
            Edit <code>src/App.tsx</code> and save to test HMR
          </p>
        </div>
        <p className="read-the-docs">
          Click on the Vite and React logos to learn more
        </p> */}
      </div>
    // </ChakraProvider>
  );
}

export default App;
