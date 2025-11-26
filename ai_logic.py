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
                print("🔄 Initializing ChatOpenAI with gpt-4o...")
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
        
        self.memory = ConversationBufferMemory(return_messages=True)
        self.business_context = business_context  # Store for later use
        self.setup_chain(business_context)

    def setup_chain(self, business_context=""):
        # Initialize a default generic chain for general chat
        if not self.llm:
            return

        system_prompt = "Eres un asistente experto en marketing digital. Ayuda al usuario con sus dudas sobre marketing y ventas."
        
        if business_context:
            system_prompt += f"\n\nCONTEXTO DEL NEGOCIO:\n{business_context}\n\nUsa este contexto para dar respuestas personalizadas y específicas para este negocio."
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

        self.chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt
        )

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
            "AVATAR": f"""Eres un Estratega de Marketing Senior.
{base_info}

Genera 1 Avatar de Cliente Ideal MUY ESPECÍFICO (no genérico) para este negocio.
Define:
- Nombre del Avatar
- Dolor Principal (Qué le quita el sueño)
- Objeciones Típicas
- Vocabulario que usa

IMPORTANTE: Responde ÚNICAMENTE con la información del Avatar. NO generes embudos, ni ads, ni ninguna otra sección. SOLO EL AVATAR.""",
            
            "EMBUDO": f"""Eres un Estratega de Marketing Senior.
{base_info}

Genera un EMBUDO DE CONTENIDO SEMANAL (3 niveles):

<<<SECTION_START: EMBUDO_TOFU>>>
TOFU (Descubrimiento) - Lunes y Jueves
Objetivo: Atrae atención.
Incluye: Formato, Gancho y CTA.

<<<SECTION_START: EMBUDO_MOFU>>>
MOFU (Consideración) - Martes y Viernes
Objetivo: Educa y muestra solución.
Incluye: Formato, Gancho y CTA.

<<<SECTION_START: EMBUDO_BOFU>>>
BOFU (Cierre) - Miércoles, Sábado y Domingo
Objetivo: Venta directa.
Incluye: Formato, Gancho y CTA.

Sé CONCISO y DIRECTO. Contenido específico para {business_info.get('rubro')}.""",
            
            "ADS": f"""Eres un Estratega de Ads.
{base_info}

Genera ESTRATEGIA DE ADS (3 niveles):

<<<SECTION_START: ADS_FRIO>>>
🔥 TRÁFICO FRÍO
Objetivo: Atraer desconocidos.
Define: Objetivo, Ángulo (Dolor), 3 Variaciones Copy, Creativos, Segmentación, Presupuesto (50%).

<<<SECTION_START: ADS_TIBIO>>>
🔥 TRÁFICO TIBIO
Objetivo: Retargeting.
Define: Objetivo, Ángulo (Prueba Social), Copy, Creativos, Segmentación, Presupuesto (35%).

<<<SECTION_START: ADS_CALIENTE>>>
🔥 TRÁFICO CALIENTE
Objetivo: Cierre.
Define: Objetivo, Ángulo (Urgencia), Copy Cierre, Creativos, Segmentación, Presupuesto (15%).

Sé CONCISO. Contenido específico para {business_info.get('rubro')}.""",
            
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

Sé CONCISO y PERSUASIVO.""",
            
            "ACCIONES_DIARIAS": f"""Eres un Estratega de Productividad.
{base_info}

Genera CHECKLIST DIARIO DE VENTAS:
1. Prospección (Nuevos)
2. Seguimiento (Tibios)
3. Contenido (Historia)
4. Métricas
5. Cierres

Incluye micro-métricas. Sé BREVE y ACCIONABLE.""",
            
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


    def generate_strategy_progressive(self, business_info, progress_callback=None):
        """
        Generates marketing strategy section by section, calling progress_callback after each section.
        
        Args:
            business_info: Dictionary with business information
            progress_callback: Function(section_name, section_content, section_number, total_sections)
        
        Returns:
            Complete strategy text with all sections
        """
        if not self.llm:
            return "Error: No se detectó la API Key de OpenAI. Por favor configura tu .env."
        
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
        
        # Define sections to generate
        sections = [
            {
                "name": "Avatar de Cliente",
                "marker": "AVATAR",
                "prompt": f"""Eres un Estratega de Marketing Senior.
{base_info}

Genera 1 Avatar de Cliente Ideal MUY ESPECÍFICO (no genérico) para este negocio.
Define:
- Nombre del Avatar
- Dolor Principal (Qué le quita el sueño)
- Objeciones Típicas
- Vocabulario que usa

Responde SOLO con el contenido del avatar, sin delimitadores."""
            },
            {
                "name": "Embudo de Contenido",
                "marker": "EMBUDO",
                "prompt": f"""Eres un Estratega de Marketing Senior.
{base_info}

Genera un EMBUDO DE CONTENIDO SEMANAL completo con 3 niveles:

<<<SECTION_START: EMBUDO_TOFU>>>
TOFU (Descubrimiento) - Lunes y Jueves
Objetivo: Atrae atención, habla del problema.
Incluye: Formato (Reel/Post), Gancho y CTA.

<<<SECTION_START: EMBUDO_MOFU>>>
MOFU (Consideración) - Martes y Viernes
Objetivo: Educa, muestra solución, casos de éxito.
Incluye: Formato (Historia/Carrusel), Gancho y CTA.

<<<SECTION_START: EMBUDO_BOFU>>>
BOFU (Cierre) - Miércoles, Sábado y Domingo
Objetivo: Oferta directa, urgencia, venta.
Incluye: Formato (Post Venta/Historia), Gancho y CTA.

Genera contenido REAL y ESPECÍFICO para {business_info.get('rubro')}."""
            },
            {
                "name": "Estrategia de Ads",
                "marker": "ADS",
                "prompt": f"""Eres un Estratega de Marketing Senior especializado en publicidad digital.
{base_info}

Genera una ESTRATEGIA DE ADS COMPLETA con 3 niveles de tráfico:

<<<SECTION_START: ADS_FRIO>>>
🔥 TRÁFICO FRÍO
Objetivo: Llegar a personas que NO te conocen pero tienen el dolor.
Define:
1. Objetivo de campaña (Mensajes/Leads)
2. Ángulo Principal (Pain-Based Trigger)
3. 7 Dolores a destacar
4. 3 Variaciones de Copy (Directo, Miedo, Aspiración)
5. Ideas de Creativos (Video 15s, Imágenes)
6. Segmentación Sugerida
7. Presupuesto sugerido: 50% del total ({business_info.get('presupuesto')} USD)
8. CTA específico

<<<SECTION_START: ADS_TIBIO>>>
🔥 TRÁFICO TIBIO – Retargeting
Objetivo: Convertir interesados en prospectos.
Define:
1. Objetivo de campaña
2. Ángulo Principal (Prueba Social/Lógica)
3. Dolores/Dudas a atacar
4. Copy persuasivo
5. Ideas de Creativos
6. Segmentación (Públicos personalizados)
7. Presupuesto sugerido: 35% del total
8. CTA específico

<<<SECTION_START: ADS_CALIENTE>>>
🔥 TRÁFICO CALIENTE – Cierre
Objetivo: Cerrar ventas YA.
Define:
1. Objetivo de campaña
2. Ángulo Principal (Urgencia/Oferta)
3. Beneficio final
4. Copy de Cierre directo
5. Ideas de Creativos
6. Segmentación (Checkout iniciado/Mensajes previos)
7. Presupuesto sugerido: 15% del total
8. CTA específico

Genera contenido REAL y ESPECÍFICO para {business_info.get('rubro')}."""
            },
            {
                "name": "Flujo WhatsApp 7 Días",
                "marker": "WHATSAPP",
                "prompt": f"""Eres un Estratega de Ventas especializado en conversaciones de WhatsApp.
{base_info}

Genera un FLUJO DE WHATSAPP DE 7 DÍAS completo:

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

<<<SECTION_START: WHATSAPP_DIA3>>>
🟩 DÍA 3 — Prueba Social
Objetivo: Activar confianza.
Texto del mensaje: Mini caso de éxito real + CTA suave.
Respuestas condicionadas: Qué decir si muestra interés.

<<<SECTION_START: WHATSAPP_DIA4>>>
🟧 DÍA 4 — Objeción Principal + Reencuadre
Objetivo: Atacar la objeción del avatar sin confrontar.
Texto del mensaje: "Entiendo X..." + Reencuadre + Propuesta.
Respuestas condicionadas: Manejo de la objeción específica.

<<<SECTION_START: WHATSAPP_DIA5>>>
🟥 DÍA 5 — Urgencia Ligera
Objetivo: Mover al tibio.
Texto del mensaje: Cupos/Bono/Tiempo limitado.
Respuestas condicionadas: Qué decir si pide info.

<<<SECTION_START: WHATSAPP_DIA6>>>
🟪 DÍA 6 — Aporte de Valor Final
Objetivo: Reforzar autoridad.
Texto del mensaje: Recurso/Link útil + Mini cierre.
Respuestas condicionadas: Qué decir si agradece.

<<<SECTION_START: WHATSAPP_DIA7>>>
⬛ DÍA 7 — Cierre Elegante o Parking
Objetivo: Definir o dejar puerta abierta.
Texto del mensaje: Cierre final o "Plan de mejora gratis".
Respuestas condicionadas: Qué decir si acepta el plan.

Genera mensajes REALES y ESPECÍFICOS para {business_info.get('rubro')}."""
            },
            {
                "name": "Manejo de Objeciones",
                "marker": "OBJECIONES",
                "prompt": f"""Eres un Estratega de Ventas especializado en manejo de objeciones.
{base_info}

Genera respuestas para las 5 OBJECIONES PRINCIPALES:

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

Genera respuestas REALES y ESPECÍFICAS para {business_info.get('rubro')}."""
            },
            {
                "name": "Acciones Diarias",
                "marker": "ACCIONES_DIARIAS",
                "prompt": f"""Eres un Estratega de Ventas especializado en rutinas de alto rendimiento.
{base_info}

Genera un CHECKLIST DE ACCIONES DIARIAS:

🔥 CHECKLIST DE ACCIONES DIARIAS
Genera una rutina de alto rendimiento con:
1. Contactar 5 nuevos (Mensajes plantilla)
2. Seguimiento a 3 tibios (Mensajes plantilla)
3. Publicar 1 historia (Ideas)
4. Revisar métricas (Qué mirar)
5. Agendar/Hacer 1 Demo (Estructura)

Incluye Micro-Métricas para cada punto.
Genera contenido REAL y ESPECÍFICO para {business_info.get('rubro')}."""
            },
            {
                "name": "Métricas y Optimización",
                "marker": "METRICAS",
                "prompt": f"""Eres un Estratega de Marketing especializado en métricas y optimización.
{base_info}

Genera MÉTRICAS Y OPTIMIZACIÓN:

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

Genera métricas REALES y ESPECÍFICAS para {business_info.get('rubro')}."""
            }
        ]
        
        # Generate each section
        complete_strategy = ""
        total_sections = len(sections)
        
        for idx, section in enumerate(sections, 1):
            try:
                # Use direct LLM call instead of ConversationChain to avoid memory issues
                from langchain.schema import HumanMessage, SystemMessage
                
                messages = [
                    SystemMessage(content=section["prompt"]),
                    HumanMessage(content="Genera el contenido ahora.")
                ]
                
                # Generate section
                response = self.llm(messages)
                section_content = response.content
                
                # Add section marker for parsing
                if section["marker"] == "AVATAR":
                    complete_strategy += f"<<<SECTION_START: {section['marker']}>>>\n{section_content}\n\n"
                else:
                    # For multi-part sections, content already has markers
                    complete_strategy += section_content + "\n\n"
                
                # Call progress callback
                if progress_callback:
                    progress_callback(section["name"], section_content, idx, total_sections)
                    
            except Exception as e:
                error_msg = f"Error generando {section['name']}: {str(e)}"
                print(error_msg)
                complete_strategy += f"<<<SECTION_START: {section['marker']}>>>\n{error_msg}\n\n"
                if progress_callback:
                    progress_callback(section["name"], error_msg, idx, total_sections)
        
        # Restore original chain
        self.setup_chain(self.business_context)
        
        return complete_strategy


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
