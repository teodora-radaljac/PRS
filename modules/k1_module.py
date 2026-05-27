import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def render():
    st.title("📐 Modul K1: Performanse procesora, diskova i memorije")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Amdahl-ov zakon", "CPU performanse", "Performanse diska", "Memorijska hijerarhija"]
    )

    with tab1:
        render_amdahl()
    with tab2:
        render_cpu()
    with tab3:
        render_disk()
    with tab4:
        render_memory()


# ---------------------------------------------------------------------------
# Amdahl-ov zakon
# ---------------------------------------------------------------------------
def render_amdahl():
    st.header("Amdahl-ov zakon i Gustafson-ov zakon")

    st.markdown(
        r"""
    **Amdahl-ov zakon** definiše maksimalno ubrzanje programa pri paralelizaciji:

    $$S(n) = \frac{1}{(1 - p) + \frac{p}{n}}$$

    gde je $p$ udeo programa koji se može paralelizovati, a $n$ broj procesora.

    **Gustafson-ov zakon** pretpostavlja da se veličina problema skalira sa brojem procesora:

    $$S_G(n) = n - (1 - p) \cdot (n - 1)$$
    """
    )

    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        p = st.slider(
            "Paralelizabilni deo programa (p)",
            min_value=0.0,
            max_value=1.0,
            value=0.9,
            step=0.01,
            key="amdahl_p",
        )
        max_proc = st.select_slider(
            "Maksimalan broj procesora",
            options=[8, 16, 32, 64, 128, 256, 512, 1024],
            value=64,
            key="amdahl_max_proc",
        )

        st.markdown("---")
        s_max = 1 / (1 - p) if p < 1 else float("inf")
        st.metric("Teorijski maksimum (Amdahl)", f"{s_max:.2f}x")
        st.metric("Ubrzanje sa 8 procesora", f"{1 / ((1 - p) + p / 8):.2f}x")
        st.metric("Ubrzanje sa 64 procesora", f"{1 / ((1 - p) + p / 64):.2f}x")

    with col2:
        n_values = np.arange(1, max_proc + 1)
        s_amdahl = 1 / ((1 - p) + p / n_values)
        s_gustafson = n_values - (1 - p) * (n_values - 1)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=n_values,
                y=s_amdahl,
                mode="lines",
                name="Amdahl-ov zakon",
                line=dict(color="#2196F3", width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=n_values,
                y=s_gustafson,
                mode="lines",
                name="Gustafson-ov zakon",
                line=dict(color="#FF9800", width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=n_values,
                y=n_values,
                mode="lines",
                name="Idealno (linearno)",
                line=dict(color="gray", width=1, dash="dash"),
            )
        )
        if p < 1:
            fig.add_hline(
                y=s_max,
                line_dash="dot",
                line_color="red",
                annotation_text=f"Amdahl max = {s_max:.2f}x",
            )

        fig.update_layout(
            title=f"Ubrzanje za p = {p:.0%}",
            xaxis_title="Broj procesora (n)",
            yaxis_title="Ubrzanje S(n)",
            height=500,
            legend=dict(x=0.02, y=0.98),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Uporedni prikaz više vrednosti p
    st.markdown("### Uporedni prikaz za različite vrednosti p")
    n_values = np.arange(1, 129)
    fig2 = go.Figure()
    colors = px.colors.qualitative.Set2
    for i, pv in enumerate([0.5, 0.75, 0.9, 0.95, 0.99]):
        s = 1 / ((1 - pv) + pv / n_values)
        fig2.add_trace(
            go.Scatter(
                x=n_values,
                y=s,
                mode="lines",
                name=f"p = {pv}",
                line=dict(color=colors[i % len(colors)], width=2),
            )
        )
    fig2.update_layout(
        xaxis_title="Broj procesora (n)",
        yaxis_title="Ubrzanje S(n)",
        height=400,
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.info(
        "💡 **Pitanje za razmišljanje:** Zašto čak i sa 99% paralelizabilnog koda "
        "ne možemo dobiti ubrzanje veće od 100x?"
    )


# ---------------------------------------------------------------------------
# CPU performanse
# ---------------------------------------------------------------------------
def render_cpu():
    st.header("CPU performanse: CPI, MIPS, vreme izvršavanja")

    st.markdown(
        r"""
    **Vreme izvršavanja programa:**
    $$T = N_{inst} \times CPI \times T_{clk} = \frac{N_{inst} \times CPI}{f_{clk}}$$

    **MIPS (Millions of Instructions Per Second):**
    $$MIPS = \frac{f_{clk}}{CPI \times 10^6}$$
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parametri programa")
        n_inst = st.number_input(
            "Broj instrukcija (milioni)", min_value=1, max_value=10000, value=100, key="cpu_ninst"
        )
        n_inst_abs = n_inst * 1e6

        st.subheader("Mix instrukcija")
        pct_alu = st.slider("% ALU operacija", 0, 100, 40, key="cpu_alu")
        pct_load = st.slider("% Load/Store", 0, 100 - pct_alu, 30, key="cpu_load")
        pct_branch = 100 - pct_alu - pct_load
        st.write(f"% Branch: **{pct_branch}%**")

        st.subheader("CPI po tipu")
        cpi_alu = st.number_input("CPI za ALU", 0.5, 10.0, 1.0, 0.1, key="cpu_cpi_alu")
        cpi_load = st.number_input("CPI za Load/Store", 0.5, 20.0, 3.0, 0.1, key="cpu_cpi_load")
        cpi_branch = st.number_input("CPI za Branch", 0.5, 10.0, 2.0, 0.1, key="cpu_cpi_br")

        f_clk = st.number_input(
            "Frekvencija takta (GHz)", 0.1, 10.0, 3.0, 0.1, key="cpu_fclk"
        )

    with col2:
        cpi_avg = (pct_alu / 100 * cpi_alu + pct_load / 100 * cpi_load + pct_branch / 100 * cpi_branch)
        t_exec = n_inst_abs * cpi_avg / (f_clk * 1e9)
        mips = f_clk * 1e3 / cpi_avg

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Prosečni CPI", f"{cpi_avg:.2f}")
        mc2.metric("Vreme izvršavanja", f"{t_exec * 1000:.2f} ms")
        mc3.metric("MIPS", f"{mips:.1f}")

        # CPI doprinos bar chart
        fig = go.Figure()
        categories = ["ALU", "Load/Store", "Branch"]
        fractions = [pct_alu / 100, pct_load / 100, pct_branch / 100]
        cpis = [cpi_alu, cpi_load, cpi_branch]
        contributions = [f * c for f, c in zip(fractions, cpis)]

        fig.add_trace(
            go.Bar(
                x=categories,
                y=contributions,
                marker_color=["#2196F3", "#FF9800", "#4CAF50"],
                text=[f"{c:.2f}" for c in contributions],
                textposition="auto",
            )
        )
        fig.update_layout(
            title="Doprinos svakog tipa instrukcije ukupnom CPI",
            yaxis_title="Doprinos CPI",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Osetljivost na frekvenciju
        freqs = np.linspace(0.5, 8.0, 100)
        times = n_inst_abs * cpi_avg / (freqs * 1e9) * 1000
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=freqs, y=times, mode="lines", line=dict(color="#E91E63", width=2))
        )
        fig2.add_vline(x=f_clk, line_dash="dash", line_color="gray")
        fig2.update_layout(
            title="Vreme izvršavanja vs. frekvencija takta",
            xaxis_title="Frekvencija (GHz)",
            yaxis_title="Vreme (ms)",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)


# ---------------------------------------------------------------------------
# Performanse diska
# ---------------------------------------------------------------------------
def render_disk():
    st.header("Performanse diska")

    st.markdown(
        r"""
    **Vreme pristupa disku:**
    $$T_{access} = T_{seek} + T_{rot} + T_{transfer}$$

    - $T_{seek}$ — vreme pozicioniranja glave
    - $T_{rot} = \frac{1}{2} \times \frac{60}{RPM}$ — prosečna rotaciona latencija
    - $T_{transfer} = \frac{Veličina\_bloka}{Brzina\_transfera}$
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        rpm = st.select_slider(
            "Brzina rotacije (RPM)",
            options=[5400, 7200, 10000, 15000],
            value=7200,
            key="disk_rpm",
        )
        t_seek = st.slider(
            "Prosečno vreme seek (ms)", 1.0, 20.0, 8.0, 0.5, key="disk_seek"
        )
        block_size = st.select_slider(
            "Veličina bloka (KB)",
            options=[4, 8, 16, 32, 64, 128, 256, 512, 1024],
            value=64,
            key="disk_block",
        )
        transfer_rate = st.slider(
            "Brzina transfera (MB/s)", 50, 300, 150, 10, key="disk_transfer"
        )

    with col2:
        t_rot = (60 / rpm) / 2 * 1000  # ms
        t_trans = (block_size / 1024) / transfer_rate * 1000  # ms
        t_access = t_seek + t_rot + t_trans

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("T_seek", f"{t_seek:.1f} ms")
        mc2.metric("T_rot", f"{t_rot:.2f} ms")
        mc3.metric("T_transfer", f"{t_trans:.3f} ms")
        mc4.metric("T_access", f"{t_access:.2f} ms")

        # Doprinos komponenti
        fig = go.Figure(
            go.Pie(
                labels=["Seek", "Rotaciona latencija", "Transfer"],
                values=[t_seek, t_rot, t_trans],
                marker=dict(colors=["#2196F3", "#FF9800", "#4CAF50"]),
                textinfo="label+percent+value",
                texttemplate="%{label}<br>%{value:.2f} ms<br>(%{percent})",
            )
        )
        fig.update_layout(title="Struktura vremena pristupa disku", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # IOPS analiza
        iops = 1000 / t_access
        st.metric("IOPS (I/O operacija po sekundi)", f"{iops:.0f}")

        # Poređenje RPM-ova
        rpms = [5400, 7200, 10000, 15000]
        accesses = []
        for r in rpms:
            tr = (60 / r) / 2 * 1000
            tt = (block_size / 1024) / transfer_rate * 1000
            accesses.append(t_seek + tr + tt)

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=[str(r) for r in rpms],
                y=accesses,
                marker_color=["#E3F2FD", "#90CAF9", "#42A5F5", "#1565C0"],
                text=[f"{a:.2f}" for a in accesses],
                textposition="auto",
            )
        )
        fig2.update_layout(
            title="Vreme pristupa za različite RPM vrednosti",
            xaxis_title="RPM",
            yaxis_title="Vreme pristupa (ms)",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)


# ---------------------------------------------------------------------------
# Memorijska hijerarhija
# ---------------------------------------------------------------------------
def render_memory():
    st.header("Memorijska hijerarhija i keš performanse")

    st.markdown(
        r"""
    **Prosečno vreme pristupa memoriji:**
    $$T_{avg} = \sum_{i=1}^{n} \left(\prod_{j=1}^{i-1}(1 - h_j)\right) \cdot h_i \cdot t_i + \prod_{j=1}^{n}(1 - h_j) \cdot t_{mem}$$

    gde je $h_i$ hit rate za nivo $i$, a $t_i$ vreme pristupa nivou $i$.
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parametri keš memorije")
        h1 = st.slider("L1 hit rate", 0.0, 1.0, 0.95, 0.01, key="mem_h1")
        t1 = st.number_input("L1 vreme pristupa (ns)", 0.1, 10.0, 1.0, 0.1, key="mem_t1")

        h2 = st.slider("L2 hit rate", 0.0, 1.0, 0.85, 0.01, key="mem_h2")
        t2 = st.number_input("L2 vreme pristupa (ns)", 1.0, 50.0, 5.0, 0.5, key="mem_t2")

        h3 = st.slider("L3 hit rate", 0.0, 1.0, 0.90, 0.01, key="mem_h3")
        t3 = st.number_input("L3 vreme pristupa (ns)", 5.0, 100.0, 20.0, 1.0, key="mem_t3")

        t_mem = st.number_input(
            "Glavna memorija (ns)", 10.0, 500.0, 100.0, 10.0, key="mem_tmem"
        )

    with col2:
        # Izračunavanje
        c1 = h1 * t1
        c2 = (1 - h1) * h2 * t2
        c3 = (1 - h1) * (1 - h2) * h3 * t3
        c_mem = (1 - h1) * (1 - h2) * (1 - h3) * t_mem
        t_avg = c1 + c2 + c3 + c_mem

        st.metric("Prosečno vreme pristupa", f"{t_avg:.2f} ns")

        # Stacked bar
        fig = go.Figure()
        labels = ["L1", "L2", "L3", "Glavna memorija"]
        values = [c1, c2, c3, c_mem]
        colors = ["#4CAF50", "#2196F3", "#FF9800", "#F44336"]

        fig.add_trace(
            go.Bar(
                x=labels,
                y=values,
                marker_color=colors,
                text=[f"{v:.3f} ns" for v in values],
                textposition="auto",
            )
        )
        fig.update_layout(
            title="Doprinos svakog nivoa prosečnom vremenu pristupa",
            yaxis_title="Doprinos (ns)",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Heatmapa: T_avg u zavisnosti od L1 i L2 hit rate
        st.markdown("### Osetljivost na L1 i L2 hit rate")
        h1_range = np.linspace(0.5, 0.99, 50)
        h2_range = np.linspace(0.5, 0.99, 50)
        H1, H2 = np.meshgrid(h1_range, h2_range)

        T = (
            H1 * t1
            + (1 - H1) * H2 * t2
            + (1 - H1) * (1 - H2) * h3 * t3
            + (1 - H1) * (1 - H2) * (1 - h3) * t_mem
        )

        fig2 = go.Figure(
            go.Heatmap(
                z=T,
                x=np.round(h1_range, 2),
                y=np.round(h2_range, 2),
                colorscale="RdYlGn_r",
                colorbar=dict(title="T_avg (ns)"),
            )
        )
        fig2.update_layout(
            title="Prosečno vreme pristupa (ns) za različite L1/L2 hit rate",
            xaxis_title="L1 hit rate",
            yaxis_title="L2 hit rate",
            height=450,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.info(
        "💡 **Pitanje za razmišljanje:** Šta ima veći uticaj na ukupno vreme pristupa "
        "— povećanje L1 hit rate-a sa 90% na 95%, ili L2 hit rate-a sa 80% na 90%?"
    )
