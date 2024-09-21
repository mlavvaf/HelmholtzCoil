#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 13:40:54 2024

@author: maedeh
"""

import math


class HelmholtzCoils(object):
    '''Calculates the magnetic field produced by a pair of Helmholtz coils
    wound in opposition'''
    mu_0 = 4.*math.pi*1e-7
    resistivity_copper = 1.68e-8  # Resistivity of copper (Ohm·m)

    def __init__(self, turns_per_coil, current_per_coil, coil_radius):
        self.N = int(turns_per_coil)  # Turns per coil
        self.I = float(current_per_coil)  # Current (A) per coil
        self.a = float(coil_radius)  # Common radius (m) of coils
        self.lhcoil_position = -self.a / 2.  # Pos. of left coil (m). (-a/2)
        self.rhcoil_position = self.a / 2.  # Pos. of right coil (m). (a/2)

    def H(self, position):
        '''Magnetic field at position (m) in A/m'''

        return (((4/5) ** (3/2)) * (self.N * self.I)/self.a)

    def centerH(self):
        '''Magnetic field at dead center of coils'''
        return self.H(0)

    def B(self, position):
        '''Flux density at position (m) in mT'''
        return HelmholtzCoils.mu_0 * self.H(position) * 1000

    def centerB(self):
        '''Flux density at dead center of coils'''
        return self.B(0)

    def B_mG(self, position):
        '''Flux density at position (m) in mG'''
        return self.B(position) * 1e4

    def wirelength(self):
        '''Length of wire (m) to make N turns of radius a'''
        coil_circumference = math.pi * 2. * self.a
        wire_per_coil = float(self.N) * coil_circumference
        return 2.*wire_per_coil

    def wire_resistance(self, wire_diameter):
        '''Calculate the total resistance of the wire (Ohms)
        based on diameter (m)'''
        wire_length = self.wirelength()
        # Cross-sectional area of the wire
        wire_area = math.pi * (wire_diameter / 2) ** 2
        return (self.resistivity_copper * wire_length) / wire_area

    def voltage_required(self, wire_diameter):
        '''Calculate the voltage required to drive the current through
        the wire (V)'''
        resistance = self.wire_resistance(wire_diameter)
        return self.I * resistance  # Ohm's Law: V = IR

    def awg_recommendation(self):
        '''Returns a recommendation for AWG wire gauge to use for the
        coils for currents between 0.0125 and 15 Amps.
        Conservative estimate, returns 0 as recommendation for currents
        outside this range.'''
        gauge_current = {10: 15, 11: 10, 14: 5, 16: 3.5, 17: 2.5, 18: 2,
                         20: 1.5, 21: 1.0, 22: 0.75, 24: 0.5, 27: 0.25,
                         30: 0.125, 31: 0.100, 32: 0.075, 34: 0.050,
                         37: 0.025, 40: 0.0125}
        delta = float('inf')
        epsilon = 0.
        awg_rec = 0
        if self.I >= 0.0125 and self.I <= 15:
            for gauge, current in gauge_current.items():
                epsilon = current - self.I
                if epsilon >= 0 and epsilon < delta:
                    delta = epsilon
                    awg_rec = gauge

        return awg_rec

    def awg_diameter(self, awg):
        '''Return the diameter of the wire based on AWG (in meters)'''
        awg_to_diameter = {
            10: 0.002588,
            11: 0.002305,
            12: 0.002053,
            13: 0.001828,
            14: 0.001628,
            15: 0.001450,
            16: 0.001291,
            17: 0.001150,
            18: 0.001024,
            19: 0.0009116,
            20: 0.0008128,
            21: 0.0007229,
            22: 0.0006438
        }
        return awg_to_diameter.get(awg)

    def summary(self, position):
        '''Calculates all relevant parameters and returns
        them in a dictionary'''
        return {
            "Magnetic Field at Position " + str(position) + " (A/m)": self.H(position),
            "Flux Density at Position " + str(position) + " (mT)": self.B(position),
            "Flux Density at Position " + str(position) + " (mG)": self.B_mG(position),
            "Magnetic Field at Center (A/m)": self.centerH(),
            "Flux Density at Center (mT)": self.centerB(),
            "Wire Length (m)": self.wirelength(),
            "AWG Recommendation": self.awg_recommendation(),
            "Voltage Required (V)": self.voltage_required(
                self.awg_diameter(self.awg_recommendation()))
        }

    def custom_B_field_cal(self, gauge, turns, radius, current, position):
        '''Calculates the B field with custom gauge, turns, radius, and current'''
        self.N = turns
        self.a = radius
        self.I = current
        wire_diameter = self.awg_diameter(gauge)
        if wire_diameter is None:
            raise ValueError(f"AWG {gauge} is not in the available list.")
        B_field = self.B(position)
        voltage = self.voltage_required(wire_diameter)

        return {
            "Magnetic Field at Position " + str(position) + " (A/m)": self.H(position),
            "Flux Density at Position " + str(position) + " (mT)": B_field,
            "Flux Density at Position " + str(position) + " (mG)": B_field * 1e4,
            "Magnetic Field at Center (A/m)": self.centerH(),
            "Flux Density at Center (mT)": self.centerB(),
            "Wire Length (m)": self.wirelength(),
            "Voltage Required (V)": voltage
        }


# Example usage of the new custom function:
helmholtz_coils = HelmholtzCoils(
    turns_per_coil=20, current_per_coil=5, coil_radius=0.025)

# Get all results for a position (e.g., 0.05 m from the center)
results = helmholtz_coils.summary(0)

# Custom B-field calculation using specific gauge, turns, radius, current, and position
custom_results = helmholtz_coils.custom_B_field_cal(
    gauge=14, turns=20, radius=0.025, current=1, position=0)

# Print results for comparison
print("\nStandard Results:\n==================")
for key, value in results.items():
    print(f"\n{key}: {value}")

print("\n\nCustom Results:\n================")
for key, value in custom_results.items():
    print(f"\n{key}: {value}")
