import React, { useEffect, useState } from 'react';
import DicomViewer from '../components/DicomViewer';

export default function Analysis() {
  const [dicomFile, setDicomFile] = useState(null);
  const result = JSON.parse(localStorage.getItem('result'));

  useEffect(() => {
    const storedFile = localStorage.getItem('dicomFile');
    if (storedFile) {
      const binary = atob(storedFile);
      const byteArray = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        byteArray[i] = binary.charCodeAt(i);
      }
      const blob = new Blob([byteArray], { type: 'application/dicom' });
      const file = new File([blob], 'image.dcm', { type: 'application/dicom' });
      setDicomFile(file);
    }
  }, []);

  return (
    <div className="p-6 max-w-xl mx-auto mt-10 bg-white rounded shadow text-center">
      <h2 className="text-3xl font-bold mb-4 text-blue-700">Prediction Result</h2>

      {dicomFile && <DicomViewer file={dicomFile} />}

      <div className="space-y-4 text-center">
        <p>
          <span className="font-semibold text-gray-700">Lung Condition:</span>
          <span className="ml-2 text-gray-900 font-bold text-red-900">{result.label}</span>
        </p>
        <p>
          <span className="font-semibold text-gray-700">Confidence:</span>
          <span className="ml-2 font-bold text-red-900">{result.confidence}</span>
        </p>
      </div>
    </div>
  );
}
