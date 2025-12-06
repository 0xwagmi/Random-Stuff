// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";
// import {HuffDeployer} from "foundry-huff/HuffDeployer";

// contract Simple {
//     uint256 number;

//     function updateNumber(uint256 newNumber) external {
//         number = newNumber;
//     }

//     function readNumber() external view returns (uint256) {
//         return number;
//     }
// }

// so we gonna rewrite it in huff
// #define macro MAIN() = takes(0) returns(0) {
//     push0 calldataload   // Load the first 32 bytes of calldata
//     0xe0 shr             // Shift right by 224 bits to get the first 4 bytes
//     dup1 0xb63d343f eq read_number jumpi // we use dup1 to duplicate the selector for comparison 
//     0x1b6a2481 eq update_number jumpi // dup not needed here as we already have the selector on stack
//     // If no match -> revert
//     0x00 0x00 revert

//     read_number:
//         // Load storage slot 0
//         0x00 sload
//         0x00         // memory offset 0
//         mstore       // store number at memory[0x00..0x20]
//         0x20         // length = 32
//         0x00         // offset = 0
//         return

//     update_number:
//         0x04 calldataload  // Load the new number from calldata
//         0x00               // storage slot 0
//         sstore             // store new number
//         0x00
//         0x00
//         return
// }




contract HuffFun is Test  { 
     address huffContract;

    function setUp() public {
       
        bytes memory bytecode = hex"602f8060093d393df35f3560e01c8063b63d343f1461001d57631b6a248114610026575f5ffd5b5f545f5260205ff35b6004355f555f5ff3";
          // runtime  5f3560e01c8063b63d343f1461001e5780631b6a248114610027575f5ffd5b5f545f5260205ff35b6004355f555f5ff3
        
        address addr;
        assembly {
            addr := create(0, add(bytecode, 0x20), mload(bytecode))
        }
        require(addr != address(0), "deploy failed");

        huffContract = addr;
    }

    function testNumber() public {
           (bool ok,) = huffContract.call(
            abi.encodeWithSelector(0x1b6a2481, uint256(69))
        );
        require(ok, "call failed");
       
        (bool ok2, bytes memory result) = huffContract.call(
            abi.encodeWithSelector(0xb63d343f)
        );

        require(ok2, "call failed");

        uint256 value = abi.decode(result, (uint256));
        assertEq(value, 69);
    }
} 
