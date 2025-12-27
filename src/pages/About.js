import React from 'react';
export default function About(){
  return (
    <div className="card">
      <h2>About AGRO-VISION</h2>
      <p className="small">AGRO-VISION is an AI-driven platform that predicts crop health and market prices using satellite indices and live weather.</p>
      <ul>
        <li>Backend: Flask APIs</li>
        <li>Frontend: React + Material UI</li>
        <li>Models: RandomForest demo models</li>
      </ul>
    </div>
  )
}