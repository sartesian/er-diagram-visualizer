const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    frame: true, // Включаем стандартную рамку
    backgroundColor: '#0D1117', // Устанавливаем цвет фона окна
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }
  });

  win.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

ipcMain.on('generate-json', (event, dbConfig) => {
  const dbConfigJson = JSON.stringify(dbConfig).replace(/"/g, '\\"');
  const command = `python "${path.join(__dirname, 'db_manager.py')}" "${dbConfigJson}"`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      event.sender.send('json-error', stderr || error.message);
      return;
    }

    const filePath = stdout.trim();
    if (filePath && !filePath.startsWith('Error:')) {
      event.sender.send('json-generated', { filePath, dbName: dbConfig.name });
    } else {
      event.sender.send('json-error', filePath || 'Unknown error');
    }
  });
});