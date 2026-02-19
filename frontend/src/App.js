import React, { useState } from "react";
import axios from "axios";
import { jsPDF } from "jspdf";
import "./App.css";

import {
  Upload,
  FileText,
  FileJson,
  Sunrise,
  Utensils,
  Moon,
  AlertTriangle,
  CheckCircle,
  Calendar,
  Sparkles
} from "lucide-react";

function App() {
  const [file, setFile] = useState(null);
  const [name, setName] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(0);

  const handleUpload = async () => {
    if (!file || !name) return alert("Enter name & upload report");

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(
        `http://localhost:8000/process-report?name=${name}`,
        formData
      );
      setData(res.data);
      setSelectedDay(0);
    } catch {
      alert("Backend error");
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text(`AI Nutricare Plan - ${data.name}`, 10, 20);

    data.diet_7_days.forEach((d, i) => {
      const y = 40 + i * 30;
      doc.text(`Day ${d.day}`, 10, y);
      doc.text(`Breakfast: ${d.Breakfast}`, 10, y + 7);
      doc.text(`Lunch: ${d.Lunch}`, 10, y + 14);
      doc.text(`Dinner: ${d.Dinner}`, 10, y + 21);
    });

    doc.save("diet-plan.pdf");
  };

  return (
    <div className="page">
      {/* HEADER */}
      <header className="header">
        <div className="logo">
          <Sparkles color="#2563EB" />
          <h1>AI Nutricare</h1>
        </div>
        <p className="subtitle">
          Clinical Report Analysis & Personalized Nutrition
        </p>
      </header>

      <div className="layout">
        {/* LEFT PANEL */}
        <div className="card">
          <h2>Upload Report</h2>

          <div className="uploadBox">
            <Upload size={40} color="#2563EB" />
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              style={{ marginTop: 10 }}
            />
          </div>

          <input
            placeholder="Patient Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input"
          />

          <button className="primaryBtn" onClick={handleUpload}>
            {loading ? "Analyzing..." : "Generate Plan"}
          </button>
        </div>

        {/* MAIN AREA */}
        {data ? (
          <>
            <div className="cardLarge">
              <h2>7-Day Nutrition Plan</h2>

              <div className="dayRow">
                {data.diet_7_days.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setSelectedDay(i)}
                    className="dayBtn"
                    style={{
                      background:
                        selectedDay === i ? "#2563EB" : "#E2E8F0",
                      color: selectedDay === i ? "white" : "#0F172A"
                    }}
                  >
                    Day {i + 1}
                  </button>
                ))}
              </div>

              <div className="mealCard">
                <h3>Day {data.diet_7_days[selectedDay].day}</h3>

                <Meal
                  icon={<Sunrise />}
                  label="Breakfast"
                  text={data.diet_7_days[selectedDay].Breakfast}
                />
                <Meal
                  icon={<Utensils />}
                  label="Lunch"
                  text={data.diet_7_days[selectedDay].Lunch}
                />
                <Meal
                  icon={<Moon />}
                  label="Dinner"
                  text={data.diet_7_days[selectedDay].Dinner}
                />
              </div>

              <div style={{ display: "flex", gap: 10 }}>
                <button className="secondaryBtn" onClick={downloadPDF}>
                  <FileText size={18} /> PDF
                </button>

                <button
                  className="secondaryBtn"
                  onClick={() => {
                    const blob = new Blob(
                      [JSON.stringify(data, null, 2)],
                      { type: "application/json" }
                    );
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "plan.json";
                    a.click();
                  }}
                >
                  <FileJson size={18} /> JSON
                </button>
              </div>
            </div>

            {/* INSIGHTS */}
            <div className="card">
              <h2>Clinical Insights</h2>

              {data.insights.map((ins, i) => {
                const isHigh = ins.includes("HIGH");

                return (
                  <div
                    key={i}
                    className="insight"
                    style={{
                      background: isHigh ? "#FEF2F2" : "#F0FDF4"
                    }}
                  >
                    {isHigh ? (
                      <AlertTriangle color="#EF4444" />
                    ) : (
                      <CheckCircle color="#22C55E" />
                    )}
                    <span>{ins}</span>
                  </div>
                );
              })}
            </div>
          </>
        ) : (
          <div className="empty">
            <Calendar size={60} color="#94A3B8" />
            <h2>Ready to Analyze</h2>
            <p>Upload a report to generate insights & nutrition plan</p>
          </div>
        )}
      </div>
    </div>
  );
}

const Meal = ({ icon, label, text }) => (
  <div className="mealRow">
    {icon}
    <div>
      <strong>{label}</strong>
      <div>{text}</div>
    </div>
  </div>
);

export default App;
