from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlmodel import Session, select
from models import Order
from database import engine, init_db

import pandas as pd

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from fastapi.middleware.wsgi import WSGIMiddleware

import plotly.express as px

from datetime import datetime, timezone, timedelta
import time
import logging
from functools import lru_cache
import asyncio
import contextlib
from contextlib import asynccontextmanager
from io import BytesIO

from simple_logging import log_app, log_db
from backup import backup_table_task, backup_table_once
from config import settings


MENU_PRICES = {
    "cheese_roll": 125,
    "paneer_tikka": 125,
    "schezwan_paneer": 125,
    "extra_cheese": 30,
    "normal_brownie": 60,
    "brownie_with_icecream": 80,
    "lime_juice": 20,
    "lemon_soda": 30,
    "margherita": 225,
    "peppy_paneer": 375,
    "farmhouse": 375,
    "choco_lava_cake": 180,
    "french_fries": 70,
    "cheese_nuggets": 70,
    "corn": 50,
    "spiral_potato": 70,
    "rabadi_kulfi": 70,
    "shahi_gulab": 70,
    "strawberry": 70,
    "choclate": 70,
    "pista_badam": 70,
    "malai_kulfi": 70,
}


# Initialize FastAPI app
app = FastAPI()


# Initialize Dash app
dash_app = Dash(
    __name__,
    requests_pathname_prefix="/dashboard/",
    serve_locally=True,
)


# Mount static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# Jinja2 templates folder
templates = Jinja2Templates(directory="templates")


# Initialize DB tables
init_db()


# Simple logging setup
log_app("Food Ordering Application started")
log_app("Database initialized successfully")


@lru_cache(maxsize=1)
def load_students_data():
    """Load and cache student data from Excel file."""
    start_time = time.time()

    try:
        df = pd.read_excel("Rollno.xlsx")

        df["rollno"] = df["rollno"].astype(str)
        df["residence"] = df["residence"].astype(str)
        df["occupancy"] = df["occupancy"].astype(str)

        load_time = (time.time() - start_time) * 1000

        log_app(
            f"Loaded {len(df)} student records "
            f"in {load_time:.2f}ms"
        )

        return df

    except Exception as e:
        load_time = (time.time() - start_time) * 1000

        log_app(
            f"Error loading student data after "
            f"{load_time:.2f}ms: {e}",
            "ERROR",
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to load student data",
        )


# Load Excel file into memory once
students_df = load_students_data()


def calculate_total(row_or_dict):
    """Calculate the total price for an order."""
    total = 0

    for item, price in MENU_PRICES.items():
        qty = row_or_dict.get(item, 0)

        if pd.isna(qty):
            qty = 0

        total += int(qty) * price

    return total


def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is UTC-aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt


def utc_to_ist(utc_dt: datetime) -> str:
    """Convert UTC datetime to IST string."""
    IST_OFFSET = timedelta(hours=5, minutes=30)

    utc_dt = ensure_utc(utc_dt)
    ist_dt = utc_dt + IST_OFFSET

    return ist_dt.strftime("%d-%b-%Y %I:%M %p")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(backup_table_task())

    try:
        yield

    finally:
        task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await task


app.router.lifespan_context = lifespan


# -------------------------------------------------------------------
# BACKUP
# -------------------------------------------------------------------

@app.get("/trigger-backup", response_class=HTMLResponse)
def trigger_backup_page(request: Request):

    try:
        backup_file = backup_table_once()

        message = (
            f"✅ Backup completed successfully: "
            f"{backup_file}"
        )

    except Exception as e:
        message = f"❌ Backup failed: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="backup.html",
        context={
            "message": message,
        },
    )


# -------------------------------------------------------------------
# HOME
# -------------------------------------------------------------------

@app.get("/home", response_class=HTMLResponse)
async def home_get(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "error": None,
        },
    )


# -------------------------------------------------------------------
# LOGIN
# -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def login_get(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
        },
    )


@app.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    rollno: str = Form(...),
):

    start_time = time.time()
    rollno = str(rollno)

    try:

        user_row = students_df[
            students_df["rollno"] == rollno
        ]

        if not user_row.empty:

            name = user_row.iloc[0]["studentName"]
            occupancy = user_row.iloc[0]["occupancy"]
            residence = user_row.iloc[0]["residence"]

            parts = name.split()

            first_name = (
                parts[0]
                if len(parts) > 0
                else ""
            )

            last_name = (
                " ".join(parts[1:])
                if len(parts) > 1
                else ""
            )

            final_name = (
                f"{first_name} {last_name}"
                .strip()
            )

            login_time = (
                time.time() - start_time
            ) * 1000

            log_app(
                f"Successful login for rollno "
                f"{rollno} in {login_time:.2f}ms"
            )

            return templates.TemplateResponse(
                request=request,
                name="User.html",
                context={
                    "name": final_name,
                    "rollno": rollno,
                    "residence": residence,
                    "occupancy": occupancy,
                    "photo": (
                        f"/static/photos/{rollno}.jpg"
                    ),
                },
            )

        else:

            login_time = (
                time.time() - start_time
            ) * 1000

            log_app(
                f"Failed login attempt for invalid "
                f"rollno: {rollno} in "
                f"{login_time:.2f}ms",
                "WARNING",
            )

            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "error": "Invalid roll number",
                },
            )

    except Exception as e:

        login_time = (
            time.time() - start_time
        ) * 1000

        log_app(
            f"Login error for rollno {rollno} "
            f"after {login_time:.2f}ms: {e}",
            "ERROR",
        )

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": (
                    "Login failed. "
                    "Please try again."
                ),
            },
        )


# -------------------------------------------------------------------
# ORDER FORM
# -------------------------------------------------------------------

@app.get("/order_form", response_class=HTMLResponse)
def show_order_form(
    request: Request,
    rollno: str,
):

    return templates.TemplateResponse(
        request=request,
        name="aup.html",
        context={
            "rollno": rollno,
        },
    )


# -------------------------------------------------------------------
# RECEIVE ORDER
# -------------------------------------------------------------------

@app.post("/auc", response_class=HTMLResponse)
def receive_order(
    request: Request,
    rollno: str = Form(...),
    cheese_roll: int = Form(0),
    paneer_tikka: int = Form(0),
    schezwan_paneer: int = Form(0),
    extra_cheese: int = Form(0),
    normal_brownie: int = Form(0),
    brownie_with_icecream: int = Form(0),
    lime_juice: int = Form(0),
    lemon_soda: int = Form(0),
    margherita: int = Form(0),
    peppy_paneer: int = Form(0),
    farmhouse: int = Form(0),
    choco_lava_cake: int = Form(0),
    french_fries: int = Form(0),
    cheese_nuggets: int = Form(0),
    corn: int = Form(0),
    spiral_potato: int = Form(0),
    rabadi_kulfi: int = Form(0),
    shahi_gulab: int = Form(0),
    strawberry: int = Form(0),
    choclate: int = Form(0),
    pista_badam: int = Form(0),
    malai_kulfi: int = Form(0),
):

    start_time = time.time()

    try:

        # Validate rollno
        if rollno not in students_df["rollno"].values:

            return templates.TemplateResponse(
                request=request,
                name="aup.html",
                context={
                    "rollno": rollno,
                    "error": "Invalid roll number",
                },
            )

        # Current UTC timestamp
        last_updated = datetime.now(timezone.utc)

        # Create order data
        order_data = {
            "rollno": rollno,
            "cheese_roll": cheese_roll,
            "paneer_tikka": paneer_tikka,
            "schezwan_paneer": schezwan_paneer,
            "extra_cheese": extra_cheese,
            "normal_brownie": normal_brownie,
            "brownie_with_icecream": brownie_with_icecream,
            "lime_juice": lime_juice,
            "lemon_soda": lemon_soda,
            "margherita": margherita,
            "peppy_paneer": peppy_paneer,
            "farmhouse": farmhouse,
            "choco_lava_cake": choco_lava_cake,
            "french_fries": french_fries,
            "cheese_nuggets": cheese_nuggets,
            "corn": corn,
            "spiral_potato": spiral_potato,
            "rabadi_kulfi": rabadi_kulfi,
            "shahi_gulab": shahi_gulab,
            "strawberry": strawberry,
            "choclate": choclate,
            "pista_badam": pista_badam,
            "malai_kulfi": malai_kulfi,
            "last_updated": last_updated,
        }

        order = Order(**order_data)

        with Session(engine) as session:

            session.add(order)
            session.commit()

            order_time = (
                time.time() - start_time
            ) * 1000

            menu_items = [
                value
                for key, value in order_data.items()
                if key in MENU_PRICES
            ]

            total_items = sum(menu_items)

            log_app(
                f"Order saved for rollno: {rollno} "
                f"in {order_time:.2f}ms - "
                f"Total items: {total_items}"
            )

        return templates.TemplateResponse(
            request=request,
            name="order_success.html",
            context={},
        )

    except Exception as e:

        order_time = (
            time.time() - start_time
        ) * 1000

        log_app(
            f"Error processing order for {rollno} "
            f"after {order_time:.2f}ms: {e}",
            "ERROR",
        )

        return templates.TemplateResponse(
            request=request,
            name="aup.html",
            context={
                "rollno": rollno,
                "error": (
                    "Failed to process order. "
                    "Please try again."
                ),
            },
        )


# -------------------------------------------------------------------
# ADMIN
# -------------------------------------------------------------------

@app.get("/admin", response_class=HTMLResponse)
def view_orders(request: Request):

    with Session(engine) as session:
        result = session.exec(
            select(Order)
        ).all()

    df = pd.DataFrame(
        [
            order.model_dump()
            for order in result
        ]
    )

    menu_items = list(MENU_PRICES.keys())

    if not df.empty:

        df = df.drop(
            columns=["id"],
            errors="ignore",
        )

        keep_cols = [
            "rollno",
            "last_updated",
        ] + list(MENU_PRICES.keys())

        df = df[
            [
                col
                for col in keep_cols
                if col in df.columns
            ]
        ]

        df_summary = (
            df.groupby("rollno")
            .sum(numeric_only=True)
            .reset_index()
        )

        last_times = (
            df[
                ["rollno", "last_updated"]
            ]
            .groupby("rollno")
            .max()
            .reset_index()
        )

        last_times["last_updated"] = (
            last_times["last_updated"]
            .apply(
                lambda x:
                    utc_to_ist(x)
                    if pd.notnull(x)
                    else ""
            )
        )

        df_summary = df_summary.merge(
            last_times,
            on="rollno",
            how="left",
        )

        df_summary["total_cost"] = (
            df_summary
            .apply(
                lambda row:
                    calculate_total(
                        row.to_dict()
                    ),
                axis=1,
            )
        )

        orders = (
            df_summary
            .merge(
                students_df,
                on="rollno",
                how="left",
            )
            .to_dict(
                orient="records"
            )
        )

    else:
        orders = []

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "orders": orders,
            "menu_items": menu_items,
        },
    )


# -------------------------------------------------------------------
# DOWNLOAD ORDERS
# -------------------------------------------------------------------

@app.get("/download")
def download_orders():

    try:

        with Session(engine) as session:
            result = session.exec(
                select(Order)
            ).all()

        df = pd.DataFrame(
            [
                order.model_dump()
                for order in result
            ]
        )

        if df.empty:
            return {
                "message": "No orders to export"
            }

        df = df.drop(
            columns=["id"],
            errors="ignore",
        )

        if "last_updated" not in df.columns:
            df["last_updated"] = pd.NaT

        menu_cols = [
            column
            for column in MENU_PRICES.keys()
            if column in df.columns
        ]

        last_times = (
            df.groupby("rollno")[
                "last_updated"
            ]
            .max()
            .reset_index()
        )

        df_summary = (
            df.groupby(
                "rollno",
                as_index=False,
            )[menu_cols]
            .sum()
        )

        df_summary = df_summary.merge(
            last_times,
            on="rollno",
            how="left",
        )

        df_summary = (
            df_summary
            .merge(
                students_df,
                on="rollno",
                how="left",
            )
            .sort_values(
                by="residence"
            )
        )

        df_summary["last_updated"] = (
            df_summary["last_updated"]
            .apply(
                lambda x:
                    utc_to_ist(x)
                    if pd.notnull(x)
                    else ""
            )
        )

        df_summary["total_cost"] = (
            df_summary.apply(
                calculate_total,
                axis=1,
            )
        )

        cols = (
            [
                "rollno",
                "studentName",
                "residence",
                "occupancy",
                "last_updated",
            ]
            + menu_cols
            + ["total_cost"]
        )

        df_summary = df_summary[cols]

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl",
        ) as writer:

            for residence, group in (
                df_summary.groupby("residence")
            ):

                group = group.sort_values(
                    by="rollno"
                )

                sheet_name = str(residence)[:31]

                group.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                )

        output.seek(0)

        return StreamingResponse(
            output,
            media_type=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (
                    "attachment; "
                    "filename=orders_summary.xlsx"
                )
            },
        )

    except Exception as e:

        return {
            "message": (
                f"Error downloading orders: {str(e)}"
            )
        }


# -------------------------------------------------------------------
# INDIVIDUAL REPORT FORM
# -------------------------------------------------------------------

@app.get(
    "/report_form",
    response_class=HTMLResponse,
)
async def show_report_form(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="individualreportlogin.html",
        context={},
    )


@app.post("/report_form")
def submit_report_form(
    rollno: str = Form(...),
):

    return RedirectResponse(
        url=f"/report/{rollno}",
        status_code=302,
    )


# -------------------------------------------------------------------
# INDIVIDUAL REPORT
# -------------------------------------------------------------------

@app.get(
    "/report/{rollno}",
    response_class=HTMLResponse,
)
def individual_report(
    request: Request,
    rollno: str,
):

    with Session(engine) as session:

        results = session.exec(
            select(Order).where(
                Order.rollno == rollno
            )
        ).all()

    if not results:

        return templates.TemplateResponse(
            request=request,
            name="individualreport.html",
            context={
                "error": (
                    f"No order found for "
                    f"roll number {rollno}"
                )
            },
        )

    df_full = (
        pd.DataFrame(
            [
                order.model_dump()
                for order in results
            ]
        )
        .drop(
            columns=["id"],
            errors="ignore",
        )
        .fillna(0)
    )

    menu_cols = [
        column
        for column in MENU_PRICES.keys()
        if column in df_full.columns
    ]

    entries_df = df_full[
        ["last_updated"] + menu_cols
    ].copy()

    entries_df["last_updated"] = (
        entries_df["last_updated"]
        .apply(
            lambda x:
                utc_to_ist(x)
                if pd.notnull(x)
                else ""
        )
    )

    def row_total(row):
        return sum(
            int(row.get(item, 0)) * price
            for item, price
            in MENU_PRICES.items()
        )

    entries_df["total_cost"] = (
        entries_df.apply(
            row_total,
            axis=1,
        )
    )

    entries_df["rollno"] = rollno

    entries = entries_df.to_dict(
        orient="records"
    )

    df = df_full.drop(
        columns=[
            "rollno",
            "last_updated",
        ],
        errors="ignore",
    )

    order_data = {
        key: int(value)
        for key, value in df.sum().to_dict().items()
        if key in MENU_PRICES
    }

    user_row = students_df[
        students_df["rollno"] == rollno
    ]

    if not user_row.empty:

        name = user_row.iloc[0]["studentName"]
        residence = user_row.iloc[0]["residence"]
        occupancy = user_row.iloc[0]["occupancy"]

        parts = name.split()

        final_name = (
            f"{parts[0]} "
            f"{' '.join(parts[1:])}"
        ).strip()

    else:

        final_name = "Unknown"
        residence = "Unknown"
        occupancy = "Unknown"

    total_cost = sum(
        order_data[item]
        * MENU_PRICES[item]
        for item in order_data
    )

    return templates.TemplateResponse(
        request=request,
        name="individualreport.html",
        context={
            "order": order_data,
            "name": final_name,
            "rollno": rollno,
            "residence": residence,
            "occupancy": occupancy,
            "total_cost": total_cost,
            "MENU_PRICES": MENU_PRICES,
            "entries": entries,
        },
    )


# -------------------------------------------------------------------
# DASHBOARD
# -------------------------------------------------------------------

dash_app.layout = html.Div(
    [
        html.H1(
            "🍽️ Food Order Dashboard",
            style={
                "textAlign": "center",
                "marginBottom": "30px",
            },
        ),

        dcc.Graph(
            id="order-graph"
        ),

        dcc.Interval(
            id="interval-component",
            interval=10 * 1000,
            n_intervals=0,
        ),

        html.Div(
            "Data updates automatically every 10s.",
            style={
                "textAlign": "center",
                "marginTop": "10px",
                "color": "gray",
            },
        ),
    ],
    style={
        "padding": "30px",
        "fontFamily": "Verdana",
    },
)


@dash_app.callback(
    Output(
        "order-graph",
        "figure",
    ),
    Input(
        "interval-component",
        "n_intervals",
    ),
)
def update_graph(n):

    with Session(engine) as session:

        results = session.exec(
            select(Order)
        ).all()

        df = pd.DataFrame(
            [
                order.model_dump()
                for order in results
            ]
        )

    if df.empty:

        fig = px.bar(
            title="No Orders Yet"
        )

        fig.update_layout(
            title_x=0.5,
            font={
                "family": "Verdana",
                "size": 14,
            },
        )

        return fig

    menu_cols = [
        column
        for column in MENU_PRICES.keys()
        if column in df.columns
    ]

    totals = (
        df[menu_cols]
        .sum(numeric_only=True)
        .reset_index()
    )

    totals.columns = [
        "Item",
        "Total",
    ]

    totals = totals.sort_values(
        by="Total",
        ascending=False,
    )

    fig = px.bar(
        totals,
        x="Item",
        y="Total",
        text="Total",
        title="🍽️ Total Items Ordered",
        color="Total",
        color_continuous_scale="Viridis",
    )

    fig.update_layout(
        xaxis_title="Menu Item",
        yaxis_title="Total Ordered",
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        font={
            "family": "Verdana",
            "size": 14,
        },
        title_x=0.5,
    )

    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
    )

    fig.update_yaxes(
        showgrid=False
    )

    return fig


# -------------------------------------------------------------------
# MOUNT DASH
# -------------------------------------------------------------------

app.mount(
    "/dashboard",
    WSGIMiddleware(dash_app.server),
)