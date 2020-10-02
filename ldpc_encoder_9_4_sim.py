from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.back.pysim import Simulator, Delay
from src.ldpc_encoder import LDPC_Encoder

def testbench_process():
    #Run simulation for input word '101'
    yield data_input.eq(0b0101)
    yield start.eq(1)
    yield Delay(1e-6)
    yield start.eq(0)

    #Delay for 10 clock cycles
    for i in range(6):
        yield Delay(1e-6)

    #Run simulation for input word '110'
    yield data_input.eq(0b1100)
    yield start.eq(1)
    yield Delay(1e-6)
    yield start.eq(0)

    #Delay for 10 clock cycles
    for i in range(6):
        yield Delay(1e-6)

if __name__ == "__main__":

    #Instantiate an nMigen Module
    m = Module()
    
    #Instantiate the Generator Matrix 'G' for generating ldpc Code Words
    #https://en.wikipedia.org/wiki/Low-density_parity-check_code#Example_Encoder

    generatorMatrix = [ [0b100000010],
                        [0b010011010],
                        [0b001000001],
                        [0b000110101] ]

    #Instantiate the LDPC_Encoder Module with the generator matrix and output codeword size as parameters
    m.submodules.LDPC_Encoder = LDPC_Encoder = LDPC_Encoder(generatorMatrix,9)

    #Simulation

    #[SIGNAL] - data_input - A top level signal which connects the 'data_input' signal on the LDPC Encoder
    data_input = Signal(len(generatorMatrix))

    #[SIGNAL] - start - A top level signal which connects the 'start' signal on the LDPC Encoder
    start = Signal(1)

    #Link the local data_input and start signals to the LDPC Input Ports
    m.d.comb += LDPC_Encoder.data_input.eq(data_input)
    m.d.comb += LDPC_Encoder.start.eq(start)

    #Create a simulator instance with the local nMigen module which contains the LDPC Encoder
    sim = Simulator(m)

    #Add a synchronous testbench process to the simulator
    sim.add_sync_process(testbench_process) 

    #Add a clock to the simulator
    sim.add_clock(1e-6)

    #Run the simulation with all input and output ports from the LDPC_Encoder and write out the results
    with sim.write_vcd("test_9_4.vcd", "test_9_4.gtkw", traces=[data_input,start] + LDPC_Encoder.ports()):
       sim.run()