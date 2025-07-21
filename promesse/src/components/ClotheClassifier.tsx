import { useState } from "react";
import apiClient from "@/lib/apiClient";


export default function ClotheClassifier() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);

  const onFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) return;

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    const res = await apiClient("/ml/predict-multiple/", {
      method: "POST",
      body: formData,
    });
    
    setResults(res?.data.predictions);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Batch Clothing Classifier</h1>
      <form onSubmit={onSubmit} className="mb-4">
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={onFileChange}
        />
        <button type="submit" className="ml-2 px-4 py-2 bg-blue-600 text-white rounded">
          Classify All
        </button>
      </form>

      <div className="grid grid-cols-3 gap-4">
        {results.map(({ filename, category }, idx) => (
          <div key={idx} className="border p-2 rounded shadow">
            <p className="font-semibold">{filename}</p>
            <p>Category: <span className="text-blue-700">{category}</span></p>
          </div>
        ))}
      </div>
    </div>
  );
}
