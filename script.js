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

// Set canvas dimensions
canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

// Visualization state
let isRunning = false;
let animationId = null;
let windSpeed = 3;
let windDirection = { x: 1, y: 0 }; // Wind direction (normalized)

// Smoke field implementation
class SmokeField {
    constructor(width, height) {
        this.width = width;
        this.height = height;
        this.smokeData = new Float32Array(width * height);
        this.newSmokeData = new Float32Array(width * height);
        this.velocityX = new Float32Array(width * height);
        this.velocityY = new Float32Array(width * height);
        this.diffusion = 0.0001;
        this.advection = 0.05;
        this.smokeSource = { x: width / 2, y: height / 2 };
        
        // Initialize with zeros
        this.reset();
    }
    
    reset() {
        this.smokeData.fill(0);
        this.newSmokeData.fill(0);
        this.velocityX.fill(0);
        this.velocityY.fill(0);
    }
    
    addSmoke(x, y, amount) {
        const radius = 20;
        const startX = Math.max(0, Math.floor(x - radius));
        const endX = Math.min(this.width, Math.floor(x + radius));
        const startY = Math.max(0, Math.floor(y - radius));
        const endY = Math.min(this.height, Math.floor(y + radius));
        
        for (let j = startY; j < endY; j++) {
            for (let i = startX; i < endX; i++) {
                const dx = i - x;
                const dy = j - y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < radius) {
                    const idx = j * this.width + i;
                    this.smokeData[idx] += amount * (1 - distance / radius);
                    this.smokeData[idx] = Math.min(1, this.smokeData[idx]);
                }
            }
        }
    }
    
    diffuse() {
        // Simple diffusion simulation
        for (let j = 1; j < this.height - 1; j++) {
            for (let i = 1; i < this.width - 1; i++) {
                const idx = j * this.width + i;
                const val = this.smokeData[idx];
                const left = this.smokeData[idx - 1];
                const right = this.smokeData[idx + 1];
                const top = this.smokeData[idx - this.width];
                const bottom = this.smokeData[idx + this.width];
                
                // Simple 5-point diffusion
                this.newSmokeData[idx] = val * 0.8 + 0.05 * (left + right + top + bottom);
            }
        }
        
        // Swap arrays
        const temp = this.smokeData;
        this.smokeData = this.newSmokeData;
        this.newSmokeData = temp;
    }
    
    advect() {
        // Simple advection using wind field
        for (let j = 1; j < this.height - 1; j++) {
            for (let i = 1; i < this.width - 1; i++) {
                const idx = j * this.width + i;
                const vx = windDirection.x * windSpeed * 0.02;
                const vy = windDirection.y * windSpeed * 0.02;
                
                // Simple backtrace advection (simplified for performance)
                const nx = Math.max(0, Math.min(this.width - 1, i - vx * 10));
                const ny = Math.max(0, Math.min(this.height - 1, j - vy * 10));
                
                const nx0 = Math.floor(nx);
                const ny0 = Math.floor(ny);
                const nx1 = nx0 + 1;
                const ny1 = ny0 + 1;
                
                const dx = nx - nx0;
                const dy = ny - ny0;
                
                const idx00 = ny0 * this.width + nx0;
                const idx01 = ny0 * this.width + nx1;
                const idx10 = ny1 * this.width + nx0;
                const idx11 = ny1 * this.width + nx1;
                
                // Bilinear interpolation
                this.newSmokeData[idx] = this.smokeData[idx00] * (1 - dx) * (1 - dy) +
                                       this.smokeData[idx01] * dx * (1 - dy) +
                                       this.smokeData[idx10] * (1 - dx) * dy +
                                       this.smokeData[idx11] * dx * dy;
            }
        }
        
        // Swap arrays  
        const temp = this.smokeData;
        this.smokeData = this.newSmokeData;
        this.newSmokeData = temp;
    }
    
    update() {
        this.diffuse();
        this.advect();
    }
    
    draw(ctx) {
        const imageData = ctx.createImageData(this.width, this.height);
        const data = imageData.data;
        
        for (let j = 0; j < this.height; j++) {
            for (let i = 0; i < this.width; i++) {
                const idx = j * this.width + i;
                const value = this.smokeData[idx];
                const intensity = Math.min(255, Math.floor(value * 255));
                
                const pixelIdx = (j * this.width + i) * 4;
                data[pixelIdx] = 150; // R
                data[pixelIdx + 1] = 150; // G 
                data[pixelIdx + 2] = 150; // B
                data[pixelIdx + 3] = intensity; // A
            }
        }
        
        ctx.putImageData(imageData, 0, 0);
    }
}

// Initialize smoke field
let smokeField = new SmokeField(canvas.width, canvas.height);

// Create smoke source at center
function createSmokeSource() {
    smokeField.addSmoke(smokeField.smokeSource.x, smokeField.smokeSource.y, 0.5);
}

// Update particles for rendering
function updateAndDraw() {
    smokeField.update();
    
    // Add new smoke occasionally
    if (Math.random() < 0.3) {
        createSmokeSource();
    }
    
    // Draw the smoke field
    smokeField.draw(ctx);
    
    // Draw city background
    drawBackground();
    
    // Draw smoke origin point
    ctx.fillStyle = 'rgba(255, 100, 100, 0.8)';
    ctx.beginPath();
    ctx.arc(smokeField.smokeSource.x, smokeField.smokeSource.y, 5, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw wind direction indicator
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(smokeField.smokeSource.x, smokeField.smokeSource.y);
    ctx.lineTo(
        smokeField.smokeSource.x + windDirection.x * 50,
        smokeField.smokeSource.y + windDirection.y * 50
    );
    ctx.stroke();
    
    // Draw wind direction arrow
    const arrowSize = 8;
    const angle = Math.atan2(windDirection.y, windDirection.x);
    ctx.beginPath();
    ctx.moveTo(
        smokeField.smokeSource.x + windDirection.x * 50,
        smokeField.smokeSource.y + windDirection.y * 50
    );
    ctx.lineTo(
        smokeField.smokeSource.x + windDirection.x * 50 - arrowSize * Math.cos(angle - Math.PI/6),
        smokeField.smokeSource.y + windDirection.y * 50 - arrowSize * Math.sin(angle - Math.PI/6)
    );
    ctx.lineTo(
        smokeField.smokeSource.x + windDirection.x * 50 - arrowSize * Math.cos(angle + Math.PI/6),
        smokeField.smokeSource.y + windDirection.y * 50 - arrowSize * Math.sin(angle + Math.PI/6)
    );
    ctx.closePath();
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.fill();
}

// Draw city background
function drawBackground() {
    // Draw subtle city silhouette
    ctx.fillStyle = 'rgba(20, 30, 50, 0.6)';
    for (let i = 0; i < 20; i++) {
        const x = i * 80;
        const height = Math.random() * 150 + 50;
        const width = 60 + Math.random() * 40;
        
        ctx.fillRect(x, canvas.height - height, width, height);
    }
}

// Animation loop
function animate() {
    if (!isRunning) return;
    
    // Clear with semi-transparent overlay for trailing effect
    ctx.fillStyle = 'rgba(10, 15, 30, 0.1)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
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

windSpeedSlider.addEventListener('input', () => {
    windSpeed = parseInt(windSpeedSlider.value);
    windSpeedValue.textContent = windSpeed;
    
    // Randomize wind direction occasionally
    if (Math.random() < 0.1) {
        windDirection = {
            x: Math.random() * 2 - 1,
            y: Math.random() * 2 - 1
        };
        // Normalize
        const length = Math.sqrt(windDirection.x * windDirection.x + windDirection.y * windDirection.y);
        windDirection.x /= length;
        windDirection.y /= length;
    }
    
    // Update wind vector display
    windVector.textContent = `${windDirection.x.toFixed(2)}, ${windDirection.y.toFixed(2)}`;
});

// Initialize
originCoords.textContent = `${smokeField.smokeSource.x.toFixed(0)}, ${smokeField.smokeSource.y.toFixed(0)}`;
windVector.textContent = `${windDirection.x.toFixed(2)}, ${windDirection.y.toFixed(2)}`;

// Draw initial background
drawBackground();