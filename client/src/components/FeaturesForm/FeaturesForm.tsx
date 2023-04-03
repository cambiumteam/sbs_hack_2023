import {
  FormControl,
  FormLabel,
  Input,
  FormErrorMessage,
  FormHelperText,
  Button,
  Text,
  Code,
} from "@chakra-ui/react";
import React, { useState } from "react";
import axios from "axios";

const FeaturesForm = (props: any) => {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [result, setResult] = useState({});
  const handleUrlChange = (ev: any) => setUrl(ev.target.value);

  const handleSubmit = async (ev: any) => {
    ev.preventDefault();
    try {
      setIsLoading(true);
      const { data } = await axios.get(url);
      setResult(data);
      props?.setFeatures(data);
    } catch (err) {
      console.log(err);
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* <FormHelperText>We'll never share your email.</FormHelperText> */}
        {/* <FormControl>
          <FormLabel>URL</FormLabel>
          <Input type="text" value={url} onChange={handleUrlChange} />
        </FormControl>
        <Button type="submit" isLoading={isLoading}>
          Submit
        </Button> */}
        <label>
          URL:
          <input type="text" value={url} onChange={handleUrlChange} />
        </label>
        <button type="submit" disabled={isLoading}>
          { isLoading ? 'Loading...' : 'Submit' }
        </button>
      </form>
      { Boolean(Object.keys(result).length > 0) && !isLoading && !hasError && (
        // <Code>
        //   {JSON.stringify(result)}
        // </Code>
        <code>
          {JSON.stringify(result)}
        </code>
      )}
    </div>
  );
};

export default FeaturesForm;
