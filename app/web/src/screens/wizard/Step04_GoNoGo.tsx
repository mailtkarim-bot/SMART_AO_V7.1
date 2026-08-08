// ─────────────────────────────────────────────────────────────────────────────
// SMART_AO V7 - 04_GoNoGo.tsx
// Écran 4: Go/No-Go - Le Jugement Dernier
// Connecté à l'API Backend: GET /api/v1/missions/{id}/analysis
// ─────────────────────────────────────────────────────────────────────────────

"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Activity, AlertTriangle, CheckCircle, XCircle, Clock, 
  Shield, FileWarning, TrendingUp, ArrowRight 
} from "lucide-react";

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURATION API
// ─────────────────────────────────────────────────────────────────────────────
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─────────────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────────────
interface RiskMatrix {
  juridique: RiskLevel;
  technique: RiskLevel;
  financier: RiskLevel;
}

type RiskLevel = "low" | "medium" | "high" | "critical";

interface AnalysisData {
  viabilityScore: number;
  risks: RiskMatrix;
  deadline: string;
  timeRemaining: string;
  recommendations: string[];
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPOSANT PRINCIPAL
// ─────────────────────────────────────────────────────────────────────────────
export default function GoNoGo() {
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [missionId] = useState("mission_demo_001"); // À récupérer du contexte Wizard

  useEffect(() => {
    // Simulation d'appel API - À remplacer par le vrai endpoint
    const fetchAnalysis = async () => {
      try {
        // TODO: Remplacer par: const response = await fetch(`${API_BASE_URL}/api/v1/missions/${missionId}/analysis`);
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Mock data pour démo
        setAnalysis({
          viabilityScore: 73,
          risks: {
            juridique: "medium",
            technique: "low",
            financier: "high"
          },
          deadline: "2026-08-15T23:59:59Z",
          timeRemaining: "4j 12h 30m",
          recommendations: [
            "Négocier les délais de pénalités (clause 12.3)",
            "Vérifier la conformité DTU 25.4.1",
            "Optimiser le poste Gros Œuvre (-15% possible)"
          ]
        });
      } catch (error) {
        console.error("Erreur analyse:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [missionId]);

  const getRiskColor = (level: RiskLevel) => {
    switch (level) {
      case "low": return "text-[#10B981] bg-[#10B981]/10 border-[#10B981]";
      case "medium": return "text-[#F97316] bg-[#F97316]/10 border-[#F97316]";
      case "high": return "text-red-500 bg-red-500/10 border-red-500";
      case "critical": return "text-purple-500 bg-purple-500/10 border-purple-500";
    }
  };

  const getRiskLabel = (level: RiskLevel) => {
    switch (level) {
      case "low": return "Faible";
      case "medium": return "Modéré";
      case "high": return "Élevé";
      case "critical": return "Critique";
    }
  };

  const getDecisionColor = (score: number) => {
    if (score >= 70) return "from-[#10B981] to-emerald-600";
    if (score >= 50) return "from-[#F97316] to-orange-600";
    return "from-red-500 to-rose-700";
  };

  const getDecisionText = (score: number) => {
    if (score >= 70) return "GO - Lancer l'offre";
    if (score >= 50) return "MITIGÉ - Analyse requise";
    return "NO-GO - Abandonner";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <Activity className="w-16 h-16 text-[#F97316] mx-auto mb-4 animate-pulse" />
          <p className="text-slate-400 text-lg">Analyse en cours...</p>
        </motion.div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center text-red-400">
          <AlertTriangle className="w-16 h-16 mx-auto mb-4" />
          <p>Erreur lors de l'analyse</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <h1 className="text-5xl font-black tracking-tight mb-4">
          <span className="text-white">GO / </span>
          <span className="text-[#F97316]">NO-GO</span>
        </h1>
        <p className="text-slate-400 text-lg">Tableau de bord décisionnel impitoyable</p>
      </motion.div>

      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Score de Viabilité */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-slate-900/50 border border-slate-700 rounded-3xl p-8 flex flex-col items-center justify-center"
        >
          <h2 className="text-2xl font-bold mb-6">Score de Viabilité</h2>
          
          {/* Jauge circulaire animée */}
          <div className="relative w-64 h-64 mb-6">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="128"
                cy="128"
                r="120"
                stroke="#1e293b"
                strokeWidth="16"
                fill="none"
              />
              <motion.circle
                cx="128"
                cy="128"
                r="120"
                stroke="url(#gradient)"
                strokeWidth="16"
                fill="none"
                strokeLinecap="round"
                initial={{ strokeDasharray: "0 754" }}
                animate={{ 
                  strokeDasharray: `${(analysis.viabilityScore / 100) * 754} 754` 
                }}
                transition={{ duration: 2, ease: "easeOut" }}
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" className={`${getDecisionColor(analysis.viabilityScore).split(' ')[0].replace('from-', 'text-')}`} stopColor={analysis.viabilityScore >= 70 ? "#10B981" : analysis.viabilityScore >= 50 ? "#F97316" : "#EF4444"} />
                  <stop offset="100%" className={`${getDecisionColor(analysis.viabilityScore).split(' ')[2].replace('to-', 'text-')}`} stopColor={analysis.viabilityScore >= 70 ? "#059669" : analysis.viabilityScore >= 50 ? "#EA580C" : "#DC2626"} />
                </linearGradient>
              </defs>
            </svg>
            
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <motion.span
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-6xl font-black"
              >
                {analysis.viabilityScore}%
              </motion.span>
              <span className={`text-lg font-bold mt-2 ${
                analysis.viabilityScore >= 70 ? "text-[#10B981]" :
                analysis.viabilityScore >= 50 ? "text-[#F97316]" : "text-red-500"
              }`}>
                {getDecisionText(analysis.viabilityScore)}
              </span>
            </div>
          </div>

          {/* Deadline */}
          <div className="flex items-center gap-2 text-slate-400 mt-4">
            <Clock className="w-5 h-5" />
            <span>Temps restant: <span className="text-white font-bold">{analysis.timeRemaining}</span></span>
          </div>
        </motion.div>

        {/* Matrice des Risques */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          <h2 className="text-2xl font-bold mb-6">Matrice des Risques</h2>
          
          {/* Risque Juridique */}
          <div className={`p-6 rounded-2xl border-2 ${getRiskColor(analysis.risks.juridique)}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <Shield className="w-8 h-8" />
                <span className="text-lg font-bold">Risque Juridique</span>
              </div>
              <span className="px-3 py-1 rounded-full text-sm font-bold uppercase">
                {getRiskLabel(analysis.risks.juridique)}
              </span>
            </div>
            <div className="space-y-2 text-sm opacity-90">
              <p>• Clauses pénales détectées: 3</p>
              <p>• Délais de recours: 10 jours</p>
              <p>• Garanties exigées: 10%</p>
            </div>
          </div>

          {/* Risque Technique */}
          <div className={`p-6 rounded-2xl border-2 ${getRiskColor(analysis.risks.technique)}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <FileWarning className="w-8 h-8" />
                <span className="text-lg font-bold">Risque Technique</span>
              </div>
              <span className="px-3 py-1 rounded-full text-sm font-bold uppercase">
                {getRiskLabel(analysis.risks.technique)}
              </span>
            </div>
            <div className="space-y-2 text-sm opacity-90">
              <p>• DTU non conformes: 0</p>
              <p>• Normes NF: 100% OK</p>
              <p>• Complexité chantier: Moyenne</p>
            </div>
          </div>

          {/* Risque Financier */}
          <div className={`p-6 rounded-2xl border-2 ${getRiskColor(analysis.risks.financier)}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <TrendingUp className="w-8 h-8" />
                <span className="text-lg font-bold">Risque Financier</span>
              </div>
              <span className="px-3 py-1 rounded-full text-sm font-bold uppercase">
                {getRiskLabel(analysis.risks.financier)}
              </span>
            </div>
            <div className="space-y-2 text-sm opacity-90">
              <p>• Marge brute estimée: 18%</p>
              <p>• BQE concurrents: 5 soumissionnaires</p>
              <p>• Délais de paiement: 45 jours</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Recommandations & Actions */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="max-w-6xl mx-auto mt-12"
      >
        <div className="bg-slate-900/50 border border-slate-700 rounded-3xl p-8">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Activity className="w-6 h-6 text-[#F97316]" />
            Recommandations de l'IA
          </h2>
          
          <ul className="space-y-3 mb-8">
            {analysis.recommendations.map((rec, idx) => (
              <motion.li
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + idx * 0.1 }}
                className="flex items-start gap-3"
              >
                <ArrowRight className="w-5 h-5 text-[#F97316] flex-shrink-0 mt-0.5" />
                <span className="text-slate-300">{rec}</span>
              </motion.li>
            ))}
          </ul>

          {/* Boutons d'action */}
          <div className="flex gap-4 justify-center">
            {analysis.viabilityScore < 50 ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-12 py-6 bg-red-600 hover:bg-red-700 text-white font-black text-xl rounded-2xl shadow-lg shadow-red-600/30"
              >
                <XCircle className="w-6 h-6 inline-block mr-2" />
                ABANDONNER
              </motion.button>
            ) : (
              <>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-6 bg-slate-700 hover:bg-slate-600 text-white font-bold text-lg rounded-2xl"
                >
                  Analyser les risques
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-12 py-6 bg-gradient-to-r ${getDecisionColor(analysis.viabilityScore)} text-white font-black text-xl rounded-2xl shadow-lg`}
                >
                  <CheckCircle className="w-6 h-6 inline-block mr-2" />
                  {analysis.viabilityScore >= 70 ? "LANCER L'OFFRE" : "CONTINUER L'ANALYSE"}
                </motion.button>
              </>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
