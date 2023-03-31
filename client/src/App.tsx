import React, { useState } from 'react'
import { ChakraProvider } from '@chakra-ui/react'
import Map from 'react-map-gl';
import maplibregl from 'maplibre-gl';

import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'

import 'maplibre-gl/dist/maplibre-gl.css';
import './App.css'


import { isMapboxURL, transformMapboxUrl } from 'maplibregl-mapbox-request-transformer'

const transformRequest = (url: string, resourceType: string) => {
  if (isMapboxURL(url)) {
    return transformMapboxUrl(url, resourceType, import.meta.env.VITE_MAPBOX_ACCESS_TOKEN)
  }
  
  // Do any other transforms you want
  return {url}
}


function App() {
  const [count, setCount] = useState(0)

  console.log(import.meta.env)
  // console.log(process.env)
  return (
    <ChakraProvider>
      <div className="App">
        <Map mapLib={maplibregl} 
          initialViewState={{
            longitude: 16.62662018,
            latitude: 49.2125578,
            zoom: 14
          }}
          mapStyle='mapbox://styles/mapbox/satellite-streets-v11'
          transformRequest={transformRequest}
          style={{width: "300px", height: "300px"}}
        />

        <div>
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
        </p>
      </div>
    </ChakraProvider>
  )
}

export default App
