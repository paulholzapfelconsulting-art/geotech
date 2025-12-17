import streamlit as st
import math

# --- BERECHNUNGSLOGIK (Identisch zum vorherigen Skript) ---

def calculate_coefficients(phi_deg, alpha_deg, beta_deg, delta_ratio, phi_min_deg=40):
    
    def get_coulomb_k(phi_val, alpha_val, beta_val, delta_ratio_val):
        phi = math.radians(phi_val)
        alpha = math.radians(alpha_val)
        beta = math.radians(beta_val)
        delta = delta_ratio_val * phi
        
        num = math.cos(phi - alpha)**2
        d1 = math.cos(alpha)**2
        d2 = math.cos(alpha + delta)
        
        try:
            sqrt_term_num = math.sin(phi + delta) * math.sin(phi - beta)
            sqrt_term_den = math.cos(alpha + delta) * math.cos(alpha - beta)
            
            if sqrt_term_den == 0 or (sqrt_term_num / sqrt_term_den) < 0:
                return None
            
            sqrt_val = math.sqrt(sqrt_term_num / sqrt_term_den)
            bracket = (1 + sqrt_val)**2
            
            K_a_total = num / (d1 * d2 * bracket)
            K_ah_horizontal = K_a_total * math.cos(delta + alpha)
            return K_ah_horizontal
        except ValueError:
            return None

    def get_kach(phi_val, alpha_val, beta_val, delta_ratio_val):
        phi = math.radians(phi_val)
        alpha = math.radians(alpha_val)
        beta = math.radians(beta_val)
        delta = delta_ratio_val * phi

        try:
            num = 2 * math.cos(alpha - beta) * math.cos(phi) * math.cos(alpha + delta)
            den = 1 + math.sin(phi + alpha + delta - beta)
            if den == 0: return None
            return num / den
        except ValueError:
            return None

    k_agh = get_coulomb_k(phi_deg, alpha_deg, beta_deg, delta_ratio)
    k_ach = get_kach(phi_deg, alpha_deg, beta_deg, delta_ratio)
    k_min = get_coulomb_k(phi_min_deg, alpha_deg, beta_deg, delta_ratio)
    
    return k_agh, k_ach, k_min

# --- WEB-INTERFACE (Streamlit) ---

st.set_page_config(page_title="Geotechnik Rechner", page_icon="🏗️")

st.title("🏗️ Geotechnische Erddruck-Berechnung")
st.markdown("Berechnung von $K_{agh}$, $K_{ach}$ und $K_{ah,min}$ nach DIN 4085 / Coulomb.")

# Eingabebereich in der Seitenleiste oder oben
with st.container():
    st.subheader("Eingabewerte")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        in_phi = st.number_input("Reibungswinkel φ [°]", value=25.0, step=0.5, format="%.2f")
    with col2:
        in_alpha = st.number_input("Wandneigung α [°]", value=0.0, step=0.5, format="%.2f")
    with col3:
        in_beta = st.number_input("Geländeneigung β [°]", value=13.0, step=0.5, format="%.2f")

    # Wandreibung: Auswahl zwischen Standard 2/3 oder eigenem Wert
    use_custom_delta = st.checkbox("Manuelles Wandreibungsverhältnis eingeben", value=False)
    
    if use_custom_delta:
        in_delta_ratio = st.number_input("Verhältnis δ/φ", value=0.667, step=0.01)
    else:
        in_delta_ratio = 2.0/3.0
        st.info(f"Es wird mit dem Standardwert **δ/φ = 2/3** ({in_delta_ratio:.4f}...) gerechnet.")

    # Fester Wert V Hinweis
    st.caption("Hinweis: Ersatzwinkel für Mindesterddruck V ist fest auf **40°** eingestellt.")

# Berechnung
k_agh, k_ach, k_min = calculate_coefficients(in_phi, in_alpha, in_beta, in_delta_ratio)

st.divider()

# Ergebnisse anzeigen
st.subheader("Ergebnisse")

res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
    if k_agh is not None:
        st.metric(label="K_agh (Aktiv, horiz.)", value=f"{k_agh:.5f}")
    else:
        st.error("Fehler bei K_agh")

with res_col2:
    if k_ach is not None:
        st.metric(label="K_ach (Kohäsion)", value=f"{k_ach:.5f}")
    else:
        st.error("Fehler bei K_ach")

with res_col3:
    if k_min is not None:
        st.metric(label="K_ah,min (Mindesterddruck)", value=f"{k_min:.5f}")
    else:
        st.error("Fehler bei K_ah,min")

# Zusatzinfos
if k_agh is None:
    st.warning("Prüfung erforderlich: Ist die Geländeneigung β größer als der Reibungswinkel φ?")