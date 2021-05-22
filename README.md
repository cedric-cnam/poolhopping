# A NEW APPROACH FOR BITCOIN POOL-HOPPING DETECTION

## DESCRIPTION

The project was carried out as a master thesis work for the Politecnico di Milano at CNAM Paris. It is a new approach to detect pool-hopping and aims to measure the presence of the phenomenon in the recent part of the blockchain. Specifically what we want to understand are the differences in earnings between static miners and hoppers, if any. Since reward methods such as PPS and PPLNS are adopted by the considered pools, the revenue should be earned equally. The considered pools have similar hash rates in the May-July 2020 period and are Ant Pool, BTC Pool, F2 Pool, Huobi Pool and Poolin Pool.
The project is organized into three main phases:
- Reward distribution analysis and pool ownership assignment.
- Identification of miners
- Definition of the time with respect to the minimum payout threshold  
- Identification and distinction of hoppers

## INSTRUCTIONS

1. Download the blockchain from Bitcoincore.com, following the [guide](https://bitcoin.org/en/full-node#initial-block-downloadibd).
2. Use Python 2.7 and install Bitcoin library with command __pip install python-bitcoinlib__
3. Run the script in the following order:
  - analyseTransactions.py
  - analyseCoinbaseTransactions.py
  - analyseRevenueStream.py
  - minersIdentification.py
  - homonymsCollection.py
  - rewardsRegistry.py
  - epochsSchedule.py
  - hoppersCategorization.py
  - roundsSchedule.py
  - windowing.py
  - graphics.py

_Note_:
The first and the second script ask for the local directory of the blockchain.
In all the other cases the inputs required are 'first' and 'last'. They refer to number of the first and last file to analyze. Example: for file blk00757.dat the number to input is 0757.

### Contributors
- Eugenio Cortesi, CNAM/POLIMI
- Stefano Secci, CNAM
- Sami Taktak, CNAM

## License & copyright
Licensed under [Apache 2.0 License](LICENSE).
