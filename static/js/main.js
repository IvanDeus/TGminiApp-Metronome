// main.js
import * as practice from './practice.js';

let userId = null;

// Send user preferences to the server
function sendUserPrefs() {
    if (userId === null) {
        console.warn("User ID not available. Cannot save preferences.");
        return;
    }
    const formData = new URLSearchParams();
    formData.append('user_id', userId);
    formData.append('bpm', practice.currentBPM);
    //console.log("Sending preferences:", formData.toString());
    if (navigator.sendBeacon) {
        const success = navigator.sendBeacon('update_user_prefs', formData);
        if (!success) {
            console.warn("Failed to send beacon");
        }
    } else {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', 'update_user_prefs', false);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.send(formData);
    }
}
// --- Load metr.html via AJAX ---
function loadMetronomeHTML(callback) {
    fetch('static/html/metr.html')
        .then(response => {
            if (!response.ok) throw new Error("Failed to load metr.html");
            return response.text();
        })
        .then(html => {
            const appContainer = document.getElementById('app');
            if (appContainer) {appContainer.innerHTML = html;}
            if (callback) callback();
        })
        .catch(err => {
            console.error("Error loading metr.html:", err);
            showErrorMessage("Failed to load app interface.");
        });
}
// --- TELEGRAM INIT FUNCTION ---
if (window.Telegram && Telegram.WebApp) {
    const initData = Telegram.WebApp.initData;

    fetch('init_telegram', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `initData=${encodeURIComponent(initData)}`
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
    })
    .then(data => {
        loadMetronomeHTML(() => {  
        userId = data.user_id;
        updateBPMDisplay();
        updateBPMLevelIndicator();
        const profilePic = document.getElementById('profile-pic');
        if (profilePic) {
            profilePic.style.backgroundImage = `url('${data.photo_url}')`;
        }

        const profileNameElement = document.getElementById("profile-name");
        if (profileNameElement) {
           profileNameElement.innerText = `[ ${data.first_name} ]`;
        }

        setupButtonHandlers();
        setupBPMTouchControl();
        // --- Save preferences ---
        setInterval(sendUserPrefs, 53000); // Every 53 seconds
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                sendUserPrefs();
            }
        });
     });
    })
    .catch(error => {
        console.error('Init failed:', error);
        showErrorMessage("This app only works inside Telegram");
    });
}
function showErrorMessage(message) {
    document.body.innerHTML = `<div class="telegram-error">${message}</div>`;
}
// Disable context menu
 document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    }, false);
