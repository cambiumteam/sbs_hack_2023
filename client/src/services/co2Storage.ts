import { FGStorage } from "@co2-storage/js-api";

const authType = "metamask";
const ipfsNodeType = "browser";
// const ipfsNodeAddr = "/ip4/127.0.0.1/tcp/5001";
//const fgApiUrl = "http://localhost:3020"
const ipfsNodeAddr = "/dns4/web2.co2.storage/tcp/5002/https"
const fgApiUrl = "https://co2.storage";

// export default function () {
//   const fgStorage = new FGStorage({
//     authType: authType,
//     ipfsNodeType: ipfsNodeType,
//     ipfsNodeAddr: ipfsNodeAddr,
//     fgApiHost: fgApiUrl,
//   });
//   return;
// }
export const config = {
  authType,
  ipfsNodeAddr,
  ipfsNodeType,
  fgApiHost: fgApiUrl,
}

export default function() {
  return new FGStorage(config);
}
