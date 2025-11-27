"""
Script to generate an example PDF for prospects to download
This shows what the system can generate
"""
import sys
sys.path.append('.')

from pdf_gen import generate_pdf

# Sample business info for a fictional attractive business
business_info = {
    "nombre": "Panadería Artesanal La Masa Madre",
    "rubro": "Panadería Artesanal y Repostería",
    "tipo": "Negocio Local con Venta Online",
    "producto": "Pan de Masa Madre Artesanal",
    "precio": 8,
    "meta": "Aumentar ventas online en un 50% y abrir un segundo local",
    "presupuesto": 500,
    "presupuesto_diario": 16.67,
    "plataforma": "Facebook Ads, Google Ads",
    "modalidad_venta": "Venta en local + Delivery + E-commerce",
    "buyer_persona": "Familias de clase media-alta que valoran productos naturales y saludables"
}

# Sample strategy text (simplified version for demo)
strategy_text = """
<<<SECTION_START: AVATAR>>>
👤 AVATAR DE CLIENTE IDEAL

Nombre: María Wellness

Dolor Principal: María está cansada del pan industrial lleno de conservantes. Busca opciones saludables para su familia pero no encuentra productos de calidad cerca de su casa. Le preocupa la alimentación de sus hijos y quiere lo mejor para ellos.

Objeciones Típicas: "¿Es realmente más saludable?", "El precio es alto comparado con el supermercado", "¿Cuánto dura fresco?"

Vocabulario: "Natural", "Artesanal", "Sin conservantes", "Masa madre", "Saludable", "Para mi familia", "Ingredientes de calidad"

<<<SECTION_START: EMBUDO_TOFU>>>
📢 EMBUDO - TOFU (Descubrimiento) - Lunes y Jueves

Objetivo: Educar sobre los beneficios de la masa madre vs pan industrial

Formato: Reels cortos (15-30s) mostrando el proceso artesanal

Gancho: "¿Sabías que el pan industrial tiene más de 20 ingredientes artificiales? El nuestro solo tiene 4: harina, agua, sal y tiempo."

CTA: "Descubre la diferencia. Link en bio para conocer más."

<<<SECTION_START: EMBUDO_MOFU>>>
📢 EMBUDO - MOFU (Consideración) - Martes y Viernes

Objetivo: Mostrar testimonios y casos de éxito

Formato: Carrusel con fotos de clientes satisfechos y sus historias

Gancho: "Desde que María cambió al pan de masa madre, sus hijos piden más y ella sabe que les da lo mejor."

CTA: "Únete a nuestra comunidad saludable. Haz tu primer pedido hoy."

<<<SECTION_START: EMBUDO_BOFU>>>
📢 EMBUDO - BOFU (Cierre) - Miércoles, Sábado y Domingo

Objetivo: Convertir con ofertas y urgencia

Formato: Post directo con oferta especial

Gancho: "🔥 SOLO HOY: 20% OFF en tu primer pedido + Delivery GRATIS. Cupos limitados."

CTA: "Ordena ahora por WhatsApp y recibe hoy mismo."

<<<SECTION_START: ADS_FRIO>>>
❄️ TRÁFICO FRÍO - Facebook Ads, Google Ads

Objetivo: Captar personas interesadas en alimentación saludable

Ángulo: Dolor - "¿Cansado del pan industrial lleno de químicos?"

3 Variaciones Copy:
1. DIRECTO: "Pan artesanal de masa madre. Solo 4 ingredientes naturales. Sin conservantes. Delivery en 24hs."
2. MIEDO: "Tu familia merece mejor que pan con 20 ingredientes artificiales. Descubre la diferencia de lo artesanal."
3. ASPIRACIÓN: "Únete a las familias que eligen calidad. Pan de masa madre como se hacía antes."

Creativos: 
- Video del proceso de amasado (Facebook)
- Foto del pan recién horneado con vapor (Facebook/Google Display)
- Anuncio de búsqueda: "Pan artesanal cerca de mí" (Google Search)

Segmentación:
- Facebook: Intereses en alimentación saludable, cocina, maternidad, vida sana
- Google: Keywords "pan artesanal", "masa madre", "panadería saludable"

Presupuesto: 50% = $250 USD (60% Facebook / 40% Google)

CTA: "Ordena tu primer pan artesanal"

<<<SECTION_START: ADS_TIBIO>>>
🔥 TRÁFICO TIBIO - Retargeting en Facebook Ads, Google Ads

Objetivo: Convertir visitantes del sitio web en clientes

Ángulo: Prueba Social - "Más de 500 familias ya eligieron lo natural"

Copy: "Volviste porque sabes que es diferente. Hoy es el día de probarlo. 15% OFF en tu primer pedido."

Creativos:
- Testimonios en video de clientes reales (Facebook)
- Carrusel con variedad de productos (Facebook)
- Display remarketing con oferta especial (Google)

Segmentación:
- Facebook: Visitantes del sitio web últimos 7 días
- Google: Remarketing de visitantes que vieron productos

Presupuesto: 35% = $175 USD (60% Facebook / 40% Google)

CTA: "Aprovecha tu descuento ahora"

<<<SECTION_START: ADS_CALIENTE>>>
🌡️ TRÁFICO CALIENTE - Cierre en Facebook Ads, Google Ads

Objetivo: Cerrar la venta con urgencia

Ángulo: Urgencia - "Últimos cupos para delivery hoy"

Copy Cierre: "Ya conoces la calidad. Hoy es el día. Ordena antes de las 6pm y recibe hoy mismo. Cupos limitados."

Creativos:
- Stories con contador de tiempo (Facebook)
- Anuncio dinámico de productos (Facebook/Google)

Segmentación:
- Facebook: Carrito abandonado, visitantes frecuentes
- Google: Búsquedas de marca, remarketing de alta intención

Presupuesto: 15% = $75 USD (60% Facebook / 40% Google)

CTA: "Ordenar ahora por WhatsApp"

<<<SECTION_START: WHATSAPP_DIA1>>>
💬 DÍA 1 — Contacto + Diagnóstico

Mensaje: "¡Hola! 👋 Soy Ana de La Masa Madre. Vi que te interesa nuestro pan artesanal. ¿Ya probaste pan de masa madre antes? ¿Qué es lo que más te importa al elegir pan para tu familia?"

Respuestas condicionadas:
- Si dice "No lo probé": "Perfecto, te va a encantar la diferencia. Es más digestivo y tiene un sabor único."
- Si dice "Salud": "Excelente, nuestro pan solo tiene 4 ingredientes naturales, sin conservantes ni aditivos."
- Si dice "Sabor": "Vas a notar la diferencia desde el primer bocado. El proceso de fermentación le da un sabor incomparable."

<<<SECTION_START: WHATSAPP_DIA2>>>
💬 DÍA 2 — Valor + Invitación

Mensaje: "María, te comparto un dato: el pan industrial puede tener hasta 20 ingredientes artificiales 😱. El nuestro solo tiene harina, agua, sal y tiempo. ¿Te gustaría probar la diferencia? Tengo un descuento especial para nuevos clientes."

Respuestas condicionadas:
- Si acepta: "¡Genial! Te doy 15% OFF en tu primer pedido. ¿Prefieres delivery o retiras en el local?"
- Si duda: "Sin compromiso. Si no te gusta, te devuelvo el dinero. Pero estoy segura que te va a encantar."

<<<SECTION_START: WHATSAPP_DIA3>>>
💬 DÍA 3 — Prueba Social

Mensaje: "Te cuento que Laura, una mamá como vos, estaba igual de dudosa. Hoy hace 6 meses que nos compra todas las semanas. Sus hijos piden 'el pan rico' 😊. ¿Querés ser la próxima en sumarte?"

Respuestas condicionadas:
- Si muestra interés: "Perfecto, te armo un pedido inicial con nuestros 3 panes más populares. ¿Te va bien?"

<<<SECTION_START: WHATSAPP_DIA4>>>
💬 DÍA 4 — Objeción + Reencuadre

Mensaje: "Entiendo que el precio puede parecer alto comparado con el super. Pero pensalo así: estás invirtiendo en la salud de tu familia. Un pan nuestro equivale a 2 del super en calidad y nutrición. ¿No vale la pena?"

Respuestas condicionadas:
- Si acepta: "Exacto, es una inversión en salud. Te hago el pedido ahora?"

<<<SECTION_START: WHATSAPP_DIA5>>>
💬 DÍA 5 — Urgencia

Mensaje: "María, te aviso que mañana es el último día para aprovechar el 15% OFF. Solo tengo 5 cupos más para delivery esta semana. ¿Reservo el tuyo?"

Respuestas condicionadas:
- Si dice sí: "Perfecto, te reservo un cupo. ¿Qué día te viene mejor para recibir?"

<<<SECTION_START: WHATSAPP_DIA6>>>
💬 DÍA 6 — Valor Final

Mensaje: "Te comparto nuestra guía gratuita: '5 formas de conservar tu pan artesanal fresco por más tiempo'. Es un regalo para que cuando hagas tu primer pedido, lo disfrutes al máximo 📖"

Respuestas condicionadas:
- Si agradece: "De nada! Cuando quieras hacer tu pedido, avisame. El descuento sigue vigente."

<<<SECTION_START: WHATSAPP_DIA7>>>
💬 DÍA 7 — Cierre/Parking

Mensaje: "María, fue un placer charlar con vos. Si en algún momento decidís probar pan de verdad, acá estoy. Te dejo mi número guardado para cuando quieras. ¡Que tengas linda semana! 😊"

Respuestas condicionadas:
- Si responde: "Genial! Cuando quieras, hacemos tu primer pedido con el descuento."

<<<SECTION_START: OBJECION_COSTO>>>
🛡️ OBJECIÓN: COSTO

Pregunta: "Entiendo que el precio es importante. ¿Cuánto estás gastando ahora en pan por semana?"

Reframing: "Nuestro pan dura el doble que el industrial y alimenta mejor. En realidad, estás ahorrando porque compras menos y comes mejor."

Propuesta: "Te propongo esto: probá un pan nuestro y uno del super. Compará sabor, duración y cómo te sentís. Si no notas la diferencia, te devuelvo el dinero."

Mini Cierre: "¿Hacemos la prueba esta semana?"

<<<SECTION_START: OBJECION_TIEMPO>>>
🛡️ OBJECIÓN: TIEMPO

Pregunta: "¿Cuánto tiempo te lleva ir al super a comprar pan?"

Reframing: "Nosotros te lo llevamos a tu casa. Vos seguís con tu día y el pan llega fresco a tu puerta."

Propuesta: "Podés hacer pedidos programados semanales. Una vez por semana te llega tu pan sin que tengas que pensar en nada."

Mini Cierre: "¿Arrancamos con un pedido semanal?"

<<<SECTION_START: OBJECION_PERSONAL>>>
🛡️ OBJECIÓN: PERSONAL/SOCIOS

Pregunta: "¿Tu familia ya probó pan artesanal antes?"

Reframing: "Lo bueno es que a los chicos les encanta. Es más rico y más sano. Es una decisión que toda la familia va a agradecer."

Propuesta: "Hacé esto: comprá uno para probar. Si a tu familia no le gusta, no seguís. Pero te aseguro que van a pedir más."

Mini Cierre: "¿Probamos con uno esta semana?"

<<<SECTION_START: OBJECION_INTEGRACION>>>
🛡️ OBJECIÓN: INTEGRACIÓN/CAMBIO

Pregunta: "¿Qué es lo que más te preocupa del cambio?"

Reframing: "No es un cambio drástico. Seguís comiendo pan, solo que mejor. Es el mismo hábito, con mejor calidad."

Propuesta: "Empezá de a poco. Comprá uno nuestro y seguí con el otro. En 2 semanas me contás cuál preferís."

Mini Cierre: "¿Hacemos la prueba gradual?"

<<<SECTION_START: OBJECION_MIEDO>>>
🛡️ OBJECIÓN: MIEDO/DESCONFIANZA

Pregunta: "¿Qué es lo que te genera dudas?"

Reframing: "Te entiendo. Por eso tenemos garantía de devolución. Si no te gusta, te devuelvo el 100% del dinero. Sin preguntas."

Propuesta: "Además, podés venir al local a ver cómo trabajamos. Somos transparentes en todo el proceso."

Mini Cierre: "¿Te parece bien probar con la garantía?"

<<<SECTION_START: ACCIONES_DIARIAS>>>
✅ CHECKLIST DE ACCIONES DIARIAS

1. Contactar 5 nuevos (Mensajes plantilla)
   - Mensaje: "Hola [Nombre], vi que te interesa la alimentación saludable. ¿Ya conoces el pan de masa madre? Te cuento..."
   - Métrica: 5 contactos nuevos por día = 150 por mes

2. Seguimiento a 3 tibios (Mensajes plantilla)
   - Mensaje: "Hola [Nombre], ¿pudiste pensar en lo que hablamos? Hoy tengo una promo especial..."
   - Métrica: 3 seguimientos por día = 90 por mes

3. Publicar 1 historia (Ideas)
   - Lunes/Jueves: Proceso de elaboración
   - Martes/Viernes: Testimonios de clientes
   - Miércoles/Sábado/Domingo: Ofertas y promociones
   - Métrica: 7 historias por semana = 28 por mes

4. Revisar métricas (Qué mirar)
   - Costo por lead en Facebook/Google
   - Tasa de respuesta en WhatsApp
   - Conversión de consulta a venta
   - Métrica: Revisión diaria de 10 minutos

5. Agendar/Hacer 1 Demo (Estructura)
   - Ofrecer degustación gratuita en el local
   - Enviar muestra pequeña con delivery
   - Métrica: 1 demo por día = 30 por mes

<<<SECTION_START: METRICAS>>>
📈 MÉTRICAS Y OPTIMIZACIÓN

### Costo por Lead

Definición y Valor Ideal: Cuánto gastas para que alguien te contacte por WhatsApp o llene el formulario. Ideal: $2-5 USD por lead.

Umbral de Alerta: Si supera $8 USD por lead, hay que optimizar.

Acción de Mejora Inmediata: Cambiar creativos, ajustar segmentación, probar nuevos ángulos de copy.

Acción de Escalamiento: Si está en $2-3 USD, aumentar presupuesto en 20% y monitorear.

### Tasa de Cierre

Definición y Valor Ideal: Cuántos leads se convierten en clientes. Ideal: 20-30% de los leads.

Umbral de Alerta: Si baja de 15%, revisar el proceso de venta por WhatsApp.

Acción de Mejora Inmediata: Mejorar scripts de WhatsApp, ofrecer garantía de devolución, agregar urgencia.

Acción de Escalamiento: Si está en 30%+, documentar el proceso y replicarlo.

### Tasa de Conversión

Definición y Valor Ideal: Porcentaje de visitantes del sitio que se convierten en leads. Ideal: 3-5%.

Umbral de Alerta: Si baja de 2%, revisar la landing page.

Acción de Mejora Inmediata: Mejorar el CTA, agregar testimonios, simplificar el formulario.

Acción de Escalamiento: Si está en 5%+, hacer A/B testing para llegar a 7-10%.

### Engagement

Definición y Valor Ideal: Interacción en redes sociales (likes, comentarios, shares). Ideal: 5-10% de engagement rate.

Umbral de Alerta: Si baja de 3%, el contenido no está resonando.

Acción de Mejora Inmediata: Publicar más contenido educativo, hacer preguntas, responder todos los comentarios.

Acción de Escalamiento: Si está en 10%+, aumentar frecuencia de publicaciones y probar nuevos formatos.
"""

# Generate the PDF
print("Generating example PDF...")
pdf_bytes = generate_pdf(strategy_text, business_info)

# Save to assets folder
with open("assets/ejemplo-estrategia.pdf", "wb") as f:
    f.write(pdf_bytes)

print("✅ Example PDF generated successfully at: assets/ejemplo-estrategia.pdf")
print("📄 File size:", len(pdf_bytes), "bytes")
