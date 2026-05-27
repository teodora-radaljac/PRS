import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd


def render():
    st.title("🌐 Modul K3: Otvorene mreže i operaciona analiza")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Otvorene mreže (Džekson)",
            "MVA algoritam",
            "Interaktivni sistemi",
            "Operaciona analiza",
        ]
    )

    with tab1:
        render_jackson()
    with tab2:
        render_mva()
    with tab3:
        render_interactive_systems()
    with tab4:
        render_operational()


# ---------------------------------------------------------------------------
# Otvorene mreže — Džeksonova teorema
# ---------------------------------------------------------------------------
def render_jackson():
    st.header("Otvorene mreže čekanja — Džeksonova teorema")

    st.markdown(
        r"""
    **Džeksonova teorema:** U otvorenoj mreži čekanja sa Poasonovim dolascima
    i eksponencijalnim opsluživanjima, svaka stanica se ponaša kao nezavisan M/M/c red.

    **Klasičan pristup** — sistem jednačina za stope dolazaka:
    $$\lambda_i = \gamma_i + \sum_{j=1}^{M} \lambda_j \cdot r_{ji}$$

    gde je $\gamma_i$ eksterna stopa dolazaka na stanicu $i$, a $r_{ji}$ verovatnoća prelaza od $j$ ka $i$.

    **Matrični pristup:**
    $$\boldsymbol{\lambda} = \boldsymbol{\gamma} + \mathbf{R}^T \boldsymbol{\lambda}$$
    $$\boldsymbol{\lambda} = (\mathbf{I} - \mathbf{R}^T)^{-1} \boldsymbol{\gamma}$$
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        M = st.slider("Broj stanica", 2, 5, 3, key="jk_M")
        gamma_ext = st.number_input(
            "Eksterna stopa dolazaka γ (na stanicu 1)",
            0.1, 20.0, 5.0, 0.5, key="jk_gamma",
        )

        st.markdown("#### Matrica prelaza R")
        st.caption("r[i][j] = verovatnoća prelaza od stanice i ka stanici j")

        R = np.zeros((M, M))
        exit_probs = []
        for i in range(M):
            st.markdown(f"**Stanica {i+1}:**")
            remaining = 1.0
            for j in range(M):
                if remaining <= 0.001:
                    R[i][j] = 0.0
                    continue
                default_val = 0.0
                if i == 0 and j == 1 and M > 1:
                    default_val = 0.6
                elif i == 1 and j == 2 and M > 2:
                    default_val = 0.4
                elif i == 1 and j == 0:
                    default_val = 0.3
                R[i][j] = st.number_input(
                    f"r[{i+1}→{j+1}]",
                    0.0, remaining, min(default_val, remaining), 0.05,
                    key=f"jk_r{i}{j}",
                )
                remaining -= R[i][j]
            exit_probs.append(remaining)
            st.caption(f"Verovatnoća izlaska: {remaining:.2f}")

        mu_vals = []
        st.markdown("#### Stope opsluživanja")
        for i in range(M):
            mu_i = st.number_input(
                f"μ_{i+1}", 0.1, 50.0, 8.0 - i, 0.5, key=f"jk_mu{i}"
            )
            mu_vals.append(mu_i)

    with col2:
        # Matrični pristup
        gamma_vec = np.zeros(M)
        gamma_vec[0] = gamma_ext

        try:
            I = np.eye(M)
            A = I - R.T
            lambdas = np.linalg.solve(A, gamma_vec)

            if np.any(lambdas < 0):
                st.error("Negativne stope dolazaka — proverite matricu prelaza!")
                return

            # Izračunaj metrike za svaku stanicu (M/M/1)
            rhos = lambdas / np.array(mu_vals)
            stable = np.all(rhos < 1)

            st.markdown("### Rezultati (matrični pristup)")

            df_data = {
                "Stanica": [f"Stanica {i+1}" for i in range(M)],
                "λ_i": [f"{l:.3f}" for l in lambdas],
                "μ_i": [f"{m:.1f}" for m in mu_vals],
                "ρ_i": [f"{r:.3f}" for r in rhos],
            }

            if stable:
                Ls = rhos / (1 - rhos)
                Ws = 1 / (np.array(mu_vals) - lambdas)
                df_data["L_i"] = [f"{l:.3f}" for l in Ls]
                df_data["W_i (s)"] = [f"{w:.4f}" for w in Ws]
            else:
                df_data["Status"] = ["OK" if r < 1 else "NESTABILNA!" for r in rhos]

            st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

            if stable:
                L_total = np.sum(Ls)
                W_total = L_total / gamma_ext
                mc1, mc2 = st.columns(2)
                mc1.metric("L (ukupno u mreži)", f"{L_total:.2f}")
                mc2.metric("W (ukupno vreme)", f"{W_total:.4f} s")

            # Vizualizacija iskorišćenja
            colors = ["#4CAF50" if r < 0.7 else "#FF9800" if r < 0.9 else "#F44336" for r in rhos]
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=[f"Stanica {i+1}" for i in range(M)],
                    y=rhos,
                    marker_color=colors,
                    text=[f"{r:.3f}" for r in rhos],
                    textposition="auto",
                )
            )
            fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="ρ=1")
            fig.update_layout(
                title="Iskorišćenje stanica (ρ_i)",
                yaxis_title="ρ_i",
                yaxis=dict(range=[0, 1.1]),
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Prikaži matricu R
            st.markdown("### Matrica prelaza R")
            r_df = pd.DataFrame(
                R,
                index=[f"Od {i+1}" for i in range(M)],
                columns=[f"Ka {j+1}" for j in range(M)],
            )
            st.dataframe(r_df, use_container_width=True)

        except np.linalg.LinAlgError:
            st.error("Matrica (I - R^T) je singularna. Proverite matricu prelaza.")


# ---------------------------------------------------------------------------
# MVA algoritam
# ---------------------------------------------------------------------------
def render_mva():
    st.header("MVA (Mean Value Analysis) algoritam")

    st.markdown(
        r"""
    **MVA algoritam** iterativno izračunava performanse zatvorene mreže čekanja sa $M$ stanica i $N$ korisnika.

    Za svaku iteraciju $n = 1, 2, \ldots, N$:

    1. **Prosečno vreme odziva:** $R_i(n) = S_i \cdot (1 + \bar{n}_i(n-1))$
    2. **Propusna moć:** $X_0(n) = \frac{n}{\sum_{i=1}^{M} V_i \cdot R_i(n) + Z}$
    3. **Prosečan broj korisnka:** $\bar{n}_i(n) = X_0(n) \cdot V_i \cdot R_i(n)$

    Inicijalni uslov: $\bar{n}_i(0) = 0$ za sve $i$.
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        M = st.slider("Broj stanica (M)", 2, 6, 3, key="mva_M")
        N = st.slider("Broj korisnika (N)", 1, 30, 10, key="mva_N")
        Z = st.number_input("Think time Z (s)", 0.0, 30.0, 5.0, 0.5, key="mva_Z")

        V_vals = []
        S_vals = []
        for i in range(M):
            v = st.number_input(
                f"V_{i+1} (broj poseta)", 0.1, 20.0, 1.0 + 0.5 * i, 0.1, key=f"mva_v{i}"
            )
            s = st.number_input(
                f"S_{i+1} (service time, s)", 0.001, 5.0, 0.05 * (i + 1), 0.005, key=f"mva_s{i}"
            )
            V_vals.append(v)
            S_vals.append(s)

    with col2:
        V = np.array(V_vals)
        S = np.array(S_vals)
        D = V * S  # Service demands

        # MVA iteracije
        n_bar = np.zeros(M)  # prosečan broj na svakoj stanici

        # Čuvamo istoriju za vizualizaciju
        X_history = []
        R_total_history = []
        n_bar_history = [n_bar.copy()]

        for n in range(1, N + 1):
            R = S * (1 + n_bar)
            X0 = n / (np.sum(V * R) + Z)
            n_bar = X0 * V * R
            X_history.append(X0)
            R_total_history.append(np.sum(V * R))
            n_bar_history.append(n_bar.copy())

        # Konačni rezultati
        R_final = S * (1 + n_bar_history[-2]) if N > 1 else S
        U = X_history[-1] * D

        st.markdown("### Rezultati MVA")

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Propusna moć X₀", f"{X_history[-1]:.4f} pos/s")
        mc2.metric("Ukupno vreme odziva R", f"{R_total_history[-1]:.4f} s")
        mc3.metric("Iskorišćenje max", f"{max(U):.3f}")

        # Tabela po stanici
        df = pd.DataFrame({
            "Stanica": [f"Stanica {i+1}" for i in range(M)],
            "V_i": [f"{v:.2f}" for v in V],
            "S_i (s)": [f"{s:.4f}" for s in S],
            "D_i (s)": [f"{d:.4f}" for d in D],
            "R_i (s)": [f"{r:.4f}" for r in R_final],
            "U_i": [f"{u:.4f}" for u in U],
            "n̄_i": [f"{n:.3f}" for n in n_bar],
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Grafik: X0 i R vs N
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=list(range(1, N + 1)),
                y=X_history,
                mode="lines+markers",
                name="Propusna moć X₀",
                line=dict(color="#2196F3", width=2),
            )
        )
        fig.update_layout(
            title="Propusna moć vs. broj korisnika (MVA)",
            xaxis_title="Broj korisnika (N)",
            yaxis_title="X₀ (pos/s)",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=list(range(1, N + 1)),
                y=R_total_history,
                mode="lines+markers",
                name="Vreme odziva R",
                line=dict(color="#FF9800", width=2),
            )
        )
        fig2.update_layout(
            title="Vreme odziva vs. broj korisnika (MVA)",
            xaxis_title="Broj korisnika (N)",
            yaxis_title="R (s)",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Prosečan broj korisnika po stanici za svaki N
        n_bar_arr = np.array(n_bar_history[1:])
        fig3 = go.Figure()
        for i in range(M):
            fig3.add_trace(
                go.Scatter(
                    x=list(range(1, N + 1)),
                    y=n_bar_arr[:, i],
                    mode="lines",
                    name=f"Stanica {i+1}",
                    line=dict(width=2),
                )
            )
        fig3.update_layout(
            title="Prosečan broj korisnika po stanici vs. N",
            xaxis_title="Broj korisnika (N)",
            yaxis_title="n̄_i",
            height=350,
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.info(
        "💡 **Pitanje:** Kako se menja propusna moć kada povećavamo N? "
        "Zašto postoji plato?"
    )


# ---------------------------------------------------------------------------
# Interaktivni sistemi
# ---------------------------------------------------------------------------
def render_interactive_systems():
    st.header("Interaktivni sistemi")

    st.markdown(
        r"""
    Interaktivni sistem = zatvorena mreža sa terminalom (think time $Z$).

    **Zakon odziva za interaktivne sisteme:**
    $$R = \frac{N}{X_0} - Z$$

    **Granice performansi (Balanced Job Bounds):**
    - $X_0 \leq \min\left(\frac{1}{D_{max}}, \frac{N}{D + Z}\right)$
    - $R \geq \max(D, N \cdot D_{max} - Z)$

    gde je $D = \sum_{i=1}^{M} D_i$ ukupna potražnja, $D_{max} = \max_i(D_i)$ usko grlo.
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        M = st.slider("Broj stanica", 2, 6, 3, key="is_M")
        N_max = st.slider("Maksimalan broj korisnika", 5, 100, 40, key="is_Nmax")
        Z = st.number_input("Think time Z (s)", 0.0, 60.0, 10.0, 1.0, key="is_Z")

        D_vals = []
        for i in range(M):
            di = st.number_input(
                f"D_{i+1} (service demand, s)",
                0.001, 5.0, 0.1 * (i + 1), 0.01, key=f"is_d{i}"
            )
            D_vals.append(di)

    with col2:
        D_arr = np.array(D_vals)
        D_total = np.sum(D_arr)
        D_max = np.max(D_arr)
        bottleneck_idx = np.argmax(D_arr)

        st.warning(f"⚠️ Usko grlo: **Stanica {bottleneck_idx + 1}** (D = {D_max:.3f} s)")

        N_range = np.arange(1, N_max + 1, dtype=float)

        # Granice
        X_upper = np.minimum(1 / D_max, N_range / (D_total + Z))
        R_lower = np.maximum(D_total, N_range * D_max - Z)

        # MVA tačne vrednosti
        S = D_arr  # V_i = 1 za svaku stanicu
        V = np.ones(M)
        X_mva = []
        R_mva = []

        for N_cur in range(1, N_max + 1):
            n_bar = np.zeros(M)
            for n in range(1, N_cur + 1):
                R = S * (1 + n_bar)
                X0 = n / (np.sum(V * R) + Z)
                n_bar = X0 * V * R
            X_mva.append(X0)
            R_mva.append(np.sum(V * S * (1 + n_bar)) if N_cur > 0 else D_total)
        # Recalculate R_mva properly
        R_mva_correct = []
        n_bar_reset = np.zeros(M)
        for N_cur in range(1, N_max + 1):
            n_b = np.zeros(M)
            for n in range(1, N_cur + 1):
                Ri = S * (1 + n_b)
                X0 = n / (np.sum(V * Ri) + Z)
                n_b = X0 * V * Ri
            Ri_final = S * (1 + (np.zeros(M) if N_cur == 1 else n_b))
            R_mva_correct.append(N_cur / X0 - Z)

        # Grafik propusne moći
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=N_range, y=X_upper, mode="lines", name="Gornja granica",
                line=dict(color="#F44336", width=2, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=N_range, y=X_mva, mode="lines", name="MVA (tačno)",
                line=dict(color="#2196F3", width=3),
            )
        )
        # Saturacioni tačka: N* = (D + Z) / D_max
        N_star = (D_total + Z) / D_max
        fig.add_vline(
            x=N_star, line_dash="dot", line_color="green",
            annotation_text=f"N* = {N_star:.1f}",
        )
        fig.update_layout(
            title="Propusna moć: MVA vs. granice",
            xaxis_title="Broj korisnika (N)",
            yaxis_title="X₀ (pos/s)",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Grafik vremena odziva
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=N_range, y=R_lower, mode="lines", name="Donja granica",
                line=dict(color="#F44336", width=2, dash="dash"),
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=N_range, y=R_mva_correct, mode="lines", name="MVA (tačno)",
                line=dict(color="#FF9800", width=3),
            )
        )
        fig2.add_vline(
            x=N_star, line_dash="dot", line_color="green",
            annotation_text=f"N* = {N_star:.1f}",
        )
        fig2.update_layout(
            title="Vreme odziva: MVA vs. granice",
            xaxis_title="Broj korisnika (N)",
            yaxis_title="R (s)",
            height=400,
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.info(
            f"💡 **N*** = {N_star:.1f} — tačka saturacije. "
            "Pre ove tačke dodavanje korisnika ne degradira vreme odziva značajno. "
            "Posle nje, vreme odziva raste linearno."
        )


# ---------------------------------------------------------------------------
# Operaciona analiza
# ---------------------------------------------------------------------------
def render_operational():
    st.header("Operaciona analiza")

    st.markdown(
        r"""
    Operaciona analiza koristi merljive veličine za analizu performansi:

    | Zakon | Formula | Opis |
    |-------|---------|------|
    | **Little-ov zakon** | $L = \lambda \cdot W$ | Broj u sistemu = stopa dolazaka × vreme |
    | **Zakon iskorišćenja** | $U_i = X \cdot S_i$ | Iskorišćenje = propusna moć × service time |
    | **Zakon prinudnog toka** | $X_i = V_i \cdot X_0$ | Propusna moć stanice = posete × ukupna propusna moć |
    | **Zakon service demand** | $D_i = V_i \cdot S_i$ | Potražnja = posete × service time |
    """
    )

    subtab1, subtab2, subtab3 = st.tabs(
        ["Little-ov zakon", "Zakon iskorišćenja", "Zakon prinudnog toka"]
    )

    with subtab1:
        render_little()
    with subtab2:
        render_utilization_law()
    with subtab3:
        render_forced_flow()


def render_little():
    st.subheader("Little-ov zakon: L = λ · W")

    st.markdown(
        "Menjajte dva od tri parametra i posmatrajte kako se treći izračunava."
    )

    mode = st.radio(
        "Izračunaj:",
        ["L (prosečan broj u sistemu)", "λ (stopa dolazaka)", "W (prosečno vreme)"],
        key="little_mode",
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        if mode == "L (prosečan broj u sistemu)":
            lam = st.slider("λ (dolazaka/s)", 0.1, 20.0, 5.0, 0.1, key="lit_lam")
            W = st.slider("W (s)", 0.01, 10.0, 2.0, 0.01, key="lit_W")
            L = lam * W
            st.metric("L = λ · W", f"{L:.2f}")
        elif mode == "λ (stopa dolazaka)":
            L = st.slider("L (prosečan broj)", 0.1, 50.0, 10.0, 0.1, key="lit_L2")
            W = st.slider("W (s)", 0.01, 10.0, 2.0, 0.01, key="lit_W2")
            lam = L / W
            st.metric("λ = L / W", f"{lam:.2f} dol/s")
        else:
            L = st.slider("L (prosečan broj)", 0.1, 50.0, 10.0, 0.1, key="lit_L3")
            lam = st.slider("λ (dolazaka/s)", 0.1, 20.0, 5.0, 0.1, key="lit_lam3")
            W = L / lam
            st.metric("W = L / λ", f"{W:.3f} s")

    with col2:
        # 3D vizualizacija Little-ovog zakona
        lam_r = np.linspace(0.1, 20, 50)
        W_r = np.linspace(0.1, 10, 50)
        LAM, WW = np.meshgrid(lam_r, W_r)
        LL = LAM * WW

        fig = go.Figure(
            go.Surface(
                x=lam_r, y=W_r, z=LL,
                colorscale="Viridis",
                colorbar=dict(title="L"),
            )
        )
        fig.update_layout(
            title="Little-ov zakon: L = λ · W",
            scene=dict(
                xaxis_title="λ (dolazaka/s)",
                yaxis_title="W (s)",
                zaxis_title="L",
            ),
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)


def render_utilization_law():
    st.subheader("Zakon iskorišćenja: U_i = X · S_i")

    col1, col2 = st.columns([1, 2])

    with col1:
        X = st.slider("Propusna moć X (pos/s)", 0.1, 20.0, 5.0, 0.1, key="util_X")
        n_devices = st.slider("Broj uređaja", 1, 6, 3, key="util_nd")

        S_vals = []
        for i in range(n_devices):
            s = st.number_input(
                f"S_{i+1} (ms)", 0.1, 500.0, 20.0 * (i + 1), 1.0, key=f"util_s{i}"
            )
            S_vals.append(s / 1000)  # u sekunde

    with col2:
        U_vals = [X * s for s in S_vals]
        names = [f"Uređaj {i+1}" for i in range(n_devices)]

        colors = [
            "#4CAF50" if u < 0.7 else "#FF9800" if u < 0.9 else "#F44336"
            for u in U_vals
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=names, y=U_vals, marker_color=colors,
                text=[f"{u:.3f}" for u in U_vals],
                textposition="auto",
            )
        )
        fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="U=1 (saturacija)")
        fig.update_layout(
            title="Iskorišćenje uređaja",
            yaxis_title="U_i",
            yaxis=dict(range=[0, max(1.1, max(U_vals) * 1.1)]),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        if any(u >= 1 for u in U_vals):
            saturated = [names[i] for i, u in enumerate(U_vals) if u >= 1]
            st.error(f"⚠️ Saturiran: {', '.join(saturated)} — sistem nestabilan!")

        # Maksimalna propusna moć
        X_max = min(1 / s for s in S_vals)
        bottleneck = names[np.argmax(S_vals)]
        st.metric("Maksimalna propusna moć X_max", f"{X_max:.2f} pos/s")
        st.warning(f"Usko grlo: **{bottleneck}**")


def render_forced_flow():
    st.subheader("Zakon prinudnog toka: X_i = V_i · X₀")

    col1, col2 = st.columns([1, 2])

    with col1:
        X0 = st.slider("Ukupna propusna moć X₀ (pos/s)", 0.1, 10.0, 2.0, 0.1, key="ff_X0")
        n_stations = st.slider("Broj stanica", 2, 6, 4, key="ff_ns")

        V_vals = []
        S_vals = []
        for i in range(n_stations):
            v = st.number_input(
                f"V_{i+1} (posete)", 0.1, 20.0, 1.0 + i * 0.5, 0.1, key=f"ff_v{i}"
            )
            s = st.number_input(
                f"S_{i+1} (ms)", 0.1, 200.0, 10.0 + 5.0 * i, 1.0, key=f"ff_s{i}"
            )
            V_vals.append(v)
            S_vals.append(s / 1000)

    with col2:
        X_vals = [X0 * v for v in V_vals]
        D_vals = [v * s for v, s in zip(V_vals, S_vals)]
        U_vals = [X0 * d for d in D_vals]
        names = [f"Stanica {i+1}" for i in range(n_stations)]

        df = pd.DataFrame({
            "Stanica": names,
            "V_i": [f"{v:.2f}" for v in V_vals],
            "S_i (s)": [f"{s:.4f}" for s in S_vals],
            "X_i (pos/s)": [f"{x:.3f}" for x in X_vals],
            "D_i (s)": [f"{d:.4f}" for d in D_vals],
            "U_i": [f"{u:.4f}" for u in U_vals],
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=names, y=X_vals, name="X_i (pos/s)",
                marker_color="#2196F3",
                text=[f"{x:.2f}" for x in X_vals],
                textposition="auto",
            )
        )
        fig.update_layout(
            title="Propusna moć po stanici (X_i = V_i · X₀)",
            yaxis_title="X_i (pos/s)",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        colors = [
            "#4CAF50" if u < 0.7 else "#FF9800" if u < 0.9 else "#F44336"
            for u in U_vals
        ]
        fig2.add_trace(
            go.Bar(
                x=names, y=U_vals, marker_color=colors,
                text=[f"{u:.3f}" for u in U_vals],
                textposition="auto",
            )
        )
        fig2.add_hline(y=1.0, line_dash="dash", line_color="red")
        fig2.update_layout(
            title="Iskorišćenje po stanici (U_i = X₀ · D_i)",
            yaxis_title="U_i",
            yaxis=dict(range=[0, max(1.1, max(U_vals) * 1.1) if U_vals else 1.1]),
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)
