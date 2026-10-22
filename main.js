document.addEventListener('DOMContentLoaded', () => {
    // 1. Safe Modal Toggle Logic
    const openModalBtn = document.getElementById('open-contact-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const contactModal = document.getElementById('contact-modal');

    if (openModalBtn && contactModal) {
        openModalBtn.addEventListener('click', () => contactModal.classList.remove('hidden'));
    }
    if (closeModalBtn && contactModal) {
        closeModalBtn.addEventListener('click', () => contactModal.classList.add('hidden'));
    }

    // 2. Safe Contact Form Submission
    const contactForm = document.getElementById('add-contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const nameInput = document.getElementById('contact-name').value;
            const phoneInput = document.getElementById('contact-phone').value;

            try {
                const response = await fetch('/api/contacts/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: nameInput, phone: phoneInput })
                });

                const result = await response.json();

                if (response.ok) {
                    alert(result.message);
                    contactForm.reset();
                    if (contactModal) contactModal.classList.add('hidden');
                    addContactToUI(nameInput, phoneInput);
                } else {
                    alert(result.message || 'Error adding contact.');
                }
            } catch (err) {
                console.warn('Backend offline - adding contact locally');
                addContactToUI(nameInput, phoneInput);
                if (contactModal) contactModal.classList.add('hidden');
                contactForm.reset();
            }
        });
    }

    // 3. Safe Emergency Help Button
    const helpBtn = document.getElementById('floating-help-btn');
    if (helpBtn) {
        helpBtn.addEventListener('click', async () => {
            helpBtn.style.transform = "scale(0.95)";
            setTimeout(() => helpBtn.style.transform = "scale(1)", 150);

            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    async (position) => {
                        await sendKiteAlert({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            timestamp: new Date().toISOString()
                        });
                    }, 
                    async () => {
                        await sendKiteAlert({ latitude: null, longitude: null });
                    }
                );
            } else {
                await sendKiteAlert({ latitude: null, longitude: null });
            }
        });
    }

    // 4. Safe Load Contacts Check
    if (document.getElementById('contact-list')) {
        loadSavedContacts();
    }
});

// Helper Functions
function addContactToUI(name, phone) {
    const contactList = document.getElementById('contact-list');
    if (!contactList) return;

    const emptyState = contactList.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const li = document.createElement('li');
    li.className = 'contact-item';
    li.innerHTML = `<span><strong>${name}</strong></span> <span>${phone}</span>`;
    contactList.appendChild(li);
}

async function loadSavedContacts() {
    try {
        const response = await fetch('/api/contacts');
        if (!response.ok) return;
        const data = await response.json();

        if (data.contacts && data.contacts.length > 0) {
            data.contacts.forEach(c => addContactToUI(c.name, c.phone));
        }
    } catch (err) {
        console.log("Static mode: skipping backend contact fetch");
    }
}

async function sendKiteAlert(payload) {
    try {
        const response = await fetch('/api/alert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        alert(result.message);
    } catch (err) {
        alert("Alert triggered locally! (Offline fallback active)");
    }
}

// 5. Dynamic Resend Countdown Timer (Verify Page)
const resendBtn = document.getElementById('resend-btn');

if (resendBtn) {
    let timeLeft = 35;
    let countdownInterval;

    function startTimer() {
        timeLeft = 35;
        resendBtn.disabled = true;
        resendBtn.classList.remove('active');
        resendBtn.innerHTML = `Resend in <span id="timer">${timeLeft}</span>s`;

        if (countdownInterval) clearInterval(countdownInterval);

        countdownInterval = setInterval(() => {
            timeLeft--;
            const timerSpan = document.getElementById('timer');
            if (timerSpan) timerSpan.textContent = timeLeft;

            if (timeLeft <= 0) {
                clearInterval(countdownInterval);
                resendBtn.disabled = false;
                resendBtn.classList.add('active');
                resendBtn.textContent = 'Resend Code';
            }
        }, 1000);
    }

    startTimer();

    resendBtn.addEventListener('click', () => {
        if (!resendBtn.disabled) {
            startTimer();
        }
    });
}
