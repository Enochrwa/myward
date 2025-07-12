import React, { useEffect, useState } from "react";

interface Outfit {
  filename: string;
  category: string;
  color_name: string;
  tone: string;
  temperature: string;
  hex_color: string;
}

const Recommendations = ({ occasion }: { occasion: string }) => {
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!occasion) return;
    setLoading(true);
    fetch(`http://127.0.0.1:5000/recommend/?occasion=${occasion}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.results) setOutfits(data.results);
        else setOutfits([]);
      })
      .finally(() => setLoading(false));
  }, [occasion]);

  if (loading) return <div>Loading recommendations...</div>;
  if (!outfits.length) return <div>No recommendations found for "{occasion}"</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {outfits.map((outfit) => (
        <div
          key={outfit.filename}
          className="border rounded p-4 flex flex-col items-center space-y-2"
        >
          <img
            src={`http://127.0.0.1:5000/uploads/${outfit.filename}`}
            alt={outfit.category}
            className="w-32 h-32 object-cover rounded"
          />
          <div>
            <strong>Category:</strong> {outfit.category}
          </div>
          <div className="flex items-center space-x-2">
            <div
              className="w-6 h-6 rounded border"
              style={{ backgroundColor: outfit.hex_color }}
              title={outfit.color_name}
            ></div>
            <div>{outfit.color_name}</div>
          </div>
          <div>
            <strong>Tone:</strong> {outfit.tone}
          </div>
          <div>
            <strong>Temperature:</strong> {outfit.temperature}
          </div>
        </div>
      ))}
    </div>
  );
};



const RenderRecommendations = () => {
    const [occasion, setOccasion] = useState("casual");

    return (

        <div>
          <h2 className="text-2xl font-bold mb-4">Recommendations</h2>
          <input
            type="text"
            value={occasion}
            onChange={(e) => setOccasion(e.target.value)}
            placeholder="Enter occasion (e.g., casual)"
            className="mb-4 p-2 border rounded w-full"
          />
          <Recommendations occasion={occasion} />
        </div>
    )
}
export default RenderRecommendations
