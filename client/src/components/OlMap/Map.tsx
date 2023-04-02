import React, { useRef, useState, useEffect } from "react"
import "./Map.css";
import MapContext from "./MapContext";
// import * as ol from "ol";
import OlMap from 'ol/Map';
import OlView from 'ol/View';


interface Props {
  children: any
  zoom: number
  center: number[]
}

const Map = ({ children, zoom, center }: Props) => {
  const mapRef = useRef<HTMLDivElement>();
  const [map, setMap] = useState<OlMap>();
  // on component mount
  useEffect(() => {
    const options = {
      view: new OlView({ zoom, center }),
      layers: [],
      controls: [],
      overlays: []
    };
    const mapObject = new OlMap(options);
    mapObject.setTarget(mapRef.current);
    setMap(mapObject);
    return () => mapObject.setTarget(undefined);
  }, []);
  // zoom change handler
  useEffect(() => {
    if (!map) return;
    map.getView().setZoom(zoom);
  }, [zoom]);
  // center change handler
  useEffect(() => {
    if (!map) return;
    map.getView().setCenter(center)
  }, [center])
  return (
    <MapContext.Provider value={{ map }}>
      <div ref={mapRef} className="ol-map">
        {children}
      </div>
    </MapContext.Provider>
  )
}
export default Map;