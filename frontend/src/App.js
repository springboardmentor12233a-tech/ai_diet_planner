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
  const [mealPlanResult, setMealPlanResult] = useState(null);
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
    setMealPlanResult(null);

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
  // Generate Complete Meal Plan
  // ===============================
  const generateMealPlan = async () => {
    setLoading(true);
    setMealPlanResult(null);

    const res = await fetch("http://127.0.0.1:8000/generate-meal-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    const data = await res.json();
    setMealPlanResult(data);
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
  // Export Functions
  // ===============================
  const exportToPDF = async (data) => {
    const res = await fetch("http://127.0.0.1:8000/export-pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `diet_plan_${Date.now()}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  const exportToJSON = async (data) => {
    const res = await fetch("http://127.0.0.1:8000/export-json", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `diet_plan_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  // ===============================
  // UI Helpers
  // ===============================
  const getRiskClass = () => {
    if (!result && !mealPlanResult) return "";
    const risk = result?.risk_level || mealPlanResult?.risk_level;
    if (risk === "Low Risk") return "low";
    if (risk === "Moderate Risk") return "medium";
    return "high";
  };

  // ===============================
  // Meal Card Component
  // ===============================
  const MealCard = ({ title, meal }) => (
    <div className="meal-card">
      <h4>{title}</h4>
      <h5>{meal.name}</h5>
      <p className="meal-description">{meal.description}</p>
      <div className="meal-nutrition">
        <span>🔥 {meal.calories} cal</span>
        <span>💪 {meal.protein}</span>
        <span>🍞 {meal.carbs}</span>
      </div>
    </div>
  );

  // ===============================
  // UI
  // ===============================
  return (
    <div className="container">
      <h1>AI Diet Planner</h1>
      <p className="subtitle">AI-Powered Diabetes Risk & Personalized Diet Recommendation System</p>

      {/* ===============================
          Diabetes Prediction Section
         =============================== */}
      <div className="card">
        <h3>📋 Patient Health Parameters</h3>

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

        <div className="button-group">
          <button onClick={predict} disabled={loading} className="btn-primary">
            {loading ? "Analyzing..." : "Predict Risk"}
          </button>
          <button onClick={generateMealPlan} disabled={loading} className="btn-success">
            {loading ? "Generating..." : "Generate Full Meal Plan"}
          </button>
        </div>
      </div>

      {result && !mealPlanResult && (
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
          Complete Meal Plan Display
         =============================== */}
      {mealPlanResult && mealPlanResult.meal_plan && (
        <div className="meal-plan-container">
          <div className={`result-card ${getRiskClass()}`}>
            <h2>Health Assessment</h2>
            <p><strong>Risk Level:</strong> {mealPlanResult.risk_level}</p>
            <p><strong>Diabetes Probability:</strong> {(mealPlanResult.diabetes_probability * 100).toFixed(1)}%</p>
            <p><strong>Conditions:</strong> {mealPlanResult.conditions.join(", ")}</p>
          </div>

          <div className="card meal-plan-card">
            <div className="plan-header">
              <h2>📅 Your Personalized Daily Meal Plan</h2>
              <div className="export-buttons">
                <button onClick={() => exportToPDF(mealPlanResult)} className="btn-export">
                  📄 Export PDF
                </button>
                <button onClick={() => exportToJSON(mealPlanResult)} className="btn-export">
                  💾 Export JSON
                </button>
              </div>
            </div>

            <div className="meals-grid">
              <MealCard title="🍳 Breakfast" meal={mealPlanResult.meal_plan.breakfast} />
              <MealCard title="🍽️ Lunch" meal={mealPlanResult.meal_plan.lunch} />
              <MealCard title="🌙 Dinner" meal={mealPlanResult.meal_plan.dinner} />
            </div>

            {mealPlanResult.meal_plan.snacks && (
              <div className="snacks-section">
                <h4> Recommended Snacks</h4>
                <div className="snacks-grid">
                  {mealPlanResult.meal_plan.snacks.map((snack, i) => (
                    <div key={i} className="snack-card">
                      <strong>{snack.name}</strong>
                      <p>{snack.description}</p>
                      <span>{snack.calories} cal</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {mealPlanResult.meal_plan.daily_summary && (
              <div className="daily-summary">
                <h4>Daily Nutritional Summary</h4>
                <div className="summary-grid">
                  <div className="summary-item">
                    <strong>Total Calories</strong>
                    <p>{mealPlanResult.meal_plan.daily_summary.total_calories}</p>
                  </div>
                  <div className="summary-item">
                    <strong>Protein</strong>
                    <p>{mealPlanResult.meal_plan.daily_summary.protein}</p>
                  </div>
                  <div className="summary-item">
                    <strong>Carbs</strong>
                    <p>{mealPlanResult.meal_plan.daily_summary.carbs}</p>
                  </div>
                  <div className="summary-item">
                    <strong>Focus</strong>
                    <p>{mealPlanResult.meal_plan.daily_summary.focus}</p>
                  </div>
                </div>
              </div>
            )}

            {mealPlanResult.meal_plan.hydration && (
              <div className="hydration-section">
                <h4>Hydration</h4>
                <p>{mealPlanResult.meal_plan.hydration}</p>
              </div>
            )}

            {mealPlanResult.meal_plan.notes && (
              <div className="notes-section">
                <h4>Important Notes</h4>
                <ul>
                  {mealPlanResult.meal_plan.notes.map((note, i) => (
                    <li key={i}>{note}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
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

      {dietResult && dietResult.meal_plan && (
        <div className="meal-plan-container">
          <div className="card">
            <h3>🔍 Extracted Medical Information</h3>
            {dietResult.interpreted_data && (
              <>
                <div className="info-section">
                  <h4>Health Conditions Detected:</h4>
                  <p>{dietResult.interpreted_data.conditions.join(", ")}</p>
                </div>
                <div className="info-section">
                  <h4>Dietary Restrictions:</h4>
                  <ul>
                    {dietResult.interpreted_data.dietary_restrictions.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </div>

          <div className="card meal-plan-card">
            <div className="plan-header">
              <h2>📅 Your Personalized Meal Plan</h2>
              <div className="export-buttons">
                <button onClick={() => exportToPDF(dietResult)} className="btn-export">
                  📄 Export PDF
                </button>
                <button onClick={() => exportToJSON(dietResult)} className="btn-export">
                  💾 Export JSON
                </button>
              </div>
            </div>

            <div className="meals-grid">
              <MealCard title="🍳 Breakfast" meal={dietResult.meal_plan.breakfast} />
              <MealCard title="🍽️ Lunch" meal={dietResult.meal_plan.lunch} />
              <MealCard title="🌙 Dinner" meal={dietResult.meal_plan.dinner} />
            </div>

            {dietResult.meal_plan.snacks && (
              <div className="snacks-section">
                <h4>Recommended Snacks</h4>
                <div className="snacks-grid">
                  {dietResult.meal_plan.snacks.map((snack, i) => (
                    <div key={i} className="snack-card">
                      <strong>{snack.name}</strong>
                      <p>{snack.description}</p>
                      <span>{snack.calories} cal</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {dietResult.diet_rules && (
              <div className="notes-section">
                <h4>Dietary Guidelines</h4>
                <ul>
                  {dietResult.diet_rules.map((rule, i) => (
                    <li key={i}>{rule}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

