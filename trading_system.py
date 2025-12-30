"""
Simple Trading System
A basic implementation of a trading system with portfolio management and order execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from decimal import Decimal


class OrderType(Enum):
    """Types of orders supported by the trading system."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Status of an order."""
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class Stock:
    """Represents a stock or tradeable asset."""
    symbol: str
    name: str
    current_price: Decimal
    
    def __str__(self):
        return f"{self.symbol} ({self.name}) - ${self.current_price}"


@dataclass
class Order:
    """Represents a trading order."""
    order_id: int
    symbol: str
    order_type: OrderType
    quantity: int
    price: Decimal
    timestamp: datetime = field(default_factory=datetime.now)
    status: OrderStatus = OrderStatus.PENDING
    
    def execute(self):
        """Mark the order as executed."""
        self.status = OrderStatus.EXECUTED
    
    def cancel(self):
        """Cancel the order."""
        self.status = OrderStatus.CANCELLED
    
    def __str__(self):
        return f"Order #{self.order_id}: {self.order_type.value} {self.quantity} {self.symbol} @ ${self.price} - {self.status.value}"


@dataclass
class Position:
    """Represents a position in a stock."""
    symbol: str
    quantity: int
    average_price: Decimal
    
    @property
    def total_cost(self) -> Decimal:
        """Calculate the total cost of the position."""
        return self.average_price * Decimal(self.quantity)
    
    def __str__(self):
        return f"{self.symbol}: {self.quantity} shares @ ${self.average_price} avg (Total: ${self.total_cost})"


class Portfolio:
    """Manages a trading portfolio with positions and cash."""
    
    def __init__(self, initial_cash: Decimal = Decimal("10000.00")):
        self.cash: Decimal = initial_cash
        self.positions: Dict[str, Position] = {}
        self.order_history: List[Order] = []
    
    def add_position(self, symbol: str, quantity: int, price: Decimal):
        """Add or update a position in the portfolio."""
        if symbol in self.positions:
            existing = self.positions[symbol]
            total_quantity = existing.quantity + quantity
            total_cost = existing.total_cost + (price * Decimal(quantity))
            new_avg_price = total_cost / Decimal(total_quantity)
            self.positions[symbol] = Position(symbol, total_quantity, new_avg_price)
        else:
            self.positions[symbol] = Position(symbol, quantity, price)
    
    def remove_position(self, symbol: str, quantity: int) -> bool:
        """Remove shares from a position."""
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        if position.quantity < quantity:
            return False
        
        position.quantity -= quantity
        if position.quantity == 0:
            del self.positions[symbol]
        
        return True
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get a position by symbol."""
        return self.positions.get(symbol)
    
    def get_total_value(self, market_prices: Dict[str, Decimal]) -> Decimal:
        """Calculate total portfolio value including cash and positions."""
        total = self.cash
        for symbol, position in self.positions.items():
            if symbol in market_prices:
                total += market_prices[symbol] * Decimal(position.quantity)
        return total
    
    def __str__(self):
        lines = [f"Portfolio - Cash: ${self.cash}"]
        lines.append("Positions:")
        for position in self.positions.values():
            lines.append(f"  {position}")
        return "\n".join(lines)


class TradingSystem:
    """Main trading system that manages orders and portfolio."""
    
    def __init__(self, initial_cash: Decimal = Decimal("10000.00")):
        self.portfolio = Portfolio(initial_cash)
        self.market_data: Dict[str, Stock] = {}
        self.order_counter = 0
    
    def add_stock(self, symbol: str, name: str, price: Decimal):
        """Add a stock to the market data."""
        self.market_data[symbol] = Stock(symbol, name, price)
    
    def update_price(self, symbol: str, new_price: Decimal):
        """Update the price of a stock."""
        if symbol in self.market_data:
            self.market_data[symbol].current_price = new_price
    
    def get_stock(self, symbol: str) -> Optional[Stock]:
        """Get stock information."""
        return self.market_data.get(symbol)
    
    def place_order(self, symbol: str, order_type: OrderType, quantity: int, price: Optional[Decimal] = None) -> Optional[Order]:
        """Place a buy or sell order."""
        if symbol not in self.market_data:
            print(f"Error: Stock {symbol} not found in market data")
            return None
        
        stock = self.market_data[symbol]
        order_price = price if price else stock.current_price
        
        self.order_counter += 1
        order = Order(self.order_counter, symbol, order_type, quantity, order_price)
        
        # Execute the order immediately (simplified execution)
        if self._execute_order(order):
            order.execute()
            self.portfolio.order_history.append(order)
            return order
        else:
            order.status = OrderStatus.REJECTED
            self.portfolio.order_history.append(order)
            return None
    
    def _execute_order(self, order: Order) -> bool:
        """Execute an order (internal method)."""
        total_cost = order.price * Decimal(order.quantity)
        
        if order.order_type == OrderType.BUY:
            # Check if we have enough cash
            if self.portfolio.cash < total_cost:
                print(f"Error: Insufficient funds. Need ${total_cost}, have ${self.portfolio.cash}")
                return False
            
            # Execute buy
            self.portfolio.cash -= total_cost
            self.portfolio.add_position(order.symbol, order.quantity, order.price)
            print(f"Executed: Bought {order.quantity} {order.symbol} @ ${order.price} (Total: ${total_cost})")
            return True
        
        elif order.order_type == OrderType.SELL:
            # Check if we have the position
            position = self.portfolio.get_position(order.symbol)
            if not position or position.quantity < order.quantity:
                print(f"Error: Insufficient shares. Need {order.quantity}, have {position.quantity if position else 0}")
                return False
            
            # Execute sell
            self.portfolio.remove_position(order.symbol, order.quantity)
            self.portfolio.cash += total_cost
            print(f"Executed: Sold {order.quantity} {order.symbol} @ ${order.price} (Total: ${total_cost})")
            return True
        
        return False
    
    def get_portfolio_summary(self) -> str:
        """Get a summary of the portfolio."""
        market_prices = {symbol: stock.current_price for symbol, stock in self.market_data.items()}
        total_value = self.portfolio.get_total_value(market_prices)
        
        summary = [str(self.portfolio)]
        summary.append(f"\nTotal Portfolio Value: ${total_value}")
        return "\n".join(summary)


def main():
    """Example usage of the trading system."""
    print("=" * 60)
    print("Welcome to the Trading System")
    print("=" * 60)
    
    # Initialize trading system with $10,000
    trading_system = TradingSystem(Decimal("10000.00"))
    
    # Add some stocks to the market
    trading_system.add_stock("AAPL", "Apple Inc.", Decimal("150.00"))
    trading_system.add_stock("GOOGL", "Alphabet Inc.", Decimal("2800.00"))
    trading_system.add_stock("MSFT", "Microsoft Corporation", Decimal("300.00"))
    trading_system.add_stock("TSLA", "Tesla Inc.", Decimal("200.00"))
    
    print("\nAvailable Stocks:")
    for stock in trading_system.market_data.values():
        print(f"  {stock}")
    
    print("\n" + "=" * 60)
    print("Initial Portfolio:")
    print(trading_system.get_portfolio_summary())
    
    # Place some orders
    print("\n" + "=" * 60)
    print("Placing Orders:")
    print("-" * 60)
    
    trading_system.place_order("AAPL", OrderType.BUY, 10)
    trading_system.place_order("GOOGL", OrderType.BUY, 2)
    trading_system.place_order("MSFT", OrderType.BUY, 15)
    
    print("\n" + "=" * 60)
    print("Portfolio After Purchases:")
    print(trading_system.get_portfolio_summary())
    
    # Update some prices
    print("\n" + "=" * 60)
    print("Market Update - Prices Changed:")
    print("-" * 60)
    trading_system.update_price("AAPL", Decimal("155.00"))
    trading_system.update_price("GOOGL", Decimal("2850.00"))
    trading_system.update_price("MSFT", Decimal("295.00"))
    
    for stock in trading_system.market_data.values():
        print(f"  {stock}")
    
    print("\n" + "=" * 60)
    print("Portfolio After Price Changes:")
    print(trading_system.get_portfolio_summary())
    
    # Sell some shares
    print("\n" + "=" * 60)
    print("Selling Shares:")
    print("-" * 60)
    trading_system.place_order("AAPL", OrderType.SELL, 5)
    
    print("\n" + "=" * 60)
    print("Final Portfolio:")
    print(trading_system.get_portfolio_summary())
    
    # Show order history
    print("\n" + "=" * 60)
    print("Order History:")
    print("-" * 60)
    for order in trading_system.portfolio.order_history:
        print(f"  {order}")
    
    print("\n" + "=" * 60)
    print("Trading Session Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
