# SBS Boston Hackathon

## About

Info about this hackathon project.

Goals:
- CO2.Storage & Bacalhau compute
  - Demonstrate efficient processing of Sentinel satellite imagery over CO2.Storage assets
  - Allow networking in Bacalhau docker image for efficient querying of COG data
- Interoperability in ecological assets
  - Process Sentinel data for any CO2.Storage asset that has Geojson data
  - Provide NDVI results back on CO2.Storage in standard format
- Tracking deforestation
  - Use Sentinel imagery to compute NDVI summaries over long time periods

### Docker

`docker pull ghcr.io/cambiumteam/sentinel-processing:latest`

The docker image contains a file `process.py` which handles processing of Sentinel data. Run this script with the
following parameters:
- `-s`, `--start`: Start date.
- `-e`, `--end`: End date.
- `p`, `--process`: Process type: `ndvi-summary`, `rgb`. Defaults to `ndvi-summary`.

Configure input and output directories. A docker volume can be mounted if not running in Bacalhau:
- `-i`, `--input`: Input directory. Directory with geojson files, or a single input file. Defaults to `/inputs`.
- `-o`, `--output`: Output directory to write results to. Defaults to `/outputs`.

### Bacalhau

Create a Bacalhau job that runs `ghcr.io/cambiumteam/sentinel-processing:latest`.

The following inputs are supported:
- CID with GeoJSON content `--inputs $CID`
- GeoJSON URL `--input-urls $URL`

```
bacalhau --api-host $HOST \
  docker run --network full --inputs $CID \
  ghcr.io/cambiumteam/sentinel-processing:latest -- \
  python process.py -s 2021-01-01 -e 2021-06-01`
```

### Local containers

Run `local-containers/start.sh` to configure a local environment:
- `ipfs_host`: IPFS node connected to CO2.Storage IPFS swarm.
- `bacalhau`: Bacalhau requester & compute node. Configured to allow full network access for jobs.