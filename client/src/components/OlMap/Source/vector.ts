import { Vector as VectorSource } from 'ol/source';
import GeoJSON from "ol/format/GeoJSON";

function vector({ features, url }: { features: any[], url: string }) {
	const params: any = {};
	if (features) {
		params.features = features;
	}
	if (url) {
		params.url = url;
		params.format = new GeoJSON();
	}
	const source = new VectorSource(params);
	// source.on('change', window?.olmap.getView().fit(source.getExtent()))
	return source;
}

export default vector;