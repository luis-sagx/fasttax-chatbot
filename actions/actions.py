# FastTax Custom Actions
# Acciones personalizadas para el chatbot de consultas sobre Impuesto a la Renta

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet


# ==================== TABLAS Y CONSTANTES 2025 ====================

# Tabla progresiva de Impuesto a la Renta 2025 (Personas Naturales)
TABLA_IMPUESTO_2025 = [
    {"base": 0, "hasta": 12081, "impuesto_base": 0, "porcentaje": 0},
    {"base": 12081, "hasta": 15387, "impuesto_base": 0, "porcentaje": 5},
    {"base": 15387, "hasta": 19978, "impuesto_base": 165, "porcentaje": 10},
    {"base": 19978, "hasta": 26422, "impuesto_base": 624, "porcentaje": 12},
    {"base": 26422, "hasta": 34770, "impuesto_base": 1398, "porcentaje": 15},
    {"base": 34770, "hasta": 46089, "impuesto_base": 2650, "porcentaje": 20},
    {"base": 46089, "hasta": 61359, "impuesto_base": 4914, "porcentaje": 25},
    {"base": 61359, "hasta": 81817, "impuesto_base": 8731, "porcentaje": 30},
    {"base": 81817, "hasta": 108810, "impuesto_base": 14869, "porcentaje": 35},
    {"base": 108810, "hasta": float('inf'), "impuesto_base": 24316, "porcentaje": 37},
]

# Valor Canasta Familiar Básica 2025 (septiembre 2025)
CFB_2025 = 819.77

# Número de canastas básicas por cargas familiares
CANASTAS_POR_CARGAS = {
    0: 7,
    1: 9,
    2: 11,
    3: 14,
    4: 17,
    5: 20,  # 5 o más
    100: 100  # Enfermedad catastrófica
}

# Porcentaje de rebaja por gastos personales
PORCENTAJE_REBAJA = 0.18


# ==================== FUNCIONES DE CÁLCULO ====================

def calcular_impuesto_tabla_progresiva(base_imponible: float) -> float:
    """
    Calcula el impuesto causado según la tabla progresiva del SRI 2025.
    
    Args:
        base_imponible: Base imponible calculada (ingresos - deducciones)
    
    Returns:
        Impuesto causado según tabla progresiva
    """
    for tramo in TABLA_IMPUESTO_2025:
        if base_imponible <= tramo["hasta"]:
            exceso = base_imponible - tramo["base"]
            impuesto = tramo["impuesto_base"] + (exceso * tramo["porcentaje"] / 100)
            return max(0, impuesto)
    return 0


def calcular_limite_gastos_personales(cargas_familiares: int) -> float:
    """
    Calcula el límite máximo de gastos personales deducibles según cargas familiares.
    
    Args:
        cargas_familiares: Número de cargas familiares (0 a 5+)
    
    Returns:
        Límite máximo de gastos personales en USD
    """
    # Ajustar si es mayor a 5
    if cargas_familiares >= 5:
        cargas_familiares = 5
    
    num_canastas = CANASTAS_POR_CARGAS.get(cargas_familiares, 7)
    limite = CFB_2025 * num_canastas
    return limite


def calcular_rebaja_gastos_personales(gastos_declarados: float, cargas_familiares: int) -> float:
    """
    Calcula la rebaja por gastos personales (18% del menor entre gastos declarados y límite).
    
    Args:
        gastos_declarados: Gastos personales declarados por el contribuyente
        cargas_familiares: Número de cargas familiares
    
    Returns:
        Rebaja aplicable en USD
    """
    limite = calcular_limite_gastos_personales(cargas_familiares)
    base_rebaja = min(gastos_declarados, limite)
    rebaja = base_rebaja * PORCENTAJE_REBAJA
    return rebaja


# ==================== ACCIÓN PRINCIPAL: CALCULAR IMPUESTO ====================

class ActionCalcularImpuestoRenta(Action):
    """
    Acción que calcula el Impuesto a la Renta según normativa SRI 2025.
    """

    def name(self) -> Text:
        return "action_calcular_impuesto_renta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtener valores de los slots
        ingresos = tracker.get_slot("ingresos_anuales")
        gastos = tracker.get_slot("gastos_personales")
        cargas = tracker.get_slot("cargas_familiares")
        iess = tracker.get_slot("aporte_iess")
        retenciones = tracker.get_slot("retenciones")
        
        # Validar que todos los datos estén presentes
        if None in [ingresos, gastos, cargas, iess, retenciones]:
            dispatcher.utter_message(
                text="Necesito todos los datos para calcular tu impuesto. Por favor completa la informacion."
            )
            return []
        
        # Convertir a números
        try:
            ingresos = float(ingresos)
            gastos = float(gastos)
            cargas = int(cargas)
            iess = float(iess)
            retenciones = float(retenciones)
        except (ValueError, TypeError):
            dispatcher.utter_message(
                text="Hubo un error con los datos ingresados. Por favor verifica que sean numeros validos."
            )
            return []
        
        # PASO 1: Calcular base imponible
        base_imponible = ingresos - iess
        
        # PASO 2: Calcular impuesto causado según tabla progresiva
        impuesto_causado = calcular_impuesto_tabla_progresiva(base_imponible)
        
        # PASO 3: Calcular rebaja por gastos personales
        rebaja_gastos = calcular_rebaja_gastos_personales(gastos, cargas)
        
        # PASO 4: Calcular impuesto después de rebaja
        impuesto_despues_rebaja = max(0, impuesto_causado - rebaja_gastos)
        
        # PASO 5: Restar retenciones en la fuente
        impuesto_neto = impuesto_despues_rebaja - retenciones
        
        # Determinar si paga o tiene saldo a favor
        if impuesto_neto > 0:
            resultado_texto = f"IMPUESTO A PAGAR: ${impuesto_neto:.2f}"
        elif impuesto_neto < 0:
            resultado_texto = f"SALDO A FAVOR (devolucion): ${abs(impuesto_neto):.2f}"
        else:
            resultado_texto = "NO TIENES IMPUESTO A PAGAR NI SALDO A FAVOR"
        
        # Calcular límite de gastos personales
        limite_gastos = calcular_limite_gastos_personales(cargas)
        
        # Construir mensaje detallado
        mensaje = (
            f"CALCULO DE IMPUESTO A LA RENTA 2025\n"
            f"{'='*50}\n\n"
            f"DATOS INGRESADOS:\n"
            f"- Ingresos anuales: ${ingresos:,.2f}\n"
            f"- Gastos personales: ${gastos:,.2f}\n"
            f"- Cargas familiares: {cargas}\n"
            f"- Aporte IESS: ${iess:,.2f}\n"
            f"- Retenciones: ${retenciones:,.2f}\n\n"
            f"CALCULO PASO A PASO:\n\n"
            f"1. BASE IMPONIBLE:\n"
            f"   ${ingresos:,.2f} - ${iess:,.2f} = ${base_imponible:,.2f}\n\n"
            f"2. IMPUESTO CAUSADO (tabla progresiva SRI 2025):\n"
            f"   ${impuesto_causado:,.2f}\n\n"
            f"3. REBAJA POR GASTOS PERSONALES:\n"
            f"   Limite para {cargas} cargas: ${limite_gastos:,.2f}\n"
            f"   Gastos considerados: ${min(gastos, limite_gastos):,.2f}\n"
            f"   Rebaja (18%): ${rebaja_gastos:,.2f}\n\n"
            f"4. IMPUESTO DESPUES DE REBAJA:\n"
            f"   ${impuesto_causado:,.2f} - ${rebaja_gastos:,.2f} = ${impuesto_despues_rebaja:,.2f}\n\n"
            f"5. RESTAR RETENCIONES EN LA FUENTE:\n"
            f"   ${impuesto_despues_rebaja:,.2f} - ${retenciones:,.2f} = ${impuesto_neto:,.2f}\n\n"
            f"{'='*50}\n"
            f"{resultado_texto}\n"
            f"{'='*50}\n\n"
            
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
        """Valida que los ingresos sean un número positivo."""
        try:
            ingresos = float(slot_value)
            if ingresos < 0:
                dispatcher.utter_message(text="Los ingresos no pueden ser negativos. Intenta de nuevo.")
                return {"ingresos_anuales": None}
            if ingresos > 10000000:  # Validación de cordura
                dispatcher.utter_message(text="El monto parece muy alto. Verifica el valor ingresado.")
                return {"ingresos_anuales": None}
            return {"ingresos_anuales": ingresos}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un numero valido. Ejemplo: 25000")
            return {"ingresos_anuales": None}

    def validate_gastos_personales(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida que los gastos sean un número positivo."""
        try:
            gastos = float(slot_value)
            if gastos < 0:
                dispatcher.utter_message(text="Los gastos no pueden ser negativos. Intenta de nuevo.")
                return {"gastos_personales": None}
            return {"gastos_personales": gastos}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un numero valido. Ejemplo: 5000")
            return {"gastos_personales": None}

    def validate_cargas_familiares(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida que las cargas familiares sean un número entero entre 0 y 10."""
        try:
            cargas = int(slot_value)
            if cargas < 0 or cargas > 10:
                dispatcher.utter_message(text="El numero de cargas debe estar entre 0 y 10. Intenta de nuevo.")
                return {"cargas_familiares": None}
            return {"cargas_familiares": cargas}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un numero entero. Ejemplo: 2")
            return {"cargas_familiares": None}

    def validate_aporte_iess(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida que el aporte IESS sea un número positivo."""
        try:
            iess = float(slot_value)
            if iess < 0:
                dispatcher.utter_message(text="El aporte IESS no puede ser negativo. Intenta de nuevo.")
                return {"aporte_iess": None}
            return {"aporte_iess": iess}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un numero valido. Ejemplo: 2000")
            return {"aporte_iess": None}

    def validate_retenciones(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida que las retenciones sean un número positivo."""
        try:
            retenciones = float(slot_value)
            if retenciones < 0:
                dispatcher.utter_message(text="Las retenciones no pueden ser negativas. Intenta de nuevo.")
                return {"retenciones": None}
            return {"retenciones": retenciones}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Por favor ingresa un numero valido. Ejemplo: 1500")
            return {"retenciones": None}


# ==================== ACCIONES INFORMATIVAS EXISTENTES ====================

class ActionExplicarCalculoEjemplo(Action):
    """
    Accion para proporcionar explicaciones sobre cálculos tributarios
    con ejemplos según normativa del SRI
    """

    def name(self) -> Text:
        return "action_explicar_calculo_ejemplo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mensaje = ("Cálculo Detallado del Impuesto a la Renta\n\n"
                  "Puedo explicarte:\n"
                  "- Cómo aplicar la tabla progresiva del SRI\n"
                  "- Cómo calcular la base imponible\n"
                  "- Cómo determinar la rebaja por gastos personales\n"
                  "- Cómo restar retenciones y anticipos\n\n"
                  "¿Sobre qué parte del cálculo necesitas más detalles?")
        
        dispatcher.utter_message(text=mensaje)
        return []


class ActionInformacionNormativaSRI(Action):
    """
    Acción para proporcionar información actualizada sobre normativa del SRI
    """

    def name(self) -> Text:
        return "action_informacion_normativa_sri"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mensaje = ("Información Normativa del SRI\n\n"
                  "Te puedo ayudar con:\n\n"
                  "Leyes y Reglamentos:\n"
                  "- LORTI - Ley Orgánica de Régimen Tributario Interno\n"
                  "- Reglamento para aplicación de la LORTI\n"
                  "- Resoluciones del SRI vigentes\n\n"
                  "Temas Específicos:\n"
                  "- Gastos personales deducibles\n"
                  "- Tabla de impuesto a la renta\n"
                  "- Retenciones en la fuente\n"
                  "- Plazos de declaración\n"
                  "- Formularios oficiales\n\n"
                  "¿Qué tema específico te interesa conocer?")
        
        dispatcher.utter_message(text=mensaje)
        return []


class ActionCompararCasos(Action):
    """
    Acción que compara diferentes casos tributarios
    """

    def name(self) -> Text:
        return "action_comparar_casos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mensaje = ("Comparación de Casos Tributarios\n\n"
                  "Puedo ayudarte a entender diferencias entre:\n\n"
                  "- Relación de dependencia vs Servicios profesionales\n"
                  "- Diferentes tramos de ingresos\n"
                  "- Con gastos personales vs Sin gastos personales\n"
                  "- Diferentes tipos de retenciones\n\n"
                  "Esto te ayudará a comprender mejor cómo la normativa "
                  "se aplica a situaciones específicas.")
        
        dispatcher.utter_message(text=mensaje)
        return []


