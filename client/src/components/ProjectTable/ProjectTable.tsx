import React, { useEffect, useState } from "react";
import Co2Storage from "../../services/co2Storage";

const ProjectTable = (props: any) => {
  const storage = Co2Storage();
  // window.co2storage = storage;
  // console.log(storage);

  const [assets, setAssets] = useState([]);
  const [activeCid, setActiveCid] = useState("");
  const [activeAssetData, setActiveAssetData] = useState();

  const [assetIsLoading, setAssetIsLoading] = useState(false);

  const handleSelectOnChange = (ev: any) => {
    setActiveCid(ev.target.value);
  };

  const fetchAssets = async () => {
    const { result, error } = await storage.searchAssets(
      "sandbox",
      null,
      null,
      "Verra Project: 953"
    );
    setAssets(result.assets);
    console.log(result);
  };
  const handleClickGetAsset = async (ev: any) => {
    console.log("asset cid", activeCid);
    setAssetIsLoading(true);
    const { result, error } = await storage.getAsset(activeCid);
    setAssetIsLoading(false);
    const improvedResult = {
      ...result,
      assetData: result.asset.reduce((r: any, x: any) => {
        return { ...r, ...x };
      }, {}),
    };
    setActiveAssetData(improvedResult);
    props?.setFcUrl(`https://web2.co2.storage/ipfs/${improvedResult.assetData.GeoCid}/`)
    console.log(improvedResult);
  };
  // fetchAssets();
  // useEffect(() => {
  //   fetchAssets();
  // });

  return (
    <div>
      <button onClick={fetchAssets}>Populate projects</button>
      {/* <ul>
        <li></li>
      </ul> */}
      <select onChange={handleSelectOnChange}>
        {assets.map((asset: any) => (
          <option
            key={`${asset.asset.cid}---${asset.asset.timestamp}`}
            value={asset.asset.cid}
          >
            {asset.asset.name}
          </option>
        ))}
      </select>
      <button onClick={handleClickGetAsset} disabled={assetIsLoading}>
        {assetIsLoading ? "Asset loading..." : "Get Asset"}
      </button>
    </div>
  );
};

export default ProjectTable;
