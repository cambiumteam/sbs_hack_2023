emove existing
docker rm ipfs_host bacalhau --force
docker network rm bacalhau-network

# Create docker network
docker network create --driver bridge bacalhau-network

# Start ipfs node
docker run \
        -d --network bacalhau-network --name ipfs_host \
        -v $(pwd)/staging:/export -v $(pwd)/ipfs:/data/ipfs \
        -v 001-init.sh:/container-init.d/001-init.sh \
        -p 8080:8080 -p 5001:5001 \
        -p 4002:4001 -p 4002:4001/udp \
        ipfs/kubo:latest

docker run \
        -d --network bacalhau-network --name bacalhau \
        -u root \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v /tmp:/tmp \
        -p 1234:1234 -p 1235:1235 \
        -p 1235:1235/udp \
        ghcr.io/bacalhau-project/bacalhau:latest \
        serve \
          --ipfs-connect /dns4/ipfs_host/tcp/5001 \
          --peer "none" \
          --node-type requester,compute \
          --job-selection-accept-networked true

