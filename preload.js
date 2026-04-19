const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  fileNew: () => ipcRenderer.invoke('file:new'),
  fileOpen: () => ipcRenderer.invoke('file:open'),
  fileOpenPath: (p) => ipcRenderer.invoke('file:open-path', p),
  fileSave: (data, filePath) => ipcRenderer.invoke('file:save', { data, filePath }),
  fileSaveAs: (data) => ipcRenderer.invoke('file:save-as', { data }),
  getRecentFiles: () => ipcRenderer.invoke('file:get-recent'),

  // Print
  printHTML: (html) => ipcRenderer.invoke('print:html', html),

  // Window
  setTitle: (t) => ipcRenderer.send('window:set-title', t),
  setEdited: (e) => ipcRenderer.send('window:set-edited', e),
  closeConfirmed: () => ipcRenderer.send('window:close-confirmed'),

  // App info
  getVersion: () => ipcRenderer.invoke('app:get-version'),
  checkForUpdates: () => ipcRenderer.invoke('app:check-for-updates'),

  // Listen for events from main process
  on: (channel, fn) => {
    const allowed = [
      'app:file-opened',
      'app:check-dirty',
      'app:check-dirty-then-new',
      'app:check-dirty-then-open',
      'app:save',
      'app:save-as',
      'app:undo',
      'app:new-card',
      'app:flip-all',
      'app:fit-all',
      'app:set-view',
      'app:print-outline',
      'app:print-beats',
    ];
    if (allowed.includes(channel)) {
      const wrapped = (e, ...args) => fn(...args);
      ipcRenderer.on(channel, wrapped);
      return () => ipcRenderer.removeListener(channel, wrapped);
    }
  },
});
