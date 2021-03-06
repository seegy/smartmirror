'use strict';

const {app, BrowserWindow} = require('electron');
const locals = {/* ...*/};
const pug = require('electron-pug')({pretty: true}, locals);
const electron = require('electron');
const dialog = electron.dialog;
const DEBUG = false;
// Standard stuff

var server = require('http').createServer();
var sio = require('../routes/modules/sio');
sio.create(server);
server.listen(3000);

let win;

function createWindow() {
  win= new BrowserWindow({fullscreen: true,
                          title: "SmartMirror"
                        });

  win.loadURL(`file://${__dirname}/../views/index.pug`);

  if(DEBUG){
    win.webContents.openDevTools()
  }

  win.setMenuBarVisibility(false);

  // Emitted when the window is closed.
  win.on('closed', () => {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    win = null
  })
}

app.on('ready', createWindow);

// Disable error dialogs by overriding
// FIX: https://goo.gl/YsDdsS
dialog.showErrorBox = function(title, content) {
    //console.log(`${title}\n${content}`);
};


// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (win === null) {
    createWindow()
  }
})
