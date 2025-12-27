import React from "react";

export default function CropSelector({ crop, setCrop }) {
  const cropCategories = {
    Grains: [
      { value: "wheat", label: "🌾 Wheat" },
      { value: "rice", label: "🌾 Rice" },
      { value: "maize", label: "🌽 Maize" },
      { value: "soybean", label: "🫘 Soybean" },
      { value: "sunflower", label: "🌻 Sunflower" },
    ],
    Vegetables: [
      { value: "potato", label: "🥔 Potato" },
      { value: "onion", label: "🧅 Onion" },
      { value: "tomato", label: "🍅 Tomato" },
      { value: "brinjal", label: "🍆 Brinjal" },
      { value: "cucumber", label: "🥒 Cucumber" },
    ],
    Fruits: [
      { value: "banana", label: "🍌 Banana" },
      { value: "orange", label: "🍊 Orange" },
      { value: "mango", label: "🥭 Mango" },
      { value: "apple", label: "🍎 Apple" },
      { value: "grapes", label: "🍇 Grapes" },
    ],
  };

  return (
    <select
      value={crop}
      onChange={(e) => setCrop(e.target.value)}
      style={{
        width: "100%",
        padding: "10px",
        borderRadius: "8px",
        border: "1px solid #ccc",
        background: "#f9f9f9",
        fontSize: "1rem",
      }}
    >
      <option value="" disabled>
        -- Select Crop --
      </option>
      {Object.entries(cropCategories).map(([category, crops]) => (
        <optgroup key={category} label={`🌱 ${category}`}>
          {crops.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  );
}
