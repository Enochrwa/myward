import React, { useState } from "react";

const UploadForm = () => {
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState("");
  const [occasion, setOccasion] = useState("");
  const [response, setResponse] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !category || !occasion) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("category", category);
    formData.append("occasion", occasion);

    const res = await fetch("http://127.0.0.1:5000/upload-outfit/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setResponse(data);
  };

  return (
    <div className="p-6 max-w-2xl mx-auto bg-white rounded-xl shadow-md space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Upload Outfit</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
        />
        <input
          type="text"
          placeholder="Category (e.g., shirt)"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full px-3 py-2 border rounded"
        />
        <input
          type="text"
          placeholder="Occasion (e.g., wedding)"
          value={occasion}
          onChange={(e) => setOccasion(e.target.value)}
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
          <h3 className="text-lg font-semibold text-gray-700">Outfit Info</h3>

          {/* Image preview */}
          {response.image_url && (
            <img
              src={`http://127.0.0.1:5000${response.image_url}`}
              alt="Uploaded"
              className="w-64 rounded border"
            />
          )}

          {/* Color Info */}
          <div>
            <span className="font-semibold">Color Name:</span>{" "}
            {response.item.color_name} (
            {response.item.tone}, {response.item.temperature}, Saturation:{" "}
            {response.item.saturation})
          </div>
          <div className="flex space-x-4 mt-2">
            {Object.entries(response.item.color_palette).map(([label, hex]) => (
              <div key={label} className="text-center">
                <div
                  className="w-10 h-10 rounded border"
                  style={{ backgroundColor: hex }}
                />
                <div className="text-xs">{label}</div>
              </div>
            ))}
          </div>

          {/* Dominant Colors */}
          <div>
            <span className="font-semibold">Top Colors:</span>
            <div className="flex space-x-4 mt-2">
              {response.item.dominant_colors.map(
                (c: any, i: number) => (
                  <div key={i} className="text-center">
                    <div
                      className="w-10 h-10 rounded border"
                      style={{
                        backgroundColor: `rgb(${c.rgb.map((v: number) =>
                          Math.round(v)
                        ).join(",")})`,
                      }}
                    />
                    <div className="text-xs">
                      {Math.round(c.percentage * 100)}%
                    </div>
                  </div>
                )
              )}
            </div>
          </div>

          {/* Texture Info */}
          <div>
            <span className="font-semibold">Texture:</span>{" "}
            {response.item.texture_features.texture_type} (
            Contrast:{" "}
            {response.item.texture_features.contrast.toFixed(2)}, Brightness:{" "}
            {response.item.texture_features.brightness.toFixed(1)})
          </div>

          {/* Distribution Metrics */}
          <div>
            <span className="font-semibold">Color Diversity:</span>{" "}
            H: {response.item.color_distribution.hue_diversity.toFixed(2)}, S:{" "}
            {response.item.color_distribution.saturation_diversity.toFixed(2)}, V:{" "}
            {response.item.color_distribution.value_diversity.toFixed(2)}
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadForm;
