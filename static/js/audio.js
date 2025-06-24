// audio.js
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
// Resume AudioContext if suspended
if (audioContext.state === 'suspended') { audioContext.resume(); }
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
