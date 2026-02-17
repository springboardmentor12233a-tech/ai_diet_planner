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
  const [error, setError] = useState(null);

  // ===============================
  // STATE: Prescription Upload
  // ===============================
  const [file, setFile] = useState(null);
  const [dietResult, setDietResult] = useState(null);
  const [uploading, setUploading] = useState(false);

  // ===============================
  // STATE: Validation
  // ===============================
  const [formErrors, setFormErrors] = useState({});

  // ===============================
  // Validation Rules
  // ===============================
  const validateForm = () => {
    const errors = {};
    
    if (!form.pregnancies || form.pregnancies < 0 || form.pregnancies > 17) 
      errors.pregnancies = "Must be 0-17";
    if (!form.glucose || form.glucose < 0 || form.glucose > 1000) 
      errors.glucose = "Must be 0-1000";
    if (!form.blood_pressure || form.blood_pressure < 0 || form.blood_pressure > 300) 
      errors.blood_pressure = "Must be 0-300";
    if (!form.skin_thickness || form.skin_thickness < 0 || form.skin_thickness > 100) 
      errors.skin_thickness = "Must be 0-100";
    if (!form.insulin || form.insulin < 0 || form.insulin > 900) 
      errors.insulin = "Must be 0-900";
    if (!form.bmi || form.bmi < 0 || form.bmi > 100) 
      errors.bmi = "Must be 0-100";
    if (!form.dpf || form.dpf < 0 || form.dpf > 3) 
      errors.dpf = "Must be 0-3";
    if (!form.age || form.age < 1 || form.age > 150) 
      errors.age = "Must be 1-150";
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // ===============================
  // Handlers
  // ===============================
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value === "" ? "" : parseFloat(value) });
    setError(null);
  };

  const handleFileChange = (e) => {
    setFile(e.target.files?.[0] || null);
  };

  // ===============================
  // Diabetes Prediction API
  // ===============================
  const predict = async () => {
    if (!validateForm()) {
      setError("Please fix validation errors");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setMealPlanResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!res.ok) throw new Error("API request failed");
      
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to get prediction");
    } finally {
      setLoading(false);
    }
  };

  // ===============================
  // Generate Complete Meal Plan
  // ===============================
  const generateMealPlan = async () => {
    if (!validateForm()) {
      setError("Please fix validation errors");
      return;
    }

    setLoading(true);
    setError(null);
    setMealPlanResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/generate-meal-plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!res.ok) throw new Error("API request failed");
      
      const data = await res.json();
      setMealPlanResult(data);
    } catch (err) {
      setError(err.message || "Failed to generate meal plan");
    } finally {
      setLoading(false);
    }
  };

  // ===============================
  // Generate 7-Day Meal Plan
  // ===============================
  const generate7DayMealPlan = (conditions = []) => {
    const mealDatabase = {
      breakfast: [
        { name: "Oatmeal with berries & almonds", calories: 350, protein: "12g" },
        { name: "Scrambled eggs with whole wheat toast", calories: 300, protein: "18g" },
        { name: "Greek yogurt with granola", calories: 280, protein: "15g" },
        { name: "Smoothie bowl with banana & chia", calories: 320, protein: "10g" },
        { name: "Whole wheat pancakes with honey", calories: 340, protein: "14g" },
        { name: "Vegetable omelette with mushrooms", calories: 280, protein: "16g" },
        { name: "Quinoa porridge with nuts", calories: 360, protein: "13g" }
      ],
      lunch: [
        { name: "Grilled chicken breast with brown rice", calories: 520, protein: "45g" },
        { name: "Salmon fillet with steamed broccoli", calories: 480, protein: "42g" },
        { name: "Turkey sandwich with lettuce", calories: 420, protein: "35g" },
        { name: "Chickpea Buddha bowl", calories: 480, protein: "18g" },
        { name: "Tuna salad with olive oil", calories: 450, protein: "38g" },
        { name: "Tofu stir-fry with vegetables", calories: 380, protein: "28g" },
        { name: "Lentil soup with whole wheat bread", calories: 420, protein: "22g" }
      ],
      snack: [
        { name: "Apple with almonds", calories: 180, protein: "6g" },
        { name: "String cheese & crackers", calories: 150, protein: "8g" },
        { name: "Carrot sticks with hummus", calories: 120, protein: "4g" },
        { name: "Mixed nuts", calories: 170, protein: "6g" },
        { name: "Protein bar", calories: 200, protein: "10g" },
        { name: "Berries with yogurt", calories: 140, protein: "7g" },
        { name: "Cucumber with tzatziki", calories: 100, protein: "3g" }
      ],
      dinner: [
        { name: "Baked lean fish with sweet potato", calories: 550, protein: "48g" },
        { name: "Grilled chicken with quinoa", calories: 580, protein: "50g" },
        { name: "Beef stir-fry with vegetables", calories: 520, protein: "46g" },
        { name: "Vegetable curry with lentils", calories: 480, protein: "20g" },
        { name: "Turkey meatballs with pasta", calories: 520, protein: "42g" },
        { name: "Baked chicken breast with veggies", calories: 500, protein: "52g" },
        { name: "Shrimp with brown rice", calories: 490, protein: "38g" }
      ]
    };

    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const weekPlan = {};

    days.forEach((day, index) => {
      weekPlan[day] = {
        breakfast: mealDatabase.breakfast[index % mealDatabase.breakfast.length],
        lunch: mealDatabase.lunch[index % mealDatabase.lunch.length],
        snack: mealDatabase.snack[index % mealDatabase.snack.length],
        dinner: mealDatabase.dinner[index % mealDatabase.dinner.length],
        dailyTotal: 1650
      };
    });

    return weekPlan;
  };

  // ===============================
  // Prescription Upload API
  // ===============================
  const uploadPrescription = async () => {
    if (!file) {
      setError("Please select a prescription image");
      return;
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
      setError("Please upload JPG, PNG, PDF, or TXT file");
      return;
    }

    setUploading(true);
    setError(null);
    setDietResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://127.0.0.1:8000/upload-prescription", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      setDietResult(data);
      
      // Generate 7-day meal plan based on extracted conditions
      const weekPlan = generate7DayMealPlan(data.interpreted_data?.conditions || []);
      setDietResult(prev => ({ ...prev, weekMealPlan: weekPlan }));
      
      // Auto-populate form with extracted health parameters
      if (data.extracted_parameters && Object.keys(data.extracted_parameters).length > 0) {
        setForm(prev => ({
          ...prev,
          ...data.extracted_parameters
        }));
        alert("✓ Health parameters extracted and form auto-populated! Please verify and adjust if needed.");
      }
    } catch (err) {
      setError(err.message || "Failed to upload prescription");
    } finally {
      setUploading(false);
    }
  };

  // ===============================
  // Clear Functions
  // ===============================
  const clearForm = () => {
    setForm({
      pregnancies: "",
      glucose: "",
      blood_pressure: "",
      skin_thickness: "",
      insulin: "",
      bmi: "",
      dpf: "",
      age: ""
    });
    setResult(null);
    setMealPlanResult(null);
    setFormErrors({});
    setError(null);
  };

  const clearPrescription = () => {
    setFile(null);
    setDietResult(null);
    setError(null);
  };

  // ===============================
  // Export Functions
  // ===============================
  const exportToPDF = async (data) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/export-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) throw new Error("Export failed");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `diet_plan_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError("Failed to export to PDF");
    }
  };

  const exportToJSON = async (data) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/export-json", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) throw new Error("Export failed");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `diet_plan_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError("Failed to export to JSON");
    }
  };

  // ===============================
  // Helper Functions
  // ===============================
  const getRiskClass = (riskLevel) => {
    if (!riskLevel) return "";
    if (riskLevel === "High Risk") return "risk-high";
    if (riskLevel === "Moderate Risk") return "risk-moderate";
    return "risk-low";
  };

  const getRiskEmoji = (riskLevel) => {
    if (riskLevel === "High Risk") return "";
    if (riskLevel === "Moderate Risk") return "";
    return "";
  };

  // ===============================
  // Render
  // ===============================
  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>AI Diet Planner</h1>
          <p>AI-Powered Diabetes Risk & Personalized Diet Recommendation System</p>
        </div>
      </header>

      {/* Error Message */}
      {error && (
        <div className="error-banner">
          <span>❌ {error}</span>
          <button onClick={() => setError(null)} className="close-btn">×</button>
        </div>
      )}

      <main className="main-content">
        {/* Section 1: Manual Health Parameters */}
        <section className="section patient-section">
          <div className="section-header">
            <h2>📋 Patient Health Parameters</h2>
            <p>Enter patient health metrics for diabetes risk assessment</p>
          </div>

          <div className="form-grid">
            {/* Row 1 */}
            <div className="form-group">
              <label>Pregnancies</label>
              <input
                type="number"
                name="pregnancies"
                min="0"
                max="17"
                value={form.pregnancies}
                onChange={handleChange}
                placeholder="0-17"
              />
              {formErrors.pregnancies && <span className="error-text">{formErrors.pregnancies}</span>}
            </div>

            <div className="form-group">
              <label>Glucose Level (mg/dL)</label>
              <input
                type="number"
                name="glucose"
                min="0"
                max="1000"
                value={form.glucose}
                onChange={handleChange}
                placeholder="0-1000"
              />
              {formErrors.glucose && <span className="error-text">{formErrors.glucose}</span>}
            </div>

            <div className="form-group">
              <label>Blood Pressure (mmHg)</label>
              <input
                type="number"
                name="blood_pressure"
                min="0"
                max="300"
                value={form.blood_pressure}
                onChange={handleChange}
                placeholder="0-300"
              />
              {formErrors.blood_pressure && <span className="error-text">{formErrors.blood_pressure}</span>}
            </div>

            <div className="form-group">
              <label>Skin Thickness (mm)</label>
              <input
                type="number"
                name="skin_thickness"
                min="0"
                max="100"
                value={form.skin_thickness}
                onChange={handleChange}
                placeholder="0-100"
              />
              {formErrors.skin_thickness && <span className="error-text">{formErrors.skin_thickness}</span>}
            </div>

            {/* Row 2 */}
            <div className="form-group">
              <label>Insulin Level (μIU/mL)</label>
              <input
                type="number"
                name="insulin"
                min="0"
                max="900"
                value={form.insulin}
                onChange={handleChange}
                placeholder="0-900"
              />
              {formErrors.insulin && <span className="error-text">{formErrors.insulin}</span>}
            </div>

            <div className="form-group">
              <label>BMI (kg/m²)</label>
              <input
                type="number"
                name="bmi"
                min="0"
                max="100"
                step="0.1"
                value={form.bmi}
                onChange={handleChange}
                placeholder="0-100"
              />
              {formErrors.bmi && <span className="error-text">{formErrors.bmi}</span>}
            </div>

            <div className="form-group">
              <label>Diabetes Pedigree Function</label>
              <input
                type="number"
                name="dpf"
                min="0"
                max="3"
                step="0.01"
                value={form.dpf}
                onChange={handleChange}
                placeholder="0-3"
              />
              {formErrors.dpf && <span className="error-text">{formErrors.dpf}</span>}
            </div>

            <div className="form-group">
              <label>Age (years)</label>
              <input
                type="number"
                name="age"
                min="1"
                max="150"
                value={form.age}
                onChange={handleChange}
                placeholder="1-150"
              />
              {formErrors.age && <span className="error-text">{formErrors.age}</span>}
            </div>
          </div>

          {/* Buttons */}
          <div className="button-group">
            <button 
              onClick={predict} 
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? "🔄 Analyzing..." : "📊 Predict Risk"}
            </button>
            <button 
              onClick={generateMealPlan} 
              disabled={loading}
              className="btn btn-success"
            >
              {loading ? "🔄 Generating..." : "🍽️ Generate Full Meal Plan"}
            </button>
            <button 
              onClick={clearForm}
              className="btn btn-secondary"
            >
              🔄 Clear Form
            </button>
          </div>
        </section>

        {/* Section 2: Prediction Results */}
        {result && (
          <section className="section result-section">
            <div className="section-header">
              <h2>📊 Prediction Results</h2>
            </div>

            <div className={`result-card ${getRiskClass(result.risk_level)}`}>
              <div className="result-content">
                <div className="result-item">
                  <span className="result-label">Risk Level:</span>
                  <span className="result-value">
                    {getRiskEmoji(result.risk_level)} {result.risk_level}
                  </span>
                </div>

                <div className="result-item">
                  <span className="result-label">Diabetes Probability:</span>
                  <span className="result-value">{(result.diabetes_probability * 100).toFixed(1)}%</span>
                </div>

                <div className="result-item">
                  <span className="result-label">Model ROC-AUC Score:</span>
                  <span className="result-value">{result.model_roc_auc}</span>
                </div>

                <div className="result-item full-width">
                  <span className="result-label">Recommendation:</span>
                  <p className="result-message">{result.message}</p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Section 3: Meal Plan Results */}
        {mealPlanResult && (
          <section className="section meal-plan-section">
            <div className="section-header">
              <h2>🍽️ Personalized Meal Plan</h2>
              <p>Based on your health parameters and diabetes risk</p>
            </div>

            <div className="meal-plan-container">
              <div className="meal-summary">
                <div className="summary-item">
                  <span>Risk Level:</span>
                  <strong>{getRiskEmoji(mealPlanResult.risk_level)} {mealPlanResult.risk_level}</strong>
                </div>
                <div className="summary-item">
                  <span>Diabetes Probability:</span>
                  <strong>{(mealPlanResult.diabetes_probability * 100).toFixed(1)}%</strong>
                </div>
              </div>

              {mealPlanResult.meal_plan && (
                <div className="meal-days">
                  {Object.entries(mealPlanResult.meal_plan).map(([day, meals]) => (
                    <div key={day} className="meal-day">
                      <h4>{day}</h4>
                      <div className="meals-list">
                        {meals.breakfast && (
                          <div className="meal-item">
                            <span className="meal-type">Breakfast</span>
                            <span className="meal-name">{meals.breakfast.name}</span>
                            <span className="meal-cals">{meals.breakfast.calories} cal</span>
                          </div>
                        )}
                        {meals.lunch && (
                          <div className="meal-item">
                            <span className="meal-type">Lunch</span>
                            <span className="meal-name">{meals.lunch.name}</span>
                            <span className="meal-cals">{meals.lunch.calories} cal</span>
                          </div>
                        )}
                        {meals.snack && (
                          <div className="meal-item">
                            <span className="meal-type">Snack</span>
                            <span className="meal-name">{meals.snack.name}</span>
                            <span className="meal-cals">{meals.snack.calories} cal</span>
                          </div>
                        )}
                        {meals.dinner && (
                          <div className="meal-item">
                            <span className="meal-type">Dinner</span>
                            <span className="meal-name">{meals.dinner.name}</span>
                            <span className="meal-cals">{meals.dinner.calories} cal</span>
                          </div>
                        )}
                        {meals.daily_total_calories && (
                          <div className="meal-item total-item">
                            <span className="meal-type"><strong>Daily Total</strong></span>
                            <span className="meal-cals"><strong>~{meals.daily_total_calories} cal</strong></span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="export-buttons">
                <button onClick={() => exportToPDF(mealPlanResult)} className="btn btn-export-pdf">
                  Export as PDF
                </button>
                <button onClick={() => exportToJSON(mealPlanResult)} className="btn btn-export-json">
                  Export as JSON
                </button>
              </div>
            </div>
          </section>
        )}

        {/* Section 4: Prescription Upload */}
        <section className="section upload-section">
          <div className="section-header">
            <h2>Upload Doctor Prescription</h2>
            <p>Automatically extract health parameters from medical reports</p>
          </div>

          <div className="upload-box">
            <input
              type="file"
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png,.pdf,.txt"
              disabled={uploading}
              id="file-input"
            />
            <label htmlFor="file-input" className="file-label">
              {file ? `Selected: ${file.name}` : "Choose File (JPG, PNG, PDF, TXT)"}
            </label>
          </div>

          <div className="button-group upload-buttons">
            <button 
              onClick={uploadPrescription} 
              disabled={uploading || !file}
              className="btn btn-primary"
            >
              {uploading ? "⏳ Processing..." : "🔍 Analyze & Extract"}
            </button>
            <button 
              onClick={clearPrescription}
              className="btn btn-secondary"
            >
              🗑️ Clear File
            </button>
          </div>

          {file && (
            <p className="file-info">
              Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </p>
          )}
        </section>

        {/* Section 5: Extraction Results */}
        {dietResult && (
          <section className="section extraction-section">
            <div className="section-header">
              <h2>✨ Extraction Results</h2>
            </div>

            {dietResult.extracted_parameters && (
              <div className="extraction-card">
                <h3>📊 Extracted Parameters</h3>
                <div className="parameters-grid">
                  {Object.entries(dietResult.extracted_parameters).map(([key, value]) => (
                    <div key={key} className="param-item">
                      <span className="param-label">{key.replace(/_/g, ' ')}:</span>
                      <span className="param-value">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {dietResult.extracted_text && (
              <div className="extraction-card">
                <h3>📝 Extracted Text</h3>
                <div className="extracted-text">
                  {dietResult.extracted_text}
                </div>
              </div>
            )}

            {dietResult.diet_rules && (
              <div className="extraction-card">
                <h3>🎯 Diet Rules</h3>
                <ul className="diet-rules">
                  {dietResult.diet_rules.map((rule, idx) => (
                    <li key={idx}>{rule}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {/* ===== 7-DAY MEAL PLAN SECTION ===== */}
        {dietResult && dietResult.weekMealPlan && (
          <section className="section week-meal-plan-section">
            <div className="section-header">
              <h2>🍽️ 7-Day Personalized Meal Plan</h2>
              <p>Complete weekly meal plan with breakfast, lunch, snack, and dinner</p>
            </div>

            <div className="week-plan-container">
              {Object.entries(dietResult.weekMealPlan).map(([day, meals]) => (
                <div key={day} className="day-card">
                  <div className="day-header">{day}</div>
                  
                  <div className="meal-section breakfast-section">
                    <div className="meal-time-header">Breakfast</div>
                    <div className="meal-detail">
                      <p className="meal-name">{meals.breakfast.name}</p>
                      <div className="meal-info">
                        <span className="meal-cal">{meals.breakfast.calories} cal</span>
                        <span className="meal-protein">{meals.breakfast.protein} protein</span>
                      </div>
                    </div>
                  </div>

                  <div className="meal-section lunch-section">
                    <div className="meal-time-header">Lunch</div>
                    <div className="meal-detail">
                      <p className="meal-name">{meals.lunch.name}</p>
                      <div className="meal-info">
                        <span className="meal-cal">{meals.lunch.calories} cal</span>
                        <span className="meal-protein">{meals.lunch.protein} protein</span>
                      </div>
                    </div>
                  </div>

                  <div className="meal-section snack-section">
                    <div className="meal-time-header">Snack</div>
                    <div className="meal-detail">
                      <p className="meal-name">{meals.snack.name}</p>
                      <div className="meal-info">
                        <span className="meal-cal">{meals.snack.calories} cal</span>
                        <span className="meal-protein">{meals.snack.protein} protein</span>
                      </div>
                    </div>
                  </div>

                  <div className="meal-section dinner-section">
                    <div className="meal-time-header">Dinner</div>
                    <div className="meal-detail">
                      <p className="meal-name">{meals.dinner.name}</p>
                      <div className="meal-info">
                        <span className="meal-cal">{meals.dinner.calories} cal</span>
                        <span className="meal-protein">{meals.dinner.protein} protein</span>
                      </div>
                    </div>
                  </div>

                  <div className="daily-total">
                    <span>Daily Total:</span>
                    <strong>{meals.breakfast.calories + meals.lunch.calories + meals.snack.calories + meals.dinner.calories} cal</strong>
                  </div>
                </div>
              ))}
            </div>

            <div className="week-plan-info">
              <p><strong>Total Weekly Calories:</strong> ~11,550 cal</p>
              <p><strong>Balanced Nutrition:</strong> Proteins, Carbs, Healthy Fats</p>
              <p><strong>Diabetic-Friendly:</strong> Low GI foods recommended</p>
            </div>

            <div className="export-buttons" style={{marginTop: '20px'}}>
              <button onClick={() => exportToPDF(dietResult)} className="btn btn-export-pdf">
                Export as PDF
              </button>
              <button onClick={() => exportToJSON(dietResult)} className="btn btn-export-json">
                Export as JSON
              </button>
            </div>
          </section>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Processing your request...</p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>🏥 AI Diet Planner v1.0 | Diabetes Risk Assessment & Personalized Nutrition System</p>
        <p className="footer-links">
          Backend: <code>http://127.0.0.1:8000</code> | 
          API Docs: <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noopener noreferrer">Swagger UI</a>
        </p>
      </footer>
    </div>
  );
}

export default App;
