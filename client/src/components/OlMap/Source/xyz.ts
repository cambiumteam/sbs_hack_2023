import * as olSource from "ol/source";

function xyz({
  url,
  attributions,
  maxZoom,
}: {
  url: string;
  attributions: string;
  maxZoom: number;
}) {
  return new olSource.XYZ({ url, attributions, maxZoom });
}

export default xyz;
