import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

load_dotenv()
from langchain_community.callbacks.manager import get_openai_callback
import auth_subscription

class MarketingStrategist:
    def __init__(self, business_context=""):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.llm = None
        self.memory = None
        self.chain = None
        
        # Debug logging
        if self.api_key:
            print(f"✅ API Key found: {self.api_key[:10]}...{self.api_key[-4:]}")
        else:
            print("❌ API Key NOT found in environment variables")
        
        if self.api_key:
            try:
                print("🔄 Initializing ChatOpenAI with gpt-4o-mini...")
                self.llm = ChatOpenAI(
                    model_name="gpt-4o-mini",
                    openai_api_key=self.api_key,
                    temperature=0.7
                )
                print("✅ LLM initialized successfully")
            except Exception as e:
                # Fallback or error handling
                print(f"❌ Error initializing LLM: {e}")
                self.llm = None
        
        
        # Initialize memory
        self.memory = ConversationBufferMemory()
        self.business_context = business_context  # Store for later use
        self.setup_chain(business_context)

    def setup_chain(self, business_context=""):
        # Initialize a default generic chain for general chat
        if not self.llm:
            return

        # Build system message
        system_message = "Eres un asistente experto en marketing digital. Ayuda al usuario con sus dudas sobre marketing y ventas."
        
        if business_context:
            system_message += f"\n\nCONTEXTO DEL NEGOCIO:\n{business_context}\n\nUsa este contexto para dar respuestas personalizadas y específicas para este negocio."
        
        # Use simple PromptTemplate
        from langchain.prompts import PromptTemplate
        
        template = f"""{system_message}

Current conversation:
{{history}}

Human: {{input}}
Assistant:"""
        
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=template
        )
        
        self.chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=False
        )

    def update_context(self, new_context):
        """Updates the business context and refreshes the chain, preserving memory."""
        self.business_context = new_context
        self.setup_chain(new_context)

    def generate_section(self, section_name, business_info):
        """
        Generates a single section of the strategy on-demand.
        
        Args:
            section_name: Name of the section to generate (e.g., "AVATAR", "EMBUDO", "ADS", etc.)
            business_info: Dictionary with business information
        
        Returns:
            Section content as string
        """
        if not self.llm:
            return "Error: No se detectó la API Key de OpenAI."
        
        # Prepare common context
        buyer_persona_text = ""
        if business_info.get('buyer_persona'):
            buyer_persona_text = f"\n- Buyer Persona Base (expandir y profundizar): {business_info.get('buyer_persona')}"
        
        # OPTIMIZATION: Removed business_context from strategy generation for speed
        # business_context_text = ""
        # if self.business_context:
        #     business_context_text = f"\n\nCONTEXTO DEL NEGOCIO (Cerebro):\n{self.business_context}\n\nIMPORTANTE: Usa este contexto para personalizar toda la estrategia según la personalidad, tono de voz y valores del negocio.\n"
        
        base_info = f"""INPUTS DEL CLIENTE:
- Rubro: {business_info.get('rubro')}
- Nombre: {business_info.get('nombre')}
- Tipo: {business_info.get('tipo')}
- Producto Estrella: {business_info.get('producto')}
- Precio: {business_info.get('precio', 'No especificado')}
- Meta: {business_info.get('meta')}
- Presupuesto: {business_info.get('presupuesto')}
- Modalidad de Venta: {business_info.get('modalidad_venta', 'No especificado')}
- Sistema Actual: {business_info.get('sistema_actual', 'No especificado')}
- Plataformas: {business_info.get('plataforma')}{buyer_persona_text}"""
        
        # Define section prompts
        section_prompts = {
            "AVATAR": f"""Eres un Estratega de Marketing Senior especializado en Buyer Personas.
{base_info}

Genera 1 AVATAR DE CLIENTE IDEAL ultra-detallado y específico (NO genérico) siguiendo EXACTAMENTE esta estructura:

AVATAR 1 — "[NOMBRE DESCRIPTIVO EN MAYÚSCULAS]"

**Descripción general**
Párrafo de 2-3 líneas describiendo quién es, su situación actual y qué busca.

**Datos demográficos**
- Edad: [rango específico]
- Género: [género predominante]
- Ubicación: [país/región específica]
- Ingresos: [nivel económico]
- Estado civil: [situación familiar]
- Nivel educativo: [educación]

**Situación actual**
Lista de 3-4 puntos describiendo:
- Su trabajo/ocupación actual
- Sus responsabilidades diarias
- Sus desafíos cotidianos
- Su relación con el producto/servicio

**Dolor principal**
❌ [Descripción del dolor #1 más grande que le quita el sueño]

**Otros dolores**
- [Dolor secundario 1]
- [Dolor secundario 2]
- [Dolor secundario 3]
- [Dolor secundario 4]

**Deseos y metas**
- [Deseo/meta 1]
- [Deseo/meta 2]
- [Deseo/meta 3]
- [Deseo/meta 4]

**Objeciones típicas**
- "[Objeción 1 en primera persona]"
- "[Objeción 2 en primera persona]"
- "[Objeción 3 en primera persona]"
- "[Objeción 4 en primera persona]"

**Disparadores de compra**
- [Disparador 1 - qué lo hace decidirse]
- [Disparador 2]
- [Disparador 3]
- [Disparador 4]
- [Disparador 5]

**Tipo de contenido que consume**
- [Tipo de contenido 1]
- [Tipo de contenido 2]
- [Tipo de contenido 3]
- [Tipo de contenido 4]

**Red social principal**
[Red social principal] ([formato específico que más consume])
Secundaria: [Red social secundaria]

**Tono y palabras que conectan**
[Descripción del tono ideal: emocional/racional, formal/informal, etc.]
Enfoque en [temas clave que resuenan].

Ejemplos de palabras clave:
"[palabra 1]", "[palabra 2]", "[palabra 3]", "[palabra 4]", "[palabra 5]".

**Ejemplo de mensaje gancho**
✨ "[Mensaje gancho de 1-2 líneas que conecte emocionalmente con el avatar]" ✨

IMPORTANTE: 
- Sé MUY ESPECÍFICO con edad, ubicación, situación
- Usa datos demográficos reales del mercado {business_info.get('rubro')}
- Las objeciones deben estar en primera persona como si el avatar hablara
- El mensaje gancho debe usar el tono y palabras identificadas
- NO menciones otras secciones
- TERMINA tu respuesta después del Avatar""",
            
            "EMBUDO": f"""Eres un Estratega de Marketing Senior.
{base_info}

Genera un EMBUDO DE CONTENIDO SEMANAL (3 niveles) siguiendo EXACTAMENTE esta estructura:

<<<SECTION_START: EMBUDO_TOFU>>>
🎣 TOFU — ATRACCIÓN

**Objetivo:** Llamar la atención desde el dolor real, generar identificación inmediata y conversación.

**Formato:** [Reel/Post/Video] ([duración si aplica])

**Gancho (primeros 3 segundos):**
❌ "[Frase gancho que ataque el dolor directamente]"

**Desarrollo breve:**
- [Punto 1: Mostrar el caos/problema]
- [Punto 2: Frase clave memorable]

**CTA:**
👉 "[Call to action suave que invite a comentar/escribir]"

💡 **Por qué funciona:**
[Explicación breve de la estrategia psicológica]

<<<SECTION_START: EMBUDO_MOFU>>>
🧠 MOFU — EDUCACIÓN

**Objetivo:** Demostrar que la solución es simple, real y ya funciona en negocios como el suyo.

**Formato:** [Carrusel/Historia/Video educativo]

**Gancho (portada):**
✅ "[Transformación o resultado logrado]"

**Estructura del contenido:**
1️⃣ [El problema común]
2️⃣ [Qué pasaba antes]
3️⃣ [Qué cambió con la solución]
4️⃣ [Resultados concretos]
5️⃣ [Mini testimonio o frase de cliente]

**CTA:**
👉 "[Invitación a ver demo o conocer más]"

💡 **Por qué funciona:**
[Explicación de cómo educa y baja objeciones]

<<<SECTION_START: EMBUDO_BOFU>>>
💰 BOFU — CIERRE

**Objetivo:** Acción inmediata con urgencia clara y riesgo percibido bajo.

**Formato:** [Historias encadenadas/Post de venta/Video directo]

**Secuencia:**

**Parte 1 – Dolor:**
"[Consecuencia negativa de no actuar]"

**Parte 2 – Solución:**
"[Cómo el producto/servicio resuelve el problema]"

**Parte 3 – Oferta + urgencia:**
🔥 [Oferta especial/prueba gratis]
💰 [Precio accesible]
⏰ [Urgencia temporal]

**CTA:**
👉 "[Acción directa: link, mensaje, etc.]"

💡 **Por qué funciona:**
✔ [Razón 1: urgencia]
✔ [Razón 2: precio/accesibilidad]
✔ [Razón 3: bajo riesgo]

---

🧠 **Ajuste estratégico clave:**

**TOFU** = emoción y dolor
**MOFU** = prueba y claridad
**BOFU** = decisión rápida

📌 Usar la MISMA frase clave toda la semana para crear recordación + coherencia.

Sé ESPECÍFICO para {business_info.get('rubro')}. NO uses placeholders genéricos.""",
            
            "ADS": f"""Eres un Estratega de Ads especializado en {business_info.get('plataforma')}.
{base_info}

IMPORTANTE - PLATAFORMA(S): {business_info.get('plataforma')}

Genera ESTRATEGIA DE ADS (3 niveles) siguiendo EXACTAMENTE esta estructura:

<<<SECTION_START: ADS_FRIO>>>
❄️ TRÁFICO FRÍO (Descubrimiento)

🎯 **Objetivo**
Reconocimiento + engagement inicial. Que el cliente se identifique con el problema y recuerde la marca.

🎯 **Ángulo principal (Dolor real)**
❌ [Dolor 1]
❌ [Dolor 2]
❌ [Dolor 3]
❌ [Dolor 4]

✍️ **Variaciones de Copy ({business_info.get('plataforma')})**

**Copy 1 – Dolor directo**
❌ "[Frase gancho sobre el dolor]"

[Desarrollo breve]
Descubrí cómo [solución sin complicarte].

**Copy 2 – Tiempo = dinero**
⏳ "[Pregunta sobre pérdida de tiempo/dinero]"

[Beneficio claro]

**Copy 3 – Anti-[competencia/método viejo]**
📉 "[Crítica al método actual]"

[Propuesta de valor]

🎨 **Creativos (muy específicos para {business_info.get('plataforma')})**

**Para Instagram Reels / Facebook Feed:**
Video corto 10–15s:
- Escena 1: [problema/caos]
- Escena 2: [solución/orden]
- Texto en pantalla: "[Frase clave]"

**Para Feed:**
Imagen comparativa:
- Izquierda: "[Método viejo] ❌"
- Derecha: "[Tu solución] ✅"

🎯 **Segmentación (Frío real)**
- Ubicación: [país/región]
- Edad: [rango]
- Intereses: [lista de intereses relevantes]
- Excluir: Visitantes web, leads existentes

💰 **Presupuesto**
50% – ${business_info.get('presupuesto', 0)*0.5} USD

👉 **CTA**
"[CTA suave: 'Conocé', 'Descubrí cómo funciona']"

<<<SECTION_START: ADS_TIBIO>>>
🔥 TRÁFICO TIBIO (Consideración)

🎯 **Objetivo**
Generación de leads / mensajes / visitas calificadas

🎯 **Ángulo (Prueba social + alivio)**
👉 "No sos el único, a otros ya les funcionó"

✍️ **Copy optimizado**
⭐ "[Historia personal o de cliente]"

Hoy [resultado logrado].

👉 Mirá cómo otros [público objetivo] ya [beneficio] con [producto/servicio].

🎨 **Creativos**

**Opciones recomendadas:**
- Video testimonio corto (15–30s)
- Imagen con cita real: "[Testimonio de cliente]"

🎯 **Segmentación**
Personas que:
- Vieron videos (25%–50%)
- Interactuaron con Instagram/Facebook
- Visitaron la web
- Lookalike de leads (si existe)

💰 **Presupuesto**
35% – ${business_info.get('presupuesto', 0)*0.35} USD

👉 **CTA**
"Ver demostración" o "Solicitar demo gratis"

<<<SECTION_START: ADS_CALIENTE>>>
🌋 TRÁFICO CALIENTE (Conversión)

🎯 **Objetivo**
Ventas / Prueba directa YA

🎯 **Ángulo (Urgencia + bajo riesgo)**
⏰ Tiempo limitado
🛡 Sin riesgo (prueba/garantía)

✍️ **Copy de cierre (más fuerte)**
🔥 "[Urgencia: Últimos cupos/Oferta por tiempo limitado]"

[Beneficio principal]

⏰ [Urgencia específica]

🎨 **Creativos**

**Historias (clave):**
- Historia 1: "[Consecuencia de no actuar]"
- Historia 2: "[Cómo funciona la solución]"
- Historia 3: "[Urgencia + CTA directo]"

🎯 **Segmentación**
Personas que:
- Enviaron mensaje
- Visitaron página de precios
- Interactuaron con anuncios tibios

💰 **Presupuesto**
15% – ${business_info.get('presupuesto', 0)*0.15} USD

👉 **CTA**
"Empezar ahora" o "Activar prueba"

---

🧠 **Ajuste estratégico importante**

📌 **Frase eje para TODA la campaña:**
"[Frase memorable que conecte frío → tibio → caliente]"

Eso crea coherencia entre los 3 niveles de tráfico.

Sé MUY ESPECÍFICO para {business_info.get('rubro')} y {business_info.get('plataforma')}. NO uses placeholders genéricos.""",
            
            "WHATSAPP": f"""Eres un Estratega de Ventas.
{base_info}

Genera FLUJO WHATSAPP 7 DÍAS:

<<<SECTION_START: WHATSAPP_DIA1>>>
🔵 DÍA 1: Contacto + Diagnóstico.
Mensaje: Saludo + 2 preguntas clave.

<<<SECTION_START: WHATSAPP_DIA2>>>
🟦 DÍA 2: Valor + Invitación.
Mensaje: Tip útil + invitación suave.

<<<SECTION_START: WHATSAPP_DIA3>>>
🟩 DÍA 3: Prueba Social.
Mensaje: Caso éxito breve + CTA.

<<<SECTION_START: WHATSAPP_DIA4>>>
🟧 DÍA 4: Objeción.
Mensaje: Reencuadre de objeción principal.

<<<SECTION_START: WHATSAPP_DIA5>>>
🟥 DÍA 5: Urgencia.
Mensaje: Cupos/Tiempo limitado.

<<<SECTION_START: WHATSAPP_DIA6>>>
🟪 DÍA 6: Valor Final.
Mensaje: Recurso extra + mini cierre.

<<<SECTION_START: WHATSAPP_DIA7>>>
⬛ DÍA 7: Cierre/Parking.
Mensaje: Última llamada o despedida elegante.

Sé CONCISO. Mensajes listos para copiar y pegar.""",
            
            "OBJECIONES": f"""Eres un Estratega de Ventas.
{base_info}

Responde a 5 OBJECIONES (Pregunta, Reframing, Propuesta, Cierre):

<<<SECTION_START: OBJECION_COSTO>>>
OBJECIÓN: COSTO

<<<SECTION_START: OBJECION_TIEMPO>>>
OBJECIÓN: TIEMPO

<<<SECTION_START: OBJECION_PERSONAL>>>
OBJECIÓN: PERSONAL/SOCIOS

<<<SECTION_START: OBJECION_INTEGRACION>>>
OBJECIÓN: INTEGRACIÓN/CAMBIO

<<<SECTION_START: OBJECION_MIEDO>>>
OBJECIÓN: MIEDO/DESCONFIANZA

Sé CONCISO y PERSUASIVO.
NO agregues comentarios finales como 'Espero que estas respuestas sean útiles'.""",
            
            "ACCIONES_DIARIAS": f"""Eres un Estratega de Productividad.
{base_info}

Genera CHECKLIST DIARIO DE VENTAS:
1. Prospección (Nuevos)
2. Seguimiento (Tibios)
3. Contenido (Historia)
4. Métricas
5. Cierres

Incluye micro-métricas. Sé BREVE y ACCIONABLE.
NO agregues comentarios finales como 'Con esta rutina, Rodrigo podrá...'.""",
            
            "METRICAS": f"""Eres un Analista de Marketing.
{base_info}

Genera MÉTRICAS CLAVE (Definición, Meta, Acción Mejora):

### Costo por Lead

### Tasa de Cierre

### Tasa de Conversión

### Engagement

Sé CONCISO."""
        }
        
        if section_name not in section_prompts:
            return f"Error: Sección '{section_name}' no reconocida."
        
        try:
            from langchain.schema import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content=section_prompts[section_name]),
                HumanMessage(content="Genera el contenido ahora.")
            ]
            
            response = self.llm(messages)
            return response.content
            
        except Exception as e:
            return f"Error generando {section_name}: {str(e)}"


    def generate_strategy_progressive(self, business_info, progress_callback=None, username=None):
        """
        Generates complete marketing strategy with a SINGLE prompt, then parses sections.
        Simulates progressive loading with callbacks for UI updates.
        
        Args:
            business_info: Dictionary with business information
            progress_callback: Function(section_name, section_content, section_number, total_sections)
            username: Optional username to track token usage
        
        Returns:
            Complete strategy text with all sections
        """
        if not self.llm:
            return "Error: No se detectó la API Key de OpenAI. Por favor configura tu .env."
        
        # Prepare common context
        buyer_persona_text = ""
        if business_info.get('buyer_persona'):
            buyer_persona_text = f"\n- Buyer Persona Base (expandir y profundizar): {business_info.get('buyer_persona')}"
        
        base_info = f"""INPUTS DEL CLIENTE:
- Rubro: {business_info.get('rubro')}
- Nombre: {business_info.get('nombre')}
- Tipo: {business_info.get('tipo')}
- Producto Estrella: {business_info.get('producto')}
- Precio: {business_info.get('precio', 'No especificado')}
- Meta: {business_info.get('meta')}
- Presupuesto: {business_info.get('presupuesto')}
- Modalidad de Venta: {business_info.get('modalidad_venta', 'No especificado')}
- Sistema Actual: {business_info.get('sistema_actual', 'No especificado')}
- Plataformas: {business_info.get('plataforma')}{buyer_persona_text}
- Duración de la Estrategia: {business_info.get('duration_days', 30)} días
"""
        
        # SINGLE UNIFIED PROMPT - generates all sections at once
        unified_prompt = f"""Eres un Estratega de Marketing Senior y Experto en Ventas.
{base_info}

Genera una ESTRATEGIA COMPLETA DE MARKETING Y VENTAS siguiendo EXACTAMENTE esta estructura con los delimitadores indicados:


<<<SECTION_START: AVATAR>>>
👤 AVATAR DE CLIENTE IDEAL

Genera 1 AVATAR ultra-detallado siguiendo esta estructura:

AVATAR 1 — "[NOMBRE DESCRIPTIVO EN MAYÚSCULAS]"

**Descripción general**
Párrafo de 2-3 líneas describiendo quién es, su situación actual y qué busca.

**Datos demográficos**
- Edad: [rango específico]
- Género: [género predominante]
- Ubicación: [país/región específica]
- Ingresos: [nivel económico]
- Estado civil: [situación familiar]
- Nivel educativo: [educación]

**Situación actual**
- Su trabajo/ocupación actual
- Sus responsabilidades diarias
- Sus desafíos cotidianos
- Su relación con el producto/servicio

**Dolor principal**
❌ [Descripción del dolor #1 más grande que le quita el sueño]

**Otros dolores**
- [Dolor secundario 1]
- [Dolor secundario 2]
- [Dolor secundario 3]
- [Dolor secundario 4]

**Deseos y metas**
- [Deseo/meta 1]
- [Deseo/meta 2]
- [Deseo/meta 3]
- [Deseo/meta 4]

**Objeciones típicas**
- "[Objeción 1 en primera persona]"
- "[Objeción 2 en primera persona]"
- "[Objeción 3 en primera persona]"
- "[Objeción 4 en primera persona]"

**Disparadores de compra**
- [Disparador 1]
- [Disparador 2]
- [Disparador 3]
- [Disparador 4]

**Tipo de contenido que consume**
- [Tipo 1]
- [Tipo 2]
- [Tipo 3]

**Red social principal**
[Red principal] ([formato específico])
Secundaria: [Red secundaria]

**Tono y palabras que conectan**
[Descripción del tono ideal]
Enfoque en [temas clave].
Palabras clave: "[palabra 1]", "[palabra 2]", "[palabra 3]".

**Ejemplo de mensaje gancho**
✨ "[Mensaje gancho de 1-2 líneas]" ✨

<<<SECTION_START: EMBUDO_TOFU>>>
🎣 TOFU — ATRACCIÓN

**Objetivo:** Llamar la atención desde el dolor real, generar identificación inmediata.

**Formato:** [Reel/Post/Video]
**Gancho (primeros 3 segundos):**
❌ "[Frase gancho que ataque el dolor directamente]"

**Desarrollo breve:**
- [Mostrar el caos/problema]
- [Frase clave memorable]

**CTA:**
👉 "[Call to action suave]"

💡 **Por qué funciona:**
[Explicación breve]

<<<SECTION_START: EMBUDO_MOFU>>>
🧠 MOFU — EDUCACIÓN

**Objetivo:** Demostrar que la solución es simple, real y ya funciona.

**Formato:** [Carrusel/Historia/Video]
**Gancho:**
✅ "[Transformación lograda]"

**Estructura:**
1️⃣ [Problema común]
2️⃣ [Qué pasaba antes]
3️⃣ [Qué cambió]
4️⃣ [Resultados]
5️⃣ [Testimonio]

**CTA:**
👉 "[Invitación a demo]"

💡 **Por qué funciona:**
[Educa y baja objeciones]

<<<SECTION_START: EMBUDO_BOFU>>>
� BOFU — CIERRE

**Objetivo:** Acción inmediata con urgencia y bajo riesgo.

**Formato:** [Historias/Post/Video]

**Secuencia:**
**Parte 1:** "[Consecuencia de no actuar]"
**Parte 2:** "[Cómo resuelve el problema]"
**Parte 3:** 🔥 [Oferta] 💰 [Precio] ⏰ [Urgencia]

**CTA:**
👉 "[Acción directa]"

💡 **Por qué funciona:**
✔ Urgencia ✔ Accesibilidad ✔ Bajo riesgo

<<<SECTION_START: ADS_FRIO>>>
❄️ TRÁFICO FRÍO - {business_info.get('plataforma')}
Objetivo: Llegar a personas que NO te conocen.
Define: Objetivo, Ángulo (Dolor), 3 Variaciones Copy (adaptadas a {business_info.get('plataforma')}), Creativos (específicos para {business_info.get('plataforma')}), Segmentación (según {business_info.get('plataforma')}), Presupuesto (50% = ${business_info.get('presupuesto')*0.5} USD), CTA.
Si son ambas plataformas: especifica distribución 60% Facebook / 40% Google y estrategia para cada una.

<<<SECTION_START: ADS_TIBIO>>>
🔥 TRÁFICO TIBIO - Retargeting en {business_info.get('plataforma')}
Objetivo: Convertir interesados en prospectos.
Define: Objetivo, Ángulo (Prueba Social), Copy (adaptado a {business_info.get('plataforma')}), Creativos (específicos para {business_info.get('plataforma')}), Segmentación (según {business_info.get('plataforma')}), Presupuesto (35% = ${business_info.get('presupuesto')*0.35} USD), CTA.
Si son ambas plataformas: especifica distribución 60% Facebook / 40% Google y estrategia para cada una.

<<<SECTION_START: ADS_CALIENTE>>>
🌡️ TRÁFICO CALIENTE - Cierre en {business_info.get('plataforma')}
Objetivo: Cerrar ventas YA.
Define: Objetivo, Ángulo (Urgencia), Copy Cierre (adaptado a {business_info.get('plataforma')}), Creativos (específicos para {business_info.get('plataforma')}), Segmentación (según {business_info.get('plataforma')}), Presupuesto (15% = ${business_info.get('presupuesto')*0.15} USD), CTA.
Si son ambas plataformas: especifica distribución 60% Facebook / 40% Google y estrategia para cada una.

<<<SECTION_START: WHATSAPP_DIA1>>>
💬 DÍA 1 — Contacto + Diagnóstico
Mensaje: Saludo + 2 Preguntas.
Respuestas condicionadas.

<<<SECTION_START: WHATSAPP_DIA2>>>
💬 DÍA 2 — Valor + Invitación
Mensaje: Tip útil + Invitación suave.
Respuestas condicionadas.

<<<SECTION_START: WHATSAPP_DIA3>>>
💬 DÍA 3 — Prueba Social
Mensaje: Caso éxito + CTA.
Respuestas condicionadas.

<<<SECTION_START: WHATSAPP_DIA4>>>
💬 DÍA 4 — Objeción + Reencuadre
Mensaje: Reencuadre + Propuesta.
Respuestas condicionadas.

<<<SECTION_START: WHATSAPP_DIA5>>>
💬 DÍA 5 — Urgencia
Mensaje: Cupos/Tiempo limitado.
Respuestas condicionadas.

<<<SECTION_START: WHATSAPP_DIA6>>>
💬 DÍA 6 — Valor Final
Mensaje: Recurso extra + Mini cierre.
Respuestas condicionadas.

<<<SECTION_START: WHATSAPP_DIA7>>>
💬 DÍA 7 — Cierre/Parking
Mensaje: Última llamada o despedida elegante.
Respuestas condicionadas.

<<<SECTION_START: OBJECION_COSTO>>>
🛡️ OBJECIÓN: COSTO
Pregunta, Reframing, Propuesta, Mini Cierre.

<<<SECTION_START: OBJECION_TIEMPO>>>
🛡️ OBJECIÓN: TIEMPO
Pregunta, Reframing, Propuesta, Mini Cierre.

<<<SECTION_START: OBJECION_PERSONAL>>>
🛡️ OBJECIÓN: PERSONAL/SOCIOS
Pregunta, Reframing, Propuesta, Mini Cierre.

<<<SECTION_START: OBJECION_INTEGRACION>>>
🛡️ OBJECIÓN: INTEGRACIÓN/CAMBIO
Pregunta, Reframing, Propuesta, Mini Cierre.

<<<SECTION_START: OBJECION_MIEDO>>>
🛡️ OBJECIÓN: MIEDO/DESCONFIANZA
Pregunta, Reframing, Propuesta, Mini Cierre.


<<<SECTION_START: METRICAS>>>
� MÉTRICAS Y OPTIMIZACIÓN

### Costo por Lead
Definición y Valor Ideal.

Umbral de Alerta.

Acción de Mejora Inmediata.

Acción de Escalamiento.

### Tasa de Cierre
Definición y Valor Ideal.

Umbral de Alerta.

Acción de Mejora Inmediata.

Acción de Escalamiento.

### Tasa de Conversión
Definición y Valor Ideal.

Umbral de Alerta.

Acción de Mejora Inmediata.

Acción de Escalamiento.

### Engagement
Definición y Valor Ideal.

Umbral de Alerta.

Acción de Mejora Inmediata.

Acción de Escalamiento.

- NO agregues comentarios finales como "Espero que...", "¡Mucho éxito!", etc.
- Sé CONCISO pero COMPLETO en cada sección"""

        # PROMPT 2: SINGLE ROADMAP JSON
        roadmap_prompt = f"""CONTEXTO:
{base_info}

OBJETIVO:
Genera el ROADMAP ESTRATÉGICO en formato JSON.

ESTRUCTURA JSON REQUERIDA:
[
  {{
    "semana": 1,
    "foco": "Nombre del foco (ej. Setup & Awareness)",
    "descripcion": "Descripción breve de objetivos"
  }},
  ...
]
Cubriendo {int(business_info.get('duration_days', 30)/7)} semanas. SOLO JSON. SIN MARKDOWN.
"""



        try:
            # Single LLM call for entire strategy
            from langchain.schema import HumanMessage, SystemMessage
            import time
            
            # Start token tracking
            with get_openai_callback() as cb:
                # Simulate progressive updates for UI (fake progress)
                section_names = [
                    "Embudo de Contenido",  # Step 2
                    "Estrategia de Ads",     # Step 3
                    "Flujo WhatsApp 7 Días", # Step 4
                    "Manejo de Objeciones",  # Step 5
                    "Acciones Diarias",      # Step 6
                    "Métricas y Optimización" # Step 7
                ]
                
                # Show progressive steps 2-7 BEFORE calling the AI
                # Timing: Step 2-3 (4s), Step 4-7 (4.5s)
                if progress_callback:
                    for idx, section_name in enumerate(section_names, 2):  # Start from step 2
                        progress_callback(section_name, "Preparando...", idx, 8)
                        
                        if idx <= 3:
                            time.sleep(4)  # 4 seconds for steps 2-3
                        else:
                            time.sleep(4.5)  # 4.5 seconds for steps 4-7
                    
                    # Force Step 8 display BEFORE the real AI call starts
                    # This ensures the "long wait" happens on Step 8, not Step 7
                    progress_callback("Finalizando ajustes", "Procesando...", 8, 8)
                
                # 1. Generate Strategy Text (Legacy Prompt)
                messages_strat = [
                    SystemMessage(content=unified_prompt),
                    HumanMessage(content="Genera la estrategia de texto ahora.")
                ]
                response_strat = self.llm(messages_strat)
                strategy_text = response_strat.content
                
                # 2. Generate Roadmap JSON (New Prompt)
                # We do this separately to ensure valid JSON and avoid token limit truncation on the text
                messages_roadmap = [
                    SystemMessage(content=roadmap_prompt),
                    HumanMessage(content="Genera el JSON del Roadmap ahora.")
                ]
                response_roadmap = self.llm(messages_roadmap)
                roadmap_json = response_roadmap.content
                
                # Clean JSON if wrapped in markdown
                if "```json" in roadmap_json:
                    roadmap_json = roadmap_json.split("```json")[1].split("```")[0].strip()
                elif "```" in roadmap_json:
                    roadmap_json = roadmap_json.split("```")[1].split("```")[0].strip()
                
                # 3. Combine output for parsing
                full_response = f"{strategy_text}\n\n<<<SECTION_START: ROADMAP>>>\n{roadmap_json}"
                
                # Restore original chain
                self.setup_chain(self.business_context)
                
                # Save token usage if username provided
                if username:
                    try:
                        total_tokens = cb.total_tokens
                        auth_subscription.track_tokens(username, total_tokens)
                        print(f"💰 Tokens tracked for {username}: {total_tokens}")
                    except Exception as e:
                        print(f"Error tracking tokens: {e}")
                
                return full_response
            
        except Exception as e:
            error_msg = f"Error generando estrategia: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"

    def generate_weekly_tasks_content(self, business_info, strategy_context, week_num, prev_feedback):
        """
        Generates specific tasks for a given week based on roadmap and feedback.
        """
        if not self.llm:
            return "[]"
            
        prompt = f"""Eres un Project Manager de Marketing.
        
CONTEXTO NEGOCIO:
{business_info}

CONTEXTO ESTRATEGIA (Roadmap):
{strategy_context.get('roadmap', '[]')}

FEEDBACK SEMANA ANTERIOR:
{prev_feedback}

OBJETIVO: Generar el PLAN DE TAREAS para la SEMANA {week_num}.
Analiza el feedback (si existe) para optimizar las tareas. 
Si el feedback fue negativo, sugiere cambios. Si fue positivo, escala.

Genera una lista de tareas JSON válida:
[
  {{
    "titulo": "Acción específica",
    "descripcion": "Detalle de cómo hacerlo",
    "categoria": "contenido|ads|whatsapp|metricas|setup",
    "prioridad": "alta|media|baja",
    "frecuencia": "unica|diaria|semanal",
    "dia_semana": 0-6 (0=Lunes)
  }}
]
Genera entre 15-25 tareas para la semana. SOLO JSON.
"""
        try:
            from langchain.schema import HumanMessage, SystemMessage
            response = self.llm([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            print(f"Error generation weekly tasks: {e}")
            return "[]"



    def generate_strategy(self, business_info):
        """
        Generates the initial marketing strategy based on business info.
        """
        if not self.llm:
            return "Error: No se detectó la API Key de OpenAI. Por favor configura tu .env."

        # Format the system prompt with business info
        buyer_persona_text = ""
        if business_info.get('buyer_persona'):
            buyer_persona_text = f"\n- Buyer Persona Base (expandir y profundizar): {business_info.get('buyer_persona')}"
        
        # Add business context if available
        business_context_text = ""
        if self.business_context:
            business_context_text = f"\n\nCONTEXTO DEL NEGOCIO (Cerebro):\n{self.business_context}\n\nIMPORTANTE: Usa este contexto para personalizar toda la estrategia según la personalidad, tono de voz y valores del negocio.\n"
        
        system_prompt = f"""Eres un Estratega de Marketing Senior y Experto en Ventas B2B/B2C.
Tu objetivo es crear un PLAN DE ACCIÓN DE VENTAS Y MARKETING de alto nivel, ultra-personalizado y orientado a resultados (Leads y Cierres).
{business_context_text}
INPUTS DEL CLIENTE:
- Rubro: {business_info.get('rubro')}
- Nombre: {business_info.get('nombre')}
- Tipo: {business_info.get('tipo')}
- Producto Estrella: {business_info.get('producto')}
- Precio: {business_info.get('precio', 'No especificado')}
- Meta: {business_info.get('meta')}
- Presupuesto: {business_info.get('presupuesto')}
- Modalidad de Venta: {business_info.get('modalidad_venta', 'No especificado')}
- Sistema Actual: {business_info.get('sistema_actual', 'No especificado')}
- Plataformas: {business_info.get('plataforma')}{buyer_persona_text}

ESTRUCTURA DE RESPUESTA OBLIGATORIA (Usa EXACTAMENTE estos delimitadores):

<<<SECTION_START: AVATAR>>>
Genera 1 Avatar de Cliente Ideal MUY ESPECÍFICO (no genérico).
Define: Nombre, Dolor Principal (Qué le quita el sueño), Objeciones Típicas y Vocabulario.
Toda la estrategia siguiente debe basarse en ESTE avatar.

<<<SECTION_START: EMBUDO_TOFU>>>
Genera contenido TOFU (Descubrimiento) para Lunes y Jueves.
Objetivo: Atrae atención, habla del problema.
Incluye: Formato (Reel/Post), Gancho y CTA.

<<<SECTION_START: EMBUDO_MOFU>>>
Genera contenido MOFU (Consideración) para Martes y Viernes.
Objetivo: Educa, muestra solución, casos de éxito.
Incluye: Formato (Historia/Carrusel), Gancho y CTA.

<<<SECTION_START: EMBUDO_BOFU>>>
Genera contenido BOFU (Cierre) para Miércoles, Sábado y Domingo.
Objetivo: Oferta directa, urgencia, venta.
Incluye: Formato (Post Venta/Historia), Gancho y CTA.

<<<SECTION_START: ADS_FRIO>>>
🔥 TRÁFICO FRÍO
Objetivo: Llegar a personas que NO te conocen pero tienen el dolor.
Define:
1. Objetivo de campaña (Mensajes/Leads).
2. Ángulo Principal (Pain-Based Trigger).
3. 7 Dolores a destacar.
4. 3 Variaciones de Copy (Directo, Miedo, Aspiración).
5. Ideas de Creativos (Video 15s, Imágenes).
6. Segmentación Sugerida.
7. Presupuesto sugerido: 50% del total ({business_info.get('presupuesto')} USD).
8. CTA específico.

<<<SECTION_START: ADS_TIBIO>>>
🔥 TRÁFICO TIBIO – Retargeting
Objetivo: Convertir interesados en prospectos.
Define:
1. Objetivo de campaña.
2. Ángulo Principal (Prueba Social/Lógica).
3. Dolores/Dudas a atacar.
4. Copy persuasivo.
5. Ideas de Creativos.
6. Segmentación (Públicos personalizados).
7. Presupuesto sugerido: 35% del total.
8. CTA específico.

<<<SECTION_START: ADS_CALIENTE>>>
🔥 TRÁFICO CALIENTE – Cierre
Objetivo: Cerrar ventas YA.
Define:
1. Objetivo de campaña.
2. Ángulo Principal (Urgencia/Oferta).
3. Beneficio final.
4. Copy de Cierre directo.
5. Ideas de Creativos.
6. Segmentación (Checkout iniciado/Mensajes previos).
7. Presupuesto sugerido: 15% del total.
8. CTA específico.

<<<SECTION_START: WHATSAPP_DIA1>>>
🔵 DÍA 1 — Contacto + Diagnóstico Inteligente
Objetivo: Romper el hielo.
Texto del mensaje: Saludo + 2 Preguntas de diagnóstico.
Respuestas condicionadas: Qué decir si responde A, B o C.
IMPORTANTE: Usa párrafos separados para cada parte.

<<<SECTION_START: WHATSAPP_DIA2>>>
🟦 DÍA 2 — Aporte de Valor + Invitación a Demo
Objetivo: Enseñar algo útil + agendar sin presión.
Texto del mensaje: Dato curioso/Tip + Invitación suave.
Respuestas condicionadas: Qué decir si acepta o rechaza.
IMPORTANTE: Usa párrafos separados.

<<<SECTION_START: WHATSAPP_DIA3>>>
🟩 DÍA 3 — Prueba Social
Objetivo: Activar confianza.
Texto del mensaje: Mini caso de éxito real + CTA suave.
Respuestas condicionadas: Qué decir si muestra interés.
IMPORTANTE: Usa párrafos separados.

<<<SECTION_START: WHATSAPP_DIA4>>>
🟧 DÍA 4 — Objeción Principal + Reencuadre
Objetivo: Atacar la objeción del avatar sin confrontar.
Texto del mensaje: "Entiendo X..." + Reencuadre + Propuesta.
Respuestas condicionadas: Manejo de la objeción específica.
IMPORTANTE: Usa párrafos separados.

<<<SECTION_START: WHATSAPP_DIA5>>>
🟥 DÍA 5 — Urgencia Ligera
Objetivo: Mover al tibio.
Texto del mensaje: Cupos/Bono/Tiempo limitado.
Respuestas condicionadas: Qué decir si pide info.
IMPORTANTE: Usa párrafos separados.

<<<SECTION_START: WHATSAPP_DIA6>>>
🟪 DÍA 6 — Aporte de Valor Final
Objetivo: Reforzar autoridad.
Texto del mensaje: Recurso/Link útil + Mini cierre.
Respuestas condicionadas: Qué decir si agradece.
IMPORTANTE: Usa párrafos separados.

<<<SECTION_START: WHATSAPP_DIA7>>>
⬛ DÍA 7 — Cierre Elegante o Parking
Objetivo: Definir o dejar puerta abierta.
Texto del mensaje: Cierre final o "Plan de mejora gratis".
Respuestas condicionadas: Qué decir si acepta el plan.
IMPORTANTE: Usa párrafos separados.

<<<SECTION_START: OBJECION_COSTO>>>
OBJECIÓN: COSTO
Genera la respuesta en párrafos separados:
Pregunta: (La pregunta para indagar)

Reframing: (Cambio de perspectiva)

Propuesta: (Solución concreta)

Mini Cierre: (Pregunta de cierre)

<<<SECTION_START: OBJECION_TIEMPO>>>
OBJECIÓN: TIEMPO
Genera la respuesta en párrafos separados:
Pregunta:

Reframing:

Propuesta:

Mini Cierre:

<<<SECTION_START: OBJECION_PERSONAL>>>
OBJECIÓN: PERSONAL/SOCIOS
Genera la respuesta en párrafos separados:
Pregunta:

Reframing:

Propuesta:

Mini Cierre:

<<<SECTION_START: OBJECION_INTEGRACION>>>
OBJECIÓN: INTEGRACIÓN/CAMBIO
Genera la respuesta en párrafos separados:
Pregunta:

Reframing:

Propuesta:

Mini Cierre:

<<<SECTION_START: OBJECION_MIEDO>>>
OBJECIÓN: MIEDO/DESCONFIANZA
Genera la respuesta en párrafos separados:
Pregunta:

Reframing:

Propuesta:

Mini Cierre:

<<<SECTION_START: ACCIONES_DIARIAS>>>
🔥 CHECKLIST DE ACCIONES DIARIAS
Genera una rutina de alto rendimiento con:
1. Contactar 5 nuevos (Mensajes plantilla).
2. Seguimiento a 3 tibios (Mensajes plantilla).
3. Publicar 1 historia (Ideas).
4. Revisar métricas (Qué mirar).
5. Agendar/Hacer 1 Demo (Estructura).
Incluye Micro-Métricas para cada punto.

<<<SECTION_START: METRICAS>>>
🔥 MÉTRICAS Y OPTIMIZACIÓN
Genera CADA métrica como un bloque separado con su título exacto.
IMPORTANTE: Dentro de cada métrica, usa PÁRRAFOS SEPARADOS para cada punto:

### Costo por Lead
Definición y Valor Ideal.

Umbral de Alerta.

Acción de Mejora Inmediata.

Acción de Escalamiento.

### Tasa de Cierre
Definición y Valor Ideal.

Umbral de Alerta.

Acción de Mejora Inmediata.

Acción de Escalamiento.

### Tasa de Conversión
Definición y Valor Ideal.

Umbral de Alerta.

Acción de Mejora Inmediata.

Acción de Escalamiento.

### Engagement
Definición y Valor Ideal.

Umbral de Alerta.

Acción de Mejora Inmediata.

Acción de Escalamiento.


REGLAS DE ORO:
- NUNCA uses placeholders. Genera contenido REAL y ESPECÍFICO para el rubro {business_info.get('rubro')}.
- Habla con autoridad pero empatía.
- Enfócate en VENTAS y RESULTADOS ($$$).
- Adapta todo al Sistema Actual ({business_info.get('sistema_actual')}) y Modalidad ({business_info.get('modalidad_venta')}).
"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

        # Re-initialize chain with the specific system prompt for this strategy
        self.chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt
        )

        input_text = "Genera la estrategia completa ahora."
        
        try:
            response = self.chain.predict(input=input_text)
            
            # After generating strategy, restore the original chat chain with business context
            # This ensures subsequent chat interactions have the business context
            self.setup_chain(self.business_context)
            
            return response
        except Exception as e:
            return f"Ocurrió un error al generar la estrategia: {str(e)}"

    def chat(self, user_input):
        """
        Continues the conversation with the user.
        """
        if not self.llm:
            return "Error: No se detectó la API Key de OpenAI."
        
        try:
            response = self.chain.predict(input=user_input)
            return response
        except Exception as e:
            return f"Ocurrió un error en el chat: {str(e)}"
