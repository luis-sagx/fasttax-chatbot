# FastTax Custom Actions
# Acciones personalizadas para el chatbot de consultas sobre Impuesto a la Renta

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


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


