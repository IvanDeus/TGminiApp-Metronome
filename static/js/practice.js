// main.js
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
export let currentBPM = 90;
export let isPlaying = false;
let metronomeIntervalId = null;

export function playClick() {
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
// Update the setupBPMTouchControl function:
export function setupBPMTouchControl() {
    const bpmControl = document.querySelector('.bpm-control');
    if (!bpmControl) return;

    let isDragging = false;
    const minBPM = 24;
    const maxBPM = 320;

    function calculateBPMFromPosition(clientX) {
        const rect = bpmControl.getBoundingClientRect();
        const position = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        return Math.round(minBPM + (maxBPM - minBPM) * position);
    }

    function handleStart(e) {
        isDragging = true;
        handleMove(e); // Update position immediately on start
        e.preventDefault();
    }

    function handleMove(e) {
        if (!isDragging) return;
        const clientX = e.clientX || (e.touches && e.touches[0].clientX);
        if (clientX) {
            const newBPM = calculateBPMFromPosition(clientX);
            if (newBPM !== currentBPM) {
                currentBPM = newBPM;
                updateBPMDisplay();
                updateBPMLevelIndicator(); // Update visual position
                if (isPlaying) {
                    startMetronome();
                }
            }
        }
        e.preventDefault();
    }

    function handleEnd() {
        if (isDragging) {
            isDragging = false;
            sendUserPrefs();
        }
    }

    bpmControl.addEventListener('mousedown', handleStart);
    bpmControl.addEventListener('touchstart', handleStart);
    document.addEventListener('mousemove', handleMove);
    document.addEventListener('touchmove', handleMove);
    document.addEventListener('mouseup', handleEnd);
    document.addEventListener('touchend', handleEnd);
}
