import React from 'react';

export default function MapDisplay({ lat, lon }){
  if(!lat || !lon) return null;
  const src = `https://maps.google.com/maps?q=${lat},${lon}&z=8&output=embed`;
  return <iframe title="map" src={src} className="map-embed" />;
}