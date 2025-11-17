// static/js/script.js - Updated for Deewanshi Car Center (November 2025)
document.addEventListener('DOMContentLoaded', () => {
    const orb = document.getElementById('orb');
    const conversationLog = document.getElementById('conversation-log');
    const statusText = document.getElementById('status-text');

    let femaleVoice;
    let recognition;
    let isMicEnabled = false;

    // === VOICE SELECTION (Female Indian/English) ===
    function loadFemaleVoice() {
        const voices = speechSynthesis.getVoices();
        femaleVoice = voices.find(v => 
            v.lang.includes('en') && (
                v.name.toLowerCase().includes('female') ||
                v.name.toLowerCase().includes('zira') ||
                v.name.toLowerCase().includes('heera') ||
                v.name.toLowerCase().includes('riya')
            )
        ) || voices.find(v => v.lang === 'en-IN') || voices[0];
    }
    speechSynthesis.onvoiceschanged = loadFemaleVoice;
    loadFemaleVoice();

    // === SPEECH RECOGNITION SETUP ===
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'en-IN';  // Best for Indian English
        recognition.continuous = false;
        recognition.interimResults = false;
    } else {
        statusText.textContent = "Speech Recognition not supported";
        orb.style.display = 'none';
        return;
    }

    // === ADD MESSAGE TO LOG ===
    function addMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `message ${sender}-message`;
        div.textContent = text;
        conversationLog.appendChild(div);
        conversationLog.scrollTop = conversationLog.scrollHeight;
    }

    // === SPEAK TEXT (Browser TTS) ===
    function speak(text) {
        speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        if (femaleVoice) utterance.voice = femaleVoice;
        utterance.rate = 0.9;
        utterance.pitch = 1.1;
        speechSynthesis.speak(utterance);
    }

    // === DISABLE MIC VISUALLY ===
    function disableMic() {
        orb.classList.add('disabled');
        orb.classList.remove('listening');
        isMicEnabled = false;
    }

    // === ENABLE MIC VISUALLY ===
    function enableMic() {
        orb.classList.remove('disabled');
        statusText.textContent = "Click the orb and speak";
        isMicEnabled = true;
    }

    // === START THE CONVERSATION ===
    function startAssistant() {
        statusText.textContent = "Assistant is speaking...";
        disableMic();
        addMessage('assistant', "Good morning! Welcome to Deewanshi Car Center. May I know your name please?");

        fetch('/start', { method: 'POST' })
            .then(r => r.json())
            .then(data => {
                setTimeout(() => {
                    enableMic();
                }, 1500); // Small delay to ensure assistant finishes
            });
    }

    // === ORB CLICK - USER SPEAKS ===
    orb.addEventListener('click', () => {
        if (!isMicEnabled || orb.classList.contains('listening')) return;

        disableMic();
        statusText.textContent = "Listening...";
        orb.classList.add('listening');

        recognition.start();

        recognition.onresult = (e) => {
            const userText = e.results[0][0].transcript;
            addMessage('user', userText);
            statusText.textContent = "Processing...";

            fetch('/listen', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userText })
            })
            .then(r => r.json())
            .then(data => {
                addMessage('assistant', data.reply);

                if (data.done) {
                    statusText.textContent = "Thank you! Have a great day!";
                    disableMic();
                } else if (data.enable_mic !== false) {
                    setTimeout(enableMic, 1000); // Wait for assistant to finish speaking
                }
            })
            .catch(err => {
                console.error(err);
                addMessage('assistant', "Sorry, something went wrong.");
                setTimeout(enableMic, 1000);
            });
        };

        recognition.onerror = () => {
            addMessage('assistant', "I couldn't hear you clearly. Please try again.");
            setTimeout(enableMic, 1000);
        };

        recognition.onend = () => {
            orb.classList.remove('listening');
        };
    });

    // === PARTICLE BACKGROUND (Your beautiful animation) ===
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = innerWidth;
    canvas.height = innerHeight;
    let particlesArray = [];

    class Particle {
        constructor(x, y, dirX, dirY, size) {
            this.x = x; this.y = y;
            this.directionX = dirX; this.directionY = dirY;
            this.size = size;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = '#00f2ff';
            ctx.fill();
        }
        update() {
            if (this.x > canvas.width || this.x < 0) this.directionX = -this.directionX;
            if (this.y > canvas.height || this.y < 0) this.directionY = -this.directionY;
            this.x += this.directionX;
            this.y += this.directionY;
            this.draw();
        }
    }

    function init() {
        particlesArray = [];
        const num = (canvas.width * canvas.height) / 9000;
        for (let i = 0; i < num; i++) {
            const size = Math.random() * 2 + 1;
            const x = Math.random() * (innerWidth - size * 2) + size;
            const y = Math.random() * (innerHeight - size * 2) + size;
            const dirX = (Math.random() * 0.4) - 0.2;
            const dirY = (Math.random() * 0.4) - 0.2;
            particlesArray.push(new Particle(x, y, dirX, dirY, size));
        }
    }

    function connect() {
        for (let a = 0; a < particlesArray.length; a++) {
            for (let b = a; b < particlesArray.length; b++) {
                const dx = particlesArray[a].x - particlesArray[b].x;
                const dy = particlesArray[a].y - particlesArray[b].y;
                const dist = dx * dx + dy * dy;
                if (dist < 20000) {
                    const opacity = 1 - dist / 20000;
                    ctx.strokeStyle = `rgba(0, 242, 255, ${opacity})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                    ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        requestAnimationFrame(animate);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particlesArray.forEach(p => p.update());
        connect();
    }

    window.addEventListener('resize', () => {
        canvas.width = innerWidth;
        canvas.height = innerHeight;
        init();
    });

    init();
    animate();

    // === START THE ASSISTANT ON PAGE LOAD ===
    setTimeout(startAssistant, 800);

        // === ADMIN DATABASE PANEL - MINIMAL ADDITION (Password: deewanshi2005) ===
    const adminBtn = document.getElementById('admin-btn');
    const passwordModal = document.getElementById('password-modal');
    const databaseModal = document.getElementById('database-modal');
    const submitPassword = document.getElementById('submit-password');
    const cancelPassword = document.getElementById('cancel-password');
    const closeDb = document.getElementById('close-db');
    const speakAllBtn = document.getElementById('speak-all-btn');
    const adminPasswordInput = document.getElementById('admin-password');

    const CORRECT_PASSWORD = "deewanshi2005";

    // Triple tap orb to reveal admin button
    let taps = 0;
    orb.addEventListener('click', () => {
        taps++;
        setTimeout(() => taps = 0, 1000);
        if (taps === 3) {
            adminBtn.classList.add('visible');
            speak("Admin access enabled");
        }
    });

    // Open password modal
    adminBtn.addEventListener('click', () => {
        passwordModal.classList.add('active');
        adminPasswordInput.focus();
    });

    // Check password
    function checkPassword() {
        if (adminPasswordInput.value === CORRECT_PASSWORD) {
            passwordModal.classList.remove('active');
            adminPasswordInput.value = '';
            loadAppointments();
            databaseModal.classList.add('active');
            speak("Welcome Admin. Showing all appointments.");
        } else {
            speak("Wrong password");
            alert("Incorrect password!");
        }
    }

    submitPassword.addEventListener('click', checkPassword);
    adminPasswordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') checkPassword();
    });

    cancelPassword.addEventListener('click', () => {
        passwordModal.classList.remove('active');
        adminPasswordInput.value = '';
    });

    closeDb.addEventListener('click', () => {
        databaseModal.classList.remove('active');
    });

    // Load appointments from backend
    async function loadAppointments() {
        try {
            const res = await fetch('/admin/database');
            const data = await res.json();
            const tbody = document.querySelector('#appointments-table tbody');
            tbody.innerHTML = '';

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#aaa;">No appointments found</td></tr>';
                return;
            }

            data.forEach(appt => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${appt.id}</td>
                    <td>${appt.username}</td>
                    <td><strong>${appt.vehicle_no}</strong></td>
                    <td>${new Date(appt.date).toLocaleDateString('en-IN', { day:'numeric', month:'long', year:'numeric' })}</td>
                    <td>${appt.time}</td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error(err);
        }
    }

    // Speak all entries one by one
    speakAllBtn.addEventListener('click', () => {
        const rows = document.querySelectorAll('#appointments-table tbody tr');
        if (rows.length === 0) {
            speak("No appointments to read.");
            return;
        }

        speakAllBtn.disabled = true;
        speakAllBtn.textContent = "Speaking...";

        let i = 0;
        function speakNext() {
            if (i >= rows.length) {
                speakAllBtn.disabled = false;
                speakAllBtn.textContent = "Speak All Entries";
                speak("End of appointment list.");
                return;
            }
            const cells = rows[i].querySelectorAll('td');
            const text = `Appointment ${i + 1}. Name: ${cells[1].textContent}, Vehicle: ${cells[2].textContent}, Date: ${cells[3].textContent}, Time: ${cells[4].textContent}`;
            speak(text);

            const utter = new SpeechSynthesisUtterance(text);
            utter.onend = () => {
                i++;
                setTimeout(speakNext, 600);
            };
            speechSynthesis.speak(utter);
        }
        speakNext();
    });

    // === END OF ADMIN PANEL CODE ===
});
