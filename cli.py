import typer
from binance.exceptions import BinanceAPIException
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import validate_symbol, validate_side, validate_order_type, validate_quantity, validate_price, validate_stop_price
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
    symbol: str = typer.Option(..., "--symbol", "-s", help="Symbol (e.g., BTCUSDT)"),
    side: str = typer.Option(..., "--side", "-d", help="Side (BUY/SELL)"),
    order_type: str = typer.Option(..., "--order-type", "-t", help="Order Type (MARKET/LIMIT/STOP_LIMIT)"),
    quantity: float = typer.Option(..., "--quantity", "-q", help="Quantity to trade"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Price (required for LIMIT/STOP_LIMIT)"),
    stop_price: Optional[float] = typer.Option(None, "--stop-price", help="Stop Price (required for STOP_LIMIT)")
):
    """Place an order on Binance Futures Testnet."""
    
    try:
        # 1. Validation Layer
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        quantity = validate_quantity(quantity)
        price = validate_price(price, order_type)
        stop_price = validate_stop_price(stop_price, order_type)

        # 2. Order Request Summary
        summary_text = (
            f"[bold cyan]Order Request Summary[/bold cyan]\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Symbol:      [yellow]{symbol}[/yellow]\n"
            f"Side:        [bold {'green' if side == 'BUY' else 'red'}]{side}[/bold {'green' if side == 'BUY' else 'red'}]\n"
            f"Type:        [blue]{order_type}[/blue]\n"
            f"Quantity:    [magenta]{quantity}[/magenta]\n"
        )
        if price:
            summary_text += f"Price:       [magenta]{price}[/magenta]\n"
        if stop_price:
            summary_text += f"Stop Price:  [magenta]{stop_price}[/magenta]\n"
        
        console.print(Panel(
            summary_text,
            title="[bold white]Step 1: Request[/bold white]",
            expand=False
        ))

        # 3. API Layer
        client = BinanceFuturesClient()
        manager = OrderManager(client)

        logger.info(f"CLI: Placing {order_type} {side} order for {quantity} {symbol}...")
        
        # 4. Execute Order
        response = manager.place_order(symbol, side, order_type, quantity, price, stop_price)
        
        # 5. Output Response Details
        summary = manager.format_response(response)
        
        table = Table(
            title="[bold green]Step 2: Order Response Details[/bold green]",
            show_header=True,
            header_style="bold white on blue",
            box=None
        )
        table.add_column("Field", style="dim", width=15)
        table.add_column("Value", style="bold")

        for key, value in summary.items():
            color = "green" if key == "status" and value == "FILLED" else "white"
            table.add_row(key, f"[{color}]{value}[/{color}]")

        console.print(table)
        console.print("\n[bold green]✔ SUCCESS: Order placed and processed.[/bold green]")

    except ValueError as e:
        console.print(f"[bold red]✘ Validation Error:[/bold red] {str(e)}")
        logger.error(f"Validation Error: {str(e)}")
        raise typer.Exit(code=1)
    except BinanceAPIException as e:
        console.print(f"[bold red]✘ API Error:[/bold red] {e.message} (Code: {e.code})")
        if e.code == -2014 or e.code == -2015:
            console.print("[yellow]Hint: Please verify your BINANCE_API_KEY and BINANCE_API_SECRET in the .env file. Ensure they are for the Testnet environment.[/yellow]")
        logger.error(f"API Error: {str(e)}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]✘ Unexpected Error:[/bold red] {str(e)}")
        logger.error(f"CLI Error: {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
