from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.asserts import Assert, Assume, Cover, Past
from src.ldpc_encoder import LDPC_Encoder

def verification_statements(m):
    #Create Local Reference to the LDPC_Encoder
    LDPC_Encoder = m.submodules.LDPC_Encoder
    
    #Ensure all codewords can be obtained
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b000000000)) #0b0000
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b000110101)) #0b0001
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b001000001)) #0b0010
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b001110100)) #0b0011
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b010011010)) #0b0100
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b010101111)) #0b0101
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b011011011)) #0b0110
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b011101110)) #0b0111
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b100000010)) #0b1000
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b100110111)) #0b1001
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b101000011)) #0b1010
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b101110110)) #0b1011
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b110011000)) #0b1100
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b110101101)) #0b1101
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b111011001)) #0b1110
    m.d.sync+=Cover((LDPC_Encoder.data_output == 0b111101100)) #0b1111

    


    #Ensure invalid codewords cannot be obtained
    m.d.sync+=Cover((LDPC_Encoder.data_output != 0b111111111))


    #Ensure the correct codeword output is obtained for each input word.
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b0000) & (LDPC_Encoder.data_output == 0b000000000))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b0001) & (LDPC_Encoder.data_output == 0b000110101))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b0010) & (LDPC_Encoder.data_output == 0b001000001))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b0011) & (LDPC_Encoder.data_output == 0b001110100))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b0100) & (LDPC_Encoder.data_output == 0b010011010))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b0101) & (LDPC_Encoder.data_output == 0b010101111))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b0110) & (LDPC_Encoder.data_output == 0b011011011))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b0111) & (LDPC_Encoder.data_output == 0b011101110))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b1000) & (LDPC_Encoder.data_output == 0b100000010))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b1001) & (LDPC_Encoder.data_output == 0b100110111))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b1010) & (LDPC_Encoder.data_output == 0b101000011))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b1011) & (LDPC_Encoder.data_output == 0b101110110))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b1100) & (LDPC_Encoder.data_output == 0b110011000))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b1101) & (LDPC_Encoder.data_output == 0b110101101))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b1110) & (LDPC_Encoder.data_output == 0b111011001))
    m.d.sync+=Cover((LDPC_Encoder.data_input == 0b1111) & (LDPC_Encoder.data_output == 0b111101100))
    

    
    #Ensure that done and output signals are reset when start is toggled.
    with m.If((LDPC_Encoder.start == 0) & Past(LDPC_Encoder.start)):
        m.d.sync+=Assert((LDPC_Encoder.done == 0))
        m.d.sync+=Assert((LDPC_Encoder.data_output == 0))

    return


if __name__ == "__main__":

    #Instantiate a command line argument parser
    parser = main_parser()
    args = parser.parse_args()

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

    #Run the design verification
    verification_statements(m)

    main_runner(parser, args, m, ports=[LDPC_Encoder.data_input, LDPC_Encoder.data_output, LDPC_Encoder.start, LDPC_Encoder.done])    
