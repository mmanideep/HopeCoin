// HopeCoin ICO

pragma solidity ^0.4.11;

contract HopeCoinICO {
    
    // Maximum number of coins
    
    uint public max_hope_coins = 1000000;
    
    // Conversion Rate
    uint public hope_coins_per_usd = 1000;
    
    
    // Coins bought by investors
    uint public total_hope_coins_bought = 0;
    
    // Mapping from investor to HopeCoins and USD
    mapping(address => uint) equity_hope_coins;
    mapping(address => uint) equity_usd;
    
    // Check if an investor can buy HopeCoins
    modifier can_buy_hope_coins(uint usd_invested){
        require (usd_invested * hope_coins_per_usd + total_hope_coins_bought <= max_hope_coins);
        _;
    }
    
    // Getting the equity in HopeCoins of investor
    
    function equity_in_hope_coins(address investor) external constant returns(uint){
        return equity_hope_coins[investor];
    }
    
    // Getting the equity in USD of investor
    
    function equity_in_usd(address investor) external constant returns(uint){
        return equity_usd[investor];
    }
    
    // Buying HopeCoins
    
    function buy_hope_coins(address investor, uint usd_invested) external can_buy_hope_coins(usd_invested) {
        uint hope_coins_bought = usd_invested * hope_coins_per_usd; 
        equity_hope_coins[investor] += hope_coins_bought;
        equity_usd[investor] += usd_invested;
        total_hope_coins_bought += hope_coins_bought;
    }
    
    // Selling HopeCoins
    
    function sell_hope_coins(address investor, uint hope_coins_to_sell) external can_buy_hope_coins(usd_invested) {
        uint usd_invested = hope_coins_to_sell / hope_coins_per_usd; 
        equity_hope_coins[investor] -= hope_coins_to_sell;
        equity_usd[investor] -= usd_invested;
        total_hope_coins_bought -= hope_coins_to_sell;
    }
    
}

