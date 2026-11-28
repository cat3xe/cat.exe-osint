import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer('angle');
// Chromium pré-installé dans l'environnement cloud (Linux) : utilisé seulement s'il existe.
// Sur Windows, Remotion télécharge son propre navigateur ; REMOTION_CHROME permet de forcer un chemin.
import {existsSync} from 'node:fs';
const cloudChrome = '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome';
const exe = process.env.REMOTION_CHROME ?? (existsSync(cloudChrome) ? cloudChrome : undefined);
if (exe) {
  Config.setBrowserExecutable(exe);
}
