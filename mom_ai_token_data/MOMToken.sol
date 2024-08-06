// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract MOMToken is ERC20, Ownable {
    using SafeMath for uint256;

    constructor() ERC20("MOMToken", "MOM") Ownable(msg.sender) {}

    // 1. Mint on demand and automatically send to the specified wallet address
    function mintAndSend(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }

    // 2. Check out the current circulation of MOM token - i.e. how much has been minted
    function totalMinted() public view returns (uint256) {
        return totalSupply();
    }

    
    }

// GENEEEEESIS CODE