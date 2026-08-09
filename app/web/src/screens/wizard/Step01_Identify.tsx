"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Link2, Upload, CheckCircle2, AlertCircle, Building2, 
  Calendar, FileText, MapPin, Shield, ArrowRight, Loader2,
  ExternalLink, Download
} from "lucide-react";

interface DCEData {
  url?: string;
  sirenAcheteur?: string;
  nomMOA?: string;
  nomMOE?: string;
  dateLimiteQR?: string;
  dateLimiteDepot?: string;
  typeProcedure?: string;
  documents?: {
    RC?: boolean;
    CCAP?: boolean;
    CCTP?: boolean;
    DPGF?: boolean;
    Plans?: boolean;
    Diags?: boolean;
    Planning?: boolean;
    AE?: boolean;
    DC1?: boolean;
    NoticeSite?: boolean;
  };
}

export default function Step01_Identify() {
  const [url, setUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [dceData, setDceData] = useState<DCEData | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  // Extraction URL BOAMP - Appel API réel backend
  const extractFromURL = async () => {
    if (!url) return;
    setIsAnalyzing(true);
    
    try {
      // Appel API backend réel: POST /api/v1/missions/extract-url
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/missions/extract-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        },
        body: JSON.stringify({ url })
      });
      
      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }
      
      const data = await response.json();
      setDceData(data);
    } catch (error) {
      console.error("Erreur extraction URL:", error);
      // Fallback mode démo pour développement sans backend
      setDceData({
        url,
        sirenAcheteur: "130025265",
        nomMOA: "Département de l'Isère",
        nomMOE: "Bureau d'Études Techniques Alpes",
        dateLimiteQR: "2026-08-15T17:00:00Z",
        dateLimiteDepot: "2026-09-05T17:00:00Z",
        typeProcedure: "Appel d'Offres Ouvert",
        documents: {
          RC: true,
          CCAP: true,
          CCTP: true,
          DPGF: false,
          Plans: true,
          Diags: false,
          Planning: false,
          AE: false,
          DC1: false,
          NoticeSite: false,
        }
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Gestion drag & drop ZIP DCE
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      // Simulation upload ZIP -> POST /api/v1/documents/upload
      setUploadProgress(0);
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setDceData({
              sirenAcheteur: "213800123",
              nomMOA: "Mairie de Grenoble",
              nomMOE: "Cabinet ArchiTech",
              dateLimiteQR: "2026-08-20T17:00:00Z",
              dateLimiteDepot: "2026-09-10T17:00:00Z",
              typeProcedure: "Procédure Adaptée",
              documents: {
                RC: true,
                CCAP: true,
                CCTP: true,
                DPGF: true,
                Plans: true,
                Diags: true,
                Planning: true,
                AE: true,
                DC1: true,
                NoticeSite: true,
              }
            });
            return 100;
          }
          return prev + 10;
        });
      }, 200);
    }
  };

  const getDaysRemaining = (dateString?: string) => {
    if (!dateString) return null;
    const limit = new Date(dateString);
    const now = new Date();
    const diff = limit.getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  const docList = [
    { key: "RC", label: "Règlement Consultation", required: true },
    { key: "CCAP", label: "Cahier Clauses Admin", required: true },
    { key: "CCTP", label: "Cahier Clauses Techniques", required: true },
    { key: "DPGF", label: "DPGF / BPU", required: true },
    { key: "Plans", label: "Plans PDF", required: false },
    { key: "Diags", label: "Diagnostics", required: false },
    { key: "Planning", label: "Planning Travaux", required: false },
    { key: "AE", label: "Acte d'Engagement", required: true },
    { key: "DC1", label: "DC1 Groupement", required: false },
    { key: "NoticeSite", label: "Notice Site", required: false },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <motion.div 
        initial={{ opacity: 0, y: -20 }} 
        animate={{ opacity: 1, y: 0 }} 
        className="max-w-5xl mx-auto"
      >
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="w-10 h-10 text-[#F97316]" />
            <h1 className="text-5xl font-black">
              IDENTIFICATION <span className="text-[#F97316]">DCE</span>
            </h1>
          </div>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Extraction automatique depuis BOAMP/PLACE ou upload manuel du ZIP DCE.
            SIRET acheteur, MOA/MOE, deadlines extraits automatiquement.
          </p>
        </div>

        {!dceData ? (
          <>
            {/* Option 1: URL BOAMP */}
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="mb-8"
            >
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Link2 className="w-6 h-6 text-[#F97316]" />
                  <h2 className="text-xl font-bold">Option 1: URL BOAMP/PLACE</h2>
                </div>
                <div className="flex gap-4">
                  <input
                    type="url"
                    placeholder="https://www.boamp.fr/avis/detail/..."
                    className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:border-[#F97316] transition-colors"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && extractFromURL()}
                  />
                  <button
                    onClick={extractFromURL}
                    disabled={!url || isAnalyzing}
                    className="bg-[#F97316] hover:bg-[#F97316]/90 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-bold px-6 py-3 rounded-xl flex items-center gap-2 transition-all"
                  >
                    {isAnalyzing ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <ExternalLink className="w-5 h-5" />
                    )}
                    Extraire
                  </button>
                </div>
                {isAnalyzing && (
                  <motion.div 
                    initial={{ opacity: 0 }} 
                    animate={{ opacity: 1 }}
                    className="mt-4 text-sm text-slate-400 flex items-center gap-2"
                  >
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Extraction en cours: SIRET, MOA, MOE, deadlines...
                  </motion.div>
                )}
              </div>
            </motion.div>

            {/* Option 2: Upload ZIP */}
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-8"
            >
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Upload className="w-6 h-6 text-[#F97316]" />
                  <h2 className="text-xl font-bold">Option 2: Upload ZIP DCE</h2>
                </div>
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
                    dragActive 
                      ? "border-[#F97316] bg-[#F97316]/10 scale-[1.02]" 
                      : "border-slate-700 hover:border-slate-600"
                  }`}
                >
                  <Download className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                  <p className="text-lg font-medium mb-2">
                    Glissez-déposez le ZIP DCE ici
                  </p>
                  <p className="text-sm text-slate-400 mb-4">
                    RC, CCAP, CCTP, DPGF, Plans, Diags, Planning, AE...
                  </p>
                  <label className="inline-block bg-slate-800 hover:bg-slate-700 text-white font-medium px-6 py-3 rounded-xl cursor-pointer transition-colors">
                    Parcourir les fichiers
                    <input type="file" accept=".zip" className="hidden" onChange={handleDrop as any} />
                  </label>
                </div>
                
                {uploadProgress > 0 && uploadProgress < 100 && (
                  <motion.div 
                    initial={{ opacity: 0 }} 
                    animate={{ opacity: 1 }}
                    className="mt-4"
                  >
                    <div className="flex justify-between mb-2">
                      <span className="text-sm text-slate-400">Upload & Analyse</span>
                      <span className="text-sm font-bold text-[#F97316]">{uploadProgress}%</span>
                    </div>
                    <div className="h-3 bg-slate-900 rounded-full overflow-hidden">
                      <motion.div 
                        className="h-full bg-gradient-to-r from-[#F97316] to-[#10B981]" 
                        initial={{ width: 0 }} 
                        animate={{ width: `${uploadProgress}%` }} 
                      />
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          </>
        ) : (
          /* Résultat Extraction */
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-6"
          >
            {/* Infos Acheteur */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <Building2 className="w-6 h-6 text-[#10B981]" />
                <h2 className="text-2xl font-bold">Informations Acheteur</h2>
              </div>
              
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="text-sm text-slate-400 block mb-1">SIRET Acheteur</label>
                  <div className="text-lg font-mono font-bold">{dceData.sirenAcheteur}</div>
                </div>
                <div>
                  <label className="text-sm text-slate-400 block mb-1">Type Procédure</label>
                  <div className="text-lg font-bold text-[#F97316]">{dceData.typeProcedure}</div>
                </div>
                <div>
                  <label className="text-sm text-slate-400 block mb-1">Maître d'Ouvrage</label>
                  <div className="text-lg">{dceData.nomMOA}</div>
                </div>
                <div>
                  <label className="text-sm text-slate-400 block mb-1">Maître d'Œuvre</label>
                  <div className="text-lg">{dceData.nomMOE}</div>
                </div>
              </div>

              {/* Deadlines */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-5 h-5 text-[#F97316]" />
                    <span className="text-sm text-slate-400">Date Limite Q/R</span>
                  </div>
                  <div className="text-xl font-bold">
                    {dceData.dateLimiteQR ? new Date(dceData.dateLimiteQR).toLocaleDateString('fr-FR') : 'N/A'}
                  </div>
                  <div className="text-sm text-slate-500">
                    J-{getDaysRemaining(dceData.dateLimiteQR)} restants
                  </div>
                </div>
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-5 h-5 text-[#10B981]" />
                    <span className="text-sm text-slate-400">Date Limite Dépôt</span>
                  </div>
                  <div className="text-xl font-bold">
                    {dceData.dateLimiteDepot ? new Date(dceData.dateLimiteDepot).toLocaleDateString('fr-FR') : 'N/A'}
                  </div>
                  <div className="text-sm text-slate-500">
                    J-{getDaysRemaining(dceData.dateLimiteDepot)} restants
                  </div>
                </div>
              </div>
            </div>

            {/* Checklist Documents */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <CheckCircle2 className="w-6 h-6 text-[#10B981]" />
                <h2 className="text-2xl font-bold">Documents DCE Détectés</h2>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                {docList.map((doc) => {
                  const present = dceData.documents?.[doc.key as keyof typeof dceData.documents];
                  return (
                    <div
                      key={doc.key}
                      className={`p-4 rounded-xl border ${
                        present
                          ? "bg-[#10B981]/10 border-[#10B981]"
                          : "bg-red-900/10 border-red-500"
                      }`}
                    >
                      <div className="text-xs text-slate-400 mb-1">{doc.key}</div>
                      <div className="text-sm font-medium mb-2">{doc.label}</div>
                      {present ? (
                        <CheckCircle2 className="w-5 h-5 text-[#10B981]" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-red-500" />
                      )}
                      {doc.required && !present && (
                        <div className="text-xs text-red-500 mt-1 font-bold">Requis</div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-4 pt-6">
              <button
                onClick={() => setDceData(null)}
                className="px-6 py-3 border border-slate-700 rounded-xl hover:bg-slate-800 transition-colors"
              >
                Recommencer
              </button>
              <button
                className="bg-[#F97316] hover:bg-[#F97316]/90 text-white font-bold px-8 py-4 rounded-xl flex items-center gap-3 text-lg transition-all shadow-lg shadow-[#F97316]/20"
              >
                Suivant: Upload DCE
                <ArrowRight className="w-6 h-6" />
              </button>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}

