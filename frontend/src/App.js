import { useState } from "react";
import "./App.css";

function App() {
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

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

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

  const getRiskClass = () => {
    if (!result) return "";
    if (result.risk_level === "Low Risk") return "low";
    if (result.risk_level === "Moderate Risk") return "medium";
    return "high";
  };

  return (
    <div className="container">
      <h1>AI Diet Planner</h1>
      <p className="subtitle">Diabetes Risk Assessment</p>

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
    </div>
  );
}

export default App;
