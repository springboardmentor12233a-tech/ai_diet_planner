import React, { useCallback, useState } from 'react';
import { Upload, X, File, CheckCircle2 } from 'lucide-react';

const FileUpload = ({ onUpload, loading }) => {
    const [file, setFile] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    return (
        <div className="w-full">
            {!file ? (
                <div
                    className={`relative border-2 border-dashed rounded-3xl p-12 transition-all cursor-pointer bg-white group
            ${dragActive ? 'border-primary bg-blue-50/50 scale-[1.01]' : 'border-slate-200 hover:border-primary/50'}
          `}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('input-file-upload').click()}
                >
                    <input
                        id="input-file-upload"
                        type="file"
                        className="hidden"
                        onChange={handleChange}
                        accept=".pdf,.png,.jpg,.jpeg"
                    />

                    <div className="flex flex-col items-center justify-center gap-4">
                        <div className="p-4 bg-blue-50 text-primary rounded-2xl group-hover:scale-110 transition-transform">
                            <Upload size={32} />
                        </div>
                        <div>
                            <p className="text-xl font-semibold">Drop your medical report here</p>
                            <p className="text-slate-400 text-sm mt-1">Supports PDF, PNG, JPG (Max 10MB)</p>
                        </div>
                        <button className="mt-4 px-6 py-2 bg-slate-900 text-white rounded-full text-sm font-medium hover:bg-slate-800 transition-colors">
                            Browse Files
                        </button>
                    </div>
                </div>
            ) : (
                <div className="bg-white border border-slate-200 rounded-3xl p-8 flex items-center justify-between shadow-sm">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-secondary/10 text-secondary rounded-xl">
                            <File size={24} />
                        </div>
                        <div className="text-left">
                            <p className="font-semibold text-slate-900">{file.name}</p>
                            <p className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB • Ready to analyze</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setFile(null)}
                            className="p-2 hover:bg-red-50 text-slate-400 hover:text-red-500 rounded-lg transition-colors"
                            disabled={loading}
                        >
                            <X size={20} />
                        </button>
                        <button
                            onClick={() => onUpload(file)}
                            className={`px-8 py-3 rounded-full font-bold flex items-center gap-2 transition-all
                ${loading ? 'bg-slate-100 text-slate-400' : 'bg-primary text-white hover:shadow-lg hover:shadow-primary/30'}
              `}
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-slate-300 border-t-slate-500" />
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    <CheckCircle2 size={18} />
                                    Start Analysis
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FileUpload;
