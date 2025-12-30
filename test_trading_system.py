"""
Tests for the Trading System
Simple test suite to validate core functionality.
"""

from trading_system import (
    TradingSystem, OrderType, OrderStatus, Stock, Order, Position, Portfolio
)
from decimal import Decimal
import sys


def test_stock_creation():
    """Test stock creation and representation."""
    stock = Stock("AAPL", "Apple Inc.", Decimal("150.00"))
    assert stock.symbol == "AAPL"
    assert stock.name == "Apple Inc."
    assert stock.current_price == Decimal("150.00")
    print("✓ Stock creation test passed")


def test_portfolio_initialization():
    """Test portfolio initialization."""
    portfolio = Portfolio(Decimal("10000.00"))
    assert portfolio.cash == Decimal("10000.00")
    assert len(portfolio.positions) == 0
    print("✓ Portfolio initialization test passed")


def test_add_position():
    """Test adding positions to portfolio."""
    portfolio = Portfolio(Decimal("10000.00"))
    portfolio.add_position("AAPL", 10, Decimal("150.00"))
    
    assert "AAPL" in portfolio.positions
    position = portfolio.get_position("AAPL")
    assert position.quantity == 10
    assert position.average_price == Decimal("150.00")
    print("✓ Add position test passed")


def test_average_price_calculation():
    """Test average price calculation when adding to existing position."""
    portfolio = Portfolio(Decimal("10000.00"))
    portfolio.add_position("AAPL", 10, Decimal("150.00"))
    portfolio.add_position("AAPL", 10, Decimal("160.00"))
    
    position = portfolio.get_position("AAPL")
    assert position.quantity == 20
    assert position.average_price == Decimal("155.00")  # (150*10 + 160*10) / 20
    print("✓ Average price calculation test passed")


def test_remove_position():
    """Test removing shares from a position."""
    portfolio = Portfolio(Decimal("10000.00"))
    portfolio.add_position("AAPL", 10, Decimal("150.00"))
    
    success = portfolio.remove_position("AAPL", 5)
    assert success
    
    position = portfolio.get_position("AAPL")
    assert position.quantity == 5
    print("✓ Remove position test passed")


def test_remove_entire_position():
    """Test removing all shares removes the position."""
    portfolio = Portfolio(Decimal("10000.00"))
    portfolio.add_position("AAPL", 10, Decimal("150.00"))
    
    portfolio.remove_position("AAPL", 10)
    assert "AAPL" not in portfolio.positions
    print("✓ Remove entire position test passed")


def test_buy_order():
    """Test placing and executing a buy order."""
    trading_system = TradingSystem(Decimal("10000.00"))
    trading_system.add_stock("AAPL", "Apple Inc.", Decimal("150.00"))
    
    order = trading_system.place_order("AAPL", OrderType.BUY, 10)
    
    assert order is not None
    assert order.status == OrderStatus.EXECUTED
    assert trading_system.portfolio.cash == Decimal("8500.00")  # 10000 - 1500
    
    position = trading_system.portfolio.get_position("AAPL")
    assert position.quantity == 10
    print("✓ Buy order test passed")


def test_sell_order():
    """Test placing and executing a sell order."""
    trading_system = TradingSystem(Decimal("10000.00"))
    trading_system.add_stock("AAPL", "Apple Inc.", Decimal("150.00"))
    
    # First buy some shares
    trading_system.place_order("AAPL", OrderType.BUY, 10)
    
    # Then sell them
    order = trading_system.place_order("AAPL", OrderType.SELL, 5, Decimal("160.00"))
    
    assert order is not None
    assert order.status == OrderStatus.EXECUTED
    assert trading_system.portfolio.cash == Decimal("9300.00")  # 8500 + 800
    
    position = trading_system.portfolio.get_position("AAPL")
    assert position.quantity == 5
    print("✓ Sell order test passed")


def test_insufficient_funds():
    """Test that orders are rejected when insufficient funds."""
    trading_system = TradingSystem(Decimal("1000.00"))
    trading_system.add_stock("AAPL", "Apple Inc.", Decimal("150.00"))
    
    order = trading_system.place_order("AAPL", OrderType.BUY, 100)  # Would cost $15,000
    
    assert order is None
    assert len([o for o in trading_system.portfolio.order_history if o.status == OrderStatus.REJECTED]) == 1
    print("✓ Insufficient funds test passed")


def test_insufficient_shares():
    """Test that sell orders are rejected when insufficient shares."""
    trading_system = TradingSystem(Decimal("10000.00"))
    trading_system.add_stock("AAPL", "Apple Inc.", Decimal("150.00"))
    
    # Try to sell without owning any shares
    order = trading_system.place_order("AAPL", OrderType.SELL, 10)
    
    assert order is None
    assert len([o for o in trading_system.portfolio.order_history if o.status == OrderStatus.REJECTED]) == 1
    print("✓ Insufficient shares test passed")


def test_portfolio_value_calculation():
    """Test portfolio total value calculation."""
    trading_system = TradingSystem(Decimal("10000.00"))
    trading_system.add_stock("AAPL", "Apple Inc.", Decimal("150.00"))
    trading_system.add_stock("GOOGL", "Alphabet Inc.", Decimal("2800.00"))
    
    trading_system.place_order("AAPL", OrderType.BUY, 10)  # $1,500
    trading_system.place_order("GOOGL", OrderType.BUY, 2)  # $5,600
    
    # Portfolio should have: $2,900 cash + 10 AAPL + 2 GOOGL
    market_prices = {
        "AAPL": Decimal("150.00"),
        "GOOGL": Decimal("2800.00")
    }
    total_value = trading_system.portfolio.get_total_value(market_prices)
    assert total_value == Decimal("10000.00")
    print("✓ Portfolio value calculation test passed")


def test_price_update():
    """Test updating stock prices."""
    trading_system = TradingSystem(Decimal("10000.00"))
    trading_system.add_stock("AAPL", "Apple Inc.", Decimal("150.00"))
    
    trading_system.update_price("AAPL", Decimal("160.00"))
    
    stock = trading_system.get_stock("AAPL")
    assert stock.current_price == Decimal("160.00")
    print("✓ Price update test passed")


def test_order_history():
    """Test that order history is maintained."""
    trading_system = TradingSystem(Decimal("10000.00"))
    trading_system.add_stock("AAPL", "Apple Inc.", Decimal("150.00"))
    
    trading_system.place_order("AAPL", OrderType.BUY, 10)
    trading_system.place_order("AAPL", OrderType.BUY, 5)
    
    assert len(trading_system.portfolio.order_history) == 2
    assert all(order.symbol == "AAPL" for order in trading_system.portfolio.order_history)
    print("✓ Order history test passed")


def run_all_tests():
    """Run all tests."""
    tests = [
        test_stock_creation,
        test_portfolio_initialization,
        test_add_position,
        test_average_price_calculation,
        test_remove_position,
        test_remove_entire_position,
        test_buy_order,
        test_sell_order,
        test_insufficient_funds,
        test_insufficient_shares,
        test_portfolio_value_calculation,
        test_price_update,
        test_order_history,
    ]
    
    print("=" * 60)
    print("Running Trading System Tests")
    print("=" * 60)
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Tests completed: {len(tests) - failed}/{len(tests)} passed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
