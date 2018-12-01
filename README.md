# AutoTrader
Automated stock market trading algorithm framework.

Framework to write 'trader' scripts that can execute a trading strategy for marking profits on a live market.
Originally written with trading APIs for Upstox broker, but it should be easy to replace this APIs from any stock broker
by changing api_helper.py

Aim of the framework is to provide a simulated market that will be built on historical data to test the performance
of stock trading algorithms as well as an environment to run algorithms over live market with real money.
