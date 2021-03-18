#include <fstream>
#include <iostream>

#include "Parameters.h"
#include "model.h"

using namespace std;

int main(void) {
    Parameters::ReadParameters("example/optimization_ini.ini");
    // Minimization function: we are launcihg a projectile in thin
    // athmosphere, and want it to land as close to the target as
    // possible. On the market we can buy cannons that shoot at 100 m/s,
    // so we want to save money and use this kind of a cannon, with as
    // little modification as possible.
    // The target function to optimize is the square of the difference
    // of the landing location and desired landing location,
    // and the square difference of starting velocity and the desired
    // starting velocity multiplied by 100
    //
    const double target_x = 500;
    const double target_v0 = 100;
    double v0 = Parameters::GetValueDouble("optimization_v0", "parameters");
    const double phi =
        Parameters::GetValueDouble("optimization_phi", "parameters");
    double x, vx, vy;
    projectile_flight(v0, phi, x, vx, vy);
    const double d = (x - target_x);
    const double d_v0 = v0 - target_v0;
    const double cost = d * d + d_v0 * d_v0 * 100;

    cout << "Projectile launched at angle " << phi << " and velocity " << v0
         << " landed at " << x << ", difference from target is " << d
         << ", cost is " << cost << endl;
    {
        std::ofstream f_result("result.txt", std::ios_base::binary);
        f_result << cost;
    }

    return 0;
};
