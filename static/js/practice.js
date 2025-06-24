// main.js
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
import { currentBPM } from './main.js';
let isPlaying = false;
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

export function updateBPMDisplay() {
    const display = document.getElementById('bpm-display');
    if (display) {
        const paddedBPM = currentBPM.toString().padStart(3, '0');
        display.textContent = `BPM: ${paddedBPM}`;
    }
}
// Function to handle touch/drag on the BPM line
// Update the BPM level indicator position
export function updateBPMLevelIndicator() {
    const bpmLevel = document.querySelector('.bpm-level');
    if (bpmLevel) {
        const percentage = ((currentBPM - 24) / (320 - 24)) * 100;
        bpmLevel.style.width = `${percentage}%`;
    }
}
// --- Metronome Play/Stop Button Handler ---
const playMetrButton = document.getElementById('playmetr');
if (playMetrButton) {
    playMetrButton.onclick = () => {
        if (isPlaying) {
            // Currently playing, so stop the metronome
            stopMetronome();
            playMetrButton.textContent = 'Start Metronome';
            isPlaying = false;
        } else {
            // Not playing, so start the metronome and save user prefs
            isPlaying = true;
            sendUserPrefs();
            startMetronome();
            playMetrButton.textContent = 'Stop Metronome';
        }
    };
}
}
