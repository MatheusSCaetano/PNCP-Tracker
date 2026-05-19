const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain, shell } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const http = require("http");

let pythonProcess = null;
let mainWindow = null;
let tray = null;
let isQuitting = false;

// ─── Config ───────────────────────────────────────────────────────────────────
const CONFIG_PATH = path.join(app.getPath("userData"), "config.json");

function loadConfig() {
  if (fs.existsSync(CONFIG_PATH)) {
    try { return JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8")); }
    catch { }
  }
  return { horario: "08:00", ativo: true, email: "", prompt: "" };
}

// ─── Python ───────────────────────────────────────────────────────────────────
function startPython() {
  const isProd = app.isPackaged;

  let cmd, args;
  if (isProd) {
    cmd = path.join(process.resourcesPath, "backend", "backend");
    args = [];
  } else {
    cmd = process.platform === "win32" ? "python" : "python3";
    args = [path.join(__dirname, "../backend/app.py")];
  }

  pythonProcess = spawn(cmd, args, {
    env: { ...process.env },
    cwd: isProd ? path.join(process.resourcesPath, "backend") : path.join(__dirname, "../backend"),
  });

  pythonProcess.stdout.on("data", d => console.log("[Python]", d.toString().trim()));
  pythonProcess.stderr.on("data", d => console.error("[Python ERR]", d.toString().trim()));
  pythonProcess.on("close", code => console.log("[Python] encerrado com código", code));
}

// Aguarda Flask responder antes de carregar a janela
function waitForFlask(retries = 20, delay = 500) {
  return new Promise((resolve, reject) => {
    const attempt = () => {
      http.get("http://localhost:5000/health", res => {
        if (res.statusCode === 200) resolve();
        else retry();
      }).on("error", retry);
    };
    const retry = () => {
      if (retries-- <= 0) reject(new Error("Flask não subiu"));
      else setTimeout(attempt, delay);
    };
    attempt();
  });
}

// ─── Janela principal ─────────────────────────────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: "#0d0f1a",
    titleBarStyle: process.platform === "darwin" ? "hiddenInset" : "default",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    show: false,
    title: "Monitor de Licitações",
  });

  mainWindow.on("ready-to-show", () => mainWindow.show());

  mainWindow.on("close", e => {
    if (!isQuitting) {
      e.preventDefault();
      mainWindow.hide();
      tray && tray.displayBalloon &&
        tray.displayBalloon({ title: "Monitor de Licitações", content: "Rodando em segundo plano." });
    }
  });

  waitForFlask()
    .then(() => mainWindow.loadURL("http://localhost:5000"))
    .catch(() => mainWindow.loadFile(path.join(__dirname, "error.html")));
}

// ─── Bandeja ──────────────────────────────────────────────────────────────────
function createTray() {
  const iconPath = path.join(__dirname, "icon.png");
  const icon = fs.existsSync(iconPath)
    ? nativeImage.createFromPath(iconPath).resize({ width: 16, height: 16 })
    : nativeImage.createEmpty();

  tray = new Tray(icon);
  tray.setToolTip("Monitor de Licitações");

  const rebuildMenu = () => {
    const config = loadConfig();
    const menu = Menu.buildFromTemplate([
      { label: "📋 Abrir painel", click: () => { mainWindow?.show(); mainWindow?.focus(); } },
      { type: "separator" },
      {
        label: "▶ Executar coleta agora",
        click: () => fetch("http://localhost:5000/executar-agora", { method: "POST" })
          .catch(e => console.error("Erro ao executar:", e))
      },
      { label: `⏰ Agendado: ${config.horario} diariamente`, enabled: false },
      { type: "separator" },
      {
        label: "Sair",
        click: () => {
          isQuitting = true;
          pythonProcess?.kill("SIGTERM");
          app.quit();
        }
      },
    ]);
    tray.setContextMenu(menu);
  };

  rebuildMenu();
  tray.on("double-click", () => { mainWindow?.show(); mainWindow?.focus(); });

  // Atualiza o menu quando config mudar
  ipcMain.on("config-updated", rebuildMenu);
}

// ─── IPC ──────────────────────────────────────────────────────────────────────
ipcMain.handle("get-app-version", () => app.getVersion());
ipcMain.handle("open-external", (_, url) => shell.openExternal(url));

// ─── Lifecycle ────────────────────────────────────────────────────────────────
app.whenReady().then(() => {
  startPython();
  createTray();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
    else mainWindow?.show();
  });
});

app.on("before-quit", () => {
  isQuitting = true;
  pythonProcess?.kill("SIGTERM");
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
