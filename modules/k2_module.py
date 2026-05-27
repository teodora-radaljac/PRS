import streamlit as st
import numpy as np
import plotly.graph_objects as go
from math import factorial, exp


def render():
    st.title(" Modul K2: Sistemi masovnog opsluživanja")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Poasonov proces",
            "M/M/1",
            "M/M/c",
            "Ciklički model",
            "Centralni server",
            "Bjuzenov algoritam",
        ]
    )

    with tab1:
        render_poisson()
    with tab2:
        render_mm1()
    with tab3:
        render_mmc()
    with tab4:
        render_cyclic()
    with tab5:
        render_central_server()
    with tab6:
        render_buzen()


# ---------------------------------------------------------------------------
# Poasonov proces
# ---------------------------------------------------------------------------
def render_poisson():
    st.header("Poasonov proces")

    st.markdown(
        r"""
    **Poasonova raspodela** opisuje verovatnoću $k$ dolazaka u intervalu $t$:

    $$P(X = k) = \frac{(\lambda t)^k \cdot e^{-\lambda t}}{k!}$$

    **Eksponencijalna raspodela** opisuje vreme između uzastopnih dolazaka:

    $$f(x) = \lambda e^{-\lambda x}, \quad x \geq 0$$
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        lam = st.slider("Stopa dolazaka λ (dolazaka/s)", 0.1, 10.0, 2.0, 0.1, key="poi_lam")
        t_interval = st.slider("Vremenski interval t (s)", 0.5, 10.0, 1.0, 0.5, key="poi_t")

    with col2:
        k_vals = np.arange(0, 25)
        mu_val = lam * t_interval
        probs = [(mu_val ** k) * exp(-mu_val) / factorial(k) for k in k_vals]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=k_vals,
                y=probs,
                marker_color="#2196F3",
                name="P(X=k)",
                text=[f"{p:.3f}" for p in probs],
                textposition="auto",
            )
        )
        fig.update_layout(
            title=f"Poasonova raspodela: λ={lam}, t={t_interval}, λt={mu_val:.1f}",
            xaxis_title="Broj dolazaka (k)",
            yaxis_title="Verovatnoća P(X=k)",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Eksponencijalna raspodela
        x_exp = np.linspace(0, 5 / lam, 200)
        y_exp = lam * np.exp(-lam * x_exp)

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=x_exp,
                y=y_exp,
                mode="lines",
                fill="tozeroy",
                line=dict(color="#FF9800", width=2),
                name="f(x)",
            )
        )
        mean_inter = 1 / lam
        fig2.add_vline(
            x=mean_inter,
            line_dash="dash",
            line_color="red",
            annotation_text=f"E[X] = 1/λ = {mean_inter:.2f} s",
        )
        fig2.update_layout(
            title="Eksponencijalna raspodela (vreme između dolazaka)",
            xaxis_title="Vreme (s)",
            yaxis_title="Gustina verovatnoće f(x)",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)


# ---------------------------------------------------------------------------
# M/M/1
# ---------------------------------------------------------------------------
def render_mm1():
    st.header("M/M/1 red čekanja")

    st.markdown(
        r"""
    **M/M/1 sistem:** Jedan server, Poasonovi dolasci (stopa $\lambda$), eksponencijalna opsluživanja (stopa $\mu$).

    | Metrika | Formula |
    |---------|---------|
    | Iskorišćenje | $\rho = \lambda / \mu$ |
    | Prosečan broj u sistemu | $L = \frac{\rho}{1 - \rho}$ |
    | Prosečan broj u redu | $L_q = \frac{\rho^2}{1 - \rho}$ |
    | Prosečno vreme u sistemu | $W = \frac{1}{\mu - \lambda}$ |
    | Prosečno vreme čekanja u redu | $W_q = \frac{\rho}{\mu(1 - \rho)}$ |
    | Verovatnoća $n$ korisnika | $P_n = (1 - \rho)\rho^n$ |
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        lam = st.slider("Stopa dolazaka λ", 0.1, 10.0, 3.0, 0.1, key="mm1_lam")
        mu = st.slider("Stopa opsluživanja μ", 0.1, 15.0, 5.0, 0.1, key="mm1_mu")

        rho = lam / mu
        if rho < 1:
            st.success(f"ρ = {rho:.3f} < 1 → Sistem je stabilan")
        else:
            st.error(f"ρ = {rho:.3f} ≥ 1 → Sistem je NESTABILAN!")

    with col2:
        if rho < 1:
            L = rho / (1 - rho)
            Lq = rho ** 2 / (1 - rho)
            W = 1 / (mu - lam)
            Wq = rho / (mu * (1 - rho))

            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("L (u sistemu)", f"{L:.2f}")
            mc2.metric("Lq (u redu)", f"{Lq:.2f}")
            mc3.metric("W (vreme u sist.)", f"{W:.3f} s")
            mc4.metric("Wq (vreme u redu)", f"{Wq:.3f} s")

            # Distribucija broja korisnika
            n_max = min(int(L * 4) + 10, 50)
            n_vals = np.arange(0, n_max)
            pn = (1 - rho) * rho ** n_vals

            fig = go.Figure()
            fig.add_trace(
                go.Bar(x=n_vals, y=pn, marker_color="#2196F3", name="P(n)")
            )
            fig.update_layout(
                title="Distribucija broja korisnika u sistemu",
                xaxis_title="Broj korisnika (n)",
                yaxis_title="P(n)",
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)

            # L i W u funkciji od rho
            rho_range = np.linspace(0.01, 0.99, 200)
            L_range = rho_range / (1 - rho_range)
            W_range = 1 / (mu - mu * rho_range)

            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=rho_range,
                    y=L_range,
                    mode="lines",
                    name="L (prosečan broj)",
                    line=dict(color="#2196F3", width=2),
                )
            )
            fig2.add_vline(
                x=rho,
                line_dash="dash",
                line_color="red",
                annotation_text=f"ρ = {rho:.2f}",
            )
            fig2.update_layout(
                title="Prosečan broj korisnika vs. iskorišćenje",
                xaxis_title="ρ",
                yaxis_title="L",
                height=350,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Sistem nije stabilan (ρ ≥ 1). L i W → ∞. Smanjite λ ili povećajte μ.")


# ---------------------------------------------------------------------------
# M/M/c
# ---------------------------------------------------------------------------
def render_mmc():
    st.header("M/M/c — Ekvivalentni paralelni serveri")

    st.markdown(
        r"""
    **M/M/c sistem:** $c$ identičnih paralelnih servera, Poasonovi dolasci (stopa $\lambda$), eksponencijalna opsluživanja (stopa $\mu$ po serveru).

    Iskorišćenje: $\rho = \frac{\lambda}{c \cdot \mu}$

    Erlang-C formula (verovatnoća čekanja):
    $$C(c, a) = \frac{\frac{a^c}{c!} \cdot \frac{1}{1 - \rho}}{\sum_{k=0}^{c-1}\frac{a^k}{k!} + \frac{a^c}{c!} \cdot \frac{1}{1 - \rho}}$$

    gde je $a = \lambda / \mu$ ponuđeno opterećenje.
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        lam = st.slider("Stopa dolazaka λ", 0.1, 20.0, 8.0, 0.1, key="mmc_lam")
        mu = st.slider("Stopa opsluživanja μ (po serveru)", 0.1, 10.0, 3.0, 0.1, key="mmc_mu")
        c = st.slider("Broj servera c", 1, 20, 4, key="mmc_c")

        a = lam / mu  # offered load
        rho = a / c

        if rho < 1:
            st.success(f"ρ = {rho:.3f} < 1 → Stabilan")
        else:
            st.error(f"ρ = {rho:.3f} ≥ 1 → Nestabilan!")

    with col2:
        if rho < 1:
            # Erlang-C
            sum_terms = sum(a ** k / factorial(k) for k in range(c))
            last_term = (a ** c / factorial(c)) * (1 / (1 - rho))
            erlang_c = last_term / (sum_terms + last_term)

            Lq = erlang_c * rho / (1 - rho)
            Wq = Lq / lam
            W = Wq + 1 / mu
            L = lam * W

            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("P(čekanje)", f"{erlang_c:.3f}")
            mc2.metric("Lq", f"{Lq:.2f}")
            mc3.metric("Wq", f"{Wq:.3f} s")
            mc4.metric("L", f"{L:.2f}")

            # Poređenje: L za različit broj servera
            c_range = range(max(1, int(np.ceil(a))), int(np.ceil(a)) + 10)
            L_vals = []
            for ci in c_range:
                rhoi = a / ci
                if rhoi >= 1:
                    L_vals.append(None)
                    continue
                si = sum(a ** k / factorial(k) for k in range(ci))
                li = (a ** ci / factorial(ci)) * (1 / (1 - rhoi))
                ec = li / (si + li)
                lqi = ec * rhoi / (1 - rhoi)
                L_vals.append(lam * (lqi / lam + 1 / mu))

            fig = go.Figure()
            valid_c = [ci for ci, lv in zip(c_range, L_vals) if lv is not None]
            valid_L = [lv for lv in L_vals if lv is not None]
            fig.add_trace(
                go.Bar(
                    x=[str(ci) for ci in valid_c],
                    y=valid_L,
                    marker_color="#2196F3",
                    text=[f"{lv:.2f}" for lv in valid_L],
                    textposition="auto",
                )
            )
            fig.update_layout(
                title="Prosečan broj korisnika (L) vs. broj servera",
                xaxis_title="Broj servera (c)",
                yaxis_title="L",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Sistem nije stabilan. Povećajte broj servera ili smanjite λ.")


# ---------------------------------------------------------------------------
# Ciklički model multiprogramiranja
# ---------------------------------------------------------------------------
def render_cyclic():
    st.header("Ciklički model multiprogramiranja")

    st.markdown(
        r"""
    U cikličkom modelu, korisnik naizmenično koristi CPU i I/O uređaj.
    Svaki ciklus se sastoji od:
    - **Think time** ($Z$) — vreme razmišljanja
    - **Service time** ($S$) — vreme opsluživanja

    Za $N$ korisnika u sistemu, propusna moć i vreme odziva se izračunavaju iterativno.

    **Granice performansi:**
    - Gornja granica propusne moći: $X \leq \min\left(\frac{1}{D_{max}}, \frac{N}{D + Z}\right)$
    - Donja granica vremena odziva: $R \geq \max(D, N \cdot D_{max} - Z)$

    gde je $D = \sum D_i$ ukupna potražnja za opsluživanjem.
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        N = st.slider("Broj korisnika (N)", 1, 50, 10, key="cyc_N")
        Z = st.slider("Think time Z (s)", 0.1, 30.0, 5.0, 0.5, key="cyc_Z")
        S_cpu = st.slider("CPU service time (s)", 0.01, 2.0, 0.1, 0.01, key="cyc_scpu")
        S_io = st.slider("I/O service time (s)", 0.01, 2.0, 0.2, 0.01, key="cyc_sio")

    with col2:
        D = S_cpu + S_io
        D_max = max(S_cpu, S_io)

        # Granice performansi za različit N
        N_range = np.arange(1, 51)
        X_upper = np.minimum(1 / D_max, N_range / (D + Z))
        R_lower = np.maximum(D, N_range * D_max - Z)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=N_range,
                y=X_upper,
                mode="lines",
                name="Gornja granica X",
                line=dict(color="#2196F3", width=2),
            )
        )
        fig.add_vline(
            x=N, line_dash="dash", line_color="red", annotation_text=f"N = {N}"
        )
        fig.update_layout(
            title="Gornja granica propusne moći vs. broj korisnika",
            xaxis_title="Broj korisnika (N)",
            yaxis_title="Propusna moć X (poslova/s)",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=N_range,
                y=R_lower,
                mode="lines",
                name="Donja granica R",
                line=dict(color="#FF9800", width=2),
            )
        )
        fig2.add_vline(
            x=N, line_dash="dash", line_color="red", annotation_text=f"N = {N}"
        )
        fig2.update_layout(
            title="Donja granica vremena odziva vs. broj korisnika",
            xaxis_title="Broj korisnika (N)",
            yaxis_title="Vreme odziva R (s)",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Izračunavanje tačnih vrednosti za izabrani N
        X_current = min(1 / D_max, N / (D + Z))
        R_current = max(D, N * D_max - Z)
        st.markdown(f"**Za N = {N}:**")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("X (gornja granica)", f"{X_current:.3f} pos/s")
        mc2.metric("R (donja granica)", f"{R_current:.3f} s")
        mc3.metric("D (ukupna potražnja)", f"{D:.3f} s")


# ---------------------------------------------------------------------------
# Centralni server model
# ---------------------------------------------------------------------------
def render_central_server():
    st.header("Model mreže sa centralnim serverom")

    st.markdown(
        r"""
    Mreža sa centralnim serverom (CPU) i $M$ perifernih uređaja.
    Svaki posao posle CPU-a ide na uređaj $i$ sa verovatnoćom $p_i$, ili napušta sistem sa verovatnoćom $p_0$.

    **Broj poseta svakom serveru:**
    $$V_i = \frac{p_i}{p_0}$$

    **Potražnja za opsluživanjem:**
    $$D_i = V_i \times S_i$$
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        M = st.slider("Broj perifernih uređaja", 1, 5, 3, key="cs_M")
        p0 = st.slider("Verovatnoća napuštanja p₀", 0.05, 0.5, 0.2, 0.05, key="cs_p0")

        probs = []
        services = []
        remaining = 1.0 - p0
        for i in range(M):
            if i < M - 1:
                pi = st.slider(
                    f"p_{i+1} (uređaj {i+1})",
                    0.0,
                    remaining,
                    min(remaining / (M - i), remaining),
                    0.05,
                    key=f"cs_p{i+1}",
                )
                remaining -= pi
            else:
                pi = remaining
                st.write(f"p_{i+1} = {pi:.2f} (preostalo)")
            probs.append(pi)
            si = st.number_input(
                f"S_{i+1} (ms)", 0.1, 100.0, 5.0 * (i + 1), 0.5, key=f"cs_s{i+1}"
            )
            services.append(si)

        S_cpu = st.number_input("S_CPU (ms)", 0.1, 50.0, 2.0, 0.5, key="cs_scpu")

    with col2:
        # Izračunavanje
        visits = [p / p0 for p in probs]
        demands = [v * s for v, s in zip(visits, services)]
        D_cpu = 1 / p0 * S_cpu  # CPU visits = 1/p0

        all_names = ["CPU"] + [f"Uređaj {i+1}" for i in range(M)]
        all_visits = [1 / p0] + visits
        all_demands = [D_cpu] + demands

        # Tabela
        st.markdown("### Rezultati analize")
        import pandas as pd
        df = pd.DataFrame(
            {
                "Stanica": all_names,
                "Posete (V_i)": [f"{v:.2f}" for v in all_visits],
                "Service time (ms)": [f"{S_cpu:.1f}"] + [f"{s:.1f}" for s in services],
                "Potražnja D_i (ms)": [f"{d:.2f}" for d in all_demands],
            }
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        bottleneck = all_names[np.argmax(all_demands)]
        st.warning(f" Usko grlo (bottleneck): **{bottleneck}** sa D = {max(all_demands):.2f} ms")

        # Bar chart potražnji
        colors = ["#E91E63"] + ["#2196F3"] * M
        max_d_idx = np.argmax(all_demands)
        chart_colors = ["#2196F3"] * len(all_names)
        chart_colors[max_d_idx] = "#E91E63"

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=all_names,
                y=all_demands,
                marker_color=chart_colors,
                text=[f"{d:.2f}" for d in all_demands],
                textposition="auto",
            )
        )
        fig.update_layout(
            title="Potražnja za opsluživanjem (D_i) po stanici",
            yaxis_title="D_i (ms)",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Bjuzenov algoritam
# ---------------------------------------------------------------------------
def render_buzen():
    st.header("Bjuzenov algoritam")

    st.markdown(
        r"""
    **Bjuzenov algoritam** efikasno izračunava normalizacionu konstantu $G(N)$
    za zatvorene mreže čekanja sa $M$ servera i $N$ korisnika.

    Rekurzija:
    $$G(n) = \sum_{i=1}^{M} x_i \cdot G(n - 1) \quad \text{sa } G(0) = 1$$

    gde je $x_i = \frac{V_i}{\mu_i}$ relativno opterećenje servera $i$.

    **Performansne metrike:**
    - Iskorišćenje servera $i$: $U_i = x_i \cdot \frac{G(N-1)}{G(N)}$
    - Propusna moć: $X_0 = \frac{G(N-1)}{G(N)}$
    - Prosečan broj na serveru $i$: $\bar{n}_i = \sum_{n=1}^{N} x_i^n \cdot \frac{G_{-i}(N-n)}{G(N)}$
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        M = st.slider("Broj servera (M)", 2, 6, 3, key="buz_M")
        N = st.slider("Broj korisnika (N)", 1, 30, 8, key="buz_N")

        x_vals = []
        for i in range(M):
            xi = st.number_input(
                f"x_{i+1} (relativno opterećenje)",
                0.01,
                5.0,
                0.5 + 0.3 * i,
                0.05,
                key=f"buz_x{i+1}",
            )
            x_vals.append(xi)

    with col2:
        # Bjuzenov algoritam
        G = np.zeros(N + 1)
        G[0] = 1.0
        for n in range(1, N + 1):
            G[n] = sum(x * G[n - 1] for x in x_vals) if n == 1 else 0
            # Puni rekurzija
        # Korektna implementacija Bjuzenovog algoritma (konvolucija)
        G = np.zeros(N + 1)
        G[0] = 1.0
        # Za svaki server dodajemo njegov doprinos
        for i in range(M):
            G_new = np.zeros(N + 1)
            for n in range(N + 1):
                for j in range(n + 1):
                    G_new[n] += (x_vals[i] ** j) * (G[n - j] if i > 0 else (1.0 if n - j == 0 else 0.0))
            G = G_new.copy()

        # Alternativna iterativna implementacija (standardna)
        G = np.zeros(N + 1)
        G[0] = 1.0
        for i in range(M):
            G_new = np.zeros(N + 1)
            for n in range(N + 1):
                s = 0.0
                for k in range(n + 1):
                    s += (x_vals[i] ** k) * G[n - k]
                G_new[n] = s
            G = G_new.copy()

        # Normalizacija i metrike
        if G[N] > 0:
            X0 = G[N - 1] / G[N]

            # Iskorišćenje
            U = [xi * G[N - 1] / G[N] for xi in x_vals]

            # Prosečan broj korisnika na svakom serveru (koristeći marginals)
            avg_n = []
            for i in range(M):
                ni = 0
                for n in range(1, N + 1):
                    # Izračunaj G bez servera i za N-n
                    # Pojednostavljena aproksimacija: U_i * L formula
                    pass
                avg_n.append(U[i] / (1 - U[i]) if U[i] < 1 else N)

            st.markdown("### Rezultati Bjuzenovog algoritma")
            st.metric("Propusna moć X₀", f"{X0:.4f}")

            # Tabela G vrednosti
            import pandas as pd
            g_df = pd.DataFrame(
                {"n": list(range(N + 1)), "G(n)": [f"{g:.6f}" for g in G]}
            )
            st.markdown("#### Tabela G(n) vrednosti")
            st.dataframe(g_df, use_container_width=True, hide_index=True, height=250)

            # Iskorišćenje servera
            server_names = [f"Server {i+1}" for i in range(M)]
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=server_names,
                    y=U,
                    marker_color=["#2196F3" if u < 0.8 else "#FF9800" if u < 0.95 else "#F44336" for u in U],
                    text=[f"{u:.3f}" for u in U],
                    textposition="auto",
                )
            )
            fig.add_hline(y=1.0, line_dash="dash", line_color="red")
            fig.update_layout(
                title="Iskorišćenje servera (U_i)",
                yaxis_title="U_i",
                yaxis=dict(range=[0, 1.1]),
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Propusna moć vs N
            X_vs_N = []
            for n in range(1, N + 1):
                Gn = np.zeros(n + 1)
                Gn[0] = 1.0
                for ii in range(M):
                    Gn_new = np.zeros(n + 1)
                    for nn in range(n + 1):
                        s = 0.0
                        for k in range(nn + 1):
                            s += (x_vals[ii] ** k) * Gn[nn - k]
                        Gn_new[nn] = s
                    Gn = Gn_new.copy()
                if Gn[n] > 0:
                    X_vs_N.append(Gn[n - 1] / Gn[n])
                else:
                    X_vs_N.append(0)

            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=list(range(1, N + 1)),
                    y=X_vs_N,
                    mode="lines+markers",
                    line=dict(color="#E91E63", width=2),
                    name="X₀",
                )
            )
            fig2.update_layout(
                title="Propusna moć vs. broj korisnika",
                xaxis_title="Broj korisnika (N)",
                yaxis_title="Propusna moć X₀",
                height=350,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.error("G(N) = 0: Nemoguće izračunati metrike.")
