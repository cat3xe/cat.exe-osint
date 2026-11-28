import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer('angle');
// Chromium pré-installé dans l'environnement (évite un téléchargement).
const exe = process.env.REMOTION_CHROME ?? '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome';
Config.setBrowserExecutable(exe);
