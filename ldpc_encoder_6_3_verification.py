from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.asserts import Assert, Assume, Cover, Past
from src.ldpc_encoder import LDPC_Encoder

def verification_statements(m):
    #Create Local Reference to the LDPC_Encoder
    LDPC_Encoder = m.submodules.LDPC_Encoder
    
    #Ensure all codewords can be obtained
    m.d.sync+=Cover((LDPC_Encoder.output == 0b000000))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b011001))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b110010))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b101011))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b111100))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b100101))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b001110))
    m.d.sync+=Cover((LDPC_Encoder.output == 0b010111))


    #Ensure invalid codewords cannot be obtained
    m.d.sync+=Cover((LDPC_Encoder.output != 0b111111))


    #Ensure the correct codeword output is obtained for each input word.
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b000) & (LDPC_Encoder.output == 0b000000))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b011) & (LDPC_Encoder.output == 0b011001))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b110) & (LDPC_Encoder.output == 0b110010))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b101) & (LDPC_Encoder.output == 0b101011))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b111) & (LDPC_Encoder.output == 0b111100))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b100) & (LDPC_Encoder.output == 0b100101))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b001) & (LDPC_Encoder.output == 0b001110))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b010) & (LDPC_Encoder.output == 0b010111))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b011) & (LDPC_Encoder.output != 0b010111))
    

    
    #Ensure that done and output signals are reset when start is toggled.
    with m.If((LDPC_Encoder.start == 0) & Past(LDPC_Encoder.start)):
        m.d.sync+=Assert((LDPC_Encoder.done == 0))
        m.d.sync+=Assert((LDPC_Encoder.output == 0))

    return


if __name__ == "__main__":

    #Instantiate a command line argument parser
    parser = main_parser()
    args = parser.parse_args()

    #Instantiate an nMigen Module
    m = Module()
    
    #Instantiate the Generator Matrix 'G' for generating ldpc Code Words
    #https://en.wikipedia.org/wiki/Low-density_parity-check_code#Example_Encoder

    generatorMatrix = [ [0b100101],
                        [0b010111],
                        [0b001110], ]

    #Instantiate the LDPC_Encoder Module with the generator matrix and output codeword size as parameters
    m.submodules.LDPC_Encoder = LDPC_Encoder = LDPC_Encoder(generatorMatrix,6)

    #Run the design verification
    verification_statements(m)

    main_runner(parser, args, m, ports=[LDPC_Encoder.data_input, LDPC_Encoder.output, LDPC_Encoder.start, LDPC_Encoder.done])    
