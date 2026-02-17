import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ReferenceLine } from 'recharts';
import { AlertCircle, CheckCircle, Info, ShieldCheck } from 'lucide-react';

const HealthDashboard = ({ data }) => {
    if (!data) return null;

    const { health_metrics, ml_analysis, health_score, recommendations } = data;

    // Format metrics for the chart
    const chartData = [
        { name: 'Glucose', value: health_metrics.blood_sugar_fasting || 100, normal: 99, status: (health_metrics.blood_sugar_fasting > 125 ? 'High' : 'Normal') },
        { name: 'BP (Sys)', value: parseInt(health_metrics.blood_pressure?.split('/')[0]) || 120, normal: 120, status: (parseInt(health_metrics.blood_pressure?.split('/')[0]) > 140 ? 'High' : 'Normal') },
        { name: 'BMI', value: health_metrics.bmi || 24, normal: 25, status: (health_metrics.bmi > 30 ? 'High' : 'Normal') },
        { name: 'LDL', value: health_metrics.ldl_cholesterol || 110, normal: 100, status: (health_metrics.ldl_cholesterol > 130 ? 'High' : 'Normal') },
    ];

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-secondary';
        if (score >= 60) return 'text-yellow-500';
        return 'text-red-500';
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-700 slide-in-from-bottom-4">
            {/* Top Header Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-3xl border border-slate-100 flex flex-col justify-between">
                    <p className="text-slate-400 text-sm font-medium">Health Score</p>
                    <div className="mt-2 flex items-baseline gap-1">
                        <span className={`text-4xl font-extrabold ${getScoreColor(health_score)}`}>{health_score || 85}</span>
                        <span className="text-slate-300 font-semibold">/100</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-2">Based on extracted clinical markers</p>
                </div>

                <div className="bg-white p-6 rounded-3xl border border-slate-100 col-span-1 md:col-span-3 flex items-center justify-between">
                    <div className="flex gap-4">
                        <div className="p-3 bg-blue-50 text-primary rounded-2xl h-fit">
                            <ShieldCheck size={28} />
                        </div>
                        <div>
                            <p className="font-bold text-lg">AI Analysis Summary</p>
                            <p className="text-slate-500 text-sm mt-1">
                                Our ensemble models detected <span className="text-slate-900 font-medium">
                                    {ml_analysis.conditions_detected?.length > 0 ? ml_analysis.conditions_detected.join(", ") : "no critical medical conditions"}
                                </span> with a confidence of <span className="text-primary font-bold">{(ml_analysis.ml_confidence * 100).toFixed(1)}%</span>.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Visual Chart */}
                <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
                    <h3 className="font-bold mb-6 flex items-center gap-2">
                        <Info size={18} className="text-slate-400" />
                        Metabolic Markers vs. Normal Range
                    </h3>
                    <div className="h-[250px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                                <YAxis hide />
                                <Tooltip
                                    cursor={{ fill: '#f8fafc' }}
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Bar dataKey="value" radius={[10, 10, 10, 10]} barSize={40}>
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.value > entry.normal * 1.2 ? 'oklch(0.6 0.18 20)' : 'oklch(0.6 0.18 200)'} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Recommendations */}
                <div className="bg-slate-900 text-white p-8 rounded-3xl shadow-xl space-y-6">
                    <h3 className="font-bold flex items-center gap-2 text-secondary">
                        <CheckCircle size={18} />
                        Clinical Recommendations
                    </h3>
                    <div className="space-y-4">
                        {recommendations && recommendations.length > 0 ? recommendations.map((rec, i) => (
                            <div key={i} className="flex gap-3 text-sm leading-relaxed text-slate-300 bg-white/5 p-4 rounded-2xl border border-white/10">
                                <div className="text-secondary">•</div>
                                {rec}
                            </div>
                        )) : (
                            <p className="text-slate-400 italic">No specific medical concerns detected based on the report.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HealthDashboard;
