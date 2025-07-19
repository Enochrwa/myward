import React, { useState } from "react";
import { createWardrobeItemWithImage } from "@/lib/apiClient";

const WardrobeUpload = ({ onUpload }: { onUpload: () => void }) => {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("");
  const [categoryId, setCategoryId] = useState(1);
  const [response, setResponse] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !name) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("name", name);
    formData.append("brand", brand);
    formData.append("category_id", categoryId.toString());

    try {
      const data = await createWardrobeItemWithImage(formData);
      setResponse(data);
      onUpload();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto bg-white rounded-xl shadow-md space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Upload to Wardrobe</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
        />
        <input
          type="text"
          placeholder="Item Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-3 py-2 border rounded"
        />
        <input
          type="text"
          placeholder="Brand"
          value={brand}
          onChange={(e) => setBrand(e.target.value)}
          className="w-full px-3 py-2 border rounded"
        />
        <input
          type="number"
          placeholder="Category ID"
          value={categoryId}
          onChange={(e) => setCategoryId(parseInt(e.target.value))}
          className="w-full px-3 py-2 border rounded"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Upload
        </button>
      </form>

      {response && (
        <div className="p-4 bg-gray-50 rounded shadow mt-4 text-sm space-y-4">
          <h3 className="text-lg font-semibold text-gray-700">Upload Info</h3>

          {/* Image preview */}
          {response.image_url && (
            <img
              src={`http://127.0.0.1:8000${response.image_url}`}
              alt="Uploaded"
              className="w-64 rounded border"
            />
          )}
        </div>
      )}
    </div>
  );
};

export default WardrobeUpload;
