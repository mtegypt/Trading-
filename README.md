# Trading System

A simple yet functional trading system implementation in Python that provides core trading functionality including portfolio management, order execution, and market data tracking.

## Features

- **Portfolio Management**: Track cash and stock positions
- **Order Execution**: Place buy and sell orders
- **Market Data**: Manage stock information and prices
- **Position Tracking**: Monitor average prices and total costs
- **Order History**: Keep track of all executed orders

## Installation

This project uses only Python standard library, so no external dependencies are required.

### Requirements
- Python 3.7 or higher

### Setup
```bash
git clone https://github.com/mtegypt/Trading-.git
cd Trading-
```

## Usage

### Running the Demo

Run the example trading session:

```bash
python trading_system.py
```

This will demonstrate:
- Creating a trading system with initial capital
- Adding stocks to the market
- Buying stocks
- Tracking portfolio value
- Price updates
- Selling stocks
- Viewing order history

### Using in Your Code

```python
from trading_system import TradingSystem, OrderType
from decimal import Decimal

# Initialize trading system with $10,000
trading_system = TradingSystem(Decimal("10000.00"))

# Add stocks to the market
trading_system.add_stock("AAPL", "Apple Inc.", Decimal("150.00"))
trading_system.add_stock("GOOGL", "Alphabet Inc.", Decimal("2800.00"))

# Buy stocks
trading_system.place_order("AAPL", OrderType.BUY, 10)
trading_system.place_order("GOOGL", OrderType.BUY, 2)

# Check portfolio
print(trading_system.get_portfolio_summary())

# Update prices
trading_system.update_price("AAPL", Decimal("155.00"))

# Sell stocks
trading_system.place_order("AAPL", OrderType.SELL, 5)

# View order history
for order in trading_system.portfolio.order_history:
    print(order)
```

## Architecture

### Main Components

1. **Stock**: Represents a tradeable asset with symbol, name, and price
2. **Order**: Represents a trading order (buy/sell) with status tracking
3. **Position**: Represents ownership of stock shares with average price calculation
4. **Portfolio**: Manages cash and positions with value tracking
5. **TradingSystem**: Main system that coordinates orders, market data, and portfolio

### Order Types
- `BUY`: Purchase shares
- `SELL`: Sell shares

### Order Status
- `PENDING`: Order created but not executed
- `EXECUTED`: Order successfully completed
- `CANCELLED`: Order cancelled before execution
- `REJECTED`: Order rejected (e.g., insufficient funds)

## Example Output

```
============================================================
Welcome to the Trading System
============================================================

Available Stocks:
  AAPL (Apple Inc.) - $150.00
  GOOGL (Alphabet Inc.) - $2800.00
  MSFT (Microsoft Corporation) - $300.00
  TSLA (Tesla Inc.) - $200.00

============================================================
Initial Portfolio:
Portfolio - Cash: $10000.00
Positions:

Total Portfolio Value: $10000.00

============================================================
Placing Orders:
------------------------------------------------------------
Executed: Bought 10 AAPL @ $150.00 (Total: $1500.00)
Executed: Bought 2 GOOGL @ $2800.00 (Total: $5600.00)
Executed: Bought 15 MSFT @ $300.00 (Total: $4500.00)

============================================================
Portfolio After Purchases:
Portfolio - Cash: $400.00
Positions:
  AAPL: 10 shares @ $150.00 avg (Total: $1500.00)
  GOOGL: 2 shares @ $2800.00 avg (Total: $5600.00)
  MSFT: 15 shares @ $300.00 avg (Total: $4500.00)

Total Portfolio Value: $12000.00
```

## Future Enhancements

Potential improvements for future versions:
- Real-time market data integration
- Advanced order types (limit, stop-loss, etc.)
- Multiple portfolio support
- Performance analytics and reporting
- Risk management features
- Transaction fees and commissions
- Historical data and backtesting
- Web interface or GUI
- Database persistence
- Multi-user support

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

