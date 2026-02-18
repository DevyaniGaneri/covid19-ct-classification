import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import lungImage from '../assets/lung.avif'; // Adjust path if needed

export default function Home() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.dcm')) {
      setFile(selectedFile);
      setError('');
    } else {
      setFile(null);
      setError('Please select a valid .dcm file');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please choose a .dcm file before analyzing');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64 = reader.result.split(',')[1];
        localStorage.setItem('dicomFile', base64);

        const res = await fetch('http://127.0.0.1:8000/api/predict', {
          method: 'POST',
          body: formData,
        });

        const data = await res.json();
        localStorage.setItem("result", JSON.stringify(data));
        navigate("/analysis");
      };
      reader.readAsDataURL(file);
    } catch (err) {
      setError('Error analyzing the image. Please try again.');
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto mt-10 bg-white rounded shadow text-center flex flex-col items-center">
      <h1 className="text-4xl font-bold text-blue-800 mb-4">Lung Disease Detection</h1>
      <p className="text-gray-600 mb-6">Upload your X-ray to detect potential lung diseases</p>
      <img src={lungImage} alt="Lung" className="w-[400px] h-auto mb-6 rounded shadow-lg" />
      <label className="cursor-pointer bg-blue-500 text-white font-semibold py-2 px-6 rounded hover:bg-blue-600 mb-4">
        Choose File
        <input type="file" accept=".dcm" onChange={handleFileChange} className="hidden" />
      </label>
      {file && (
        <p className="text-sm text-gray-700 mb-2">Selected file: {file.name}</p>
      )}
      {error && (
        <p className="text-sm text-red-600 mb-2">{error}</p>
      )}
      <button
        onClick={handleUpload}
        className="bg-blue-700 text-white px-6 py-2 rounded hover:bg-blue-800 transition"
      >
        Analyze
      </button>
      <p className="text-xs text-gray-500 mt-6">© 2025 Lung Detection AI</p>
    </div>
  );
}
