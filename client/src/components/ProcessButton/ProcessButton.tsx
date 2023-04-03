import React, { useState } from "react";
import axios from "axios";

const SERVER_BASE_URL = "https://slick-donkeys-ring-67-5-107-21.loca.lt";

const ProcessButton = (props: any) => {
  const [jobId, setJobId] = useState<any>();
  const [jobIsProcessing, setJobIsProcessing] = useState(false);
  const [jobResult, setJobResult] = useState<any>({});

  const pollJobStatus = (jid: string) => {
    // const poll = () => {}
    setTimeout(async () => {
      const { data } = await axios.get(`${SERVER_BASE_URL}/job/${jid}`);
      console.log(data);
      setJobResult(data);
      if (data?.State?.State === "InProgress") {
        pollJobStatus(jid);
      }
      if (data?.State.State === "Completed") {
        setJobIsProcessing(false);
      }
    }, 5000);
  };

  const handleClick = async () => {
    // HACK: we should really just store the geocid in state instead of the ipfs url
    const geocid = props.featureCollectionUrl
      .split("ipfs/")[1]
      .replace("/", "");
    const { data } = await axios.post(`${SERVER_BASE_URL}/job?`, null, {
      params: {
        inputs: geocid,
        start: "2021-01-01",
        end: "2022-01-01",
      },
      headers: {
        "Bypass-Tunnel-Reminder": true,
      },
    });
    console.log(data);
    const jid = data;
    setJobId(data);
    setJobIsProcessing(true);
    pollJobStatus(jid);
  };

  return (
    <div>
      <button onClick={handleClick}>Process</button>
      {jobIsProcessing && (
        <div>
          Job is processing...
          {/* <code>
        {JSON.stringify(jobResult, null, 2)}
      </code>
       */}
        </div>
      )}
      {jobResult?.State?.State === "Completed" && (
        <a
          href={`https://web2.co2.storage/ipfs/${jobResult.State.Executions[0].PublishedResults.CID}`}
        >
          {jobResult.State.Executions[0].PublishedResults.CID}
        </a>
      )}
    </div>
  );
};
export default ProcessButton;
