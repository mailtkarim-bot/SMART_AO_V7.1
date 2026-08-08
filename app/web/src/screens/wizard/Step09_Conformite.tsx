"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileCheck,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Package,
  Download,
  ChevronLeft,
  ChevronRight,
  Shield,
  Eye,
  Lock,
  Unlock,
  Layers,
  FolderOpen,
  Archive
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// Types
interface ZipFile {
  id: string;
  name: string;
  category: "admin" | "tech" | "price";
  size: string;
  status: "included" | "missing" | "invalid";
  critical: boolean;
}

interface ConformityCheck {
  id: string;
  label: string;
  passed: boolean;
  critical: boolean;
  details?: string;
}

interface Props {
  onNext: () => void;
  onBack: () => void;
  missionId?: string;
}

export default function ConformiteZip({ onNext, onBack, missionId }: Props) {
  const [selectedCategories, setSelectedCategories] = useState({
    admin: true,
    tech: true,
    price: true,
  });

  const [zipFiles, setZipFiles] = useState<ZipFile[]>([
    // Admin
    { id: "A01", name: "01_Actes_engagement.pdf", category: "admin", size: "245 KB", status: "included", critical: true },
    { id: "A02", name: "02_Declarations_DC1_DC2.pdf", category: "admin", size: "189 KB", status: "included", critical: true },
    { id: "A03", name: "03_Attestations_fiscales.pdf", category: "admin", size: "156 KB", status: "included", critical: true },
    { id: "A04", name: "04_Assurance_decennale.pdf", category: "admin", size: "312 KB", status: "included", critical: true },
    { id: "A05", name: "05_Kbis.pdf", category: "admin", size: "98 KB", status: "included", critical: true },
    { id: "A06", name: "06_RIB_entreprise.pdf", category: "admin", size: "45 KB", status: "included", critical: false },
    { id: "A07", name: "07_CV_dirigeant.pdf", category: "admin", size: "178 KB", status: "included", critical: false },
    { id: "A08", name: "08_References_similaires.pdf", category: "admin", size: "567 KB", status: "included", critical: true },
    
    // Tech
    { id: "T01", name: "09_Memoire_technique_general.pdf", category: "tech", size: "1.2 MB", status: "included", critical: true },
    { id: "T02", name: "10_Notes_methodologiques.pdf", category: "tech", size: "2.8 MB", status: "included", critical: true },
    { id: "T03", name: "11_Planning_previsionnel.pdf", category: "tech", size: "456 KB", status: "included", critical: true },
    { id: "T04", name: "12_Organigramme_chantier.pdf", category: "tech", size: "234 KB", status: "included", critical: true },
    { id: "T05", name: "13_Plan_installation_chantier.pdf", category: "tech", size: "1.8 MB", status: "included", critical: true },
    { id: "T06", name: "14_PPSPS_securite.pdf", category: "tech", size: "678 KB", status: "included", critical: true },
    { id: "T07", name: "15_Fiches_techniques_materiaux.pdf", category: "tech", size: "3.4 MB", status: "included", critical: false },
    { id: "T08", name: "16_Etude_thermique.pdf", category: "tech", size: "890 KB", status: "included", critical: true },
    { id: "T09", name: "17_Accessibilite_PMR.pdf", category: "tech", size: "445 KB", status: "included", critical: true },
    { id: "T10", name: "18_Garantie_parfait_achevement.pdf", category: "tech", size: "123 KB", status: "included", critical: true },
    
    // Price
    { id: "P01", name: "19_DPGF_rempli.xlsx", category: "price", size: "567 KB", status: "included", critical: true },
    { id: "P02", name: "20_Detail_quantitatifs.pdf", category: "price", size: "789 KB", status: "included", critical: true },
    { id: "P03", name: "20_Bordereau_prix_unitaires.pdf", category: "price", size: "456 KB", status: "included", critical: true },
    { id: "P04", name: "21_Devise_estimatif.pdf", category: "price", size: "234 KB", status: "included", critical: false },
  ]);

  const [conformityChecks, setConformityChecks] = useState<ConformityCheck[]>([
    { id: "C01", label: "Tous les documents obligatoires présents", passed: true, critical: true },
    { id: "C02", label: "Formats de fichiers conformes (PDF/A, XLSX)", passed: true, critical: true },
    { id: "C03", label: "Taille totale < 50 MB (limite plateforme)", passed: true, critical: true, details: "15.2 MB / 50 MB" },
    { id: "C04", label: "Nommage des fichiers respecté", passed: true, critical: false },
    { id: "C05", label: "Signatures électroniques valides", passed: true, critical: true },
    { id: "C06", label: "Horodatage des documents", passed: true, critical: false },
    { id: "C07", label: "Absence de macros dans les Excel", passed: true, critical: true },
    { id: "C08", label: "Résolution images > 150 DPI", passed: true, critical: false },
    { id: "C09", label: "Compatibilité Chorus Pro vérifiée", passed: true, critical: true },
    { id: "C10", label: "Métadonnées nettoyées (RGPD)", passed: true, critical: false },
  ]);

  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generated, setGenerated] = useState(false);

  const allCriticalPassed = conformityChecks.filter(c => c.critical && !c.passed).length === 0;
  const allCriticalFilesIncluded = zipFiles.filter(f => f.critical && f.status === "missing").length === 0;
  const canGenerateZip = allCriticalPassed && allCriticalFilesIncluded;

  const selectedFilesCount = zipFiles.filter(f => 
    selectedCategories[f.category] && f.status === "included"
  ).length;

  const totalSize = zipFiles
    .filter(f => selectedCategories[f.category] && f.status === "included")
    .reduce((acc, f) => {
      const sizeMatch = f.size.match(/([\d.]+)\s*(KB|MB)/);
      if (!sizeMatch) return acc;
      const value = parseFloat(sizeMatch[1]);
      const unit = sizeMatch[2];
      return acc + (unit === "MB" ? value * 1024 : value);
    }, 0);

  const handleGenerateZip = async () => {
    if (!canGenerateZip) return;
    
    setIsGenerating(true);
    setGenerationProgress(0);
    
    try {
      // Simulation progression
      const interval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 300);

      const response = await fetch(`/api/v1/missions/${missionId}/generate-zip`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          categories: Object.entries(selectedCategories)
            .filter(([_, v]) => v)
            .map(([k]) => k),
          files: zipFiles.filter(f => selectedCategories[f.category] && f.status === "included")
            .map(f => f.id),
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `offre-${missionId || "complete"}.zip`;
        a.click();
        setGenerated(true);
      }
    } catch (error) {
      console.error("ZIP generation error:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const simulatePlatformView = () => {
    // Mock de ce que la plateforme verra
    return {
      submitterName: "Votre Entreprise SAS",
      submissionDate: new Date().toISOString(),
      offerReference: `OFFRE-${missionId || "2024-001"}`,
      totalFiles: selectedFilesCount,
      totalPrice: "125,450.00 EUR",
      validityDays: 90,
      executionDelay: "6 mois",
    };
  };

  const platformView = simulatePlatformView();

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-orange-500 flex items-center gap-3">
              <FileCheck className="w-8 h-8" />
              CONFORMITÉ & ZIP FINAL
            </h1>
            <p className="text-slate-400 mt-1">Contrôle ultime avant dépôt</p>
          </div>
          <Badge variant="outline" className={`border-2 ${
            canGenerateZip ? "border-green-500 text-green-500" : "border-red-500 text-red-500"
          }`}>
            {canGenerateZip ? (
              <>
                <CheckCircle className="w-4 h-4 mr-2" />
                PRÊT À GÉNÉRER
              </>
            ) : (
              <>
                <AlertTriangle className="w-4 h-4 mr-2" />
                BLOQUÉ: {conformityChecks.filter(c => c.critical && !c.passed).length} checks critiques
              </>
            )}
          </Badge>
        </div>

        {/* Sélecteur de catégories ZIP */}
        <Card className="bg-slate-900/50 border-slate-700 p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Layers className="w-5 h-5 text-orange-500" />
            Sélectionner les catégories à inclure dans le ZIP
          </h3>
          <div className="grid grid-cols-3 gap-4">
            {/* Admin Column */}
            <div
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                selectedCategories.admin
                  ? "border-blue-500 bg-blue-900/20"
                  : "border-slate-700 bg-slate-800/50 hover:border-slate-600"
              }`}
              onClick={() => setSelectedCategories(prev => ({ ...prev, admin: !prev.admin }))}
            >
              <div className="flex items-center justify-between mb-3">
                <Shield className={`w-8 h-8 ${selectedCategories.admin ? "text-blue-500" : "text-slate-500"}`} />
                <Switch checked={selectedCategories.admin} onClick={(e) => e.stopPropagation()} />
              </div>
              <h4 className="font-semibold mb-1">Documents Administratifs</h4>
              <p className="text-sm text-slate-400">
                {zipFiles.filter(f => f.category === "admin" && selectedCategories.admin).length} fichiers
              </p>
            </div>

            {/* Tech Column */}
            <div
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                selectedCategories.tech
                  ? "border-orange-500 bg-orange-900/20"
                  : "border-slate-700 bg-slate-800/50 hover:border-slate-600"
              }`}
              onClick={() => setSelectedCategories(prev => ({ ...prev, tech: !prev.tech }))}
            >
              <div className="flex items-center justify-between mb-3">
                <FolderOpen className={`w-8 h-8 ${selectedCategories.tech ? "text-orange-500" : "text-slate-500"}`} />
                <Switch checked={selectedCategories.tech} onClick={(e) => e.stopPropagation()} />
              </div>
              <h4 className="font-semibold mb-1">Documents Techniques</h4>
              <p className="text-sm text-slate-400">
                {zipFiles.filter(f => f.category === "tech" && selectedCategories.tech).length} fichiers
              </p>
            </div>

            {/* Price Column */}
            <div
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                selectedCategories.price
                  ? "border-green-500 bg-green-900/20"
                  : "border-slate-700 bg-slate-800/50 hover:border-slate-600"
              }`}
              onClick={() => setSelectedCategories(prev => ({ ...prev, price: !prev.price }))}
            >
              <div className="flex items-center justify-between mb-3">
                <Archive className={`w-8 h-8 ${selectedCategories.price ? "text-green-500" : "text-slate-500"}`} />
                <Switch checked={selectedCategories.price} onClick={(e) => e.stopPropagation()} />
              </div>
              <h4 className="font-semibold mb-1">Documents Prix</h4>
              <p className="text-sm text-slate-400">
                {zipFiles.filter(f => f.category === "price" && selectedCategories.price).length} fichiers
              </p>
            </div>
          </div>

          {/* Résumé sélection */}
          <div className="mt-6 pt-6 border-t border-slate-700 flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div>
                <p className="text-sm text-slate-400">Fichiers sélectionnés</p>
                <p className="text-2xl font-bold">{selectedFilesCount}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Taille totale estimée</p>
                <p className="text-2xl font-bold">
                  {totalSize >= 1024 ? `${(totalSize / 1024).toFixed(1)} MB` : `${totalSize.toFixed(0)} KB`}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Limite plateforme</p>
                <p className="text-2xl font-bold text-slate-500">50 MB</p>
              </div>
            </div>
            {totalSize > 50 * 1024 && (
              <Badge variant="destructive">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Dépassement limite!
              </Badge>
            )}
          </div>
        </Card>
      </motion.div>

      {/* Checklist de conformité */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Tableau des fichiers */}
        <Card className="bg-slate-900/50 border-slate-700 overflow-hidden">
          <div className="p-4 border-b border-slate-700">
            <h3 className="font-semibold flex items-center gap-2">
              <Package className="w-5 h-5 text-orange-500" />
              Fichiers inclus ({selectedFilesCount})
            </h3>
          </div>
          <div className="overflow-y-auto max-h-[400px]">
            <Table>
              <TableHeader>
                <TableRow className="border-slate-700">
                  <TableHead>Fichier</TableHead>
                  <TableHead>Catégorie</TableHead>
                  <TableHead>Taille</TableHead>
                  <TableHead className="text-right">Statut</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {zipFiles
                  .filter(f => selectedCategories[f.category])
                  .map((file) => (
                    <TableRow key={file.id} className="border-slate-700">
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          {file.critical && <Lock className="w-4 h-4 text-red-500" />}
                          {file.name}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={`
                          ${file.category === "admin" ? "border-blue-500 text-blue-500" : ""}
                          ${file.category === "tech" ? "border-orange-500 text-orange-500" : ""}
                          ${file.category === "price" ? "border-green-500 text-green-500" : ""}
                        `}>
                          {file.category.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-slate-400">{file.size}</TableCell>
                      <TableCell className="text-right">
                        {file.status === "included" && (
                          <CheckCircle className="w-5 h-5 text-green-500 inline" />
                        )}
                        {file.status === "missing" && (
                          <XCircle className="w-5 h-5 text-red-500 inline" />
                        )}
                        {file.status === "invalid" && (
                          <AlertTriangle className="w-5 h-5 text-orange-500 inline" />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* Checklist validation */}
        <Card className="bg-slate-900/50 border-slate-700">
          <div className="p-4 border-b border-slate-700">
            <h3 className="font-semibold flex items-center gap-2">
              <Shield className="w-5 h-5 text-green-500" />
              Validation automatique
            </h3>
          </div>
          <div className="space-y-3 p-4 max-h-[400px] overflow-y-auto">
            {conformityChecks.map((check) => (
              <motion.div
                key={check.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`flex items-start gap-3 p-3 rounded-lg ${
                  check.passed
                    ? "bg-green-900/20 border border-green-700"
                    : "bg-red-900/20 border border-red-700"
                }`}
              >
                {check.passed ? (
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500 mt-0.5" />
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className={check.passed ? "text-green-300" : "text-red-300"}>
                      {check.label}
                    </span>
                    {check.critical && (
                      <Badge variant="outline" className="border-red-500 text-red-500 text-xs">
                        Critique
                      </Badge>
                    )}
                  </div>
                  {check.details && (
                    <p className="text-xs text-slate-400 mt-1">{check.details}</p>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      </div>

      {/* Simulation vue plateforme */}
      <Card className="bg-slate-900/50 border-slate-700 p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Eye className="w-5 h-5 text-blue-500" />
          Simulation: Vue de la plateforme (Chorus Pro)
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 bg-slate-800/50 p-6 rounded-lg">
          <div>
            <p className="text-sm text-slate-400">Soumis par</p>
            <p className="font-semibold">{platformView.submitterName}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Référence offre</p>
            <p className="font-mono text-orange-500">{platformView.offerReference}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Prix HT</p>
            <p className="text-xl font-bold text-green-500">{platformView.totalPrice}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Délai exécution</p>
            <p className="font-semibold">{platformView.executionDelay}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Validité offre</p>
            <p className="font-semibold">{platformView.validityDays} jours</p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Nombre de fichiers</p>
            <p className="font-semibold">{platformView.totalFiles}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Date soumission</p>
            <p className="text-sm">{new Date(platformView.submissionDate).toLocaleDateString("fr-FR")}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Statut simulation</p>
            <Badge className="bg-green-600">
              <CheckCircle className="w-3 h-3 mr-1" />
              Compatible
            </Badge>
          </div>
        </div>
      </Card>

      {/* Progression génération */}
      <AnimatePresence>
        {isGenerating && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card className="bg-purple-900/30 border-purple-700 p-6">
              <div className="flex items-center gap-4 mb-4">
                <Archive className="w-8 h-8 text-purple-400 animate-pulse" />
                <div className="flex-1">
                  <p className="font-semibold text-purple-300">Génération du ZIP en cours...</p>
                  <p className="text-sm text-slate-400">Compression et cryptage des fichiers</p>
                </div>
                <p className="text-2xl font-bold text-purple-400">{generationProgress}%</p>
              </div>
              <Progress value={generationProgress} className="h-3 bg-slate-800" />
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
              {selectedFilesCount} fichiers • {(totalSize / 1024).toFixed(1)} MB
            </p>
            {!canGenerateZip && (
              <Badge variant="destructive" className="mt-1">
                Résolvez les blocages avant de continuer
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-4">
            <Button
              onClick={handleGenerateZip}
              disabled={!canGenerateZip || isGenerating}
              className={`px-6 ${
                canGenerateZip && !isGenerating
                  ? "bg-green-600 hover:bg-green-700 text-white"
                  : "bg-slate-700 text-slate-400 cursor-not-allowed"
              }`}
            >
              <Download className="w-5 h-5 mr-2" />
              {isGenerating ? "Génération..." : "Générer ZIP"}
            </Button>
            
            <Button
              onClick={onNext}
              disabled={!generated}
              className={`px-8 ${
                generated
                  ? "bg-orange-600 hover:bg-orange-700 text-white"
                  : "bg-slate-700 text-slate-400 cursor-not-allowed"
              }`}
            >
              Continuer vers dépôt
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Spacer pour le footer fixe */}
      <div className="h-32" />
    </div>
  );
}
