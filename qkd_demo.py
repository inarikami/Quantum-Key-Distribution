"""

Create and simulate a quantum key exchange in cirq and initiate a symmetrically encrypted channel

BB84 protocols

Alice --------------> Bob

16 qubit Circuit w/o Eve: 
0: ────X───H───M───────

1: ────H───M───────────

2: ────H───M───────────

3: ────X───H───M───────

4: ────H───H───M───────

5: ────H───M───────────

6: ────M───────────────

7: ────X───H───M───────

8: ────H───H───M───────

9: ────M───────────────

10: ───H───H───M───────

11: ───M───────────────

12: ───H───H───M───────

13: ───X───H───H───M───

14: ───H───M───────────

15: ───M───────────────


Alice ------\-------> Bob
            ^Eve

16 qubit Circuit w/ Eve: 
0: ────X───M───────────────X───M───────────

1: ────X───H───M───────────H───M───────────

2: ────X───H───H───M───────X───H───M───────

3: ────H───M───────────────X───H───M───────

4: ────X───H───H───M───────X───H───H───M───

5: ────M───────────────────M───────────────

6: ────H───H───M───────────H───H───M───────

7: ────H───H───M───────────H───M───────────

8: ────X───H───M───────────H───M───────────

9: ────H───H───M───────────H───M───────────

10: ───H───M──────────────X───M───────────

11: ───X───M──────────────X───H───M───────

12: ───X───M──────────────X───M───────────

13: ───H───M──────────────X───H───M───────

14: ───H───M──────────────X───H───H───M───

15: ───X───H───M──────────X───M───────────

"""

import random
from numpy.random import randint
import numpy as np
import cirq 
import socket
import argparse

#refer to https://qiskit.org/textbook/ch-algorithms/quantum-key-distribution.html


def main(msg='hi', key_size=10, eve=False, repetitions=1):

    print(f"Input Message: {msg}")
    bit_msg = string_to_bits(msg)
    print(f"Bit Message: {bit_msg}")

    print("Initiating Quantum Key Exchange")

    a_bits = randint(2, size=key_size)
    a_basis = randint(2, size=key_size)
    b_basis = randint(2, size=key_size)

    if eve: # eve interception
        e_basis = randint(2, size=key_size)
        circuit = bb84_circuit(a_bits, a_basis, e_basis)
        print("Circuit 1/2: ")
        print(circuit)
        result = cirq.Simulator().run(circuit, repetitions=repetitions)
        eve_bits = [int(result.measurements[str(i)]) for i in range(key_size)]
        circuit = bb84_circuit(eve_bits, e_basis, b_basis)
        print("Circuit 2/2: ")
        print(circuit)

    else:
        circuit = bb84_circuit(a_bits, a_basis, b_basis)
        print("Circuit: ")
        print(circuit)
    
    b_result = cirq.Simulator().run(circuit, repetitions=repetitions)
    b_bits = [int(b_result.measurements[str(i)]) for i in range(key_size)]

    print("Quantum Key Exchange complete, sampling keys...\n")

    good_bits = [i for i in range(len(a_basis)) if not (a_basis[i]^b_basis[i])]

    a_key = [a_bits[i] for i in range(len(a_basis)) if i in good_bits] 
    b_key = [b_bits[i] for i in range(len(b_basis)) if i in good_bits]

    if a_key == b_key:
        print("No interference detected!")
    else:
        print("Interference detected! Keys do not match!\n Continuing anyway!")
    #encrypt using shared key


    #alice's encrypted message
    encrypted = xor_bits(bit_msg, a_key)
    print(f"Alice's encrypted bits: {encrypted}")

    
    decrypted = xor_bits(encrypted, b_key)
    print(f"Bob's decrypted bits: {decrypted}")

    msg = bits_to_string(decrypted)
    print(f"Bob's Received Message: {msg}")
    



def xor_bits(bits, key):
    xor = []
    for i in range(len(bits)):            
        xor.append(bits[i]^key[i%len(key)])
    return xor


def string_to_bits(string):
    result = []
    for char in string:
        bits = bin(ord(char))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result

def bits_to_string(bits):
    chars = []
    for b in range(int(len(bits) / 8)):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)

def bb84_circuit(a_bits, a_basis, b_basis):

    qubits = [cirq.LineQubit(i) for i in range(len(a_bits))]    

    circuit = cirq.Circuit()

    circuit = build_b92_encoder(circuit, qubits, a_bits, a_basis)

    circuit = build_b92_measurement(circuit, qubits, b_basis)

    return circuit

def build_b92_encoder(circuit, qubits, bits, basis):
    for i in range(len(bits)):
        if bits[i] == 1:
            circuit.append(cirq.X(qubits[i]))
        if basis[i] == 1:
            circuit.append(cirq.H(qubits[i]))
    return circuit

def build_b92_measurement(circuit, qubits, basis):
    for i in range(len(basis)):
        if basis[i] == 1:
            circuit.append(cirq.H(qubits[i]))
    circuit.append(cirq.measure_each(*qubits))
    return circuit


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Quantum Key Exchange')
    # parser.add_argument("--message", required=False, type=str, help="The message to send")
    # parser.add_argument("--key", required=False, type=int, help="The key size to use")
    # parser.add_argument("--eve", required=False, type=bool, help="Whether eve intercepts the message")
    # args = parser.parse_args()
    main("Hello Quantum Key Distribution", 16, False, 1)