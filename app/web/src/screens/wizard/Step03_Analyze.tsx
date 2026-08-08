"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Cpu, Activity, CheckCircle2, AlertTriangle, XCircle, 
  ChevronDown, ChevronUp, Terminal, Zap 
} from "lucide-react";

type AgentStatus = "idle" | "running" | "completed" | "warning" | "error";

interface Agent {
  id: string;
  name: string;
  category: "juridique" | "technique" | "financier" | "conformite";
  status: AgentStatus;
  progress: number;
}

const initialAgents: Agent[] = [
  { id: "j1", name: "Détection clauses pénales", category: "juridique", status: "idle", progress: 0 },
  { id: "j2", name: "Vérification garanties", category: "juridique", status: "idle", progress: 0 },
  { id: "j3", name: "Analyse délais recours", category: "juridique", status: "idle", progress: 0 },
  { id: "t1", name: "Vérification DTU", category: "technique", status: "idle", progress: 0 },
  { id: "t2", name: "Analyse normes NF", category: "technique", status: "idle", progress: 0 },
  { id: "f1", name: "Calcul marge brute", category: "financier", status: "idle", progress: 0 },
  { id: "f2", name: "Analyse BQE concurrents", category: "financier", status: "idle", progress: 0 },
  { id: "c1", name: "Vérification RSE", category: "conformite", status: "idle", progress: 0 },
];

export default function AnalyzeIA() {
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    const runAnalysis = async () => {
      for (let i = 0; i < agents.length; i++) {
        setAgents(prev => prev.map((a, idx) => 
          idx === i ? { ...a, status: "running" as AgentStatus } : a
        ));
        setLogs(prev => [...prev, `Démarrage: ${agents[i].name}`]);
        await new Promise(r => setTimeout(r, 500));
        
        setAgents(prev => prev.map((a, idx) => 
          idx === i ? { ...a, progress: 100, status: Math.random() > 0.9 ? "warning" : "completed" } : a
        ));
        setLogs(prev => [...prev, `✓ ${agents[i].name} terminé`]);
        setOverallProgress(Math.round(((i + 1) / agents.length) * 100));
      }
      setIsComplete(true);
    };
    runAnalysis();
  }, []);

  const getStatusColor = (status: AgentStatus) => {
    switch (status) {
      case "idle": return "text-slate-600 bg-slate-900 border-slate-800";
      case "running": return "text-blue-400 bg-blue-900/20 border-blue-500 animate-pulse";
      case "completed": return "text-[#10B981] bg-[#10B981]/10 border-[#10B981]";
      case "warning": return "text-[#F97316] bg-[#F97316]/10 border-[#F97316]";
      case "error": return "text-red-500 bg-red-900/20 border-red-500";
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-2">
          <Cpu className="w-8 h-8 text-[#F97316]" />
          <h1 className="text-4xl font-black">ANALYSE <span className="text-[#F97316]">IA</span></h1>
        </div>
        <p className="text-slate-400">33 agents spécialisés analysent votre dossier</p>
      </motion.div>

      {/* Progress */}
      <div className="max-w-4xl mx-auto mb-8">
        <div className="flex justify-between mb-2">
          <span className="text-sm text-slate-400">Progression</span>
          <span className="text-sm font-bold text-[#F97316]">{overallProgress}%</span>
        </div>
        <div className="h-3 bg-slate-900 rounded-full overflow-hidden">
          <motion.div className="h-full bg-gradient-to-r from-[#F97316] to-[#10B981]" 
            initial={{ width: 0 }} animate={{ width: `${overallProgress}%` }} />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 max-w-4xl mx-auto mb-8">
        <div className="bg-slate-900/50 border border-[#10B981] rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-[#10B981]">{agents.filter(a => a.status === "completed").length}</div>
          <div className="text-xs text-slate-400">Succès</div>
        </div>
        <div className="bg-slate-900/50 border border-[#F97316] rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-[#F97316]">{agents.filter(a => a.status === "warning").length}</div>
          <div className="text-xs text-slate-400">Risques</div>
        </div>
        <div className="bg-slate-900/50 border border-red-500 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-red-500">{agents.filter(a => a.status === "error").length}</div>
          <div className="text-xs text-slate-400">Erreurs</div>
        </div>
        <div className="bg-slate-900/50 border border-blue-500 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-blue-400">{agents.filter(a => a.status === "running").length}</div>
          <div className="text-xs text-slate-400">En cours</div>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {agents.map((agent, idx) => (
          <motion.div key={agent.id} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.05 }}
            className={`p-3 rounded-lg border ${getStatusColor(agent.status)}`}>
            <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">{agent.category}</div>
            <div className="text-sm font-medium">{agent.name}</div>
            {agent.status === "running" && (
              <div className="h-1 bg-slate-800 rounded-full mt-2">
                <motion.div className="h-full bg-blue-500" initial={{ width: 0 }} animate={{ width: `${agent.progress}%` }} />
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Logs Toggle */}
      <div className="max-w-4xl mx-auto">
        <button onClick={() => setShowLogs(!showLogs)} 
          className="w-full flex justify-between items-center p-4 bg-slate-900/50 border border-slate-700 rounded-xl">
          <div className="flex items-center gap-2"><Terminal className="w-5 h-5" /><span>Logs temps réel</span></div>
          <ChevronDown className={`w-5 h-5 transition-transform ${showLogs ? "rotate-180" : ""}`} />
        </button>
        
        {showLogs && (
          <motion.div initial={{ height: 0 }} animate={{ height: "auto" }} 
            className="bg-slate-950 border border-slate-800 rounded-xl p-4 mt-4 h-48 overflow-y-auto font-mono text-sm">
            {logs.map((log, i) => (
              <div key={i} className="text-[#10B981]">{log}</div>
            ))}
          </motion.div>
        )}
      </div>

      {isComplete && (
        <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
          className="fixed bottom-8 right-8 bg-[#10B981] text-white px-6 py-4 rounded-xl shadow-2xl">
          <div className="flex items-center gap-3">
            <Zap className="w-6 h-6" />
            <div><div className="font-bold">Analyse terminée</div><div className="text-sm opacity-90">Prêt pour Go/No-Go</div></div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
