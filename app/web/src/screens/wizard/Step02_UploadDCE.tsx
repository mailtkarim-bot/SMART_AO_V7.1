// ─────────────────────────────────────────────────────────────────────────────
// SMART_AO V7 - Step02_UploadDCE.tsx
// Écran 2: Upload DCE - Le Sas de Décontamination
// Connecté à l'API Backend: POST /api/v1/documents/upload
// ─────────────────────────────────────────────────────────────────────────────

"use client";

import React, { useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileText, CheckCircle, AlertCircle, ScanLine, X } from "lucide-react";

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURATION API
// ─────────────────────────────────────────────────────────────────────────────
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─────────────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────────────
type UploadStatus = "pending" | "uploading" | "scanning" | "indexed" | "parsed" | "error";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: UploadStatus;
  documentId?: string;
  uploadId?: string;
  progress: number;
  detectedPieces?: string[];
  errorMessage?: string;
  scanStatus?: string;
  indexingStatus?: string;
}

interface UploadProgressStep {
  label: string;
  completed: boolean;
  current: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// DETECTION DES PIECES DU DCE
// ─────────────────────────────────────────────────────────────────────────────
const detectPieces = (fileName: string): string[] => {
  const pieces: string[] = [];
  const upperName = fileName.toUpperCase();

  if (upperName.includes("RC") || upperName.includes("REGLEMENT")) pieces.push("Règlement de Consultation");
  if (upperName.includes("CCTP") || upperName.includes("CAHIER")) pieces.push("CCTP");
  if (upperName.includes("DPGF") || upperName.includes("PRIX")) pieces.push("DPGF");
  if (upperName.includes("ACTE") || upperName.includes("ENGAGEMENT")) pieces.push("Acte d'Engagement");
  if (upperName.includes("CCAP") || upperName.includes("ADMIN")) pieces.push("CCAP");
  if (upperName.includes("PLAN") || upperName.includes("DTU")) pieces.push("Plans & DTU");

  return pieces.length > 0 ? pieces : ["Document non identifié"];
};

// ─────────────────────────────────────────────────────────────────────────────
// APPELS API BACKEND
// ─────────────────────────────────────────────────────────────────────────────
const uploadToBackend = async (file: File, missionId?: string, documentType?: string): Promise<{ uploadId: string }> => {
  const formData = new FormData();
  formData.append("file", file);
  if (missionId) formData.append("mission_id", missionId);
  if (documentType) formData.append("document_type", documentType);

  const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erreur d'upload");
  }

  return response.json();
};

const pollUploadStatus = async (uploadId: string): Promise<{
  status: string;
  progress: number;
  scanStatus?: string;
  indexingStatus?: string;
  error?: string;
}> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload/${uploadId}/status`);
  if (!response.ok) throw new Error("Erreur statut upload");
  return response.json();
};

// ─────────────────────────────────────────────────────────────────────────────
// COMPOSANT PRINCIPAL
// ─────────────────────────────────────────────────────────────────────────────
export default function UploadDCE() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const progressSteps: UploadProgressStep[] = [
    { label: "Réception", completed: progressStep >= 1, current: progressStep === 0 },
    { label: "Analyse structure", completed: progressStep >= 2, current: progressStep === 1 },
    { label: "Extraction texte", completed: progressStep >= 3, current: progressStep === 2 },
  ];

  const handleFiles = useCallback(async (fileList: FileList | null) => {
    if (!fileList) return;

    const newFiles: UploadedFile[] = Array.from(fileList).map((file) => ({
      id: `${file.name}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      size: file.size,
      status: "uploading" as UploadStatus,
      progress: 0,
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    // Upload réel vers le backend pour chaque fichier
    for (const [index, fileObj] of newFiles.entries()) {
      uploadAndTrack(fileObj.id, fileList[index]);
    }
  }, []);

  const uploadAndTrack = async (fileId: string, file: File) => {
    try {
      // Étape 1: Upload initial
      setFiles((prev) => prev.map((f) => (f.id === fileId ? { ...f, status: "uploading", progress: 10 } : f)));
      
      const { uploadId } = await uploadToBackend(file, undefined, "DCE");
      
      setFiles((prev) =>
        prev.map((f) => (f.id === fileId ? { ...f, uploadId, progress: 30, status: "scanning" } : f))
      );

      // Étape 2: Polling du statut (scan antivirus + indexation)
      const pollInterval = setInterval(async () => {
        try {
          const statusData = await pollUploadStatus(uploadId);
          
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileId
                ? {
                    ...f,
                    progress: statusData.progress,
                    scanStatus: statusData.scanStatus,
                    indexingStatus: statusData.indexingStatus,
                    status: statusData.error
                      ? "error"
                      : statusData.status === "COMPLETED"
                      ? "indexed"
                      : "scanning",
                    errorMessage: statusData.error || undefined,
                  }
                : f
            )
          );

          if (statusData.status === "COMPLETED" || statusData.error) {
            clearInterval(pollInterval);
            
            if (!statusData.error) {
              // Étape 3: Parsing local pour détection des pièces
              setFiles((prev) =>
                prev.map((f) =>
                  f.id === fileId
                    ? {
                        ...f,
                        status: "parsed",
                        detectedPieces: detectPieces(file.name),
                        progress: 100,
                      }
                    : f
                )
              );
              setProgressStep(3);
            }
          }
        } catch (err) {
          clearInterval(pollInterval);
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileId
                ? { ...f, status: "error", errorMessage: "Erreur de suivi upload" }
                : f
            )
          );
        }
      }, 1000);
    } catch (err) {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? { ...f, status: "error", errorMessage: err instanceof Error ? err.message : "Erreur d'upload" }
            : f
        )
      );
    }
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const removeFile = (fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background Grid Effect */}
      <div className="absolute inset-0 opacity-10 pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: `linear-gradient(#F97316 1px, transparent 1px), linear-gradient(90deg, #F97316 1px, transparent 1px)`,
          backgroundSize: "40px 40px"
        }} />
      </div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12 z-10"
      >
        <h1 className="text-5xl font-black tracking-tight mb-4">
          <span className="text-white">UPLOAD</span>{" "}
          <span className="text-[#F97316]">DCE</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl">
          Sas de décontamination des documents. Glissez vos pièces pour analyse immédiate.
        </p>
      </motion.div>

      {/* Progress Steps */}
      <div className="flex gap-4 mb-12 z-10">
        {progressSteps.map((step, idx) => (
          <motion.div
            key={step.label}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`flex items-center gap-2 px-4 py-2 rounded-full border ${
              step.completed
                ? "border-[#10B981] bg-[#10B981]/10 text-[#10B981]"
                : step.current
                ? "border-[#F97316] bg-[#F97316]/10 text-[#F97316]"
                : "border-slate-700 bg-slate-900 text-slate-500"
            }`}
          >
            {step.completed ? (
              <CheckCircle className="w-4 h-4" />
            ) : step.current ? (
              <ScanLine className="w-4 h-4 animate-pulse" />
            ) : (
              <div className="w-4 h-4 rounded-full border-2 border-current" />
            )}
            <span className="text-sm font-medium">{step.label}</span>
          </motion.div>
        ))}
      </div>

      {/* Drop Zone */}
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className={`w-full max-w-4xl border-2 border-dashed rounded-3xl p-12 transition-all duration-300 ${
          isDragging
            ? "border-[#F97316] bg-[#F97316]/5 shadow-[0_0_60px_rgba(249,115,22,0.3)]"
            : "border-slate-700 bg-slate-900/50 hover:border-slate-500"
        }`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
          accept=".pdf,.doc,.docx,.xls,.xlsx,.dwg,.dxf"
        />

        <div className="flex flex-col items-center justify-center text-center">
          <motion.div
            animate={isDragging ? { scale: 1.1, rotate: 5 } : { scale: 1, rotate: 0 }}
            className="mb-6"
          >
            <UploadCloud
              className={`w-24 h-24 ${
                isDragging ? "text-[#F97316]" : "text-slate-600"
              }`}
            />
          </motion.div>

          <h3 className="text-2xl font-bold mb-2">
            {isDragging ? "Relâchez pour analyser" : "Glissez vos fichiers DCE ici"}
          </h3>
          <p className="text-slate-400 mb-6">
            ou cliquez pour parcourir • PDF, DOC, XLS, DWG acceptés
          </p>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-4 bg-[#F97316] hover:bg-[#EA620C] text-white font-bold rounded-xl transition-colors"
          >
            SÉLECTIONNER LES FICHIERS
          </motion.button>
        </div>
      </motion.div>

      {/* Files List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full max-w-4xl mt-8 space-y-4 z-10"
          >
            <h3 className="text-xl font-bold text-slate-300 mb-4">
              Fichiers en cours d'analyse ({files.length})
            </h3>

            {files.map((file, idx) => (
              <motion.div
                key={file.id}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-slate-900/80 border border-slate-700 rounded-xl p-4 flex items-center gap-4"
              >
                <div className="flex-shrink-0">
                  {file.status === "parsed" ? (
                    <CheckCircle className="w-10 h-10 text-[#10B981]" />
                  ) : file.status === "scanning" ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      <ScanLine className="w-10 h-10 text-[#F97316]" />
                    </motion.div>
                  ) : file.status === "error" ? (
                    <AlertCircle className="w-10 h-10 text-red-500" />
                  ) : (
                    <FileText className="w-10 h-10 text-slate-500" />
                  )}
                </div>

                <div className="flex-grow min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-white truncate">{file.name}</h4>
                    <span className="text-xs text-slate-500">{formatFileSize(file.size)}</span>
                  </div>

                  {/* Barre de progression intelligente */}
                  {(file.status === "uploading" || file.status === "scanning") && (
                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden mt-2">
                      <motion.div
                        className={`h-full ${file.scanStatus === "INFECTED" ? "bg-red-500" : "bg-[#F97316]"}`}
                        initial={{ width: "0%" }}
                        animate={{ width: `${file.progress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  )}

                  {/* Statut détaillé */}
                  <div className="flex gap-3 mt-2 text-xs">
                    {file.scanStatus && (
                      <span className={`px-2 py-0.5 rounded ${
                        file.scanStatus === "CLEAN" 
                          ? "bg-[#10B981]/10 text-[#10B981]" 
                          : file.scanStatus === "INFECTED"
                          ? "bg-red-500/10 text-red-500"
                          : "bg-slate-700 text-slate-400"
                      }`}>
                        {file.scanStatus === "CLEAN" ? "✓ Scan" : file.scanStatus === "INFECTED" ? "✗ Virus" : "⏳ Scan"}
                      </span>
                    )}
                    {file.indexingStatus && (
                      <span className={`px-2 py-0.5 rounded ${
                        file.indexingStatus === "COMPLETED"
                          ? "bg-[#10B981]/10 text-[#10B981]"
                          : "bg-blue-500/10 text-blue-400"
                      }`}>
                        {file.indexingStatus === "COMPLETED" ? "✓ Indexé" : "⏳ Indexation"}
                      </span>
                    )}
                  </div>

                  {/* Pièces détectées */}
                  {file.status === "parsed" && file.detectedPieces && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {file.detectedPieces.map((piece, pIdx) => (
                        <span
                          key={pIdx}
                          className="px-2 py-1 bg-[#10B981]/10 text-[#10B981] text-xs rounded-md font-medium"
                        >
                          {piece}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Erreur */}
                  {file.status === "error" && file.errorMessage && (
                    <p className="text-red-400 text-sm mt-1">{file.errorMessage}</p>
                  )}
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(file.id);
                  }}
                  className="flex-shrink-0 p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-slate-400" />
                </button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Laser Scan Effect Overlay */}
      <AnimatePresence>
        {files.some((f) => f.status === "scanning") && (
          <motion.div
            initial={{ top: "0%" }}
            animate={{ top: "100%" }}
            exit={{ opacity: 0 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute left-0 right-0 h-1 bg-[#F97316] shadow-[0_0_20px_#F97316] pointer-events-none z-20"
            style={{ boxShadow: "0 0 30px #F97316, 0 0 60px #F97316" }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
