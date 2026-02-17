import React, { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { Layout, Activity, Leaf, Upload, FileText, ChevronRight } from 'lucide-react';
import FileUpload from './components/FileUpload';
import HealthDashboard from './components/HealthDashboard';
import DietPlanView from './components/DietPlanView';
import { healthApi } from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [step, setStep] = useState('upload'); // 'upload', 'result'

  const handleFileUpload = async (file) => {
    setLoading(true);
    const toastId = toast.loading('Processing your medical report (OCR + AI Analysis)...');

    try {
      const result = await healthApi.completeAnalysis(file);
      setAnalysisResult(result);
      setStep('result');
      toast.success('Analysis complete!', { id: toastId });
    } catch (error) {
      console.error(error);
      toast.error('Failed to process report. Ensure backend is running.', { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Toaster position="top-right" />

      {/* Navigation */}
      <nav className="glass sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-primary p-2 rounded-lg">
            <Leaf className="text-white w-6 h-6" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">
            AI-Nutri<span className="text-primary">Care</span>
          </h1>
        </div>

        <div className="hidden md:flex gap-8 text-sm font-medium text-slate-600">
          <a href="#" className="hover:text-primary transition-colors">How it works</a>
          <a href="#" className="hover:text-primary transition-colors">Privacy</a>
          <a href="#" className="hover:text-primary transition-colors">Support</a>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={() => { setStep('upload'); setAnalysisResult(null); }}
            className="text-sm px-4 py-2 rounded-full border border-slate-200 hover:bg-slate-100 transition-all font-medium"
          >
            Reset
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12 max-w-6xl">
        {step === 'upload' ? (
          <div className="flex flex-col items-center text-center">
            <h2 className="text-5xl font-extrabold mb-6 gradient-text">
              Transform Medical Data into <br /> Personalized Nutrition
            </h2>
            <p className="text-slate-500 text-lg max-w-2xl mb-12">
              Upload your blood test or doctor's report. Our ensemble ML models (93.1% accuracy)
              will analyze your health risks and curate a safe, delicious 7-day diet plan just for you.
            </p>

            <div className="w-full max-w-xl">
              <FileUpload onUpload={handleFileUpload} loading={loading} />
            </div>

            <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
              {[
                { icon: <FileText />, title: "Precision OCR", text: "Advanced text extraction from PDFs and images." },
                { icon: <Activity />, title: "Risk Detection", text: "Detects Diabetes, BP, and Cholesterol trends." },
                { icon: <Leaf />, title: "Tailored Diets", text: "7-day plans based on clinical needs." }
              ].map((item, i) => (
                <div key={i} className="p-8 bg-white rounded-3xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow flex flex-col items-center">
                  <div className="p-3 bg-slate-50 text-secondary rounded-2xl mb-4">{item.icon}</div>
                  <h3 className="font-bold mb-2">{item.title}</h3>
                  <p className="text-sm text-slate-400">{item.text}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-12">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-500 mb-2">
                <span onClick={() => setStep('upload')} className="cursor-pointer hover:underline">Analysis</span>
                <ChevronRight size={16} />
                <span className="text-primary font-semibold">Results Dashboard</span>
              </div>
            </div>

            {analysisResult && (
              <>
                <HealthDashboard data={analysisResult.health_analysis} />
                <DietPlanView diet={analysisResult.diet_plan} />
              </>
            )}
          </div>
        )}
      </main>

      <footer className="py-12 border-t border-slate-100 text-center text-slate-400 text-sm mt-32">
        <p>© 2026 AI-NutriCare - Personalized Medical Nutrition AI</p>
      </footer>
    </div>
  );
}

export default App;
