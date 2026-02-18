import React, { useEffect, useRef } from 'react';
import cornerstone from 'cornerstone-core';
import cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader';
import dicomParser from 'dicom-parser';

cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
cornerstoneWADOImageLoader.external.dicomParser = dicomParser;

export default function DicomViewer({ file }) {
  const elementRef = useRef(null);

  useEffect(() => {
    if (file && elementRef.current) {
      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
      cornerstone.enable(elementRef.current);
      cornerstone.loadImage(imageId).then((image) => {
        cornerstone.displayImage(elementRef.current, image);
      });
    }
  }, [file]);

  return (
    <div
      ref={elementRef}
      style={{ width: '512px', height: '512px', backgroundColor: 'black' }}
      className="mx-auto mb-6 rounded shadow-lg"
    />
  );
}
