import React, { useState } from 'react';
import { Clock, ShoppingCart, Info, Flame, ChevronRight, Apple } from 'lucide-react';

const DietPlanView = ({ diet }) => {
    const [activeDay, setActiveDay] = useState(1);

    if (!diet || !diet.daily_plans) return null;

    const days = Object.keys(diet.daily_plans).map(k => parseInt(k)).sort((a, b) => a - b);
    const currentPlan = diet.daily_plans[activeDay.toString()];

    const getMealIcon = (type) => {
        switch (type.toLowerCase()) {
            case 'breakfast': return '🍳';
            case 'lunch': return '🥗';
            case 'dinner': return '🍲';
            case 'snack': return '🍎';
            default: return '🍽️';
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-1000 slide-in-from-bottom-8">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-extrabold flex items-center gap-3">
                    <Apple className="text-secondary" />
                    Your Personalized 7-Day Plan
                </h2>
                <button className="flex items-center gap-2 bg-secondary text-white px-6 py-2 rounded-full font-bold hover:shadow-lg hover:shadow-secondary/30 transition-all text-sm">
                    <ShoppingCart size={18} />
                    Export Shopping List
                </button>
            </div>

            {/* Day Selector */}
            <div className="flex flex-wrap gap-2 p-1.5 bg-white rounded-2xl border border-slate-100 w-fit">
                {days.map(day => (
                    <button
                        key={day}
                        onClick={() => setActiveDay(day)}
                        className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all
              ${activeDay === day ? 'bg-primary text-white shadow-md' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-50'}
            `}
                    >
                        Day {day}
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Meals List */}
                <div className="lg:col-span-2 space-y-4">
                    {['Breakfast', 'Lunch', 'Snack', 'Dinner'].map((mealType) => {
                        const meal = currentPlan[mealType];
                        return (
                            <div key={mealType} className="bg-white p-6 rounded-3xl border border-slate-100 hover:border-primary/30 transition-all group shadow-sm">
                                <div className="flex items-start justify-between">
                                    <div className="flex gap-4">
                                        <div className="text-3xl bg-slate-50 w-16 h-16 rounded-2xl flex items-center justify-center group-hover:bg-blue-50 transition-colors">
                                            {getMealIcon(mealType)}
                                        </div>
                                        <div>
                                            <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">{mealType}</p>
                                            <h4 className="text-xl font-bold text-slate-800">{meal.name}</h4>
                                            <p className="text-sm text-slate-500 mt-2 line-clamp-2">{meal.description || "Nutrient-rich balanced meal curated by AI."}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="flex items-center gap-1 text-slate-600 font-bold justify-end">
                                            <Flame size={14} className="text-orange-500" />
                                            <span>{meal.calories} kcal</span>
                                        </div>
                                        <div className="text-[10px] text-slate-400 mt-1">
                                            P: {meal.protein}g | C: {meal.carbs}g | F: {meal.fat}g
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Daily Summary Sidebar */}
                <div className="space-y-6">
                    <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <Clock size={80} />
                        </div>
                        <h4 className="font-bold text-lg mb-6">Daily Nutrition Target</h4>
                        <div className="space-y-6">
                            <div>
                                <div className="flex justify-between text-sm mb-2">
                                    <span className="text-slate-500">Day Total</span>
                                    <span className="font-bold text-slate-900">{currentPlan.Total?.calories || 2000} kcal</span>
                                </div>
                                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                                    <div className="bg-primary h-full w-[85%] rounded-full shadow-[0_0_10px_rgba(59,130,246,0.3)]"></div>
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-2 py-4 border-y border-slate-50">
                                <div className="text-center">
                                    <p className="text-[10px] uppercase text-slate-400 font-bold mb-1">Carbs</p>
                                    <p className="text-sm font-bold text-slate-800">{currentPlan.Total?.carbs}g</p>
                                </div>
                                <div className="text-center border-x border-slate-50">
                                    <p className="text-[10px] uppercase text-slate-400 font-bold mb-1">Protein</p>
                                    <p className="text-sm font-bold text-slate-800">{currentPlan.Total?.protein}g</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] uppercase text-slate-400 font-bold mb-1">Fat</p>
                                    <p className="text-sm font-bold text-slate-800">{currentPlan.Total?.fat}g</p>
                                </div>
                            </div>
                        </div>

                        <div className="mt-8 p-4 bg-secondary/5 rounded-2xl border border-secondary/10 flex gap-3">
                            <Info size={16} className="text-secondary shrink-0 mt-0.5" />
                            <p className="text-xs text-secondary leading-relaxed">
                                This plan excludes {diet.restrictions?.length > 0 ? diet.restrictions.join(", ") : "all identified allergens"} based on your medical notes.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DietPlanView;
