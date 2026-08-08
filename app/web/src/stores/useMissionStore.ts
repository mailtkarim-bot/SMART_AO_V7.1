import { create } from 'zustand';

interface MissionStep {
  id: number;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
}

interface MissionState {
  missionId: string | null;
  steps: MissionStep[];
  websocketConnected: boolean;
  events: any[];
  
  setMissionId: (id: string) => void;
  updateStepStatus: (stepId: number, status: MissionStep['status'], progress?: number) => void;
  setWebsocketConnected: (connected: boolean) => void;
  addEvent: (event: any) => void;
  reset: () => void;
}

const defaultSteps: MissionStep[] = [
  { id: 1, name: 'Parsing DCE', status: 'pending', progress: 0 },
  { id: 2, name: 'Extraction données', status: 'pending', progress: 0 },
  { id: 3, name: 'Classification', status: 'pending', progress: 0 },
  { id: 4, name: 'Analyse agents IA', status: 'pending', progress: 0 },
  { id: 5, name: 'Compilation', status: 'pending', progress: 0 },
  { id: 6, name: 'Rapport final', status: 'pending', progress: 0 },
];

export const useMissionStore = create<MissionState>((set) => ({
  missionId: null,
  steps: defaultSteps,
  websocketConnected: false,
  events: [],

  setMissionId: (id) => set({ missionId: id }),
  
  updateStepStatus: (stepId, status, progress) => set((state) => ({
    steps: state.steps.map(step => 
      step.id === stepId 
        ? { ...step, status, progress: progress ?? step.progress }
        : step
    ),
  })),
  
  setWebsocketConnected: (connected) => set({ websocketConnected: connected }),
  
  addEvent: (event) => set((state) => ({
    events: [...state.events, event].slice(-100), // Garder derniers 100 events
  })),
  
  reset: () => set({
    missionId: null,
    steps: defaultSteps,
    websocketConnected: false,
    events: [],
  }),
}));
