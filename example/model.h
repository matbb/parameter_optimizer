#pragma once
// Projectile flight
//

#include <cmath>

void projectile_flight(double v0, double phi, double& x, double& vx, double& vy,
                       const double dt = 1e-3) {
    const double g = -9.81;

    vx = v0 * cos(phi);
    vy = v0 * sin(phi);
    x = 0;
    double t = 0, y = 0;
    double l = 0;

    do {
        const double dx = vx * dt;
        const double dy = vy * dt;
        x += dx;
        y += dy;
        l += sqrt(dx * dx + dy * dy);

        vy += g * dt;

        t += dt;
    } while (y >= 0);
}
