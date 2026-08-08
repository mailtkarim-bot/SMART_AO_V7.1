"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Camera, 
  Mic, 
  MapPin, 
  Upload, 
  X, 
  Check, 
  AlertCircle,
  PenTool,
  Save,
  Trash2,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";

// Types
interface PhotoAnnotation {
  id: string;
  imageUrl: string;
  fileName: string;
  annotations: Annotation[];
  notes: string;
  location?: { lat: number; lng: number; address: string };
  timestamp: Date;
}

interface Annotation {
  id: string;
  x: number;
  y: number;
  type: "circle" | "arrow" | "text";
  color: string;
  text?: string;
}

interface ChecklistItem {
  id: string;
  label: string;
  completed: boolean;
  priority: "low" | "medium" | "high";
}

interface Props {
  onNext: () => void;
  onBack: () => void;
  missionId?: string;
}

export default function VisiteLieux({ onNext, onBack, missionId }: Props) {
  const [photos, setPhotos] = useState<PhotoAnnotation[]>([]);
  const [selectedPhoto, setSelectedPhoto] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioNotes, setAudioNotes] = useState<string[]>([]);
  const [mapVisible, setMapVisible] = useState(false);
  const [currentLocation, setCurrentLocation] = useState<{lat: number, lng: number, address: string} | null>(null);
  const [drawingMode, setDrawingMode] = useState(false);
  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>([
    { id: "1", label: "Accès chantier vérifié", completed: false, priority: "high" },
    { id: "2", label: "Zone de stockage identifiée", completed: false, priority: "medium" },
    { id: "3", label: "Contraintes techniques notées", completed: false, priority: "high" },
    { id: "4", label: "Réseaux (eau/élec) localisés", completed: false, priority: "high" },
    { id: "5", label: "Voisinage informé", completed: false, priority: "low" },
  ]);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Simulation upload vers backend
  const handlePhotoUpload = async (files: FileList) => {
    setIsUploading(true);
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const imageUrl = URL.createObjectURL(file);
      
      // Simuler upload vers backend
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("missionId", missionId || "");
        formData.append("type", "site_visit");
        
        // Appel API réel vers le backend
        const response = await fetch(`/api/v1/missions/${missionId}/site-visit/photos`, {
          method: "POST",
          body: formData,
        });
        
        if (!response.ok) throw new Error("Upload failed");
        
        const data = await response.json();
        
        const newPhoto: PhotoAnnotation = {
          id: data.id || Date.now().toString(),
          imageUrl: data.url || imageUrl,
          fileName: file.name,
          annotations: [],
          notes: "",
          timestamp: new Date(),
        };
        
        setPhotos(prev => [...prev, newPhoto]);
      } catch (error) {
        console.error("Upload error:", error);
        // Fallback local en cas d'erreur
        const newPhoto: PhotoAnnotation = {
          id: Date.now().toString(),
          imageUrl,
          fileName: file.name,
          annotations: [],
          notes: "",
          timestamp: new Date(),
        };
        setPhotos(prev => [...prev, newPhoto]);
      }
    }
    
    setIsUploading(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handlePhotoUpload(files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const toggleChecklistItem = (id: string) => {
    setChecklistItems(prev =>
      prev.map(item =>
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    );
  };

  const startRecording = () => {
    setIsRecording(true);
    // Simulation enregistrement vocal - à connecter à Web Speech API
    setTimeout(() => {
      setIsRecording(false);
      setAudioNotes(prev => [
        ...prev,
        `Note vocale ${new Date().toLocaleTimeString()} - Accès difficile par rue principale`,
      ]);
    }, 3000);
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            address: "Position acquise via GPS",
          });
          setMapVisible(true);
        },
        (error) => {
          console.error("Geolocation error:", error);
        }
      );
    }
  };

  const completedCount = checklistItems.filter(i => i.completed).length;
  const progress = (completedCount / checklistItems.length) * 100;

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-orange-500 flex items-center gap-3">
              <Camera className="w-8 h-8" />
              VISITE DES LIEUX
            </h1>
            <p className="text-slate-400 mt-1">Carnet de chantier numérique</p>
          </div>
          <Badge variant="outline" className="border-orange-500 text-orange-500">
            {photos.length} photos • {completedCount}/{checklistItems.length} checklist
          </Badge>
        </div>
        <Progress value={progress} className="h-2 bg-slate-800" />
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Colonne gauche - Upload & Photos */}
        <div className="lg:col-span-2 space-y-6">
          {/* Zone de drop */}
          <Card
            className="bg-slate-900/50 border-slate-700 p-8 cursor-pointer hover:border-orange-500 transition-colors"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={(e) => e.target.files && handlePhotoUpload(e.target.files)}
            />
            <motion.div
              className="text-center"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Upload className="w-16 h-16 mx-auto text-slate-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">
                Glissez-déposez vos photos ou cliquez pour uploader
              </h3>
              <p className="text-slate-400">
                Supporte JPG, PNG, HEIC • Annotation directe disponible
              </p>
              {isUploading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4"
                >
                  <Progress value={60} className="h-1" />
                  <p className="text-sm text-orange-500 mt-2">Upload en cours...</p>
                </motion.div>
              )}
            </motion.div>
          </Card>

          {/* Grille de photos */}
          <AnimatePresence>
            {photos.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="grid grid-cols-2 md:grid-cols-3 gap-4"
              >
                {photos.map((photo, index) => (
                  <motion.div
                    key={photo.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="relative group cursor-pointer"
                    onClick={() => setSelectedPhoto(photo.id)}
                  >
                    <img
                      src={photo.imageUrl}
                      alt={photo.fileName}
                      className="w-full h-48 object-cover rounded-lg border border-slate-700 group-hover:border-orange-500 transition-colors"
                    />
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center gap-2">
                      <Button size="sm" variant="secondary" onClick={(e) => {
                        e.stopPropagation();
                        setDrawingMode(true);
                        setSelectedPhoto(photo.id);
                      }}>
                        <PenTool className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="destructive" onClick={(e) => {
                        e.stopPropagation();
                        setPhotos(prev => prev.filter(p => p.id !== photo.id));
                      }}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                    {photo.annotations.length > 0 && (
                      <Badge className="absolute top-2 right-2 bg-orange-500">
                        {photo.annotations.length}
                      </Badge>
                    )}
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Visionneuse de photo avec annotation */}
          <AnimatePresence>
            {selectedPhoto && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 50 }}
                className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
                onClick={() => {
                  setSelectedPhoto(null);
                  setDrawingMode(false);
                }}
              >
                <div className="max-w-6xl w-full" onClick={e => e.stopPropagation()}>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-semibold">
                      {photos.find(p => p.id === selectedPhoto)?.fileName}
                    </h3>
                    <Button variant="ghost" size="sm" onClick={() => {
                      setSelectedPhoto(null);
                      setDrawingMode(false);
                    }}>
                      <X className="w-6 h-6" />
                    </Button>
                  </div>
                  
                  <div className="relative bg-slate-900 rounded-lg overflow-hidden">
                    <img
                      src={photos.find(p => p.id === selectedPhoto)?.imageUrl}
                      alt="Selected"
                      className="w-full max-h-[60vh] object-contain"
                    />
                    
                    {drawingMode && (
                      <div className="absolute top-4 left-4 flex gap-2 bg-slate-900/90 p-2 rounded-lg">
                        <Button size="sm" variant="outline" onClick={() => {}}>
                          Cercle
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => {}}>
                          Flèche
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => {}}>
                          Texte
                        </Button>
                        <Button 
                          size="sm" 
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => {
                            setDrawingMode(false);
                            // Sauvegarder les annotations vers backend
                            const photo = photos.find(p => p.id === selectedPhoto);
                            if (photo && missionId) {
                              fetch(`/api/v1/missions/${missionId}/site-visit/photos/${selectedPhoto}/annotations`, {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ annotations: photo.annotations }),
                              });
                            }
                          }}
                        >
                          <Save className="w-4 h-4 mr-2" />
                          Sauvegarder
                        </Button>
                      </div>
                    )}
                  </div>

                  <Textarea
                    placeholder="Ajoutez des notes pour cette photo..."
                    value={photos.find(p => p.id === selectedPhoto)?.notes || ""}
                    onChange={(e) => {
                      setPhotos(prev =>
                        prev.map(p =>
                          p.id === selectedPhoto ? { ...p, notes: e.target.value } : p
                        )
                      );
                    }}
                    className="mt-4 bg-slate-900 border-slate-700 min-h-[100px]"
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Colonne droite - Checklist & Audio */}
        <div className="space-y-6">
          {/* Checklist */}
          <Card className="bg-slate-900/50 border-slate-700 p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Check className="w-5 h-5 text-green-500" />
              Checklist de visite
            </h3>
            <div className="space-y-3">
              {checklistItems.map((item) => (
                <motion.div
                  key={item.id}
                  whileHover={{ x: 4 }}
                  className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                    item.completed
                      ? "bg-green-900/30 border border-green-700"
                      : "bg-slate-800/50 border border-slate-700 hover:border-orange-500"
                  }`}
                  onClick={() => toggleChecklistItem(item.id)}
                >
                  <div
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                      item.completed
                        ? "bg-green-500 border-green-500"
                        : "border-slate-500"
                    }`}
                  >
                    {item.completed && <Check className="w-3 h-3" />}
                  </div>
                  <span className={item.completed ? "line-through text-slate-400" : ""}>
                    {item.label}
                  </span>
                  <Badge
                    variant="outline"
                    className={`ml-auto ${
                      item.priority === "high"
                        ? "border-red-500 text-red-500"
                        : item.priority === "medium"
                        ? "border-orange-500 text-orange-500"
                        : "border-slate-500 text-slate-500"
                    }`}
                  >
                    {item.priority}
                  </Badge>
                </motion.div>
              ))}
            </div>
          </Card>

          {/* Notes vocales */}
          <Card className="bg-slate-900/50 border-slate-700 p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Mic className="w-5 h-5 text-orange-500" />
              Notes vocales
            </h3>
            <Button
              className={`w-full mb-4 ${
                isRecording ? "bg-red-600 hover:bg-red-700 animate-pulse" : "bg-orange-600 hover:bg-orange-700"
              }`}
              onClick={startRecording}
              disabled={isRecording}
            >
              <Mic className="w-5 h-5 mr-2" />
              {isRecording ? "Enregistrement..." : "Dicter une note"}
            </Button>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {audioNotes.map((note, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-3 bg-slate-800 rounded-lg text-sm text-slate-300"
                >
                  {note}
                </motion.div>
              ))}
              {audioNotes.length === 0 && (
                <p className="text-slate-500 text-sm text-center py-4">
                  Aucune note vocale
                </p>
              )}
            </div>
          </Card>

          {/* Carte interactive */}
          <Card className="bg-slate-900/50 border-slate-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <MapPin className="w-5 h-5 text-blue-500" />
                Localisation
              </h3>
              <Button
                size="sm"
                variant="outline"
                onClick={getCurrentLocation}
                disabled={!navigator.geolocation}
              >
                <MapPin className="w-4 h-4 mr-2" />
                Position GPS
              </Button>
            </div>
            
            {mapVisible && currentLocation ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-slate-800 rounded-lg p-4"
              >
                <div className="aspect-video bg-slate-700 rounded flex items-center justify-center">
                  <div className="text-center">
                    <MapPin className="w-12 h-12 text-orange-500 mx-auto mb-2" />
                    <p className="text-sm text-slate-300">
                      Lat: {currentLocation.lat.toFixed(6)}
                    </p>
                    <p className="text-sm text-slate-300">
                      Lng: {currentLocation.lng.toFixed(6)}
                    </p>
                    <p className="text-xs text-slate-500 mt-2">
                      {currentLocation.address}
                    </p>
                    <a
                      href={`https://www.openstreetmap.org/?mlat=${currentLocation.lat}&mlon=${currentLocation.lng}#map=19/${currentLocation.lat}/${currentLocation.lng}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-orange-500 text-xs hover:underline mt-2 inline-block"
                    >
                      Voir sur OpenStreetMap →
                    </a>
                  </div>
                </div>
              </motion.div>
            ) : (
              <div className="bg-slate-800 rounded-lg p-8 text-center">
                <MapPin className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <p className="text-slate-400 text-sm">
                  Cliquez sur "Position GPS" pour géolocaliser le chantier
                </p>
              </div>
            )}
          </Card>
        </div>
      </div>

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
              {photos.length} photos • {audioNotes.length} notes • {completedCount}/{checklistItems.length} items
            </p>
          </div>

          <Button
            onClick={onNext}
            className="bg-orange-600 hover:bg-orange-700 text-white px-8"
            disabled={photos.length === 0}
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
