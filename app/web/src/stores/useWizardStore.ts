import { create } from 'zustand';

interface WizardState {
  currentStep: number;
  missionId: string | null;
  dceData: any | null;
  analysisResults: any | null;
  goNoGoDecision: 'go' | 'no-go' | null;
  visitedSite: boolean;
  metrage: any[];
  documents: any[];
  zipReady: boolean;
  
  setStep: (step: number) => void;
  nextStep: () => void;
  previousStep: () => void;
  setMissionId: (id: string) => void;
  setDceData: (data: any) => void;
  setAnalysisResults: (results: any) => void;
  setGoNoGoDecision: (decision: 'go' | 'no-go') => void;
  setVisitedSite: (visited: boolean) => void;
  setMetrage: (metrage: any[]) => void;
  setDocuments: (docs: any[]) => void;
  setZipReady: (ready: boolean) => void;
  reset: () => void;
}

export const useWizardStore = create<WizardState>((set) => ({
  currentStep: 1,
  missionId: null,
  dceData: null,
  analysisResults: null,
  goNoGoDecision: null,
  visitedSite: false,
  metrage: [],
  documents: [],
  zipReady: false,

  setStep: (step) => set({ currentStep: step }),
  
  nextStep: () => set((state) => ({ 
    currentStep: Math.min(state.currentStep + 1, 10) 
  })),
  
  previousStep: () => set((state) => ({ 
    currentStep: Math.max(state.currentStep - 1, 1) 
  })),
  
  setMissionId: (id) => set({ missionId: id }),
  setDceData: (data) => set({ dceData: data }),
  setAnalysisResults: (results) => set({ analysisResults: results }),
  setGoNoGoDecision: (decision) => set({ goNoGoDecision: decision }),
  setVisitedSite: (visited) => set({ visitedSite: visited }),
  setMetrage: (metrage) => set({ metrage }),
  setDocuments: (docs) => set({ documents: docs }),
  setZipReady: (ready) => set({ zipReady: ready }),
  
  reset: () => set({
    currentStep: 1,
    missionId: null,
    dceData: null,
    analysisResults: null,
    goNoGoDecision: null,
    visitedSite: false,
    metrage: [],
    documents: [],
    zipReady: false,
  }),
}));
