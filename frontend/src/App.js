import { useState } from "react";
import "./App.css";

function App() {
  // ===============================
  // STATE: Diabetes Prediction
  // ===============================
  const [form, setForm] = useState({
    pregnancies: "",
    glucose: "",
    blood_pressure: "",
    skin_thickness: "",
    insulin: "",
    bmi: "",
    dpf: "",
    age: ""
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // ===============================
  // STATE: Prescription Upload
  // ===============================
  const [file, setFile] = useState(null);
  const [dietResult, setDietResult] = useState(null);
  const [uploading, setUploading] = useState(false);

  // ===============================
  // Handlers
  // ===============================
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // ===============================
  // Diabetes Prediction API
  // ===============================
  const predict = async () => {
    setLoading(true);
    setResult(null);

    const res = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  // ===============================
  // Prescription Upload API
  // ===============================
  const uploadPrescription = async () => {
    if (!file) {
      alert("Please select a prescription image");
      return;
    }

    setUploading(true);
    setDietResult(null);

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://127.0.0.1:8000/upload-prescription", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setDietResult(data);
    setUploading(false);
  };

  // ===============================
  // UI Helpers
  // ===============================
  const getRiskClass = () => {
    if (!result) return "";
    if (result.risk_level === "Low Risk") return "low";
    if (result.risk_level === "Moderate Risk") return "medium";
    return "high";
  };

  // ===============================
  // UI
  // ===============================
  return (
    <div className="container">
      <h1>AI Diet Planner</h1>
      <p className="subtitle">Diabetes Risk & Diet Recommendation System</p>

      {/* ===============================
          Diabetes Prediction Section
         =============================== */}
      <div className="card">
        <h3>Patient Health Parameters</h3>

        <div className="grid">
          <input name="pregnancies" placeholder="Pregnancies" onChange={handleChange} />
          <input name="glucose" placeholder="Glucose Level" onChange={handleChange} />
          <input name="blood_pressure" placeholder="Blood Pressure" onChange={handleChange} />
          <input name="skin_thickness" placeholder="Skin Thickness" onChange={handleChange} />
          <input name="insulin" placeholder="Insulin Level" onChange={handleChange} />
          <input name="bmi" placeholder="BMI" onChange={handleChange} />
          <input name="dpf" placeholder="Diabetes Pedigree Function" onChange={handleChange} />
          <input name="age" placeholder="Age" onChange={handleChange} />
        </div>

        <button onClick={predict} disabled={loading}>
          {loading ? "Analyzing..." : "Predict Risk"}
        </button>
      </div>

      {result && (
        <div className={`result-card ${getRiskClass()}`}>
          <h2>{result.risk_level}</h2>

          <p>
            <strong>Diabetes Probability:</strong>{" "}
            {(result.diabetes_probability * 100).toFixed(1)}%
          </p>

          <p>
            <strong>Model Reliability (ROC-AUC):</strong>{" "}
            {result.model_roc_auc}
          </p>

          <p className="message">{result.message}</p>
        </div>
      )}

      {/* ===============================
          Prescription Upload Section
         =============================== */}
      <div className="card">
        <h3>Upload Doctor Prescription</h3>

        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button onClick={uploadPrescription} disabled={uploading}>
          {uploading ? "Analyzing..." : "Analyze Prescription"}
        </button>
      </div>

      {dietResult && (
        <div className="result-card low">
          <h3>Diet Recommendations</h3>

          <ul>
            {dietResult.diet_guidelines.map((d, i) => (
              <li key={i}>{d}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
