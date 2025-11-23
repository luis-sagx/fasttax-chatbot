# 🤖 Documentación del Chatbot FastTax

## 📌 Resumen Ejecutivo

FastTax es un **chatbot educativo especializado** en normativa tributaria ecuatoriana del SRI. Su función principal es **responder preguntas** sobre el Impuesto a la Renta, gastos personales deducibles, procesos de declaración y obligaciones fiscales en Ecuador.

---

## 🎯 Objetivo del Proyecto

Crear un asistente virtual conversacional que ayude a los contribuyentes ecuatorianos a:

- Comprender la normativa del Impuesto a la Renta según el SRI
- Conocer las categorías de gastos personales deducibles
- Entender el proceso de cálculo tributario paso a paso
- Informarse sobre plazos y obligaciones fiscales
- Resolver dudas sobre el Formulario 102 y retenciones
- Consultar la tabla progresiva de impuestos

---

## 📚 Componentes Principales

### 1. **domain.yml** - Dominio del Chatbot

#### Intents Implementados (18 intents)

| Intent                         | Descripción            | Ejemplos                          |
| ------------------------------ | ---------------------- | --------------------------------- |
| `greet`                        | Saludos iniciales      | "hola", "buenos días"             |
| `goodbye`                      | Despedidas             | "adiós", "hasta luego"            |
| `affirm`                       | Confirmaciones         | "sí", "correcto"                  |
| `deny`                         | Negaciones             | "no", "negativo"                  |
| `bot_challenge`                | Identificación del bot | "eres un bot?"                    |
| `ask_about_fasttax`            | Info sobre FastTax     | "qué es FastTax?"                 |
| `ask_gastos_personales`        | Gastos deducibles      | "qué son gastos personales?"      |
| `ask_categorias_gastos`        | Categorías del SRI     | "cuáles son las categorías?"      |
| `ask_calculo_impuesto`         | Proceso de cálculo     | "cómo se calcula el impuesto?"    |
| `ask_deducibles`               | Qué es deducible       | "qué puedo deducir?"              |
| `ask_proceso_declaracion`      | Pasos para declarar    | "cómo es el proceso?"             |
| `ask_formulario_sri`           | Formulario 102         | "qué formulario uso?"             |
| `ask_retencion`                | Retenciones            | "qué son las retenciones?"        |
| `ask_base_imponible`           | Base de cálculo        | "qué es la base imponible?"       |
| `ask_plazos`                   | Fechas límite          | "cuándo debo declarar?"           |
| `ask_ayuda`                    | Menú de ayuda          | "ayuda", "qué puedes hacer?"      |
| `request_example`              | Ejemplos prácticos     | "dame un ejemplo"                 |
| `ask_tabla_impuesto`           | Tabla progresiva       | "cuál es la tabla del SRI?"       |
| `ask_facturacion_electronica`  | Comprobantes           | "qué es facturación electrónica?" |
| `ask_obligaciones_tributarias` | Deberes fiscales       | "cuáles son mis obligaciones?"    |

#### Responses Principales (18 respuestas)

Todas las respuestas están basadas en normativa oficial del SRI y proporcionan información educativa clara y precisa.

**Ejemplos de respuestas:**

**`utter_gastos_personales`** - Explica:

- Límite máximo de deducción (50% ingresos o 7 fracciones básicas)
- Requisitos de los comprobantes
- Quiénes pueden ser beneficiarios

**`utter_categorias_gastos`** - Detalla las 6 categorías:

- Vivienda (0.325 FB)
- Alimentación (0.325 FB)
- Salud (1.3 FB)
- Educación (0.325 FB)
- Vestimenta (0.325 FB)
- Turismo (0.325 FB)

**`utter_tabla_impuesto`** - Muestra tabla progresiva 2025:

- 10 tramos de ingresos
- Porcentajes del 0% al 37%
- Instrucciones de cómo aplicarla

---

### 2. **data/nlu.yml** - Entrenamiento del Lenguaje Natural

**Características:**

- **Idioma:** Español ecuatoriano
- **Total de ejemplos:** ~200 frases
- **Cobertura:** Múltiples formas de preguntar lo mismo

**Ejemplos por intent:**

```yaml
ask_gastos_personales:
  - qué son gastos personales?
  - gastos deducibles
  - puedo deducir gastos?
  - cuánto puedo deducir?
  - límite de gastos personales
  ...

ask_calculo_impuesto:
  - cómo se calcula el impuesto?
  - fórmula del impuesto
  - explícame el cálculo del impuesto
  - cómo saber cuánto debo pagar?
  ...
```

---

### 3. **data/stories.yml** - Flujos Conversacionales

**16 historias** que modelan conversaciones típicas:

**Historia 1: Consulta sobre gastos personales**

```yaml
- intent: ask_gastos_personales
- action: utter_gastos_personales
- intent: affirm
- action: utter_categorias_gastos
```

**Historia 2: Cálculo con ejemplo**

```yaml
- intent: ask_calculo_impuesto
- action: utter_calculo_impuesto
- intent: request_example
- action: utter_example
```

**Historia 3: Flujo completo de información**

- Saludo → Proceso → Gastos → Categorías → Cálculo

---

### 4. **data/rules.yml** - Reglas de Respuesta

**4 reglas básicas** para respuestas directas:

```yaml
- Despedida automática
- Identificación del bot
- Información sobre FastTax
- Ayuda general
```

Las reglas se activan en cualquier momento sin depender del contexto.

---

### 5. **actions/actions.py** - Acciones Personalizadas

**3 acciones educativas** (esqueleto funcional):

#### `ActionExplicarCalculoEjemplo`

- Proporciona explicaciones detalladas paso a paso
- Muestra cómo aplicar la tabla del SRI
- Explica cada componente del cálculo

#### `ActionInformacionNormativaSRI`

- Información sobre LORTI y reglamentos
- Referencias a resoluciones del SRI
- Temas específicos de normativa

#### `ActionCompararCasos`

- Compara diferentes situaciones tributarias
- Muestra diferencias entre escenarios
- Ayuda a entender aplicación práctica

---

## 🧠 Conocimiento Integrado

### Marco Legal y Normativo del SRI

#### 1. **Gastos Personales Deducibles**

**Límite Legal:**

```
Límite = Menor entre:
  • 50% de ingresos gravados
  • 7 fracciones básicas ($12,816 para 2025)
```

**Límites por Categoría:**

- Vivienda: 0.325 FB ($3,810)
- Alimentación: 0.325 FB ($3,810)
- Salud: 1.3 FB ($15,239)
- Educación: 0.325 FB ($3,810)
- Vestimenta: 0.325 FB ($3,810)
- Turismo: 0.325 FB ($3,810)

#### 2. **Cálculo del Impuesto a la Renta**

**Fórmula Paso a Paso:**

```
1. Base Imponible = Ingresos - Gastos Deducibles - Aporte IESS

2. Impuesto Causado = Aplicar tabla progresiva

3. Rebaja = Hasta 20% del impuesto causado

4. Impuesto Neto = Causado - Rebaja - Retenciones - Anticipos
```

#### 3. **Tabla Progresiva 2025**

| Fracción Básica | Exceso hasta | Impuesto FB | % Exceso |
| --------------- | ------------ | ----------- | -------- |
| $0              | $11,722      | $0          | 0%       |
| $11,722         | $14,930      | $0          | 5%       |
| $14,930         | $19,385      | $160        | 10%      |
| $19,385         | $25,638      | $606        | 12%      |
| $25,638         | $33,738      | $1,356      | 15%      |
| $33,738         | $44,721      | $2,571      | 20%      |
| $44,721         | $59,537      | $4,768      | 25%      |
| $59,537         | $79,388      | $8,472      | 30%      |
| $79,388         | $105,580     | $14,427     | 35%      |
| $105,580+       | ∞            | $23,594     | 37%      |

#### 4. **Plazos de Declaración**

**Mes:** Marzo del año siguiente
**Fechas según noveno dígito:**

- 1 → 10 marzo
- 2 → 12 marzo
- 3 → 14 marzo
- ...
- 0 → 28 marzo

**Multas por incumplimiento:** $30 a $150 + intereses

---

## 📊 Ejemplo Práctico Completo

**Caso: María - Empleada en relación de dependencia**

### Datos:

- Ingresos anuales: **$24,000**
- Aporte IESS (9.45%): **$2,268**
- Gastos personales válidos: **$8,000**

### Cálculo:

**1. Base Imponible:**

```
$24,000 - $8,000 - $2,268 = $13,732
```

**2. Impuesto Causado:**

```
Fracción básica hasta $11,722: $0
Exceso: $13,732 - $11,722 = $2,010
Impuesto sobre exceso (5%): $2,010 × 5% = $101
Total Impuesto Causado: $101
```

**3. Rebaja por Gastos Personales (20%):**

```
$101 × 20% = $20
```

**4. Retenciones durante el año:**

```
$95
```

**5. Impuesto Neto:**

```
$101 - $20 - $95 = -$14
```

### ✅ Resultado:

**Saldo a favor de $14** (María puede solicitar devolución)

---

## 🚀 Cómo Usar el Chatbot

### 1. Entrenar el Modelo

```bash
conda activate rasaenv
rasa train
```

### 2. Probar en Consola

```bash
rasa shell
```

### 3. Ejecutar con Acciones Personalizadas

**Terminal 1:**

```bash
rasa run actions
```

**Terminal 2:**

```bash
rasa shell
```

---

## 💬 Ejemplos de Conversación

### Conversación 1: Información General

```
👤 Usuario: Hola
🤖 FastTax: ¡Hola! Soy FastTax, tu asistente de consultas sobre
            el Impuesto a la Renta en Ecuador. Puedo ayudarte
            a entender la normativa tributaria del SRI.
            ¿Qué información necesitas?

👤 Usuario: Qué es FastTax?
🤖 FastTax: FastTax es un asistente virtual educativo que te
            ayuda a comprender la normativa del Impuesto a la
            Renta en Ecuador. Puedo ayudarte con información
            sobre gastos personales, cálculos tributarios,
            formularios...
```

### Conversación 2: Consulta Técnica

```
👤 Usuario: Cómo se calcula el impuesto?
🤖 FastTax: [Explica los 4 pasos del cálculo]
            ¿Quieres ver un ejemplo práctico?

👤 Usuario: Sí, dame un ejemplo
🤖 FastTax: [Muestra ejemplo completo con María]
```

### Conversación 3: Gastos Personales

```
👤 Usuario: Cuáles son las categorías de gastos?
🤖 FastTax: [Lista las 6 categorías con límites]

👤 Usuario: Cuánto puedo deducir en salud?
🤖 FastTax: La categoría de SALUD tiene un límite de
            1.3 fracciones básicas, equivalente a $15,239
            aproximadamente para 2025...
```

---

## 📈 Alcance y Limitaciones

### ✅ Lo que SÍ hace el chatbot:

- Explicar conceptos tributarios
- Proporcionar información normativa actualizada
- Mostrar ejemplos de cálculos
- Orientar sobre plazos y requisitos
- Responder preguntas frecuentes
- Explicar el uso del Formulario 102

### ❌ Lo que NO hace el chatbot:

- Procesar archivos XML reales
- Calcular automáticamente impuestos con datos del usuario
- Llenar formularios automáticamente
- Acceder a sistemas del SRI
- Almacenar información personal o fiscal
- Reemplazar asesoría profesional contable

---

## 🛡️ Consideraciones Importantes

### 1. **Carácter Educativo**

El chatbot proporciona información general basada en normativa pública del SRI. No constituye asesoría fiscal personalizada.

### 2. **Actualización de Información**

La normativa tributaria puede cambiar. Se recomienda verificar información actualizada en www.sri.gob.ec

### 3. **Casos Especiales**

Para situaciones tributarias complejas, se recomienda consultar con un contador o asesor tributario profesional.

### 4. **Responsabilidad**

El contribuyente es responsable de verificar la exactitud de su declaración antes de presentarla al SRI.

---

## 📚 Referencias Normativas

- **SRI Ecuador:** www.sri.gob.ec
- **LORTI:** Ley Orgánica de Régimen Tributario Interno
- **Reglamento LORTI:** Decreto Ejecutivo 374
- **Resoluciones SRI:** Normativa vigente sobre gastos personales
- **Facturación Electrónica:** Resolución NAC-DGERCGC12-00105

---

## 👥 Audiencia Objetivo

- 👨‍💼 **Contribuyentes personas naturales** en Ecuador
- 👩‍🎓 **Estudiantes** de contabilidad y tributación
- 👨‍💻 **Profesionales independientes** con dudas básicas
- 👩‍🏫 **Educadores** que enseñan tributación ecuatoriana
- 🧑‍💼 **Empleados** que deben entender sus retenciones

---

## 🎓 Contexto Académico

**Institución:** ESPE  
**Semestre:** 6to Semestre  
**Materia:** Aplicaciones Basadas en Conocimiento  
**Proyecto:** FastTax - Asistente de Consultas sobre Impuesto a la Renta

**Enfoque del Proyecto:**

- ✅ Sistema basado en conocimiento (normativa SRI)
- ✅ Procesamiento de lenguaje natural (Rasa NLU)
- ✅ Gestión de diálogo conversacional
- ✅ Base de conocimiento estructurada
- ✅ Interfaz en lenguaje natural

---

**Documento generado:** 22 de noviembre de 2025  
**Versión del Chatbot:** 1.0.0 - FastTax (Solo Consultas)  
**Framework:** Rasa 3.1  
**Idioma:** Español (Ecuador)  
**Tipo:** Chatbot Educativo - Q&A sobre Normativa Tributaria

---

_Este chatbot es una herramienta educativa para comprender la normativa del Impuesto a la Renta en Ecuador. Para declaraciones reales, consulte con un profesional contable certificado._
