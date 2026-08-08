"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight, Home } from "lucide-react";

interface WizardStep {
  id: number;
  title: string;
  subtitle: string;
}

const steps: WizardStep[] = [
  { id: 1, title: "Identification", subtitle: "DCE" },
  { id: 2, title: "Upload", subtitle: "DCE" },
  { id: 3, title: "Analyse", subtitle: "IA" },
  { id: 4, title: "Go/No-Go", subtitle: "Décision" },
  { id: 5, title: "Visite", subtitle: "Lieux" },
  { id: 6, title: "Métré", subtitle: "Chiffrage" },
  { id: 7, title: "Documents", subtitle: "Admin & Tech" },
  { id: 8, title: "Conformité", subtitle: "ZIP" },
  { id: 9, title: "Dépôt", subtitle: "Offre" },
];

interface WizardLayoutProps {
  currentStep: number;
  onPrevious?: () => void;
  onNext?: () => void;
  children: React.ReactNode;
}

export default function WizardLayout({ 
  currentStep, 
  onPrevious, 
  onNext, 
  children 
}: WizardLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* Top Navigation Bar */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <Home className="w-5 h-5 text-[#F97316]" />
              <span className="font-bold text-lg">SMART AO</span>
            </div>
            
            {/* Progress Steps */}
            <div className="hidden md:flex items-center gap-2">
              {steps.map((step, idx) => (
                <React.Fragment key={step.id}>
                  <div className="flex items-center gap-2">
                    <div 
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                        step.id <= currentStep
                          ? "bg-[#F97316] text-white"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {step.id < currentStep ? "✓" : step.id}
                    </div>
                    <span className={`text-xs ${
                      step.id <= currentStep ? "text-white" : "text-slate-500"
                    }`}>
                      {step.title}
                    </span>
                  </div>
                  {idx < steps.length - 1 && (
                    <ChevronRight className="w-4 h-4 text-slate-700" />
                  )}
                </React.Fragment>
              ))}
            </div>
            
            <div className="text-sm text-slate-400">
              Étape {currentStep}/{steps.length}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Bottom Navigation */}
      <footer className="border-t border-slate-800 bg-slate-900/50 fixed bottom-0 left-0 right-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <button
              onClick={onPrevious}
              disabled={currentStep === 1}
              className="flex items-center gap-2 px-6 py-3 border border-slate-700 rounded-xl hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
              Précédent
            </button>
            
            <div className="text-sm text-slate-400">
              {steps[currentStep - 1]?.title} — {steps[currentStep - 1]?.subtitle}
            </div>
            
            <button
              onClick={onNext}
              disabled={currentStep === steps.length}
              className="flex items-center gap-2 px-6 py-3 bg-[#F97316] hover:bg-[#F97316]/90 rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Suivant
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

