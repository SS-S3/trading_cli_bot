import typer
from binance.exceptions import BinanceAPIException
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import validate_symbol, validate_side, validate_order_type, validate_quantity, validate_price
from bot.logging_config import logger

app = typer.Typer(help="Binance Futures Testnet Trading Bot")
console = Console()

@app.command()
def ping():
    """Check connection to the Binance Futures Demo API."""
    try:
        client = BinanceFuturesClient()
        if client.ping():
            console.print("[bold green]✔ Connection successful![/bold green]")
        else:
            console.print("[bold red]✘ Connection failed.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]✘ Connection Error:[/bold red] {str(e)}")
        logger.error(f"Ping CLI Error: {str(e)}")

@app.command()
def place(
    symbol: str = typer.Option(..., help="Symbol (e.g., BTCUSDT)"),
    side: str = typer.Option(..., help="Side (BUY/SELL)"),
    order_type: str = typer.Option(..., help="Order Type (MARKET/LIMIT/STOP_LIMIT)"),
    quantity: float = typer.Option(..., help="Quantity to trade"),
    price: Optional[float] = typer.Option(None, help="Price (required for LIMIT and STOP_LIMIT)"),
    stop_price: Optional[float] = typer.Option(None, help="Stop Price (required for STOP_LIMIT)")
):
    """Place an order on Binance Futures Testnet."""
    
    try:
        # Validate inputs
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        
        # Extended validation for STOP_LIMIT (Bonus)
        if order_type.upper() == "STOP_LIMIT":
            if price is None or price <= 0:
                raise ValueError("Price is required for STOP_LIMIT orders.")
            if stop_price is None or stop_price <= 0:
                raise ValueError("Stop Price is required for STOP_LIMIT orders.")
        else:
            order_type = validate_order_type(order_type)
            price = validate_price(price, order_type)

        # Print Request Summary
        console.print(Panel(
            f"[bold blue]Order Request Summary[/bold blue]\n"
            f"Symbol: {symbol}\n"
            f"Side: {side}\n"
            f"Type: {order_type}\n"
            f"Quantity: {quantity}\n"
            + (f"Price: {price}\n" if price else "")
            + (f"Stop Price: {stop_price}\n" if stop_price else ""),
            title="Request"
        ))

        # Initialize client and manager
        client = BinanceFuturesClient()
        manager = OrderManager(client)

        # Place order
        # Handle STOP_LIMIT specifically if needed, but python-binance creates it with create_order
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity
        }
        
        if order_type.upper() == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"
        elif order_type.upper() == "STOP_LIMIT":
            params["type"] = "STOP"
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = "GTC"

        # Note: We use the manager's place_order logic or call client directly for complex types
        if order_type.upper() in ["MARKET", "LIMIT"]:
            response = manager.place_order(symbol, side, order_type, quantity, price)
        else:
            # For STOP_LIMIT or others
            logger.info(f"Placing {order_type} order...")
            response = client.client.futures_create_order(**params)
            logger.info(f"Order response: {response}")

        # Format and display response
        summary = manager.format_response(response)
        
        table = Table(title="Order Response Details", show_header=True, header_style="bold green")
        table.add_column("Field", style="dim")
        table.add_column("Value")

        for key, value in summary.items():
            table.add_row(key, str(value))

        console.print(table)
        console.print("[bold green]✔ Order placed successfully![/bold green]")

    except BinanceAPIException as e:
        console.print(f"[bold red]✘ API Error:[/bold red] {e.message} (Code: {e.code})")
        if e.code == -2014:
            console.print("[yellow]Hint: Your API Key format is invalid. Standard Binance API keys are 64 characters long. Please check your .env file for extra spaces or characters.[/yellow]")
        elif e.code == -2015:
            console.print("[yellow]Hint: Invalid API-key, IP, or permissions. Ensure 'Enable Futures' is checked in your API settings and that your keys are correct for the Demo/Testnet environment.[/yellow]")
        logger.error(f"API Error in CLI: {str(e)}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]✘ Error:[/bold red] {str(e)}")
        logger.error(f"CLI Error: {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
