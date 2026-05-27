import streamlit as st

st.set_page_config(
    page_title="Performanse računarskih sistema",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("📊 Performanse sistema")
st.sidebar.markdown("---")

module = st.sidebar.radio(
    "Izaberite modul:",
    [
        "🏠 Početna",
        "📐 K1: Procesor, disk, memorija",
        "📊 K2: Sistemi masovnog opsluživanja",
        "🌐 K3: Otvorene mreže i analiza",
    ],
)

if module == "🏠 Početna":
    st.title("Vizualizacija performansi računarskih sistema")
    st.markdown("### Interaktivni alat za učenje studenata")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📐 Modul K1")
        st.markdown(
            """
        **Performanse procesora, diskova i memorije**
        - Amdahl-ov zakon & Gustafson-ov zakon
        - CPU performanse (CPI, MIPS)
        - Performanse diska
        - Memorijska hijerarhija (keš)
        """
        )

    with col2:
        st.markdown("#### 📊 Modul K2")
        st.markdown(
            """
        **Sistemi masovnog opsluživanja**
        - Poasonov proces
        - M/M/1 red čekanja
        - M/M/c paralelni serveri
        - Ciklički model multiprogramiranja
        - Gordon-Njuelove jednačine
        - Bjuzenov algoritam
        """
        )

    with col3:
        st.markdown("#### 🌐 Modul K3")
        st.markdown(
            """
        **Otvorene mreže i analiza**
        - Otvorene mreže (Džeksonova teorema)
        - Matrični pristup
        - Interaktivni sistemi
        - MVA algoritam
        - Operaciona analiza
        """
        )

    st.markdown("---")
    st.info(
        "Izaberite modul u bočnom meniju (levo) da biste započeli interaktivne vežbe."
    )

elif module == "📐 K1: Procesor, disk, memorija":
    from modules import k1_module
    k1_module.render()

elif module == "📊 K2: Sistemi masovnog opsluživanja":
    from modules import k2_module
    k2_module.render()

elif module == "🌐 K3: Otvorene mreže i analiza":
    from modules import k3_module
    k3_module.render()
