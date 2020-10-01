from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.back.pysim import Simulator, Delay
from nmigen.asserts import Assert, Assume, Cover

class LDPC_Encoder(Elaboratable):
    def __init__(self, GeneratorMatrix, codeword_width):

        #[PARAMETER] - codeword_width: Width of the Codeword
        self.codeword_width = int(codeword_width)

        #[PARAMETER] - data_input_length: Width of the data input
        self.data_input_length = int(len(GeneratorMatrix))

        #[CONSTANT] - gen_matrix: A generator matrix constant
        self.gen_matrix =  Array([Const(GeneratorMatrix[_][0],unsigned(self.codeword_width)) for _ in range(self.data_input_length)])

        #[INPUT] - start: The start signal to start the encoding process(codeword)
        self.start = Signal(1)

        #[INPUT] - data_input: The data to be encoded
        self.data_input = Signal(self.data_input_length)
        
        #[OUTPUT] - output: The encoded data (codeword)
        self.output = Signal(self.codeword_width, reset=0)
 
        #[OUTPUT] - done: The done signal to indicate that encoding has completed.
        self.done = Signal(1, reset=0)
    
 
    def ports(self):
        return [self.data_input, self.output, self.start, self.done]

    def elaborate(self, platform):
        #Instantiate the Module
        m = Module()

        #[ARRAY[SIGNAL]] - working_matrix - An array of signals which represents the matrix used to calculate the output codeword.
        working_matrix = Array([Signal(unsigned(self.codeword_width), reset=0) for _ in range(self.data_input_length)])

        #[ARRAY[SIGNAL]] - adder_buffer - An array of signals which is used to accumulate the columns of the working matrix to calculate the codeword
        adder_buffer = Array([Signal(unsigned(self.data_input_length), reset=0) for _ in range(self.codeword_width)])

        #[SIGNAL] - cnt - A signal to count the steps completed in the encoding process
        cnt = Signal(self.data_input_length)
        
        #[SIGNAL] - running - A signal which is used to indicate the pipeline is running.
        running = Signal(1, reset=0)

        #[SIGNAL] - accumulation_completed - A signal which is used to indicate when the accumulation process has completed.
        accumulation_completed = Signal(1)
        
        #[SIGNAL] - data_input_copy - Internal copy of the data_input
        data_input_copy = Signal(self.data_input_length)

        #The accumulation process completes in fixed time complexity in (n-1) clock cycles, where n is the length of the data input
        m.d.comb += accumulation_completed.eq(cnt == self.data_input_length-1)

        #If 'start' is asserted, reset the adder_buffer, cnt, done and output variables.
        with m.If(self.start):
            for i in range(0,self.codeword_width):
                m.d.sync += [
                adder_buffer[i].eq(0)
                ]
            m.d.sync += [
                cnt.eq(0),
                self.done.eq(0),
                self.output.eq(0),
                data_input_copy.eq(self.data_input),
                running.eq(1)
            ]

        #If 'accumulation_completed' is not satisfied, increment cnt
        with m.Elif(~accumulation_completed & running):
            m.d.sync += [
                    cnt.eq(cnt + 1)
                ]
            
        #Complete the first stage of the accumulation - AND the input data with the genmatrix
        #Since this is in the combinatorial domain, there is no penalty as the size of the generator matrix and data input increases
            for i in range(0,self.codeword_width):
                for n in range(0,self.data_input_length):
                    m.d.comb += [
                            working_matrix[n][i].eq(self.gen_matrix[n][i] & data_input_copy[(self.data_input_length-n)-1] )
                    ]
        
        #Accumulate the columns of the matrix, with the Gallagher Modulo 2 rules
            for i in range(0,self.codeword_width):
                for n in range(1,self.data_input_length):
                    if(n==1):
                        m.d.sync += [
                        adder_buffer[i][n].eq(working_matrix[n][i]^working_matrix[n-1][i])
                        ]
                    else:
                        m.d.sync += [
                        adder_buffer[i][n].eq(adder_buffer[i][n-1]^working_matrix[n][i])
                        ]

        #Present the result on the output register and set the 'done' flag.
        with m.Elif(accumulation_completed & running):
            for i in range(0,self.codeword_width):
                m.d.sync += [
                        self.output[i].eq( adder_buffer[i][self.data_input_length-1]),
                        self.done.eq(1),
                        running.eq(0)
                    ]

        return m


def cover_statements(m):
    LDPC_Encoder = m.submodules.LDPC_Encoder
    m.d.sync+=Cover((LDPC_Encoder.output == 0b000000))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b011001))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b110010))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b101011))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b111100))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b100101))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b001110))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b010111))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b000) & (LDPC_Encoder.output == 0b000000))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b011) & (LDPC_Encoder.output == 0b011001))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b110) & (LDPC_Encoder.output == 0b110010))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b101) & (LDPC_Encoder.output == 0b101011))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b111) & (LDPC_Encoder.output == 0b111100))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b100) & (LDPC_Encoder.output == 0b100101))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b001) & (LDPC_Encoder.output == 0b001110))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b010) & (LDPC_Encoder.output == 0b010111))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b011) & (LDPC_Encoder.output != 0b010111))
    return

def testbench_process():
    yield data_input.eq(0b101)
    yield start.eq(1)
    yield Delay(1e-6)
    yield start.eq(0)
    yield Delay(1e-6)
    for i in range(30):
        yield Delay(1e-6)
    yield data_input.eq(0b110)
    yield start.eq(1)
    yield Delay(1e-6)
    yield start.eq(0)
    for i in range(30):
        yield Delay(1e-6)

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    generatorMatrix = [ [0b100101],
                        [0b010111],
                        [0b001110], ]
    m.submodules.LDPC_Encoder = LDPC_Encoder = LDPC_Encoder(generatorMatrix,6)

    cover_statements(m)
    main_runner(parser, args, m, ports=[LDPC_Encoder.data_input, LDPC_Encoder.output, LDPC_Encoder.start, LDPC_Encoder.done])    

    #Simulation
    data_input = Signal(len(generatorMatrix))
    start = Signal(1)
    m.d.comb += LDPC_Encoder.data_input.eq(data_input)
    m.d.comb += LDPC_Encoder.start.eq(start)
   # sim = Simulator(m)
   # sim.add_sync_process(testbench_process) # or sim.add_sync_process(process), see below 
   # sim.add_clock(1e-6)
   # with sim.write_vcd("test.vcd", "test.gtkw", traces=[data_input,start] + LDPC_Encoder.ports()):
    #    sim.run()