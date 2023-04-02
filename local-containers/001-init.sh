set -ex
ipfs bootstrap rm all
ipfs bootstrap add /dns4/proxy.co2.storage/udp/4001/quic
ipfs bootstrap add /dns4/web1.co2.storage/udp/4001/quic
ipfs bootstrap add /dns4/web2.co2.storage/udp/4001/quic
ipfs bootstrap add /dns4/green.filecoin.space/udp/4001/quic
