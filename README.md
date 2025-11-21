# Smoke Cloud Visualization

This is a web-based visualization of smoke cloud spread in a city environment with wind bias. The implementation uses HTML5 Canvas API to render a particle-based smoke system that demonstrates how smoke would disperse based on wind direction.

## Features

- Particle-based smoke simulation with realistic diffusion effects
- Wind direction bias that influences smoke movement
- City grid background with building visualization
- Interactive controls for starting, pausing, and resetting the simulation
- Adjustable wind speed using slider
- Real-time visualization of smoke origin point and wind direction

## How to Run

1. Open `index.html` in a web browser
2. Click "Start Simulation" to begin the visualization
3. Use the "Pause" and "Reset" buttons to control the simulation
4. Adjust wind speed using the slider control

## Technical Details

The visualization uses:
- HTML5 Canvas for rendering
- Particle system with physics simulation
- Wind vector field for directional bias
- Gradient effects for smoke opacity and blend
- City background with building grid and window effects

## Controls

- **Start Simulation**: Begin the smoke diffusion process
- **Pause**: Temporarily halt the animation
- **Reset**: Clear particles and restart from origin
- **Wind Speed Slider**: Adjust the strength of wind bias (0-10 scale)

## Implementation

The smoke particles are created at a central origin point and have:
- Random initial velocity
- Wind bias applied during movement
- Natural drift effects
- Gradual decay and fading
- Size variation for realism