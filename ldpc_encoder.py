from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner
from nmigen.back.pysim import Simulator, Delay
 
class LDPC_Encoder(Elaboratable):
    def __init__(self, GeneratorMatrix, codeword_width):
        self.codeword_width = int(codeword_width)
        self.data_input_length = int(len(GeneratorMatrix))
        # o = a * b
        self.data_input = Signal(self.data_input_length)
        self.genMatrix =  Array([Const(GeneratorMatrix[_][0],unsigned(self.codeword_width)) for _ in range(self.data_input_length)])


        # result has 2x more bits
        self.output = Signal(self.codeword_width, reset=0)
 
        # used to start our multiplication
        self.start = Signal(1)
 
        # notify us when done
        self.done = Signal(1, reset=0)
    
 
    def ports(self):
        return [self.data_input, self.output, self.start, self.done]

    def elaborate(self, platform):
        m = Module()
        # counter will count the amount of addition we are doing
        cnt = Signal(self.data_input_length)
        Stage1Completed = Signal(1)
        tempMatrix = Array([Signal(unsigned(self.codeword_width), reset=0) for _ in range(self.data_input_length)])
        #we are done when the cnt has reached 'width-1' steps
        m.d.comb += Stage1Completed.eq(cnt == self.data_input_length-1)
        AdderBuffer = Array([Signal(unsigned(self.data_input_length), reset=0) for _ in range(self.codeword_width)])
        #check if we got 'start' asserted, if so reset the output and counter
        with m.If(self.start):
            for i in range(0,self.codeword_width):
                m.d.sync += [
                AdderBuffer[i].eq(0)
                ]
            m.d.sync += [
                cnt.eq(0),
                self.done.eq(0),
                self.output.eq(0),
            ]
        with m.Elif(~Stage1Completed):
            m.d.sync += [
                    cnt.eq(cnt + 1)
                ]
            
            for i in range(0,self.codeword_width):
                for n in range(0,self.data_input_length):
                    m.d.comb += [
                            tempMatrix[n][i].eq(self.genMatrix[n][i] & self.data_input[(self.data_input_length-n)-1] )
                    ]
            for i in range(0,self.codeword_width):
                for n in range(1,self.data_input_length):
                    if(n==1):
                        m.d.sync += [
                        AdderBuffer[i][n].eq(tempMatrix[n][i]^tempMatrix[n-1][i])
                        ]
                    else:
                        m.d.sync += [
                        AdderBuffer[i][n].eq(AdderBuffer[i][n-1]^tempMatrix[n][i])
                        ]

        with m.Elif(Stage1Completed):
            for i in range(0,self.codeword_width):
                m.d.sync += [
                        self.output[i].eq( AdderBuffer[i][self.data_input_length-1]),
                        self.done.eq(1)
                    ]

 
 
        return m
        
if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()
    m = Module()
    generatorMatrix = [ [0b100101],
                        [0b010111],
                        [0b001110], ]
    m.submodules.LDPC_Encoder = LDPC_Encoder = LDPC_Encoder(generatorMatrix,6)
    
    data_input = Signal(len(generatorMatrix))
    output = Signal(9)
    start = Signal(1)
    m.d.comb += LDPC_Encoder.data_input.eq(data_input)
    m.d.comb += LDPC_Encoder.start.eq(start)
    sim = Simulator(m)

    def process():
        yield data_input.eq(0b101)
        yield start.eq(1)
        yield Delay(1e-6)
        yield start.eq(0)
        yield Delay(1e-6)
        for i in range(30):
            yield Delay(1e-6)
        yield data_input.eq(0b101)
        yield start.eq(1)
        yield Delay(1e-6)
        yield start.eq(0)
        for i in range(30):
            yield Delay(1e-6)


    sim.add_sync_process(process) # or sim.add_sync_process(process), see below 
    sim.add_clock(1e-6)
    with sim.write_vcd("test.vcd", "test.gtkw", traces=[data_input,start] + LDPC_Encoder.ports()):
        sim.run()