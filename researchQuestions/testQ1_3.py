from shipClass.Ship import Ship
from shipClass.SensedShip import SensedShip
from shipClass.Sensor_basic import Sensor
from tqdm import tqdm

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def sim_Quality_SensedShip(quality, sensor_count, random_seed):
    """Simulate a sensed ship with sensors of a given quality and number of sensors per component."""

    # initialize an auxiliary ship for testing
    aux_ship = Ship(f'Aux_Ship_{quality}_Sensors', 'AuxilaryPropulsionPlant_Reliability_Availability_Data.xlsx', np_rng_num=random_seed)

    # use aux ship to initialize a sensed ship
    sensors = [[(sensor_count, quality) for _ in range(len(sys.comps))] for sysName, sys in aux_ship.systems.items()]
    sensedShip = SensedShip(aux_ship, sensors)
    sensedShip.attach_sensors()
    sensedShip.simulate(720)  # simulate for 720 time steps (hours)
    return sensedShip


def plot_sensor_results(X_vals, Y_vals, Z_vals, mode: str = "surface"):
    """
    Plot sensor simulation results in 3D either as a surface ('surface') or points ('points').

    Parameters
    ----------
    X_vals : array-like
        Sensor probabilities of correct detection.
    Y_vals : array-like
        Number of sensors per component.
    Z_vals : array-like
        Overall sensed accuracy (or other metric).
    mode : str, optional
        Choose 'surface' for a 3D surface plot or 'points' for a scatter plot.
        Default is 'surface'.
    """


    # ---- 3D Plot ----
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    if mode.lower() == "surface":
        X, Y = np.meshgrid(X_vals, Y_vals)
        Z = np.tile(Z_vals, (len(Y_vals), 1))
        surf = ax.plot_surface(X, Y, Z, cmap="RdYlGn", edgecolor="none", alpha=0.9)
    elif mode.lower() == "points":
        ax.scatter(X_vals, Y_vals, Z_vals, c='red', s=50, alpha=0.8, marker='o')
    else:
        raise ValueError("Invalid mode. Use 'surface' or 'points'.")

    ax.set_xlabel("Sensor Probability of Correct Detection", labelpad=10)
    ax.set_ylabel("Number of Sensors per Component", labelpad=10)
    ax.set_zlabel("Overall Sensed State Accuracy (%)", labelpad=10)
    ax.set_title(f"Sensor Detection Accuracy vs Overall Accuracy vs Sensor Count")

    # invert the z-axis
    ax.set_zlim(0, 100)
    ax.view_init(elev=36, azim=45, roll=4) # adjust viewing angle
    plt.tight_layout()
    plt.show()

    # ---- Save Plot ----
    filename = f"sensor_accuracy_{mode}_plot.png"
    fig.savefig(filename, dpi=300)
    print(f"[✔] Saved figure as: {filename}")

    # ---- Export Results ----
    results_df = pd.DataFrame({
        "Sensor_Probability_of_Correct_Detection": X_vals,
        "Number_of_Sensors_per_Component": Y_vals,
        "Overall_Sensed_State_Accuracy": Z_vals,
    })
    csv_filename = "sensor_simulation_results.csv"
    results_df.to_csv(csv_filename, index=False)
    print(f"[✔] Saved results to: {csv_filename}")


def main():
    """Compare the overall sensing accuracy of a few moderate sensors to one really good sensor."""
    num_sims = 100              # number of simulations to average accuracy over
    comparison_limit = 10       # percent accuracy difference to stop simulations
    num_sensors = 3             # initial number of sensors per component
    max_sensors = 12            # maximum number of sensors per component

    # simulate baseline with good sensors
    baseline_accuracy = np.zeros(num_sims)
    with tqdm(total=num_sims, desc="Baseline (Good Sensors)", leave=False) as pbar:
        for i in range(num_sims):
            good_sensedShip = sim_Quality_SensedShip('good', 1, random_seed=i)
            baseline_accuracy[i] = good_sensedShip.checkSensingAccuracy()
            pbar.update(1)
    baseline_accuracy = np.mean(baseline_accuracy)
    print(f"Baseline accuracy with good sensors: {baseline_accuracy:.2f}%")

    # X, Y, Z for plotting
    # X: sensor quality (probability of correct detection) from 0.6 to 0.85
    X_vals = np.linspace(0.25, 0.95, 8)
    print(X_vals)
    
    # Y: number of sensors needed to match baseline accuracy
    Y_vals = np.ones(len(X_vals)) * num_sensors
    
    # Z: overall sensed state accuracy (percentage)
    Z_vals = np.zeros(len(X_vals))

    # For each probability value, vary number of sensors until performance matches baseline
    for i, prob in enumerate(tqdm(X_vals, desc="Varying Sensor Quality", leave=True)):

        # run simulations for a probability value with number of sensors increasing, but not exceeding max_sensors        
        while Y_vals[i] < max_sensors:
            sim_accuracy = np.zeros(num_sims)

            with tqdm(total=num_sims, desc=f"p={prob:.2f}, sensors={int(Y_vals[i])}", leave=False) as sim_pbar:
                for j in range(num_sims):
                    sensedShip = sim_Quality_SensedShip(prob, int(Y_vals[i]), j)
                    sim_accuracy[j] = sensedShip.checkSensingAccuracy()
                    sim_pbar.update(1)
            sensed_accuracy = np.mean(sim_accuracy)

            if abs(sensed_accuracy - baseline_accuracy) <= comparison_limit:
                Z_vals[i] = sensed_accuracy
                Y_vals[i] = int(Y_vals[i])
                break
            else:
                Y_vals[i] += 2

    # Plot the results
    plot_sensor_results(X_vals, Y_vals, Z_vals, mode="points")

if __name__ == "__main__":
    main()
