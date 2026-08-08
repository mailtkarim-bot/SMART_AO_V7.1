"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Edit3,
  Save,
  Download,
  Upload,
  ChevronLeft,
  ChevronRight,
  Search,
  Filter,
  Sparkles,
  Copy,
  RefreshCw,
  Eye,
  FileCheck,
  ClipboardList,
  HardHat,
  Scale,
  Euro
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Types
interface DocumentItem {
  id: string;
  name: string;
  category: "admin" | "tech";
  status: "generated" | "pending" | "missing";
  content?: string;
  lastModified?: Date;
  required: boolean;
  aiSuggestions?: string[];
}

interface Props {
  onNext: () => void;
  onBack: () => void;
  missionId?: string;
}

export default function DocumentsPipeline({ onNext, onBack, missionId }: Props) {
  const [activeTab, setActiveTab] = useState<"admin" | "tech">("admin");
  const [searchTerm, setSearchTerm] = useState("");
  const [editingDoc, setEditingDoc] = useState<DocumentItem | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [boostMode, setBoostMode] = useState(false);

  // Liste complète des 45 documents (simulée)
  const [documents, setDocuments] = useState<DocumentItem[]>([
    // Documents Admin (15)
    { id: "A01", name: "Acte d'engagement (ACT)", category: "admin", status: "generated", required: true },
    { id: "A02", name: "Déclaration sur l'honneur DC1", category: "admin", status: "generated", required: true },
    { id: "A03", name: "Déclaration candidat DC2", category: "admin", status: "pending", required: true },
    { id: "A04", name: "Attestations fiscales URSSAF", category: "admin", status: "missing", required: true },
    { id: "A05", name: "Attestation assurance décennale", category: "admin", status: "generated", required: true },
    { id: "A06", name: "RIB entreprise", category: "admin", status: "generated", required: false },
    { id: "A07", name: "Kbis de moins de 3 mois", category: "admin", status: "pending", required: true },
    { id: "A08", name: "Procuration signataire", category: "admin", status: "missing", required: false },
    { id: "A09", name: "CV dirigeant", category: "admin", status: "generated", required: false },
    { id: "A10", name: "Références similaires (3 min.)", category: "admin", status: "pending", required: true },
    { id: "A11", name: "Chiffre d'affaires 3 ans", category: "admin", status: "generated", required: false },
    { id: "A12", name: "Effectifs entreprise", category: "admin", status: "generated", required: false },
    { id: "A13", name: "Qualifications QUALIBAT", category: "admin", status: "missing", required: false },
    { id: "A14", name: "Politique RSE", category: "admin", status: "pending", required: false },
    { id: "A15", name: "Lettre de candidature", category: "admin", status: "generated", required: true },
    
    // Documents Techniques (30)
    { id: "T01", name: "Mémoire technique général", category: "tech", status: "pending", required: true, aiSuggestions: ["Paragraphe type: méthodologie coffrage", "Paragraphe type: planning prévisionnel", "Paragraphe type: moyens humains"] },
    { id: "T02", name: "Note méthodologique terrassement", category: "tech", status: "generated", required: true },
    { id: "T03", name: "Note méthodologique fondations", category: "tech", status: "pending", required: true },
    { id: "T04", name: "Note méthodologique maçonnerie", category: "tech", status: "generated", required: true },
    { id: "T05", name: "Note méthodologique couverture", category: "tech", status: "missing", required: true },
    { id: "T06", name: "Planning prévisionnel détaillé", category: "tech", status: "pending", required: true },
    { id: "T07", name: "Organigramme chantier", category: "tech", status: "generated", required: true },
    { id: "T08", name: "CV chef de chantier", category: "tech", status: "generated", required: false },
    { id: "T09", name: "CV conducteur de travaux", category: "tech", status: "generated", required: false },
    { id: "T10", name: "Moyens matériels affectés", category: "tech", status: "pending", required: true },
    { id: "T11", name: "Plan d'installation de chantier", category: "tech", status: "missing", required: true },
    { id: "T12", name: "Schéma sécurité (PPSPS)", category: "tech", status: "pending", required: true },
    { id: "T13", name: "Gestion des déchets", category: "tech", status: "generated", required: false },
    { id: "T14", name: "Approvisionnement matériaux", category: "tech", status: "pending", required: true },
    { id: "T15", name: "Contrôle qualité procédé", category: "tech", status: "missing", required: false },
    { id: "T16", name: "Fiches techniques béton", category: "tech", status: "generated", required: false },
    { id: "T17", name: "Fiches techniques acier", category: "tech", status: "generated", required: false },
    { id: "T18", name: "Détails d'exécution plans", category: "tech", status: "pending", required: true },
    { id: "T19", name: "Notes de calculs structure", category: "tech", status: "missing", required: false },
    { id: "T20", name: "Étude thermique réglementaire", category: "tech", status: "pending", required: true },
    { id: "T21", name: "Acoustique bâtiment", category: "tech", status: "missing", required: false },
    { id: "T22", name: "Accessibilité PMR", category: "tech", status: "generated", required: true },
    { id: "T23", name: "Coordination SPS", category: "tech", status: "pending", required: true },
    { id: "T24", name: "Protocole essais béton", category: "tech", status: "generated", required: false },
    { id: "T25", name: "Rapports contrôles techniques", category: "tech", status: "missing", required: false },
    { id: "T26", name: "Garantie parfait achèvement", category: "tech", status: "generated", required: true },
    { id: "T27", name: "Notice maintenance équipements", category: "tech", status: "pending", required: false },
    { id: "T28", name: "DOE liste documents", category: "tech", status: "pending", required: true },
    { id: "T29", name: "Calendrier exécution travaux", category: "tech", status: "generated", required: true },
    { id: "T30", name: "Variantes techniques proposées", category: "tech", status: "missing", required: false },
  ]);

  // Statistiques
  const stats = {
    admin: {
      total: documents.filter(d => d.category === "admin").length,
      generated: documents.filter(d => d.category === "admin" && d.status === "generated").length,
      pending: documents.filter(d => d.category === "admin" && d.status === "pending").length,
      missing: documents.filter(d => d.category === "admin" && d.status === "missing").length,
    },
    tech: {
      total: documents.filter(d => d.category === "tech").length,
      generated: documents.filter(d => d.category === "tech" && d.status === "generated").length,
      pending: documents.filter(d => d.category === "tech" && d.status === "pending").length,
      missing: documents.filter(d => d.category === "tech" && d.status === "missing").length,
    },
  };

  const filteredDocs = documents.filter(doc => {
    const matchesTab = doc.category === activeTab;
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesTab && matchesSearch;
  });

  const canProceed = documents.filter(d => d.required && d.status === "missing").length === 0;

  // Génération automatique d'un document
  const generateDocument = async (docId: string) => {
    setIsGenerating(true);
    try {
      const response = await fetch(`/api/v1/missions/${missionId}/documents/${docId}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ boostMode }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setDocuments(prev => prev.map(d => 
          d.id === docId ? { ...d, status: "generated", content: data.content, lastModified: new Date() } : d
        ));
      }
    } catch (error) {
      console.error("Generation error:", error);
      // Fallback simulation
      setTimeout(() => {
        setDocuments(prev => prev.map(d => 
          d.id === docId ? { ...d, status: "generated", lastModified: new Date() } : d
        ));
        setIsGenerating(false);
      }, 1500);
    }
    setIsGenerating(false);
  };

  // Sauvegarde édition inline
  const saveDocument = async (doc: DocumentItem) => {
    try {
      const response = await fetch(`/api/v1/missions/${missionId}/documents/${doc.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: doc.content }),
      });
      
      if (response.ok) {
        setDocuments(prev => prev.map(d => d.id === doc.id ? { ...d, lastModified: new Date() } : d));
        setEditingDoc(null);
      }
    } catch (error) {
      console.error("Save error:", error);
      setDocuments(prev => prev.map(d => d.id === doc.id ? { ...d, status: "generated" } : d));
      setEditingDoc(null);
    }
  };

  // Mode Mémoire Technique Booster
  const applyAISuggestion = (docId: string, suggestion: string) => {
    setDocuments(prev => prev.map(d => {
      if (d.id !== docId) return d;
      return {
        ...d,
        content: (d.content || "") + "\n\n" + suggestion,
      };
    }));
  };

  const exportAll = async () => {
    try {
      const response = await fetch(`/api/v1/missions/${missionId}/documents/export-all`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category: activeTab }),
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `documents-${activeTab}-${missionId}.zip`;
        a.click();
      }
    } catch (error) {
      console.error("Export error:", error);
    }
  };

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
              <FileText className="w-8 h-8" />
              DOCUMENTS & PIÈCES ÉCRITES
            </h1>
            <p className="text-slate-400 mt-1">Pipeline de génération automatisée</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="border-green-500 text-green-500">
              <CheckCircle className="w-4 h-4 mr-2" />
              {documents.filter(d => d.status === "generated").length}/{documents.length} générés
            </Badge>
            <Button
              onClick={exportAll}
              variant="outline"
              className="border-blue-600 text-blue-500 hover:bg-blue-900/30"
            >
              <Download className="w-4 h-4 mr-2" />
              Exporter tout
            </Button>
          </div>
        </div>

        {/* Progression globale */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <Card className="bg-slate-900/50 border-slate-700 p-4">
            <div className="flex items-center gap-3 mb-2">
              <ClipboardList className="w-5 h-5 text-blue-500" />
              <span className="font-semibold">Documents Administratifs</span>
            </div>
            <Progress 
              value={(stats.admin.generated / stats.admin.total) * 100} 
              className="h-2 bg-slate-800" 
            />
            <div className="flex justify-between mt-2 text-xs text-slate-400">
              <span>{stats.admin.generated} générés</span>
              <span>{stats.admin.pending} en attente</span>
              <span>{stats.admin.missing} manquants</span>
            </div>
          </Card>
          
          <Card className="bg-slate-900/50 border-slate-700 p-4">
            <div className="flex items-center gap-3 mb-2">
              <HardHat className="w-5 h-5 text-orange-500" />
              <span className="font-semibold">Documents Techniques</span>
            </div>
            <Progress 
              value={(stats.tech.generated / stats.tech.total) * 100} 
              className="h-2 bg-slate-800" 
            />
            <div className="flex justify-between mt-2 text-xs text-slate-400">
              <span>{stats.tech.generated} générés</span>
              <span>{stats.tech.pending} en attente</span>
              <span>{stats.tech.missing} manquants</span>
            </div>
          </Card>
        </div>

        {/* Toggle Boost Mode */}
        <div className="flex items-center justify-between bg-purple-900/20 border border-purple-700 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-purple-400" />
            <div>
              <p className="font-semibold text-purple-300">Mode Mémoire Technique Booster</p>
              <p className="text-sm text-slate-400">L'IA suggère des paragraphes types basés sur votre historique</p>
            </div>
          </div>
          <Button
            variant={boostMode ? "default" : "outline"}
            onClick={() => setBoostMode(!boostMode)}
            className={boostMode ? "bg-purple-600 hover:bg-purple-700" : "border-purple-600 text-purple-500"}
          >
            {boostMode ? "Activé" : "Activer"}
          </Button>
        </div>
      </motion.div>

      {/* Onglets Admin/Tech */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "admin" | "tech")} className="mb-6">
        <TabsList className="bg-slate-900 border border-slate-700">
          <TabsTrigger value="admin" className="data-[state=active]:bg-orange-600">
            <Scale className="w-4 h-4 mr-2" />
            Administratif ({stats.admin.generated}/{stats.admin.total})
          </TabsTrigger>
          <TabsTrigger value="tech" className="data-[state=active]:bg-orange-600">
            <HardHat className="w-4 h-4 mr-2" />
            Technique ({stats.tech.generated}/{stats.tech.total})
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Barre de recherche et filtres */}
      <Card className="bg-slate-900/50 border-slate-700 p-4 mb-6">
        <div className="flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              placeholder="Rechercher un document..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-slate-800 border-slate-700"
            />
          </div>
          <Button variant="outline" className="border-slate-600">
            <Filter className="w-4 h-4 mr-2" />
            Filtrer par statut
          </Button>
        </div>
      </Card>

      {/* Liste des documents */}
      <div className="space-y-3">
        <AnimatePresence>
          {filteredDocs.map((doc, index) => (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ delay: index * 0.02 }}
            >
              <Card className={`bg-slate-900/50 border-slate-700 p-4 hover:border-orange-500 transition-colors ${
                doc.required && doc.status === "missing" ? "border-l-4 border-l-red-500" : ""
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      doc.status === "generated" ? "bg-green-900/30" :
                      doc.status === "pending" ? "bg-orange-900/30" : "bg-red-900/30"
                    }`}>
                      {doc.status === "generated" ? (
                        <CheckCircle className="w-6 h-6 text-green-500" />
                      ) : doc.status === "pending" ? (
                        <RefreshCw className="w-6 h-6 text-orange-500" />
                      ) : (
                        <XCircle className="w-6 h-6 text-red-500" />
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{doc.name}</h3>
                        {doc.required && (
                          <Badge variant="outline" className="border-red-500 text-red-500 text-xs">
                            Obligatoire
                          </Badge>
                        )}
                        {doc.aiSuggestions && boostMode && (
                          <Badge className="bg-purple-600 text-xs">
                            <Sparkles className="w-3 h-3 mr-1" />
                            IA Ready
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-slate-400">
                        {doc.lastModified 
                          ? `Modifié le ${doc.lastModified.toLocaleDateString("fr-FR")}`
                          : "Jamais modifié"}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {doc.status === "missing" && (
                      <Button
                        size="sm"
                        onClick={() => generateDocument(doc.id)}
                        disabled={isGenerating}
                        className="bg-orange-600 hover:bg-orange-700"
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        Générer
                      </Button>
                    )}
                    
                    {doc.status === "pending" && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditingDoc(doc)}
                          className="border-blue-600 text-blue-500"
                        >
                          <Edit3 className="w-4 h-4 mr-2" />
                          Éditer
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => generateDocument(doc.id)}
                          disabled={isGenerating}
                          variant="outline"
                          className="border-green-600 text-green-500"
                        >
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Valider
                        </Button>
                      </>
                    )}

                    {doc.status === "generated" && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditingDoc(doc)}
                          className="border-slate-600 text-slate-400"
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          Voir
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-blue-600 text-blue-500"
                        >
                          <Download className="w-4 h-4 mr-2" />
                          PDF
                        </Button>
                      </>
                    )}
                  </div>
                </div>

                {/* Suggestions IA */}
                {boostMode && doc.aiSuggestions && doc.status !== "missing" && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="mt-4 pt-4 border-t border-slate-700"
                  >
                    <p className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
                      <Sparkles className="w-4 h-4" />
                      Suggestions de l'IA:
                    </p>
                    <div className="space-y-2">
                      {doc.aiSuggestions.map((suggestion, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1 }}
                          className="flex items-start justify-between bg-purple-900/20 p-3 rounded-lg"
                        >
                          <p className="text-sm text-slate-300">{suggestion}</p>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => applyAISuggestion(doc.id, suggestion)}
                            className="text-purple-400 hover:text-purple-300"
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Modal d'édition */}
      <Dialog open={!!editingDoc} onOpenChange={() => setEditingDoc(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto bg-slate-900 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-xl flex items-center gap-2">
              <Edit3 className="w-5 h-5 text-orange-500" />
              Édition: {editingDoc?.name}
            </DialogTitle>
          </DialogHeader>
          
          {editingDoc && (
            <div className="space-y-4">
              <Textarea
                value={editingDoc.content || ""}
                onChange={(e) => setEditingDoc({ ...editingDoc, content: e.target.value })}
                className="min-h-[400px] bg-slate-800 border-slate-700 font-mono text-sm"
                placeholder="Contenu du document..."
              />
              
              <div className="flex justify-end gap-3">
                <Button variant="ghost" onClick={() => setEditingDoc(null)}>
                  Annuler
                </Button>
                <Button
                  onClick={() => saveDocument(editingDoc)}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Enregistrer
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

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
              {documents.filter(d => d.required && d.status === "missing").length} documents obligatoires manquants
            </p>
            {!canProceed && (
              <Badge variant="destructive" className="mt-1">
                Blocage: complétez les documents requis
              </Badge>
            )}
          </div>

          <Button
            onClick={onNext}
            disabled={!canProceed}
            className={`px-8 ${
              canProceed 
                ? "bg-orange-600 hover:bg-orange-700 text-white" 
                : "bg-slate-700 text-slate-400 cursor-not-allowed"
            }`}
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
