export interface HistoryEntry {
  id: string;
  name: string;
  fastaContent: string;
  numberingScheme: string;
  timestamp: number;
  summary?: {
    numChains?: number;
    numDomains?: number;
  };
  result?: any;
}

const STORAGE_KEY = 'annotation_history_v2';

export function loadHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveHistory(entries: HistoryEntry[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

export function addHistory(entry: HistoryEntry): void {
  const items = loadHistory();
  items.unshift(entry);
  saveHistory(items.slice(0, 50)); // keep last 50
}

export function clearHistory(): void {
  localStorage.removeItem(STORAGE_KEY);
}


