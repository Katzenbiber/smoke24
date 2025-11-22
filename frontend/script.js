// Smoke Cloud Visualization with Diffusion Field
const canvas = document.getElementById('smokeCanvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const resetBtn = document.getElementById('resetBtn');
const windSpeedSlider = document.getElementById('windSpeed');
const windSpeedValue = document.getElementById('windSpeedValue');
const originCoords = document.getElementById('originCoords');
const windVector = document.getElementById('windVector');
const debugTable = document.getElementById('debugTable');

// Set canvas dimensions
canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

// Visualization state
let isRunning = false;
let animationId = null;
let windSpeed = 3;
let windDirection = { x: 1, y: 0 }; // Wind direction (normalized)

function updateDebugTable(data) {
    const tbody = debugTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    if (!data) {
        const row = tbody.insertRow();
        const fieldCell = row.insertCell(0);
        const valueCell = row.insertCell(1);
        fieldCell.textContent = 'No data';
        valueCell.textContent = 'Error fetching data';
        return;
    }
    
    // Add data to table
    Object.keys(data).forEach(key => {
        const row = tbody.insertRow();
        const fieldCell = row.insertCell(0);
        const valueCell = row.insertCell(1);
        fieldCell.textContent = key;
        
        if (key === 'data' && data[key] && data[key].length > 0) {
            // For data array, show first few elements
            valueCell.textContent = `[${data[key].slice(0, 5).join(', ')}${data[key].length > 5 ? '...' : ''}] (${data[key].length} elements)`;
        } else {
            valueCell.textContent = String(data[key]);
        }
    });
}

function getSmokeData(timestep) {
    // Fetch smoke data from the server
    return fetch(`http://localhost:5000/smokedata?timestep=${timestep}`)
        .then(response => response.arrayBuffer())
        .then(data => {
            // Decode the protobuf data
            const decodedData = decodeSmokeData(new Uint8Array(data));
            
            // Display in debug table
            updateDebugTable(decodedData);
            
            return decodedData;
        })
        .catch(error => {
            console.error('Error fetching or decoding smoke data:', error);
            updateDebugTable(null);
            return null;
        });
}

getSmokeData(0.1);

// Update particles for rendering
function updateAndDraw() {
}

// Animation loop
function animate() {
}

// Event listeners
startBtn.addEventListener('click', () => {
    if (!isRunning) {
        isRunning = true;
        animate();
    }
});

pauseBtn.addEventListener('click', () => {
    isRunning = false;
    if (animationId) {
        cancelAnimationFrame(animationId);
    }
});

resetBtn.addEventListener('click', () => {
    isRunning = false;
    if (animationId) {
        cancelAnimationFrame(animationId);
    }
    smokeField.reset();
});

// Initialize
originCoords.textContent = `${smokeField.smokeSource.x.toFixed(0)}, ${smokeField.smokeSource.y.toFixed(0)}`;
windVector.textContent = `${windDirection.x.toFixed(2)}, ${windDirection.y.toFixed(2)}`;
