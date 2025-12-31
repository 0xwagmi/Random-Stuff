
### lm 

You need, 
`fd` , `fzf` , `batcat`, `nvim` and `tmux`  installed ,

<ul>
<li>fd ->  https://github.com/sharkdp/fd?tab=readme-ov-file#installation</li>
<li>fzf -> https://github.com/junegunn/fzf?tab=readme-ov-file#installation</li>
<li>bat -> https://github.com/sharkdp/bat?tab=readme-ov-file#installation</li>
<li>nvim -> https://github.com/neovim/neovim </li>
</ul>

---

*In debian distributions fd  is fdfind when we install it through apt so just change fd into fdfind in the code if necessary*
*If you are using a debian distribution recommend to download neovim through brew because apt may install an outdated  neovim version*

</br>

In  your .zshrc/bashrc 
source ~/yourpath/lm.sh

---

### Toggle blur 
Adjust the path to windows terminal settings
`chmod + x  toggle_blur.sh`
In .zshrc or .bashrc add,
 alias toggle= '"yourpath/toogle_blur.sh"' 


---


```bash
gcc   derivative-of-sinx.c  -o   derivative-of-sinx -lm
./derivative-of-sinx

```

### OutPut
```bash
Enter the value of x:69
Dy/Dx of sin(x) at x = 69.00 is 99339037972227161442569042804075463005036525826741750294979977150464.00
Dy/Dx of sin(x) at x = 69.00 is 0.99
Value of cos(x) at x = 69.00 is 0.99
Proof correct
```


```bash
 ./price-chart.sh
Date: 15-08-2023
Bitcoin    :  $ 29206
Ethereum Ξ :  $ 1827.86
Dogecoin Ð :  $ 0.07105
Litecoin Ł :  $ 79.22
Solana SOL :  $ 23.77
Rank Name            Symbol Price           Market Cap
=====================================================================
1    Bitcoin         btc    29206           568161754620
2    Ethereum        eth    1828.13         219540876321
3    Tether          usdt   0.998804        83082527343
4    BNB             bnb    236.64          36409612430
5    XRP             xrp    0.607885        32071888066
6    USD Coin        usdc   1               26039599913
7    Lido Staked Ether steth  1827.81         14860940185
8    Dogecoin        doge   0.071056        9984009012
9    Cardano         ada    0.281205        9850414178
10   Solana          sol    23.78           9657494270


```
