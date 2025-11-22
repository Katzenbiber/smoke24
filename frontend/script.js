import { decodeSmokeData } from './modules/smokedata_pb2.js'

// Smoke Cloud Visualization with Diffusion Field
const canvas = document.getElementById('smokeCanvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('startBtn');
const timeSlider = document.getElementById('timeStep');
const timeValue = document.getElementById("timeStepValue");

// Update label when slider moves
timeSlider.addEventListener("input", () => {
    timeValue.textContent = timeSlider.value;
});

const originCoords = document.getElementById('originCoords');
const windVector = document.getElementById('windVector');
const debugTable = document.getElementById('debugTable');

// Set canvas dimensions
canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

// Visualization state
let isRunning = false;
let animationId = null;

let windDirection = { x: 1, y: 0 }; // Wind direction (normalized)

const img = new Image();
img.src = "frontend/data/houses.png";   // your picture

img.onload = () => {
    // adjust canvas to image size
    canvas.width = img.width;
    canvas.height = img.height;

    // draw the picture
    ctx.drawImage(img, 0, 0);
};

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

// Update particles for rendering
function updateAndDraw() {
    // Get smoke data
    getSmokeData(800).then(data => {
        if (!data || !data.data || !data.width || !data.height) {
            console.error('Invalid smoke data structure');
            return;
        }

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const canvas_ratio = canvas.width / canvas.height;
        const data_ratio = data.delta_x * data.width / (data.delta_y * data.height);

        let cell_width_px = 0;
        let cell_height_px = 0;

        if (data_ratio >= canvas_ratio) {
            cell_height_px = canvas.height / data.height;
            cell_width_px = cell_height_px * data_ratio;
        } else {
            cell_width_px = canvas.width / data.width;
            cell_height_px = cell_width_px / data_ratio;
        }

        // Iterate through all smoke data points
        for (let y = 0; y < data.height; y++) {
            for (let x = 0; x < data.width; x++) {

                let xpos = x * cell_width_px;
                let ypos = y * cell_height_px;

                // Set cell color with transparency based on density
                ctx.fillStyle = `rgba(255, 255, 255, ${data.data[y * data.width + x] * 1000000})`;

                // Draw cell
                ctx.fillRect(
                    xpos,
                    ypos,
                    cell_width_px,
                    cell_height_px
                );
            }
        }
    }).catch(error => {
        console.error('Error in updateAndDraw:', error);
    });
}

updateAndDraw();

// Animation loop
function animate() {
    if (!isRunning) return;

    updateAndDraw();
    animationId = requestAnimationFrame(animate);
}

// Event listeners
startBtn.addEventListener('click', () => {
    if (!isRunning) {
        isRunning = true;
        animate();
    }
});

timeSlider.addEventListener("input", () => {
    const t = parseFloat(timeSlider.value);
    timeValue.textContent = t;

    getSmokeData(t);   // TODO unit
});
// Initialize
try {
    originCoords.textContent = `${smokeField.smokeSource.x.toFixed(0)}, ${smokeField.smokeSource.y.toFixed(0)}`;
    windVector.textContent = `${windDirection.x.toFixed(2)}, ${windDirection.y.toFixed(2)}`;
} catch (e) {
    // If smokeField is not defined, provide default values
    console.warn('smokeField not defined, using default values');
    originCoords.textContent = `0, 0`;
    windVector.textContent = `${windDirection.x.toFixed(2)}, ${windDirection.y.toFixed(2)}`;
}
