from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner
from src.ldpc_encoder import LDPC_Encoder

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

    main_runner(parser, args, m, ports=[LDPC_Encoder.data_input, LDPC_Encoder.data_output, LDPC_Encoder.start, LDPC_Encoder.done])    
