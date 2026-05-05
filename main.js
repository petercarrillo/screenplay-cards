const { app, BrowserWindow, Menu, dialog, ipcMain, shell } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const fs = require('fs');

// ── App state ──────────────────────────────────────────────────────────────────
let mainWindow = null;
let recentFiles = [];
let showWelcomePref = true;
let windowBounds = null;
const userDataPath = app.getPath('userData');
const prefsPath = path.join(userDataPath, 'prefs.json');

// ── Prefs ──────────────────────────────────────────────────────────────────────
function loadPrefs() {
  try {
    if (fs.existsSync(prefsPath)) {
      const p = JSON.parse(fs.readFileSync(prefsPath, 'utf8'));
      recentFiles = p.recentFiles || [];
      showWelcomePref = p.showWelcome !== false;
      windowBounds = p.windowBounds || null;
    }
  } catch (e) { recentFiles = []; }
}

function savePrefs() {
  try {
    fs.mkdirSync(userDataPath, { recursive: true });
    fs.writeFileSync(prefsPath, JSON.stringify({ recentFiles, showWelcome: showWelcomePref, windowBounds }), 'utf8');
  } catch (e) {}
}

function addRecentFile(filePath) {
  recentFiles = [filePath, ...recentFiles.filter(f => f !== filePath)].slice(0, 10);
  savePrefs();
  buildMenu();
}

function removeRecentFile(filePath) {
  recentFiles = recentFiles.filter(f => f !== filePath);
  savePrefs();
  buildMenu();
}

// ── Window ─────────────────────────────────────────────────────────────────────
function createWindow(filePath = null) {
  const bounds = windowBounds || { width: 1280, height: 800 };
  mainWindow = new BrowserWindow({
    width: bounds.width,
    height: bounds.height,
    x: bounds.x,
    y: bounds.y,
    minWidth: 800,
    minHeight: 600,
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#1a1a18',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      spellcheck: true,
    },
    show: false,
  });

  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (filePath) openFile(filePath);
  });

  const saveBounds = () => {
    if (!mainWindow || mainWindow.isMaximized() || mainWindow.isMinimized()) return;
    windowBounds = mainWindow.getBounds();
    savePrefs();
  };
  mainWindow.on('resize', saveBounds);
  mainWindow.on('move', saveBounds);

  // ── Context menu: spell check + formatting ─────────────────────────────────
  mainWindow.webContents.on('context-menu', (event, params) => {
    if (!params.isEditable) return;
    event.preventDefault();
    const items = [];

    // Spell check suggestions
    if (params.misspelledWord) {
      const suggestions = params.dictionarySuggestions.slice(0, 5);
      if (suggestions.length > 0) {
        suggestions.forEach(word => {
          items.push({ label: word, click: () => mainWindow.webContents.replaceMisspelling(word) });
        });
      } else {
        items.push({ label: 'No suggestions', enabled: false });
      }
      items.push({ type: 'separator' });
      items.push({
        label: 'Add to Dictionary',
        click: () => mainWindow.webContents.session.addWordToSpellCheckerDictionary(params.misspelledWord),
      });
      items.push({ type: 'separator' });
    }

    // Standard edit actions
    items.push(
      { label: 'Undo', accelerator: 'CmdOrCtrl+Z', click: () => mainWindow.webContents.send('app:undo') },
      { type: 'separator' },
      { label: 'Cut',  role: 'cut',       enabled: params.editFlags.canCut },
      { label: 'Copy', role: 'copy',      enabled: params.editFlags.canCopy },
      { label: 'Paste',role: 'paste',     enabled: params.editFlags.canPaste },
      { label: 'Select All', role: 'selectAll' },
    );

    // Rich-text formatting (only meaningful in contenteditable notes fields)
    const exec = cmd =>
      mainWindow.webContents.executeJavaScript(
        `document.execCommand('${cmd}',false,null);` +
        `document.activeElement&&document.activeElement.dispatchEvent(new Event('input',{bubbles:true}));`
      );
    items.push(
      { type: 'separator' },
      { label: 'Bold',      accelerator: 'CmdOrCtrl+B', click: () => exec('bold') },
      { label: 'Italic',    accelerator: 'CmdOrCtrl+I', click: () => exec('italic') },
      { label: 'Underline', accelerator: 'CmdOrCtrl+U', click: () => exec('underline') },
      { type: 'separator' },
      { label: 'Align Left',   click: () => exec('justifyLeft') },
      { label: 'Center',       click: () => exec('justifyCenter') },
      { label: 'Align Right',  click: () => exec('justifyRight') },
    );

    Menu.buildFromTemplate(items).popup({ window: mainWindow });
  });

  mainWindow.on('close', (e) => {
    if (mainWindow && !app.isQuitting) {
      e.preventDefault();
      mainWindow.webContents.send('app:check-dirty');
      // Safety fallback — force close after 3s if renderer doesn't respond
      setTimeout(() => { if (mainWindow) mainWindow.destroy(); }, 3000);
    }
  });

  mainWindow.on('closed', () => { mainWindow = null; });
}

// ── File operations ────────────────────────────────────────────────────────────
function newProject() {
  if (!mainWindow) return;
  mainWindow.webContents.send('app:check-dirty-then-new');
}

function openFile(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      removeRecentFile(filePath);
      dialog.showErrorBox('File not found', `Could not find:\n${filePath}`);
      return;
    }
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    // Cloud sync check — warn if file on disk is newer than last known save
    if (data.savedAt) {
      const stat = fs.statSync(filePath);
      const savedAt = new Date(data.savedAt).getTime();
      if (stat.mtimeMs > savedAt + 10000) {
        const result = dialog.showMessageBoxSync(mainWindow, {
          type: 'warning',
          title: 'File May Have Changed',
          message: 'This file appears to have been modified outside the app.',
          detail: `This can happen when a cloud sync service (iCloud, Dropbox, Google Drive) has updated the file from another device.\n\nLast saved: ${new Date(savedAt).toLocaleString()}\nFile on disk: ${new Date(stat.mtimeMs).toLocaleString()}\n\nOpen it anyway?`,
          buttons: ['Open Anyway', 'Cancel'],
          defaultId: 0,
        });
        if (result === 1) return;
      }
    }
    mainWindow.webContents.send('app:file-opened', { data, filePath });
    mainWindow.setRepresentedFilename(filePath);
    mainWindow.setTitle(data.name || path.basename(filePath, '.screenplaycards'));
    addRecentFile(filePath);
  } catch (e) {
    dialog.showErrorBox('Could not open file', `There was a problem opening this file.\n\n${e.message}`);
  }
}

function openFileDialog() {
  const result = dialog.showOpenDialogSync(mainWindow, {
    title: 'Open Project',
    filters: [{ name: 'Screenplay Cards', extensions: ['screenplaycards'] }],
    properties: ['openFile'],
  });
  if (result && result[0]) {
    mainWindow.webContents.send('app:check-dirty-then-open', result[0]);
  }
}

function saveFile(data, filePath) {
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
    mainWindow.setRepresentedFilename(filePath);
    mainWindow.setTitle(data.name || path.basename(filePath, '.screenplaycards'));
    mainWindow.setDocumentEdited(false);
    addRecentFile(filePath);
    return { success: true, filePath };
  } catch (e) {
    dialog.showErrorBox('Could not save file', e.message);
    return { success: false };
  }
}

function saveFileDialog(data, suggestedName) {
  const result = dialog.showSaveDialogSync(mainWindow, {
    title: 'Save Project',
    defaultPath: path.join(app.getPath('documents'), `${suggestedName || 'Untitled'}.screenplaycards`),
    filters: [{ name: 'Screenplay Cards', extensions: ['screenplaycards'] }],
  });
  if (result) return saveFile(data, result);
  return { success: false, cancelled: true };
}

// ── IPC handlers ───────────────────────────────────────────────────────────────
ipcMain.handle('file:new', () => newProject());
ipcMain.handle('file:open', () => openFileDialog());
ipcMain.handle('file:open-path', (e, filePath) => openFile(filePath));
ipcMain.handle('file:save', (e, { data, filePath }) => {
  if (filePath) return saveFile(data, filePath);
  return saveFileDialog(data, data.name);
});
ipcMain.handle('file:save-as', (e, { data }) => saveFileDialog(data, data.name));
ipcMain.handle('file:get-recent', () => recentFiles);

ipcMain.on('window:set-title', (e, title) => { if (mainWindow) mainWindow.setTitle(title); });
ipcMain.on('window:set-edited', (e, edited) => { if (mainWindow) mainWindow.setDocumentEdited(edited); });
ipcMain.on('window:close-confirmed', () => { if (mainWindow) mainWindow.destroy(); });

ipcMain.handle('app:get-version', () => app.getVersion());
ipcMain.handle('app:check-for-updates', () => autoUpdater.checkForUpdatesAndNotify());

// ── Print handler ──────────────────────────────────────────────────────────────
ipcMain.handle('print:html', async (e, html) => {
  const os = require('os');
  const tmpHtml = path.join(os.tmpdir(), 'sc-print-' + Date.now() + '.html');
  const tmpPdf  = path.join(os.tmpdir(), 'sc-print-latest.pdf');
  fs.writeFileSync(tmpHtml, html, 'utf8');

  const printWin = new BrowserWindow({
    width: 800, height: 600, show: false,
    webPreferences: { nodeIntegration: false, contextIsolation: true },
  });

  await new Promise(resolve => {
    printWin.loadFile(tmpHtml);
    printWin.webContents.once('did-finish-load', resolve);
  });
  await new Promise(resolve => setTimeout(resolve, 150));

  try {
    const pdfData = await printWin.webContents.printToPDF({
      printBackground: false,
      pageSize: 'Letter',
      margins: { marginType: 'printableArea' },
    });
    printWin.destroy();
    try { fs.unlinkSync(tmpHtml); } catch(e2) {}
    fs.writeFileSync(tmpPdf, pdfData);
    shell.openPath(tmpPdf);
    return { success: true };
  } catch(err) {
    printWin.destroy();
    try { fs.unlinkSync(tmpHtml); } catch(e2) {}
    return { success: false, error: err.message };
  }
});

// ── Context menu ───────────────────────────────────────────────────────────────
ipcMain.handle('context:show', (e, opts) => {
  return new Promise(resolve => {
    const { canUndo, canRedo, hasSelection, isBold, isItalic, isUnderline } = opts || {};
    const sender = e.sender;
    const items = [
      { label: 'Undo', accelerator: 'CmdOrCtrl+Z', enabled: !!canUndo, click: () => { sender.send('context:action', 'undo'); } },
      { type: 'separator' },
      { label: 'Cut', role: 'cut', enabled: !!hasSelection },
      { label: 'Copy', role: 'copy', enabled: !!hasSelection },
      { label: 'Paste', role: 'paste' },
      { label: 'Select All', role: 'selectAll' },
      { type: 'separator' },
      { label: isBold ? '✓ Bold' : 'Bold', accelerator: 'CmdOrCtrl+B', click: () => { sender.send('context:action', 'bold'); } },
      { label: isItalic ? '✓ Italic' : 'Italic', accelerator: 'CmdOrCtrl+I', click: () => { sender.send('context:action', 'italic'); } },
      { label: isUnderline ? '✓ Underline' : 'Underline', accelerator: 'CmdOrCtrl+U', click: () => { sender.send('context:action', 'underline'); } },
      { type: 'separator' },
      { label: 'Align Left', click: () => { sender.send('context:action', 'justifyLeft'); } },
      { label: 'Center', click: () => { sender.send('context:action', 'justifyCenter'); } },
      { label: 'Align Right', click: () => { sender.send('context:action', 'justifyRight'); } },

    ];
    const menu = Menu.buildFromTemplate(items);
    menu.popup({ window: BrowserWindow.fromWebContents(sender) });
    resolve();
  });
});

ipcMain.handle('app:get-welcome-data', () => ({ showWelcome: showWelcomePref, recentFiles }));
ipcMain.handle('prefs:set-show-welcome', (e, val) => { showWelcomePref = val; savePrefs(); });

// ── Auto-updater ───────────────────────────────────────────────────────────────
let manualUpdateCheck = false;

function setupAutoUpdater() {
  autoUpdater.autoDownload = false;
  autoUpdater.autoInstallOnAppQuit = true;

  autoUpdater.on('update-available', (info) => {
    manualUpdateCheck = false;
    const notes = info.releaseNotes
      ? (typeof info.releaseNotes === 'string' ? info.releaseNotes : info.releaseNotes.map(n => n.note || '').join('\n')).replace(/<[^>]+>/g, '').trim()
      : '';
    const detail = (notes ? `What's new:\n${notes}\n\n` : '') + 'Would you like to download and install it? The app will restart automatically.';
    dialog.showMessageBox(mainWindow, {
      type: 'info', title: 'Update Available',
      message: `Version ${info.version} is available.`,
      detail,
      buttons: ['Download', 'Later'], defaultId: 0,
    }).then(({ response }) => {
      if (response === 0) {
        autoUpdater.downloadUpdate();
        dialog.showMessageBox(mainWindow, {
          type: 'info', title: 'Downloading Update',
          message: 'Downloading update in the background.',
          detail: 'Screenplay Cards will restart automatically when the download is complete.',
          buttons: ['OK'], defaultId: 0,
        });
      }
    });
  });

  autoUpdater.on('update-not-available', () => {
    if (manualUpdateCheck) {
      manualUpdateCheck = false;
      dialog.showMessageBox(mainWindow, {
        type: 'info', title: 'No Updates Available',
        message: 'Screenplay Cards is up to date.',
        detail: `You are running version ${app.getVersion()}.`,
        buttons: ['OK'],
      });
    }
  });

  autoUpdater.on('update-downloaded', () => {
    dialog.showMessageBox(mainWindow, {
      type: 'info', title: 'Update Ready',
      message: 'Update downloaded.',
      detail: 'Screenplay Cards will restart to apply the update.',
      buttons: ['Restart Now', 'Later'], defaultId: 0,
    }).then(({ response }) => {
      if (response === 0) autoUpdater.quitAndInstall();
    });
  });

  autoUpdater.on('error', (err) => {
    manualUpdateCheck = false;
    console.log('Updater error:', err.message);
    if (!mainWindow) return;
    dialog.showMessageBox(mainWindow, {
      type: 'warning', title: 'Update Failed',
      message: 'Could not download the update.',
      detail: err.message || 'Please check your internet connection and try again.',
      buttons: ['OK'],
    });
  });
}

// ── Menu ───────────────────────────────────────────────────────────────────────
function buildMenu() {
  const recentItems = recentFiles.length > 0
    ? recentFiles.map(f => ({
        label: path.basename(f, '.screenplaycards'),
        click: () => { if (mainWindow) mainWindow.webContents.send('app:check-dirty-then-open', f); },
      }))
    : [{ label: 'No Recent Files', enabled: false }];

  const template = [
    {
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { label: 'Check for Updates…', click: () => { manualUpdateCheck = true; autoUpdater.checkForUpdatesAndNotify(); } },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' }, { role: 'hideOthers' }, { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    {
      label: 'File',
      submenu: [
        { label: 'New Project', accelerator: 'CmdOrCtrl+N', click: () => newProject() },
        { label: 'Open…', accelerator: 'CmdOrCtrl+O', click: () => openFileDialog() },
        {
          label: 'Open Recent',
          submenu: [
            ...recentItems,
            { type: 'separator' },
            {
              label: 'Clear Recent', enabled: recentFiles.length > 0,
              click: () => { recentFiles = []; savePrefs(); buildMenu(); },
            },
          ],
        },
        { type: 'separator' },
        { label: 'Save', accelerator: 'CmdOrCtrl+S', click: () => mainWindow && mainWindow.webContents.send('app:save') },
        { label: 'Save As…', accelerator: 'CmdOrCtrl+Shift+S', click: () => mainWindow && mainWindow.webContents.send('app:save-as') },
        { type: 'separator' },
        { role: 'close' },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { label: 'Undo', accelerator: 'CmdOrCtrl+Z', click: () => mainWindow && mainWindow.webContents.send('app:undo') },
        { label: 'Redo', accelerator: 'CmdOrCtrl+Shift+Z', click: () => mainWindow && mainWindow.webContents.send('app:redo') },
        { type: 'separator' },
        { role: 'cut' }, { role: 'copy' }, { role: 'paste' }, { role: 'selectAll' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { label: 'Grid View', accelerator: 'CmdOrCtrl+1', click: () => mainWindow && mainWindow.webContents.send('app:set-view', 'grid') },
        { label: 'List View', accelerator: 'CmdOrCtrl+2', click: () => mainWindow && mainWindow.webContents.send('app:set-view', 'list') },
        { type: 'separator' },
        { label: 'Flip All Cards', accelerator: 'CmdOrCtrl+F', click: () => mainWindow && mainWindow.webContents.send('app:flip-all') },
        { label: 'Fit All on Screen', accelerator: 'CmdOrCtrl+Shift+F', click: () => mainWindow && mainWindow.webContents.send('app:fit-all') },
        { type: 'separator' },
        { role: 'togglefullscreen' },
        { type: 'separator' },
        { role: 'reload' },
        { role: 'toggleDevTools' },
      ],
    },
    {
      label: 'Card',
      submenu: [
        { label: 'New Card', accelerator: 'CmdOrCtrl+Return', click: () => mainWindow && mainWindow.webContents.send('app:new-card') },
        { type: 'separator' },
        { label: 'Print Outline…', click: () => mainWindow && mainWindow.webContents.send('app:print-outline') },
        { label: 'Print Beat Sheet…', click: () => mainWindow && mainWindow.webContents.send('app:print-beats') },
        { label: 'Print Scene Summary…', click: () => mainWindow && mainWindow.webContents.send('app:print-summary') },
      ],
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' }, { role: 'zoom' },
        { type: 'separator' }, { role: 'front' },
      ],
    },
    {
      label: 'Help',
      submenu: [
        { label: 'Screenplay Cards Website', click: () => shell.openExternal('https://petercarrillo.github.io/screenplay-cards') },
        { label: 'Contact Developer', click: () => shell.openExternal('mailto:screenplaycards@gmail.com') },
      ],
    },
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// ── App lifecycle ──────────────────────────────────────────────────────────────
loadPrefs();

app.on('before-quit', () => { app.isQuitting = true; });

app.whenReady().then(() => {
  buildMenu();
  // Open last recent file if available, otherwise start blank
  const lastFile = recentFiles.length > 0 ? recentFiles[0] : null;
  createWindow(lastFile && require('fs').existsSync(lastFile) ? lastFile : null);
  setupAutoUpdater();

  // Check for updates 3 seconds after launch (packaged app only)
  setTimeout(() => {
    if (app.isPackaged) autoUpdater.checkForUpdatesAndNotify();
  }, 3000);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// Handle file open from Finder / double-click
app.on('open-file', (e, filePath) => {
  e.preventDefault();
  if (mainWindow) {
    mainWindow.webContents.send('app:check-dirty-then-open', filePath);
  } else {
    app.whenReady().then(() => createWindow(filePath));
  }
});
