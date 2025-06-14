import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import io # Required for in-memory file operations for Excel

# --- Basic Streamlit Page Configuration ---
st.set_page_config(page_title="App 6 Jarrones", layout="wide")
st.title("💰 App de los 6 Jarrones con Subcategorías")

# --- Session State Initialization ---
# Use st.session_state to remember expenses as they are added across reruns
# Ensure this is initialized robustly on app start or reload
if 'jarron_gastos' not in st.session_state:
    st.session_state.jarron_gastos = {}
    # Initialize an empty list for each jar (jarrón) to store expenses
    for jarron_name in [
        "Gastos básicos", "Inversiones a largo plazo", "Educación",
        "Invertir", "Diversión", "Donar"
    ]:
        st.session_state.jarron_gastos[jarron_name] = []
# Ensure existing jarron_gastos have all expected jars if reloading an old session state
else:
    for jarron_name in [
        "Gastos básicos", "Inversiones a largo plazo", "Educación",
        "Invertir", "Diversión", "Donar"
    ]:
        if jarron_name not in st.session_state.jarron_gastos:
            st.session_state.jarron_gastos[jarron_name] = []


# --- User Input Section (Section 1) ---
st.header("1. Ingresa tus datos mensuales")

# Monthly Income Field (modified to appear empty initially)
# Use st.text_input so it can start empty, then convert to float
ingreso_str = st.text_input("Ingresa tu ingreso mensual total ($)", value="", placeholder="Ej: 2500000.00")

ingreso = 0.0 # Default value if the field is empty or invalid
if ingreso_str: # Only try to convert if the field is not empty
    try:
        # Replace comma with dot to ensure float conversion works for different locales
        ingreso = float(ingreso_str.replace(",", "."))
        if ingreso < 0:
            st.error("El ingreso no puede ser un valor negativo.")
            st.stop() # Stop execution if income is negative
    except ValueError:
        st.error("Por favor, ingresa un número válido para tu ingreso mensual.")
        st.stop() # Stop execution if input is not a valid number

# Validate that income is greater than 0 before proceeding
if ingreso <= 0:
    st.warning("Por favor, ingresa un ingreso mensual válido para continuar con la distribución.")
    st.stop() # Stop execution if income is 0 or negative

# Month Field (modified to appear with "Selecciona un Mes" initially)
mes_options = [
    "Selecciona un Mes", # New initial option
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
mes = st.selectbox("Mes", options=mes_options, index=0) # index=0 to start with "Selecciona un Mes"

# Month Validation
if mes == "Selecciona un Mes":
    st.warning("Por favor, selecciona un mes válido para continuar.")
    st.stop() # Stop execution of the rest of the app until a valid month is selected

# Year Field (kept with default value, common for years)
año = st.number_input("Año", min_value=2000, max_value=2100, value=2025)

# --- Jar Percentages ---
porcentajes = {
    "Gastos básicos": 0.55,
    "Inversiones a largo plazo": 0.10,
    "Educación": 0.10,
    "Invertir": 0.10,
    "Diversión": 0.10,
    "Donar": 0.05
}

# --- Predefined Subcategories ---
subcategorias_listas = {
    # "Deudas" and "Colegio o Universidad" are now in "Gastos básicos"
    "Gastos básicos": ["Deudas", "Arriendo / Hipoteca", "Servicios públicos", "Alimentación", "Transporte", "Colegio o Universidad", "Otros Gastos Básicos"],
    "Inversiones a largo plazo": ["Carro", "Casa", "Negocio propio", "Ahorro programado", "Otros Inversiones Largo Plazo"],
    # "Colegio o Universidad" removed from "Educación"
    "Educación": ["Cursos online", "Libros", "Talleres", "Certificaciones", "Otros Educación"],
    "Invertir": ["CDTs", "Bitcoins", "Acciones", "Fondos de inversión", "Otros Inversiones"],
    "Diversión": ["Viajes", "Restaurantes", "Cine / Entretenimiento", "Compras personales", "Otros Diversión"],
    "Donar": ["Fundaciones", "Familia / Amigos", "Proyectos sociales", "Iglesia / Comunidad", "Otros Donar"],
}

# --- Jar and Subcategory Logic & Visualization (Section 2) ---
st.header("2. Distribución de tu Ingreso")

# Calculate the total amount assigned globally from session state
total_ingreso_distribuido_gastos = sum(
    item["monto"] for jarron_name, expenses in st.session_state.jarron_gastos.items() for item in expenses
)

for jarron, porcentaje in porcentajes.items():
    monto_jarron = round(ingreso * porcentaje, 2)
    st.subheader(f"✨ **{jarron}** - _{porcentaje*100:.0f}% (${monto_jarron:.2f})_")

    # Calculate the currently assigned amount for this jar
    current_assigned_for_jarron = sum(item["monto"] for item in st.session_state.jarron_gastos[jarron])
    remaining_for_jarron = round(monto_jarron - current_assigned_for_jarron, 2)

    # Display table of assigned expenses for this jar
    if st.session_state.jarron_gastos[jarron]:
        st.markdown("##### Gastos Asignados en esta Sesión:")
        df_jarron_actual_display = pd.DataFrame(st.session_state.jarron_gastos[jarron])
        df_jarron_actual_display.columns = ["Subcategoría", "Monto Asignado"]
        st.dataframe(df_jarron_actual_display, hide_index=True, use_container_width=True)
    
    # Remaining balance message
    if remaining_for_jarron < 0:
        st.error(f"⚠️ **Te has excedido en '{jarron}':** ${-remaining_for_jarron:.2f} sobre el límite del jarrón.")
    elif remaining_for_jarron == 0:
        st.success(f"✅ **'{jarron}'** asignado completamente. ($0.00 restante)")
    else:
        st.info(f"💡 **Disponible en '{jarron}':** ${remaining_for_jarron:.2f}")

    st.markdown("###### Añadir nuevo gasto:")
    col1, col2, col3 = st.columns([0.4, 0.3, 0.2])

    with col1:
        # Subcategory options, including an initial "Select" option
        options_for_selectbox = ["-- Selecciona --"] + subcategorias_listas[jarron]
        selected_sub = st.selectbox(
            f"Elige Subcategoría para {jarron}",
            options=options_for_selectbox,
            key=f"select_{jarron}_{mes}_{año}" # Unique key
        )
    with col2:
        # Amount input (text_input to allow empty initial state)
        amount_str = st.text_input(
            f"Monto para {selected_sub}",
            value="",
            placeholder=f"Max: ${remaining_for_jarron:.2f}",
            key=f"amount_{jarron}_{selected_sub}_{mes}_{año}" # Unique key
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True) # Space to align button
        add_button_key = f"add_{jarron}_{mes}_{año}_{len(st.session_state.jarron_gastos[jarron])}" # Unique key
        if st.button("➕ Añadir", key=add_button_key):
            if selected_sub == "-- Selecciona --":
                st.error("Por favor, selecciona una subcategoría válida.")
            elif not amount_str:
                st.error("Por favor, ingresa un monto para el gasto.")
            else:
                try:
                    amount = float(amount_str.replace(",", ".")) # Replace comma with dot
                    if amount <= 0:
                        st.error("El monto debe ser un valor positivo.")
                    elif current_assigned_for_jarron + amount > monto_jarron + 0.001: # Small float tolerance
                        st.error(f"¡Exceso! Este gasto haría que te excedas en ${round(current_assigned_for_jarron + amount - monto_jarron, 2):.2f}. Reduce el valor.")
                    else:
                        # Add expense to session state
                        st.session_state.jarron_gastos[jarron].append({
                            "sub": selected_sub,
                            "monto": amount
                        })
                        st.rerun() # Rerun to update the interface with the new expense
                except ValueError:
                    st.error("Por favor, ingresa un monto numérico válido.")

    st.markdown("---") # Separator between jars

# --- Total Assignment Summary ---
st.subheader("Resumen de Asignación Total")
total_no_asignado_global = round(ingreso - total_ingreso_distribuido_gastos, 2)
if total_no_asignado_global > 0:
    st.warning(f"**Atención:** ${total_no_asignado_global:.2f} de tu ingreso total (${ingreso:.2f}) no ha sido asignado a ninguna subcategoría.")
elif total_no_asignado_global < 0:
     st.error(f"**¡Alerta de Exceso!** Te has excedido en ${-total_no_asignado_global:.2f} sobre tu ingreso total.")
else:
    st.success(f"**¡Felicidades!** Has asignado el 100% de tu ingreso (${ingreso:.2f}) a tus jarrones y subcategorías.")


# --- Save and Show History Button ---
# Reconstruct the 'resultados' DataFrame from session state to save
resultados_para_guardar = []

# --- IMPORTANT: Add the current month's total income as a special entry ---
resultados_para_guardar.append({
    "Año": año,
    "Mes": mes,
    "Jarrón": "Ingreso Mensual", # Special Jarrón to represent total income for the month
    "Subcategoría": "Total Ingreso",
    "Monto asignado": ingreso # The total income for this current month
})

# Add all the expenses from session state
for jarron_name, expenses in st.session_state.jarron_gastos.items():
    for expense in expenses:
        resultados_para_guardar.append({
            "Año": año,
            "Mes": mes,
            "Jarrón": jarron_name,
            "Subcategoría": expense["sub"],
            "Monto asignado": expense["monto"]
        })

if st.button("💾 Guardar y Mostrar Historial", key="save_button"):
    # Check if there are any actual expenses (besides the income entry)
    if len(resultados_para_guardar) <= 1 and ingreso == 0: # If only income entry exists and income is 0
        st.warning("No hay datos significativos (ingreso o gastos) para guardar.")
    else:
        df_resultado_actual = pd.DataFrame(resultados_para_guardar)
        
        # Save history to a CSV file
        archivo = "historial_desglose_jarrones.csv"
        df_final = pd.DataFrame()

        if os.path.exists(archivo):
            try:
                df_existente = pd.read_csv(archivo)
                # Filter out previous income entries for the current month/year to avoid duplication
                df_existente_filtered = df_existente[
                    ~((df_existente['Año'] == año) & 
                      (df_existente['Mes'] == mes) & 
                      (df_existente['Jarrón'] == "Ingreso Mensual"))
                ]
                # Filter out previous expense entries for the current month/year to avoid duplication
                # This ensures that if a user re-saves for the same month, it updates rather than duplicates
                df_existente_filtered = df_existente_filtered[
                    ~((df_existente_filtered['Año'] == año) & 
                      (df_existente_filtered['Mes'] == mes) & 
                      (df_existente_filtered['Jarrón'] != "Ingreso Mensual"))
                ]
                
                df_final = pd.concat([df_existente_filtered, df_resultado_actual], ignore_index=True)
            except pd.errors.EmptyDataError:
                st.warning("El archivo de historial está vacío. Se creará uno nuevo.")
                df_final = df_resultado_actual
            except Exception as e:
                st.error(f"Error al leer el historial existente: {e}. Se intentará guardar solo los datos actuales.")
                df_final = df_resultado_actual
        else:
            df_final = df_resultado_actual
        
        df_final.to_csv(archivo, index=False)
        st.success("✅ ¡Datos registrados y historial actualizado!")
        
        # --- NEW SECTIONS: MONTHLY AND ANNUAL ACCUMULATIONS (Simplified) ---
        st.subheader("📈 Acumulados Históricos")
        
        if not df_final.empty:
            # Monthly Accumulation - Simplified
            st.markdown("### Resumen Mensual")
            # First, map month names to numbers for correct sorting
            meses_map = {
                "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
                "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
            }
            # Ensure 'Mes_Num' is created and is a numeric type for sorting
            df_final['Mes_Num'] = df_final['Mes'].map(meses_map).fillna(0).astype(int)
            
            # Group by Year, Mes_Num, Mes, and Jarrón, then sum Monto asignado
            df_monthly_summary = df_final.groupby(['Año', 'Mes_Num', 'Mes', 'Jarrón'])['Monto asignado'].sum().reset_index()
            
            # Pivot the table to have Jarrón names as columns
            df_monthly_pivot = df_monthly_summary.pivot_table(
                index=['Año', 'Mes_Num', 'Mes'], # Mes_Num is part of the index for sorting
                columns='Jarrón', 
                values='Monto asignado', 
                fill_value=0
            ).reset_index()

            # Ensure all expected jar columns exist before reordering
            all_jars_columns = ["Ingreso Mensual"] + list(porcentajes.keys())
            for col in all_jars_columns:
                if col not in df_monthly_pivot.columns:
                    df_monthly_pivot[col] = 0.0 # Add missing jar columns with 0

            # Calculate total spent for display (excluding Ingreso Mensual)
            gastos_cols_monthly = [col for col in porcentajes.keys() if col in df_monthly_pivot.columns]
            df_monthly_pivot['Total Gastado del Mes'] = df_monthly_pivot[gastos_cols_monthly].sum(axis=1)

            # Calculate remaining balance for the month
            df_monthly_pivot['Saldo Mensual'] = df_monthly_pivot['Ingreso Mensual'] - df_monthly_pivot['Total Gastado del Mes']

            # Sort df_monthly_pivot FIRST by Year and Mes_Num, then select simplified columns
            df_monthly_pivot_sorted = df_monthly_pivot.sort_values(by=['Año', 'Mes_Num'])

            # Now create the simplified DataFrame from the *sorted* pivot table
            df_monthly_simplified = df_monthly_pivot_sorted[['Año', 'Mes', 'Ingreso Mensual', 'Total Gastado del Mes', 'Saldo Mensual']]
            
            st.dataframe(df_monthly_simplified, use_container_width=True) # No need to sort again here
            
            # Annual Accumulation - Simplified
            st.markdown("### Resumen Anual")
            df_annual_summary = df_final.groupby(['Año', 'Jarrón'])['Monto asignado'].sum().reset_index()
            df_annual_pivot = df_annual_summary.pivot_table(
                index='Año', 
                columns='Jarrón', 
                values='Monto asignado', 
                fill_value=0
            ).reset_index()

            # Reorder columns and calculate totals/balance for annual summary
            for col in all_jars_columns: # Reuse all_jars_columns from monthly for consistency
                if col not in df_annual_pivot.columns:
                    df_annual_pivot[col] = 0.0 # Add missing jar columns with 0

            df_annual_pivot['Total Gastado del Año'] = df_annual_pivot[[col for col in porcentajes.keys() if col in df_annual_pivot.columns]].sum(axis=1)
            # The 'Ingreso Mensual' column in df_annual_pivot already represents the sum for the year because
            # it was grouped by 'Año' and 'Jarrón' (where Ingreso Mensual is a Jarrón category)
            df_annual_pivot['Ingreso Total Anual'] = df_annual_pivot['Ingreso Mensual'] 
            df_annual_pivot['Saldo Anual'] = df_annual_pivot['Ingreso Total Anual'] - df_annual_pivot['Total Gastado del Año']

            df_annual_simplified = df_annual_pivot[['Año', 'Ingreso Total Anual', 'Total Gastado del Año', 'Saldo Anual']]
            st.dataframe(df_annual_simplified.sort_values(by='Año'), use_container_width=True)
            
            # Clean up temporary columns from df_final (Mes_Num is used before this point)
            if 'Mes_Num' in df_final.columns: # Check if column exists before dropping
                df_final.drop(columns=['Mes_Num'], errors='ignore', inplace=True) 

        else:
            st.info("No hay datos en el historial para mostrar acumulados.")


        # --- Download Buttons ---
        st.subheader("Opciones de Descarga")

        # Download as CSV
        csv_download = df_final.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar historial (CSV)",
            csv_download,
            "jarrones_historial.csv",
            "text/csv",
            key="download_csv"
        )
        
        # Download as Excel (New functionality)
        excel_buffer = io.BytesIO()
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Ensure 'Monto asignado' is numeric for Excel formatting if needed
        # Convert df_final 'Monto asignado' to numeric, handling errors
        df_final['Monto asignado'] = pd.to_numeric(df_final['Monto asignado'], errors='coerce').fillna(0)
        
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, sheet_name='Historial Completo', index=False)
            
            # Optionally add monthly and annual summaries to different sheets
            if not df_monthly_simplified.empty:
                # Convert 'Ingreso Mensual', 'Total Gastado del Mes', 'Saldo Mensual' to numeric
                for col in ['Ingreso Mensual', 'Total Gastado del Mes', 'Saldo Mensual']:
                    if col in df_monthly_simplified.columns:
                        df_monthly_simplified[col] = pd.to_numeric(df_monthly_simplified[col], errors='coerce').fillna(0)
                df_monthly_simplified.to_excel(writer, sheet_name='Resumen Mensual', index=False)
            if not df_annual_simplified.empty:
                # Convert 'Ingreso Total Anual', 'Total Gastado del Año', 'Saldo Anual' to numeric
                for col in ['Ingreso Total Anual', 'Total Gastado del Año', 'Saldo Anual']:
                    if col in df_annual_simplified.columns:
                        df_annual_simplified[col] = pd.to_numeric(df_annual_simplified[col], errors='coerce').fillna(0)
                df_annual_simplified.to_excel(writer, sheet_name='Resumen Anual', index=False)

        excel_buffer.seek(0) # Rewind the buffer
        st.download_button(
            "📊 Descargar historial (Excel)",
            excel_buffer.getvalue(),
            "jarrones_historial.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel"
        )

        # --- General Pie Chart (from current session) ---
        st.subheader("📊 Distribución General por Jarrón (de la sesión actual)")
        # Ensure not to try graphing if no data is assigned (excluding the income entry)
        df_current_expenses = df_resultado_actual[df_resultado_actual['Jarrón'] != 'Ingreso Mensual']
        if not df_current_expenses["Monto asignado"].sum() == 0:
            df_total_jarrones = df_current_expenses.groupby("Jarrón")["Monto asignado"].sum()
            fig1, ax1 = plt.subplots(figsize=(8, 8))
            ax1.pie(df_total_jarrones, labels=df_total_jarrones.index, autopct="%1.1f%%", startangle=90, pctdistance=0.85)
            ax1.axis("equal") # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig1)
            plt.close(fig1) # Close the figure to free up memory
        else:
            st.info("No hay montos asignados en esta sesión para el gráfico general.")

        # --- Bar Charts for Subcategories (from current session) ---
        st.subheader("📊 Detalle por Subcategorías de Cada Jarrón (de la sesión actual)")
        for jarron_nombre in df_current_expenses["Jarrón"].unique(): # Iterate over expense jars only
            df_j = df_current_expenses[df_current_expenses["Jarrón"] == jarron_nombre]
            
            # Filter subcategories with amount > 0 to graph only assigned ones
            df_j_filtrado = df_j[df_j["Monto asignado"] > 0] 

            if not df_j_filtrado.empty:
                st.markdown(f"#### 🔍 **{jarron_nombre}**")
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                ax2.bar(df_j_filtrado["Subcategoría"], df_j_filtrado["Monto asignado"], color="skyblue")
                ax2.set_ylabel("Monto ($)")
                ax2.set_xlabel("Subcategorías")
                ax2.set_title(f"Distribución en '{jarron_nombre}'")
                plt.xticks(rotation=45, ha='right') # Rotate labels for better readability
                plt.tight_layout() # Adjust layout so labels are not cut off
                st.pyplot(fig2)
                plt.close(fig2) # Close the figure to free up memory
            else:
                st.info(f"No hay montos asignados en '{jarron_nombre}' para graficar en esta sesión.")

# --- Button to clear all history ---
st.markdown("---")
st.subheader("Gestión del Historial")
if st.button("🗑️ Borrar TODO el Historial", key="clear_history_button"):
    archivo_historial = "historial_desglose_jarrones.csv"
    if os.path.exists(archivo_historial):
        try:
            os.remove(archivo_historial)
            st.success("✅ ¡Historial borrado completamente! La aplicación se reiniciará para reflejar los cambios.")
            
            # Optionally clear session state to reset the app completely
            for key in st.session_state.keys():
                del st.session_state[key]
            
            st.rerun() # Rerun the app to show a clean state
        except Exception as e:
            st.error(f"❌ Error al borrar el historial: {e}")
    else:
        st.info("No hay historial para borrar. El archivo 'historial_desglose_jarrones.csv' no existe.")
