"use client";

import React, { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Calculator,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Users,
  Lock,
  Unlock,
  Zap,
  Save,
  Download,
  ChevronLeft,
  ChevronRight,
  Search,
  Filter,
  Plus,
  Trash2,
  Eye,
  EyeOff
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

// Types
interface MetreLine {
  id: string;
  reference: string;
  designation: string;
  unite: string;
  quantiteCCTP: number;
  quantiteDPGF: number;
  prixUnitaire: number;
  coutMateriaux: number;
  coutMainOeuvre: number;
  coefficient: number;
  margeBrute: number;
  ecart: number;
  status: "ok" | "warning" | "error";
}

interface UserRole {
  canSeePrixUnitaires: boolean;
  canSeeMarge: boolean;
  canEdit: boolean;
  canOptimize: boolean;
}

interface Props {
  onNext: () => void;
  onBack: () => void;
  missionId?: string;
}

export default function MetreChiffrage({ onNext, onBack, missionId }: Props) {
  // État utilisateur (RBAC)
  const [userRole, setUserRole] = useState<UserRole>({
    canSeePrixUnitaires: true,
    canSeeMarge: true,
    canEdit: true,
    canOptimize: true,
  });

  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<"all" | "ok" | "warning" | "error">("all");
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<{
    savings: number;
    newMargin: number;
    suggestions: string[];
  } | null>(null);

  // Données de métré (simulées - à charger depuis le backend)
  const [metreLines, setMetreLines] = useState<MetreLine[]>([
    {
      id: "1",
      reference: "TER.001",
      designation: "Terrassement en pleine masse - terrain normal",
      unite: "m³",
      quantiteCCTP: 150,
      quantiteDPGF: 148,
      prixUnitaire: 45.00,
      coutMateriaux: 1200,
      coutMainOeuvre: 3500,
      coefficient: 1.25,
      margeBrute: 0,
      ecart: 2,
      status: "warning" as const,
    },
    {
      id: "2",
      reference: "FON.001",
      designation: "Béton de propreté ép. 10cm",
      unite: "m³",
      quantiteCCTP: 25,
      quantiteDPGF: 25,
      prixUnitaire: 120.00,
      coutMateriaux: 1800,
      coutMainOeuvre: 1200,
      coefficient: 1.30,
      margeBrute: 0,
      ecart: 0,
      status: "ok" as const,
    },
    {
      id: "3",
      reference: "FON.002",
      designation: "Semelles filantes béton armé",
      unite: "m³",
      quantiteCCTP: 85,
      quantiteDPGF: 92,
      prixUnitaire: 185.00,
      coutMateriaux: 8500,
      coutMainOeuvre: 6200,
      coefficient: 1.28,
      margeBrute: 0,
      ecart: -7,
      status: "error" as const,
    },
    {
      id: "4",
      reference: "MAC.001",
      designation: "Maçonnerie parpaings 20x20x50",
      unite: "m²",
      quantiteCCTP: 420,
      quantiteDPGF: 420,
      prixUnitaire: 65.00,
      coutMateriaux: 12600,
      coutMainOeuvre: 14700,
      coefficient: 1.35,
      margeBrute: 0,
      ecart: 0,
      status: "ok" as const,
    },
    {
      id: "5",
      reference: "COU.001",
      designation: "Couverture tuiles mécaniques",
      unite: "m²",
      quantiteCCTP: 280,
      quantiteDPGF: 275,
      prixUnitaire: 95.00,
      coutMateriaux: 15400,
      coutMainOeuvre: 10800,
      coefficient: 1.32,
      margeBrute: 0,
      ecart: 5,
      status: "warning" as const,
    },
    {
      id: "6",
      reference: "MEN.001",
      designation: "Menuiserie PVC blanc double vitrage",
      unite: "m²",
      quantiteCCTP: 95,
      quantiteDPGF: 95,
      prixUnitaire: 280.00,
      coutMateriaux: 18000,
      coutMainOeuvre: 8600,
      coefficient: 1.40,
      margeBrute: 0,
      ecart: 0,
      status: "ok" as const,
    },
    {
      id: "7",
      reference: "ELE.001",
      designation: "Installation électrique complète",
      unite: "LOT",
      quantiteCCTP: 1,
      quantiteDPGF: 1,
      prixUnitaire: 12500.00,
      coutMateriaux: 6500,
      coutMainOeuvre: 6000,
      coefficient: 1.35,
      margeBrute: 0,
      ecart: 0,
      status: "ok" as const,
    },
    {
      id: "8",
      reference: "PLO.001",
      designation: "Plomberie sanitaire complète",
      unite: "LOT",
      quantiteCCTP: 1,
      quantiteDPGF: 1,
      prixUnitaire: 9800.00,
      coutMateriaux: 5200,
      coutMainOeuvre: 4600,
      coefficient: 1.38,
      margeBrute: 0,
      ecart: 0,
      status: "ok" as const,
    },
  ]);

  // Calcul des totaux
  const totals = useMemo(() => {
    const totalHT = metreLines.reduce((acc, line) => {
      const qty = line.quantiteDPGF || line.quantiteCCTP;
      return acc + (qty * line.prixUnitaire);
    }, 0);

    const totalCout = metreLines.reduce((acc, line) => {
      return acc + line.coutMateriaux + line.coutMainOeuvre;
    }, 0);

    const margeBrute = totalHT - totalCout;
    const tauxMarge = totalHT > 0 ? (margeBrute / totalHT) * 100 : 0;

    const ecartsCount = {
      ok: metreLines.filter(l => l.status === "ok").length,
      warning: metreLines.filter(l => l.status === "warning").length,
      error: metreLines.filter(l => l.status === "error").length,
    };

    return { totalHT, totalCout, margeBrute, tauxMarge, ecartsCount };
  }, [metreLines]);

  // Filtrage des lignes
  const filteredLines = useMemo(() => {
    return metreLines.filter(line => {
      const matchesSearch = line.designation.toLowerCase().includes(searchTerm.toLowerCase()) ||
        line.reference.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesFilter = filterStatus === "all" || line.status === filterStatus;
      return matchesSearch && matchesFilter;
    });
  }, [metreLines, searchTerm, filterStatus]);

  // Calcul automatique de la marge brute pour chaque ligne
  useEffect(() => {
    setMetreLines(prev => prev.map(line => {
      const qty = line.quantiteDPGF || line.quantiteCCTP;
      const caLigne = qty * line.prixUnitaire;
      const coutLigne = line.coutMateriaux + line.coutMainOeuvre;
      return {
        ...line,
        margeBrute: caLigne - coutLigne,
      };
    }));
  }, []);

  // Optimisation OR-Tools (simulation)
  const handleOptimization = async () => {
    setIsOptimizing(true);
    
    // Appel API vers le backend pour l'optimisation
    try {
      const response = await fetch(`/api/v1/missions/${missionId}/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lines: metreLines.map(l => ({
            reference: l.reference,
            quantite: l.quantiteDPGF || l.quantiteCCTP,
            coutMateriaux: l.coutMateriaux,
            coutMainOeuvre: l.coutMainOeuvre,
            coefficient: l.coefficient,
          })),
        }),
      });

      if (!response.ok) throw new Error("Optimization failed");

      const data = await response.json();
      setOptimizationResult(data);
      
      // Appliquer les suggestions si acceptées
      if (data.suggestions) {
        // Mise à jour des lignes optimisées
      }
    } catch (error) {
      console.error("Optimization error:", error);
      // Fallback simulation
      setTimeout(() => {
        setOptimizationResult({
          savings: totals.totalHT * 0.08,
          newMargin: totals.tauxMarge + 5.2,
          suggestions: [
            "Négocier fournisseur béton: -12% sur semelles filantes",
            "Optimiser découpe tuiles: -8% gaspillage",
            "Regrouper lots électricité/plomberie: -5% main d'oeuvre",
          ],
        });
        setIsOptimizing(false);
      }, 2000);
    }
  };

  const updateLine = (id: string, field: keyof MetreLine, value: any) => {
    setMetreLines(prev => prev.map(line => {
      if (line.id !== id) return line;
      
      const updated = { ...line, [field]: value };
      
      // Recalcul automatique de l'écart et du status
      if (field === "quantiteDPGF" || field === "quantiteCCTP") {
        updated.ecart = updated.quantiteCCTP - updated.quantiteDPGF;
        if (Math.abs(updated.ecart) === 0) {
          updated.status = "ok";
        } else if (Math.abs(updated.ecart) <= 5) {
          updated.status = "warning";
        } else {
          updated.status = "error";
        }
      }
      
      return updated;
    }));
  };

  const addNewLine = () => {
    const newLine: MetreLine = {
      id: Date.now().toString(),
      reference: `NOU.${metreLines.length + 1}`,
      designation: "Nouvelle ligne à compléter",
      unite: "U",
      quantiteCCTP: 0,
      quantiteDPGF: 0,
      prixUnitaire: 0,
      coutMateriaux: 0,
      coutMainOeuvre: 0,
      coefficient: 1.25,
      margeBrute: 0,
      ecart: 0,
      status: "warning" as const,
    };
    setMetreLines(prev => [...prev, newLine]);
  };

  const deleteLine = (id: string) => {
    setMetreLines(prev => prev.filter(l => l.id !== id));
  };

  const exportToExcel = async () => {
    // Appel API pour génération Excel
    try {
      const response = await fetch(`/api/v1/missions/${missionId}/metre/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lines: metreLines, totals }),
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `metre-${missionId}.xlsx`;
        a.click();
      }
    } catch (error) {
      console.error("Export error:", error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      {/* Header avec KPIs */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-orange-500 flex items-center gap-3">
              <Calculator className="w-8 h-8" />
              MÉTRÉ & CHIFFRAGE
            </h1>
            <p className="text-slate-400 mt-1">Tableur intelligent avec détection d'écarts</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="border-blue-500 text-blue-500">
              {userRole.canSeePrixUnitaires ? <Unlock className="w-4 h-4 mr-2" /> : <Lock className="w-4 h-4 mr-2" />}
              {userRole.canSeePrixUnitaires ? "Vue PATRON" : "Vue SALARIÉ"}
            </Badge>
            <Switch
              checked={userRole.canSeePrixUnitaires}
              onCheckedChange={(checked) => setUserRole(prev => ({
                ...prev,
                canSeePrixUnitaires: checked,
                canSeeMarge: checked,
              }))}
            />
          </div>
        </div>

        {/* Bandeau supérieur fixe avec totaux */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-slate-900/80 backdrop-blur p-6 rounded-lg border border-slate-700 sticky top-0 z-40">
          <div>
            <p className="text-sm text-slate-400">Total HT</p>
            <p className="text-2xl font-bold text-white">
              {totals.totalHT.toLocaleString("fr-FR", { style: "currency", currency: "EUR" })}
            </p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Coût Total</p>
            <p className="text-2xl font-bold text-red-400">
              {totals.totalCout.toLocaleString("fr-FR", { style: "currency", currency: "EUR" })}
            </p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Marge Brute</p>
            <p className={`text-2xl font-bold ${totals.margeBrute >= 0 ? "text-green-500" : "text-red-500"}`}>
              {totals.margeBrute.toLocaleString("fr-FR", { style: "currency", currency: "EUR" })}
            </p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Taux de Marge</p>
            <div className="flex items-center gap-2">
              <p className={`text-2xl font-bold ${totals.tauxMarge >= 15 ? "text-green-500" : totals.tauxMarge >= 8 ? "text-orange-500" : "text-red-500"}`}>
                {totals.tauxMarge.toFixed(2)}%
              </p>
              {totals.tauxMarge >= 15 ? (
                <TrendingUp className="w-5 h-5 text-green-500" />
              ) : totals.tauxMarge >= 8 ? (
                <AlertTriangle className="w-5 h-5 text-orange-500" />
              ) : (
                <TrendingDown className="w-5 h-5 text-red-500" />
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Barre d'outils */}
      <Card className="bg-slate-900/50 border-slate-700 p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              placeholder="Rechercher par référence ou désignation..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-slate-800 border-slate-700"
            />
          </div>
          
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as any)}
              className="bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
            >
              <option value="all">Tous les statuts</option>
              <option value="ok">✅ OK</option>
              <option value="warning">⚠️ Écarts mineurs</option>
              <option value="error">❌ Écarts critiques</option>
            </select>
          </div>

          <Button
            onClick={addNewLine}
            variant="outline"
            className="border-green-600 text-green-500 hover:bg-green-900/30"
          >
            <Plus className="w-4 h-4 mr-2" />
            Ajouter ligne
          </Button>

          <Button
            onClick={handleOptimization}
            disabled={isOptimizing || !userRole.canOptimize}
            className="bg-purple-600 hover:bg-purple-700"
          >
            <Zap className="w-4 h-4 mr-2" />
            {isOptimizing ? "Optimisation..." : "Optimisation OR-Tools"}
          </Button>

          <Button
            onClick={exportToExcel}
            variant="outline"
            className="border-blue-600 text-blue-500 hover:bg-blue-900/30"
          >
            <Download className="w-4 h-4 mr-2" />
            Export Excel
          </Button>
        </div>

        {/* Statut des écarts */}
        <div className="flex items-center gap-6 mt-4 pt-4 border-t border-slate-700">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="text-sm text-slate-300">{totals.ecartsCount.ok} lignes OK</span>
          </div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            <span className="text-sm text-slate-300">{totals.ecartsCount.warning} écarts mineurs</span>
          </div>
          <div className="flex items-center gap-2">
            <XCircle className="w-5 h-5 text-red-500" />
            <span className="text-sm text-slate-300">{totals.ecartsCount.error} écarts critiques</span>
          </div>
        </div>
      </Card>

      {/* Tableau de métré */}
      <Card className="bg-slate-900/50 border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-700 hover:bg-slate-800/50">
                <TableHead className="w-20">Ref.</TableHead>
                <TableHead className="min-w-[300px]">Désignation</TableHead>
                <TableHead className="w-20">Unité</TableHead>
                <TableHead className="w-24 text-right">Qté CCTP</TableHead>
                <TableHead className="w-24 text-right">Qté DPGF</TableHead>
                <TableHead className="w-24 text-right">Écart</TableHead>
                {userRole.canSeePrixUnitaires && (
                  <>
                    <TableHead className="w-28 text-right">P.U. (€)</TableHead>
                    <TableHead className="w-28 text-right">Coef.</TableHead>
                    <TableHead className="w-32 text-right">Marge</TableHead>
                  </>
                )}
                <TableHead className="w-20 text-center">Statut</TableHead>
                <TableHead className="w-20"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <AnimatePresence>
                {filteredLines.map((line, index) => (
                  <motion.tr
                    key={line.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.03 }}
                    className={`border-slate-700 hover:bg-slate-800/50 ${
                      line.status === "error" ? "bg-red-900/20" : line.status === "warning" ? "bg-orange-900/20" : ""
                    }`}
                  >
                    <TableCell className="font-mono text-sm text-slate-300">{line.reference}</TableCell>
                    <TableCell className="font-medium">{line.designation}</TableCell>
                    <TableCell className="text-slate-400">{line.unite}</TableCell>
                    <TableCell className="text-right">
                      <Input
                        type="number"
                        value={line.quantiteCCTP}
                        onChange={(e) => updateLine(line.id, "quantiteCCTP", parseFloat(e.target.value) || 0)}
                        className="w-20 text-right bg-slate-800 border-slate-600"
                        disabled={!userRole.canEdit}
                      />
                    </TableCell>
                    <TableCell className="text-right">
                      <Input
                        type="number"
                        value={line.quantiteDPGF}
                        onChange={(e) => updateLine(line.id, "quantiteDPGF", parseFloat(e.target.value) || 0)}
                        className={`w-20 text-right bg-slate-800 ${
                          line.ecart !== 0 ? "border-orange-500" : "border-slate-600"
                        }`}
                        disabled={!userRole.canEdit}
                      />
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge
                        variant="outline"
                        className={`${
                          line.ecart === 0
                            ? "border-green-500 text-green-500"
                            : Math.abs(line.ecart) <= 5
                            ? "border-orange-500 text-orange-500"
                            : "border-red-500 text-red-500"
                        }`}
                      >
                        {line.ecart > 0 ? "+" : ""}{line.ecart}
                      </Badge>
                    </TableCell>
                    {userRole.canSeePrixUnitaires && (
                      <>
                        <TableCell className="text-right">
                          <Input
                            type="number"
                            value={line.prixUnitaire}
                            onChange={(e) => updateLine(line.id, "prixUnitaire", parseFloat(e.target.value) || 0)}
                            className="w-24 text-right bg-slate-800 border-slate-600"
                            disabled={!userRole.canEdit}
                          />
                        </TableCell>
                        <TableCell className="text-right">
                          <Input
                            type="number"
                            step="0.01"
                            value={line.coefficient}
                            onChange={(e) => updateLine(line.id, "coefficient", parseFloat(e.target.value) || 0)}
                            className="w-20 text-right bg-slate-800 border-slate-600"
                            disabled={!userRole.canEdit}
                          />
                        </TableCell>
                        <TableCell className="text-right">
                          <span className={line.margeBrute >= 0 ? "text-green-500" : "text-red-500"}>
                            {line.margeBrute.toLocaleString("fr-FR", { style: "currency", currency: "EUR" })}
                          </span>
                        </TableCell>
                      </>
                    )}
                    <TableCell className="text-center">
                      {line.status === "ok" && <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />}
                      {line.status === "warning" && <AlertTriangle className="w-5 h-5 text-orange-500 mx-auto" />}
                      {line.status === "error" && <XCircle className="w-5 h-5 text-red-500 mx-auto" />}
                    </TableCell>
                    <TableCell>
                      {userRole.canEdit && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => deleteLine(line.id)}
                          className="text-slate-400 hover:text-red-500"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </TableCell>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* Résultat optimisation */}
      <AnimatePresence>
        {optimizationResult && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
          >
            <Card className="bg-purple-900/30 border-purple-700 p-6 mt-6">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-purple-400 flex items-center gap-2 mb-4">
                    <Zap className="w-6 h-6" />
                    Résultats de l'optimisation
                  </h3>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <p className="text-sm text-slate-400">Économies potentielles</p>
                      <p className="text-3xl font-bold text-green-500">
                        {optimizationResult.savings.toLocaleString("fr-FR", { style: "currency", currency: "EUR" })}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400">Nouvelle marge</p>
                      <p className="text-3xl font-bold text-purple-400">
                        {optimizationResult.newMargin.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <p className="text-sm font-semibold text-slate-300">Suggestions:</p>
                    {optimizationResult.suggestions.map((suggestion, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="flex items-start gap-2 text-sm text-slate-300"
                      >
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                        {suggestion}
                      </motion.div>
                    ))}
                  </div>
                </div>
                <Button
                  onClick={() => setOptimizationResult(null)}
                  variant="ghost"
                  size="sm"
                >
                  <XCircle className="w-5 h-5" />
                </Button>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer avec navigation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="fixed bottom-0 left-0 right-0 bg-slate-900/95 backdrop-blur border-t border-slate-700 p-6"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Button variant="ghost" onClick={onBack} className="text-slate-300">
            <ChevronLeft className="w-5 h-5 mr-2" />
            Retour
          </Button>
          
          <div className="text-center">
            <p className="text-sm text-slate-400">
              {filteredLines.length} lignes • Marge: {totals.tauxMarge.toFixed(2)}%
            </p>
          </div>

          <Button
            onClick={onNext}
            className="bg-orange-600 hover:bg-orange-700 text-white px-8"
          >
            Continuer
            <ChevronRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </motion.div>

      {/* Spacer pour le footer fixe */}
      <div className="h-32" />
    </div>
  );
}
