import { Vector as VectorSource } from 'ol/source';

function vector({ features }: { features: any[]}) {
	return new VectorSource({
		features
	});
}

export default vector;