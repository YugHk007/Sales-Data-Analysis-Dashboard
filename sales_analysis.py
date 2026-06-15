
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots
import warnings
warnings.filterwarnings("ignore")

# ------------------------------------------------------------
# STEP 1 — LOAD DATA
# ------------------------------------------------------------
# Put your CSV file in the same folder as this script
df = pd.read_csv("Sample - Superstore.csv", encoding="latin-1")

print("=" * 50)
print("STEP 1: DATA LOADED")
print("=" * 50)
print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")
print(f"\nColumn names:\n{list(df.columns)}")

# ------------------------------------------------------------
# STEP 2 — DATA CLEANING
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("STEP 2: DATA CLEANING")
print("=" * 50)

# Check missing values
print(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")

# Fix date columns
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=False)
df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=False)

# Remove duplicates
before = len(df)
df.drop_duplicates(inplace=True)
print(f"\nDuplicates removed: {before - len(df)}")

# Extract time features
df["Year"]  = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month
df["Month Name"] = df["Order Date"].dt.strftime("%b")

print("\nData cleaning complete. Sample:")
print(df[["Order Date", "Region", "Category", "Sales", "Profit"]].head(3))

# ------------------------------------------------------------
# STEP 3 — KEY METRICS
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("STEP 3: KEY METRICS")
print("=" * 50)

total_sales   = df["Sales"].sum()
total_profit  = df["Profit"].sum()
total_orders  = df["Order ID"].nunique()
profit_margin = (total_profit / total_sales) * 100

print(f"Total Sales    : ₹{total_sales:,.0f}")
print(f"Total Profit   : ₹{total_profit:,.0f}")
print(f"Total Orders   : {total_orders}")
print(f"Profit Margin  : {profit_margin:.1f}%")

# Top 5 products by sales
top_products = (
    df.groupby("Sub-Category")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
print(f"\nTop 5 Sub-Categories by Sales:\n{top_products}")

# Region performance
region_perf = (
    df.groupby("Region")[["Sales", "Profit"]]
    .sum()
    .sort_values("Sales", ascending=False)
)
print(f"\nRegion Performance:\n{region_perf}")

# ------------------------------------------------------------
# STEP 4 — MATPLOTLIB CHARTS (Static)
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("STEP 4: CREATING MATPLOTLIB CHARTS ...")
print("=" * 50)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Sales Data Analysis Dashboard", fontsize=16, fontweight="bold", y=1.01)

COLORS = ["#2196F3", "#4CAF50", "#FF9800", "#E91E63",
          "#9C27B0", "#00BCD4", "#FF5722", "#8BC34A"]

# --- Chart 1: Top Sub-Categories by Sales (Bar) ---
ax1 = axes[0, 0]
top10 = (
    df.groupby("Sub-Category")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(8)
)
bars = ax1.bar(top10.index, top10.values, color=COLORS)
ax1.set_title("Top Sub-Categories by Sales", fontweight="bold")
ax1.set_xlabel("Sub-Category")
ax1.set_ylabel("Total Sales ($)")
ax1.tick_params(axis="x", rotation=45)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
for bar in bars:
    ax1.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 500,
             f"${bar.get_height()/1000:.0f}K",
             ha="center", va="bottom", fontsize=8)

# --- Chart 2: Monthly Sales Trend (Line) ---
ax2 = axes[0, 1]
monthly = (
    df.groupby(["Year", "Month"])["Sales"]
    .sum()
    .reset_index()
    .sort_values(["Year", "Month"])
)
monthly["Period"] = monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)
for year, grp in monthly.groupby("Year"):
    ax2.plot(range(len(grp)), grp["Sales"].values, marker="o", label=str(year), linewidth=2)
ax2.set_title("Monthly Sales Trend by Year", fontweight="bold")
ax2.set_xlabel("Month")
ax2.set_ylabel("Sales ($)")
ax2.set_xticks(range(12))
ax2.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                      "Jul","Aug","Sep","Oct","Nov","Dec"])
ax2.legend()
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))

# --- Chart 3: Category Share (Pie) ---
ax3 = axes[1, 0]
cat_sales = df.groupby("Category")["Sales"].sum()
wedges, texts, autotexts = ax3.pie(
    cat_sales.values,
    labels=cat_sales.index,
    autopct="%1.1f%%",
    colors=["#2196F3", "#4CAF50", "#FF9800"],
    startangle=140,
    pctdistance=0.8
)
for text in autotexts:
    text.set_fontsize(10)
ax3.set_title("Sales by Category", fontweight="bold")

# --- Chart 4: Region Profit Comparison (Horizontal Bar) ---
ax4 = axes[1, 1]
reg = df.groupby("Region")[["Sales", "Profit"]].sum().sort_values("Sales")
x  = range(len(reg))
w  = 0.4
ax4.barh([i + w/2 for i in x], reg["Sales"].values,  height=w, label="Sales",  color="#2196F3")
ax4.barh([i - w/2 for i in x], reg["Profit"].values, height=w, label="Profit", color="#4CAF50")
ax4.set_yticks(x)
ax4.set_yticklabels(reg.index)
ax4.set_title("Sales vs Profit by Region", fontweight="bold")
ax4.set_xlabel("Amount ($)")
ax4.legend()
ax4.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))

plt.tight_layout()
plt.savefig("sales_dashboard_static.png", dpi=150, bbox_inches="tight")
plt.show()
print("Static chart saved as: sales_dashboard_static.png")

# ------------------------------------------------------------
# STEP 5 — PLOTLY INTERACTIVE DASHBOARD
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("STEP 5: CREATING INTERACTIVE PLOTLY DASHBOARD ...")
print("=" * 50)

fig2 = plotly.subplots.make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Top Sub-Categories by Sales",
        "Monthly Sales Trend",
        "Sales by Category",
        "Sales & Profit by Region"
    ),
    specs=[
        [{"type": "bar"},  {"type": "scatter"}],
        [{"type": "pie"},  {"type": "bar"}]
    ],
    vertical_spacing=0.18,
    horizontal_spacing=0.12
)

# Plot 1 — Bar: Top Sub-Categories
top8 = (
    df.groupby("Sub-Category")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(8)
    .reset_index()
)
fig2.add_trace(
    go.Bar(
        x=top8["Sub-Category"], y=top8["Sales"],
        marker_color="#2196F3",
        name="Sales",
        hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
    ),
    row=1, col=1
)

# Plot 2 — Line: Monthly Trend
colors_line = ["#2196F3", "#FF9800", "#4CAF50", "#E91E63"]
for i, (year, grp) in enumerate(df.groupby("Year")):
    monthly_g = grp.groupby("Month")["Sales"].sum().reset_index()
    fig2.add_trace(
        go.Scatter(
            x=monthly_g["Month"], y=monthly_g["Sales"],
            mode="lines+markers",
            name=str(year),
            line=dict(color=colors_line[i % len(colors_line)], width=2),
            hovertemplate=f"<b>{year}</b> Month %{{x}}<br>Sales: $%{{y:,.0f}}<extra></extra>"
        ),
        row=1, col=2
    )

# Plot 3 — Pie: Category
cat_s = df.groupby("Category")["Sales"].sum().reset_index()
fig2.add_trace(
    go.Pie(
        labels=cat_s["Category"],
        values=cat_s["Sales"],
        hole=0.4,
        marker_colors=["#2196F3", "#4CAF50", "#FF9800"],
        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percent}<extra></extra>"
    ),
    row=2, col=1
)

# Plot 4 — Grouped Bar: Region Sales & Profit
reg2 = df.groupby("Region")[["Sales", "Profit"]].sum().reset_index()
fig2.add_trace(
    go.Bar(
        x=reg2["Region"], y=reg2["Sales"],
        name="Sales", marker_color="#2196F3",
        hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
    ),
    row=2, col=2
)
fig2.add_trace(
    go.Bar(
        x=reg2["Region"], y=reg2["Profit"],
        name="Profit", marker_color="#4CAF50",
        hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>"
    ),
    row=2, col=2
)

# Layout
fig2.update_layout(
    title=dict(
        text="📊 Sales Data Analysis Dashboard",
        font=dict(size=20),
        x=0.5
    ),
    height=750,
    showlegend=True,
    barmode="group",
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Arial", size=12),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.15,
        xanchor="center",
        x=0.5
    )
)

# Save interactive dashboard as HTML
fig2.write_html("sales_dashboard_interactive.html")
fig2.show()
print("Interactive dashboard saved as: sales_dashboard_interactive.html")

# ------------------------------------------------------------
# STEP 6 — SUMMARY INSIGHTS
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("STEP 6: KEY INSIGHTS SUMMARY")
print("=" * 50)

best_region   = region_perf["Sales"].idxmax()
best_category = df.groupby("Category")["Sales"].sum().idxmax()
best_product  = top_products.index[0]
worst_profit_cat = df.groupby("Category")["Profit"].sum().idxmin()

print(f"1. Best performing region  : {best_region}")
print(f"2. Highest sales category  : {best_category}")
print(f"3. Top selling sub-category: {best_product}")
print(f"4. Lowest profit category  : {worst_profit_cat}")
print(f"5. Overall profit margin   : {profit_margin:.1f}%")
print("\nFiles created:")
print("   sales_dashboard_static.png      — for reports/PDF")
print("   sales_dashboard_interactive.html — open in browser")
print("\nProject 1 Complete!")
