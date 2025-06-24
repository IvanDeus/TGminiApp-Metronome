// main.js
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
import { currentBPM, isPlaying } from './main.js';

let metronomeIntervalId = null;

function playClick() {
    const now = audioContext.currentTime;
    const osc = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    osc.type = 'square';
    osc.frequency.value = 800;
    gainNode.gain.setValueAtTime(0, now);
    gainNode.gain.linearRampToValueAtTime(0.1, now + 0.001);
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.02);

    osc.connect(gainNode);
    gainNode.connect(audioContext.destination);
    osc.start(now);
    osc.stop(now + 0.02);
}

export function startMetronome() {
    // Clear any existing interval to prevent multiple metronomes playing
    if (metronomeIntervalId) {
        clearInterval(metronomeIntervalId);
    }
    const interval = 60000 / currentBPM;
    playClick();
    metronomeIntervalId = setInterval(() => {
        if (isPlaying) playClick();
    }, interval);
}

export function stopMetronome() {
    if (metronomeIntervalId) {
        clearInterval(metronomeIntervalId);
        metronomeIntervalId = null;
    }
}
