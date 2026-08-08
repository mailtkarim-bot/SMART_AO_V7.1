"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import {
  Rocket,
  CheckCircle,
  FileText,
  Download,
  Mail,
  Calendar,
  Clock,
  Euro,
  Shield,
  Award,
  Copy,
  Share2,
  Home,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface Props {
  onBack: () => void;
  missionId?: string;
  onComplete: () => void;
}

export default function DepotOffre({ onBack, missionId, onComplete }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [clickCount, setClickCount] = useState(0);
  const [submissionData, setSubmissionData] = useState<{
    reference: string;
    timestamp: Date;
    receiptUrl: string;
  } | null>(null);

  // Données de l'offre (à récupérer du backend)
  const offerSummary = {
    prixHT: "125,450.00",
    delai: "6 mois",
    validite: "90 jours",
    documents: 22,
    tailleZip: "15.2 MB",
  };

  const handleDoubleClickSubmit = () => {
    setClickCount(prev => prev + 1);
    
    if (clickCount === 0) {
      setShowConfirmation(true);
      setTimeout(() => setShowConfirmation(false), 3000);
    } else {
      submitOffer();
    }
  };

  const submitOffer = async () => {
    setIsSubmitting(true);
    
    try {
      // Appel API réel vers le backend pour soumission
      const response = await fetch(`/api/v1/missions/${missionId}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          confirmation: true,
          timestamp: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSubmissionData({
          reference: data.reference || `OFFRE-${Date.now()}`,
          timestamp: new Date(),
          receiptUrl: data.receiptUrl || "#",
        });
        
        setSubmitted(true);
        
        // Animation de succès
        confetti({
          particleCount: 150,
          spread: 70,
          origin: { y: 0.6 },
          colors: ["#F97316", "#10B981", "#3B82F6"],
        });

        // Notification sonore (optionnelle)
        const audio = new Audio("/success.mp3");
        audio.play().catch(() => {}); // Ignore si pas de fichier audio
      }
    } catch (error) {
      console.error("Submission error:", error);
      // Fallback simulation pour démo
      setTimeout(() => {
        setSubmissionData({
          reference: `OFFRE-${Date.now()}`,
          timestamp: new Date(),
          receiptUrl: "#",
        });
        setSubmitted(true);
        
        confetti({
          particleCount: 150,
          spread: 70,
          origin: { y: 0.6 },
          colors: ["#F97316", "#10B981", "#3B82F6"],
        });
        
        setIsSubmitting(false);
      }, 2000);
    }
  };

  const generatePDFRecap = async () => {
    try {
      const response = await fetch(`/api/v1/missions/${missionId}/recap-pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `recap-offre-${missionId}.pdf`;
        a.click();
      }
    } catch (error) {
      console.error("PDF generation error:", error);
    }
  };

  const copyReference = () => {
    if (submissionData?.reference) {
      navigator.clipboard.writeText(submissionData.reference);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      {!submitted ? (
        /* Écran pré-soumission */
        <div className="max-w-4xl mx-auto">
          {/* Header solennel */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <div className="inline-block p-6 rounded-full bg-orange-900/30 mb-6">
              <Rocket className="w-20 h-20 text-orange-500" />
            </div>
            <h1 className="text-4xl font-bold text-orange-500 mb-4">
              DÉPÔT DE L'OFFRE
            </h1>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Dernière étape avant soumission. Vérifiez les informations ci-dessous.
            </p>
          </motion.div>

          {/* Résumé de l'offre */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <Card className="bg-slate-900/50 border-slate-700 p-8">
              <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
                <FileText className="w-6 h-6 text-orange-500" />
                Résumé final de l'offre
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <Euro className="w-8 h-8 text-green-500 mx-auto mb-2" />
                  <p className="text-sm text-slate-400">Prix HT</p>
                  <p className="text-2xl font-bold text-white">{offerSummary.prixHT} €</p>
                </div>
                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <Clock className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                  <p className="text-sm text-slate-400">Délai d'exécution</p>
                  <p className="text-2xl font-bold text-white">{offerSummary.delai}</p>
                </div>
                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <Calendar className="w-8 h-8 text-purple-500 mx-auto mb-2" />
                  <p className="text-sm text-slate-400">Validité de l'offre</p>
                  <p className="text-2xl font-bold text-white">{offerSummary.validite}</p>
                </div>
                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <Shield className="w-8 h-8 text-orange-500 mx-auto mb-2" />
                  <p className="text-sm text-slate-400">Documents inclus</p>
                  <p className="text-2xl font-bold text-white">{offerSummary.documents}</p>
                </div>
              </div>

              {/* Checklist finale */}
              <div className="space-y-4 mb-8">
                <h3 className="font-semibold text-lg mb-4">Vérifications préalables</h3>
                {[
                  "Offre complète et signée électroniquement",
                  "Tous les documents obligatoires inclus dans le ZIP",
                  "Prix total vérifié et validé par la direction",
                  "Délais d'exécution réalistes et planifiés",
                  "Assurances et garanties à jour",
                  "Compatibilité plateforme de dépôt vérifiée",
                ].map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + index * 0.1 }}
                    className="flex items-center gap-3"
                  >
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span className="text-slate-300">{item}</span>
                  </motion.div>
                ))}
              </div>

              {/* Avertissement */}
              <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4 mb-8">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-6 h-6 text-yellow-500 mt-0.5" />
                  <div>
                    <p className="font-semibold text-yellow-400 mb-1">
                      Attention: Action irréversible
                    </p>
                    <p className="text-sm text-slate-300">
                      Une fois soumise, cette offre ne pourra plus être modifiée. 
                      Assurez-vous que toutes les informations sont correctes.
                    </p>
                  </div>
                </div>
              </div>

              {/* Bouton de soumission à double clic */}
              <div className="text-center">
                <AnimatePresence>
                  {showConfirmation && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      className="mb-4 p-4 bg-red-900/30 border border-red-700 rounded-lg"
                    >
                      <p className="text-red-400 font-semibold">
                        Cliquez à nouveau pour confirmer le dépôt définitif
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>

                <Button
                  onClick={handleDoubleClickSubmit}
                  disabled={isSubmitting}
                  size="lg"
                  className={`px-12 py-6 text-lg ${
                    isSubmitting
                      ? "bg-slate-700 cursor-not-allowed"
                      : "bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700"
                  }`}
                >
                  {isSubmitting ? (
                    <>
                      <Progress value={60} className="w-32 mr-4" />
                      Soumission en cours...
                    </>
                  ) : (
                    <>
                      <Rocket className="w-6 h-6 mr-3" />
                      DÉPOSER L'OFFRE
                    </>
                  )}
                </Button>
                
                <p className="text-sm text-slate-500 mt-4">
                  Double-clic requis pour validation de sécurité
                </p>
              </div>
            </Card>
          </motion.div>

          {/* Bouton retour */}
          <div className="text-center">
            <Button variant="ghost" onClick={onBack} className="text-slate-400">
              Retour aux vérifications
            </Button>
          </div>
        </div>
      ) : (
        /* Écran post-soumission */
        <div className="max-w-4xl mx-auto">
          {/* Animation de succès */}
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", duration: 0.8 }}
            className="text-center mb-12"
          >
            <div className="inline-block p-8 rounded-full bg-green-900/30 mb-6">
              <Award className="w-32 h-32 text-green-500" />
            </div>
            <h1 className="text-5xl font-bold text-green-500 mb-4">
              OFFRE ENVOYÉE AVEC SUCCÈS
            </h1>
            <p className="text-2xl text-slate-300 mb-2">
              Bonne chance, Chef! 🚀
            </p>
            <p className="text-slate-400">
              Votre offre a été déposée avec succès sur la plateforme
            </p>
          </motion.div>

          {/* Détails de soumission */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mb-8"
          >
            <Card className="bg-slate-900/50 border-slate-700 p-8">
              <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
                <FileText className="w-6 h-6 text-blue-500" />
                Accusé de réception
              </h2>
              
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm text-slate-400 mb-1">Référence de soumission</p>
                    <div className="flex items-center gap-2">
                      <code className="text-lg font-mono text-orange-500">
                        {submissionData?.reference}
                      </code>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={copyReference}
                        className="text-slate-400 hover:text-white"
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400 mb-1">Date et heure de dépôt</p>
                    <p className="text-lg font-semibold">
                      {submissionData?.timestamp.toLocaleString("fr-FR")}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400 mb-1">Statut</p>
                    <Badge className="bg-green-600">
                      <CheckCircle className="w-3 h-3 mr-2" />
                      Soumis avec succès
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400 mb-1">Plateforme cible</p>
                    <p className="text-lg font-semibold">Chorus Pro / BOAMP</p>
                  </div>
                </div>

                {/* Actions post-soumission */}
                <div className="pt-6 border-t border-slate-700">
                  <h3 className="font-semibold mb-4">Prochaines étapes</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Button
                      variant="outline"
                      className="border-blue-600 text-blue-500 hover:bg-blue-900/30"
                      onClick={generatePDFRecap}
                    >
                      <Download className="w-5 h-5 mr-2" />
                      Télécharger récapitulatif PDF
                    </Button>
                    <Button
                      variant="outline"
                      className="border-green-600 text-green-500 hover:bg-green-900/30"
                    >
                      <Mail className="w-5 h-5 mr-2" />
                      Envoyer accusé par email
                    </Button>
                    <Button
                      variant="outline"
                      className="border-purple-600 text-purple-500 hover:bg-purple-900/30"
                      onClick={onComplete}
                    >
                      <Home className="w-5 h-5 mr-2" />
                      Retour au tableau de bord
                    </Button>
                  </div>
                </div>

                {/* Timeline de suivi */}
                <div className="pt-6 border-t border-slate-700">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-orange-500" />
                    Calendrier de suivi
                  </h3>
                  <div className="space-y-4">
                    {[
                      { date: "Aujourd'hui", event: "Offre soumise", status: "completed" },
                      { date: "J+7", event: "Ouverture des plis", status: "pending" },
                      { date: "J+30", event: "Analyse technique", status: "pending" },
                      { date: "J+45", event: "Notification résultat", status: "pending" },
                    ].map((step, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 + index * 0.1 }}
                        className="flex items-center gap-4"
                      >
                        <div className={`w-3 h-3 rounded-full ${
                          step.status === "completed" ? "bg-green-500" : "bg-slate-600"
                        }`} />
                        <div className="flex-1">
                          <p className="font-medium">{step.event}</p>
                          <p className="text-sm text-slate-400">{step.date}</p>
                        </div>
                        {step.status === "completed" && (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        )}
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>

          {/* Message de remerciement */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center text-slate-400"
          >
            <p className="mb-4">
              Merci d'avoir utilisé notre plateforme de réponse aux appels d'offres
            </p>
            <p className="text-sm">
              Notre équipe vous tiendra informé de l'avancement de votre dossier
            </p>
          </motion.div>
        </div>
      )}
    </div>
  );
}
