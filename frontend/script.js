// =============== FORM INITIALIZATION ===============
const days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
const container = document.getElementById('days-container');

// Generate day input fields
days.forEach(day => {
    const div = document.createElement('div');
    div.className = 'day-input';
    div.innerHTML = `
        <div class="day-label">${day}</div>
        <div class="input-group">
            <label>Jam mulai:</label>
            <input type="time" id="${day}-start" placeholder="Opsional">
        </div>
        <div class="input-group">
            <label>Durasi (jam):</label>
            <input type="number" id="${day}-duration" min="0" max="8" step="0.5" placeholder="0">
        </div>
    `;
    container.appendChild(div);
});

// =============== FORM SUBMISSION HANDLER ===============
document.getElementById('schedule-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Clear previous results
    document.getElementById('error-message').innerHTML = '';
    document.getElementById('schedule-result').innerHTML = '';

    // Collect form data
    const availability = {};
    days.forEach(day => {
        const start = document.getElementById(`${day}-start`).value || null;
        const duration = parseFloat(document.getElementById(`${day}-duration`).value) || 0;
        availability[day] = { start, duration };
    });

    const payload = {
        availability,
        gender: document.getElementById('gender').value,
        goal: document.getElementById('goal').value,
        targetWeight: parseFloat(document.getElementById('targetWeight').value) || null
    };

    console.log('Sending payload:', payload);

    // Send request to backend
    try {
        const res = await fetch('/api/generate-schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || 'Gagal membuat jadwal');
        }

        renderSchedule(data.schedule);
    } catch (err) {
        document.getElementById('error-message').innerHTML = `<div class="error-message">❌ Error: ${err.message}</div>`;
        console.error('Error:', err);
    }
});

// =============== SCHEDULE DISPLAY FUNCTION ===============
function renderSchedule(schedule) {
    const container = document.getElementById("schedule-result");
    container.innerHTML = "<h2>📋 Jadwal Latihan Anda</h2>";
    container.className = "schedule-result";

    // Display each day's schedule
    for (const [day, details] of Object.entries(schedule)) {
        const dayDiv = document.createElement("div");
        dayDiv.className = "day-schedule";
        
        // Day title with type
        const dayTitle = document.createElement("h3");
        dayTitle.innerHTML = `
            ${day} 
            <span class="day-type">${details.day_type}</span>
        `;
        dayDiv.appendChild(dayTitle);

        // Workout list
        if (details.workouts && details.workouts.length > 0) {
            details.workouts.forEach(workout => {
                const workoutDiv = document.createElement("div");
                workoutDiv.className = "workout-item";
                
                if (workout.type === 'rest') {
                    workoutDiv.innerHTML = `
                        <div class="workout-name">🛌 ${workout.name}</div>
                        <div class="workout-details">Hari istirahat untuk pemulihan otot</div>
                    `;
                } else {
                    workoutDiv.innerHTML = `
                        <div class="workout-name">💪 ${workout.name}</div>
                        <div class="workout-meta">
                            <span class="sets-reps">${workout.sets} set × ${workout.reps} rep</span>
                            <span class="target-muscle">${workout.type}</span>
                        </div>
                        <div class="workout-details">
                            <strong>Target Otot:</strong> ${workout.type}<br>
                            <strong>Repetisi per Set:</strong> ${workout.reps} kali<br>
                            <strong>Jumlah Set:</strong> ${workout.sets} set<br>
                            <strong>Estimasi Waktu:</strong> ${(workout.duration * 60).toFixed(0)} menit
                        </div>
                    `;
                }
                dayDiv.appendChild(workoutDiv);
            });
        }

        container.appendChild(dayDiv);
    }
}