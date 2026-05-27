# Vizuelizacija performansi računarskih sistema

Interaktivna web aplikacija za vizualizaciju modela iz oblasti performansi računarskih sistema, razvijena kao nastavno sredstvo za istoimeni kurs na Univerzitetu u Beogradu — Elektrotehničkom fakultetu.



## Funkcionalnosti

Aplikacija je organizovana u tri modula sa ukupno 14 vežbi:

**Modul K1 — Performanse hardvera**
- Amdahl-ov i Gustafson-ov zakon
- CPU performanse (CPI, MIPS, instruction mix)
- Performanse diska (seek, rotaciona latencija, transfer)
- Memorijska hijerarhija (L1/L2/L3 keš analiza sa heatmapom)

**Modul K2 — Sistemi masovnog opsluživanja**
- Poasonov proces
- M/M/1 red čekanja
- M/M/c (Erlang-C)
- Ciklički model multiprogramiranja
- Model mreže sa centralnim serverom
- Bjuzenov algoritam

**Modul K3 — Otvorene mreže i analiza**
- Otvorene mreže (Džeksonova teorema)
- MVA algoritam
- Interaktivni sistemi (balanced job bounds)
- Operaciona analiza

## Pokretanje

```bash
pip install -r requirements.txt
streamlit run app.py
```

Aplikacija se otvara u browser-u na `http://localhost:8501`.

## Tehnologije

- [Streamlit](https://streamlit.io/) — web framework
- [Plotly](https://plotly.com/python/) — interaktivni grafici
- [NumPy](https://numpy.org/) / [SciPy](https://scipy.org/) — numerički proračuni
- [Pandas](https://pandas.pydata.org/) — tabelarni prikazi

## Licenca

MIT
