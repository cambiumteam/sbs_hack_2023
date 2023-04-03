import React, { useState } from 'react';
import axios from 'axios';

const SERVER_BASE_URL = 'https://slick-donkeys-ring-67-5-107-21.loca.lt'

const ProcessButton = (props: any) => {
  const [jobId, setJobId] = useState<any>();
  const handleClick = async () => {
    // HACK: we should really just store the geocid in state instead of the ipfs url
    const geocid = props.featureCollectionUrl.split('ipfs/')[1].replace('/', '');
    const { data } = axios.post(`${SERVER_BASE_URL}/job?`, null, {
      params: {
        inputs: geocid,
        start: '2021-01-01',
        end: '2022-01-01',
      },
      headers: {
        'Bypass-Tunnel-Reminder': true,
      }
    });
    console.log(data)
    setJobId(data);

  }
  return <div>
    <button onClick={handleClick}>Process</button>

  </div>
}
export default ProcessButton;