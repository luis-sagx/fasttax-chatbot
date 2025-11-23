# actions.py
# FastTax Custom Actions (versión corregida para SRI 2025)
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

# ==================== TABLAS Y CONSTANTES 2025 ====================

# Tabla progresiva de Impuesto a la Renta 2025 (Personas Naturales)
TABLA_IMPUESTO_2025 = [
    {"base": 0, "hasta": 12081, "impuesto_base": 0.0, "porcentaje": 0.0},
    {"base": 12081, "hasta": 15387, "impuesto_base": 0.0, "porcentaje": 5.0},
    {"base": 15387, "hasta": 19978, "impuesto_base": 165.0, "porcentaje": 10.0},
    {"base": 19978, "hasta": 26422, "impuesto_base": 624.0, "porcentaje": 12.0},
    {"base": 26422, "hasta": 34770, "impuesto_base": 1398.0, "porcentaje": 15.0},
    {"base": 34770, "hasta": 46089, "impuesto_base": 2650.0, "porcentaje": 20.0},
    {"base": 46089, "hasta": 61359, "impuesto_base": 4914.0, "porcentaje": 25.0},
    {"base": 61359, "hasta": 81817, "impuesto_base": 8731.0, "porcentaje": 30.0},
    {"base": 81817, "hasta": 108810, "impuesto_base": 14869.0, "porcentaje": 35.0},
    {"base": 108810, "hasta": float('inf'), "impuesto_base": 24316.0, "porcentaje": 37.0},
]

# Valor Canasta Familiar Básica 2025 (ENERO 2025) - confirmado para cálculos oficiales
CFB_2025 = 798.31

# Valor Canasta Familiar Básica 2025 (septiembre 2025)
# CFB_2025 = 819.77

# Número de canastas básicas por cargas familiares (SRI 2025)
CANASTAS_POR_CARGAS = {
    0: 7,
    1: 9,
    2: 11,
    3: 14,
    4: 17,
    5: 20  # 5 o más → usar 20
}

# Porcentaje de rebaja por gastos personales (2025)
PORCENTAJE_REBAJA = 0.18


# ==================== FUNCIONES DE CÁLCULO ====================

def calcular_impuesto_tabla_progresiva(base_imponible: float) -> float:
    """
    Calcula el impuesto causado según la tabla progresiva del SRI 2025.
    base_imponible: número >= 0
    Devuelve impuesto redondeado a 2 decimales (float).
    """
    if base_imponible <= 0:
        return 0.0
    for tramo in TABLA_IMPUESTO_2025:
        if base_imponible <= tramo["hasta"]:
            exceso = max(0.0, base_imponible - tramo["base"])
            impuesto = tramo["impuesto_base"] + (exceso * tramo["porcentaje"] / 100.0)
            return round(max(0.0, impuesto), 2)
    return 0.0


def calcular_limite_gastos_personales(cargas_familiares: int) -> float:
    """
    Límite de gastos personales = CFB_2025 * num_canastas según cargas.
    Si cargas_familiares >= 5, se usa la entrada 5 (20 canastas).
    """
    try:
        cargas = int(cargas_familiares)
    except (ValueError, TypeError):
        cargas = 0
    if cargas >= 5:
        cargas = 5
    num_canastas = CANASTAS_POR_CARGAS.get(cargas, CANASTAS_POR_CARGAS[0])
    limite = round(CFB_2025 * num_canastas, 2)
    return limite


def calcular_rebaja_gastos_personales(gastos_declarados: float, cargas_familiares: int) -> float:
    """
    Rebaja = 18% * menor(gastos_declarados, limite_por_cargas)
    (Según normativa 2025: rebaja del 18% sobre el menor valor).
    """
    try:
        gastos = float(gastos_declarados)
    except (ValueError, TypeError):
        gastos = 0.0
    limite = calcular_limite_gastos_personales(cargas_familiares)
    base_rebaja = min(max(0.0, gastos), limite)
    rebaja = round(base_rebaja * PORCENTAJE_REBAJA, 2)
    return rebaja


# ==================== ACCIÓN PRINCIPAL: CALCULAR IMPUESTO ====================

class ActionCalcularImpuestoRenta(Action):
    """
    Acción que calcula el Impuesto a la Renta según normativa SRI 2025.
    Implementa:
      - base imponible = ingresos - aporte_iess
      - impuesto causado = función tabla progresiva
      - rebaja por gastos personales = 18% del menor entre gastos y límite por cargas
      - impuesto después de rebaja = max(0, impuesto causado - rebaja)
      - impuesto neto = impuesto después de rebaja - retenciones
    """

    def name(self) -> Text:
        return "action_calcular_impuesto_renta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Recuperar slots
        ingresos = tracker.get_slot("ingresos_anuales")
        gastos = tracker.get_slot("gastos_personales")
        cargas = tracker.get_slot("cargas_familiares")
        aporte_iess = tracker.get_slot("aporte_iess")
        retenciones = tracker.get_slot("retenciones")

        # Verificar presencia
        if None in [ingresos, gastos, cargas, aporte_iess, retenciones]:
            dispatcher.utter_message(
                text="Necesito todos los datos (ingresos, gastos, cargas, aporte IESS y retenciones) para calcular tu impuesto."
            )
            return []

        # Convertir y sanitizar
        try:
            ingresos = float(ingresos)
            gastos = float(gastos)
            cargas = int(cargas)
            aporte_iess = float(aporte_iess)
            retenciones = float(retenciones)
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Hubo un error con los datos. Asegúrate de ingresar números válidos.")
            return []

        # Paso 1: Base imponible (rebaja no se resta de ingresos, es descuento del impuesto)
        base_imponible = round(max(0.0, ingresos - aporte_iess), 2)

        # Paso 2: Impuesto causado por la tabla progresiva
        impuesto_causado = calcular_impuesto_tabla_progresiva(base_imponible)

        # Paso 3: Rebaja por gastos personales (18% * menor(gastos, límite_por_cargas))
        rebaja = calcular_rebaja_gastos_personales(gastos, cargas)

        # Paso 4: Impuesto después de la rebaja
        impuesto_despues_rebaja = round(max(0.0, impuesto_causado - rebaja), 2)

        # Paso 5: Restar retenciones (saldo neto)
        impuesto_neto = round(impuesto_despues_rebaja - retenciones, 2)

        # Resultado (pago o saldo a favor)
        if impuesto_neto > 0:
            resultado_texto = f"IMPUESTO A PAGAR: ${impuesto_neto:,.2f}"
        elif impuesto_neto < 0:
            resultado_texto = f"SALDO A FAVOR (devolución): ${abs(impuesto_neto):,.2f}"
        else:
            resultado_texto = "NO TIENES IMPUESTO A PAGAR NI SALDO A FAVOR."

        # Límite de gastos según cargas
        limite_gastos = calcular_limite_gastos_personales(cargas)

        # Mensaje detallado
        mensaje = (
            f"CALCULO DE IMPUESTO A LA RENTA 2025\n"
            f"{'='*60}\n\n"
            f"DATOS INGRESADOS:\n"
            f"- Ingresos anuales: ${ingresos:,.2f}\n"
            f"- Gastos personales (declarados): ${gastos:,.2f}\n"
            f"- Cargas familiares: {cargas}\n"
            f"- Aporte IESS (anual): ${aporte_iess:,.2f}\n"
            f"- Retenciones en la fuente: ${retenciones:,.2f}\n\n"
            f"CALCULO PASO A PASO:\n\n"
            f"1) BASE IMPONIBLE (Ingresos - Aporte IESS):\n"
            f"   ${ingresos:,.2f} - ${aporte_iess:,.2f} = ${base_imponible:,.2f}\n\n"
            f"2) IMPUESTO CAUSADO (tabla progresiva SRI 2025):\n"
            f"   ${impuesto_causado:,.2f}\n\n"
            f"3) REBAJA POR GASTOS PERSONALES (18% sobre el menor valor):\n"
            f"   Límite para {cargas} cargas: ${limite_gastos:,.2f}\n"
            f"   Gastos considerados: ${min(gastos, limite_gastos):,.2f}\n"
            f"   Rebaja (18%): ${rebaja:,.2f}\n\n"
            f"4) IMPUESTO DESPUES DE REBAJA:\n"
            f"   ${impuesto_causado:,.2f} - ${rebaja:,.2f} = ${impuesto_despues_rebaja:,.2f}\n\n"
            f"5) RESTAR RETENCIONES EN LA FUENTE:\n"
            f"   ${impuesto_despues_rebaja:,.2f} - ${retenciones:,.2f} = ${impuesto_neto:,.2f}\n\n"
            f"{'='*60}\n"
            f"{resultado_texto}\n"
            f"{'='*60}\n\n"
            f"Nota: Este cálculo usa la regla SRI 2025 (rebaja 18% sobre gastos personales limitada por canastas)."
        )

        dispatcher.utter_message(text=mensaje)
        return []


# ==================== VALIDACIÓN DEL FORMULARIO ====================

class ValidateCalculoImpuestoForm(FormValidationAction):
    """
    Valida los datos ingresados en el formulario de cálculo de impuesto.
    """

    def name(self) -> Text:
        return "validate_calculo_impuesto_form"

    def validate_ingresos_anuales(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            ingresos = float(slot_value)
            if ingresos < 0:
                dispatcher.utter_message(text="Los ingresos no pueden ser negativos. Intenta de nuevo.")
                return {"ingresos_anuales": None}
            if ingresos > 100000000:  # límite razonable alto
                dispatcher.utter_message(text="El monto parece excesivamente alto. Verifica el valor.")
                return {"ingresos_anuales": None}
            return {"ingresos_anuales": ingresos}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un número válido. Ejemplo: 25000")
            return {"ingresos_anuales": None}

    def validate_gastos_personales(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            gastos = float(slot_value)
            if gastos < 0:
                dispatcher.utter_message(text="Los gastos no pueden ser negativos. Intenta de nuevo.")
                return {"gastos_personales": None}
            return {"gastos_personales": gastos}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un número válido. Ejemplo: 5000")
            return {"gastos_personales": None}

    def validate_cargas_familiares(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            cargas = int(slot_value)
            if cargas < 0 or cargas > 50:
                dispatcher.utter_message(text="El número de cargas debe estar entre 0 y 50. Intenta de nuevo.")
                return {"cargas_familiares": None}
            return {"cargas_familiares": cargas}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un número entero. Ejemplo: 2")
            return {"cargas_familiares": None}

    def validate_aporte_iess(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            iess = float(slot_value)
            if iess < 0:
                dispatcher.utter_message(text="El aporte IESS no puede ser negativo. Intenta de nuevo.")
                return {"aporte_iess": None}
            return {"aporte_iess": iess}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un número válido. Ejemplo: 2000")
            return {"aporte_iess": None}

    def validate_retenciones(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            retenciones = float(slot_value)
            if retenciones < 0:
                dispatcher.utter_message(text="Las retenciones no pueden ser negativas. Intenta de nuevo.")
                return {"retenciones": None}
            return {"retenciones": retenciones}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un número válido. Ejemplo: 1500")
            return {"retenciones": None}


# ==================== ACCIONES INFORMATIVAS ====================

class ActionExplicarCalculoEjemplo(Action):
    def name(self) -> Text:
        return "action_explicar_calculo_ejemplo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        mensaje = (
            "Cálculo Detallado del Impuesto a la Renta (SRI 2025)\n\n"
            "Resumen:\n"
            "- Base imponible = Ingresos - Aporte IESS\n"
            "- Impuesto causado = según tabla progresiva 2025\n"
            "- Rebaja por gastos personales = 18% del menor entre gastos y límite por cargas\n"
            "- Impuesto neto = impuesto causado - rebaja - retenciones\n\n"
            "Puedo explicarte cualquier paso con más detalle si lo deseas."
        )

        dispatcher.utter_message(text=mensaje)
        return []


class ActionInformacionNormativaSRI(Action):
    def name(self) -> Text:
        return "action_informacion_normativa_sri"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        mensaje = (
            "Información Normativa del SRI (2025)\n\n"
            "Fuentes utilizadas:\n"
            "- Boletines del SRI (tablas 2025)\n"
            "- Formulario Proyección de Gastos Personales 2025 (CFB enero 2025 = USD 798.31)\n"
            "- Ley de Régimen Tributario Interno y resoluciones relacionadas\n\n"
            "Si deseas, puedo adjuntar o mostrar enlaces a las fuentes oficiales."
        )

        dispatcher.utter_message(text=mensaje)
        return []


class ActionCompararCasos(Action):
    def name(self) -> Text:
        return "action_comparar_casos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        mensaje = (
            "Comparación de Casos Tributarios\n\n"
            "Puedo mostrar diferencias entre:\n"
            "- Relación de dependencia vs Servicios profesionales\n"
            "- Diferentes tramos de ingresos y su impacto\n"
            "- Escenarios con/ sin gastos personales y su efecto en la rebaja\n"
            "- Efecto de retenciones en el resultado final\n\n"
            "Pídeme cualquier escenario y te lo calculo."
        )

        dispatcher.utter_message(text=mensaje)
        return []
