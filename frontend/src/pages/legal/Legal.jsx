import React from "react";

function LegalPage({ testId, title, updated, sections }) {
  return (
    <div className="max-w-3xl mx-auto px-6 lg:px-12 py-14 sm:py-20" data-testid={testId}>
      <div className="overline mb-3">Información legal</div>
      <h1 className="font-heading text-4xl md:text-5xl font-light leading-[1.05]">{title}</h1>
      <p className="mt-3 text-xs uppercase tracking-[0.2em] text-ink-muted">Última actualización: {updated}</p>
      <div className="mt-10 space-y-8 text-ink-soft font-light leading-relaxed text-base">
        {sections.map((s, i) => (
          <section key={i}>
            <h2 className="font-heading text-xl font-normal text-ink mb-3">{s.h}</h2>
            {Array.isArray(s.p) ? s.p.map((para, j) => <p key={j} className="mb-3">{para}</p>) : <p>{s.p}</p>}
            {s.ul && (
              <ul className="list-disc pl-6 mt-3 space-y-1.5">
                {s.ul.map((li, k) => <li key={k}>{li}</li>)}
              </ul>
            )}
          </section>
        ))}
      </div>
    </div>
  );
}

export function AvisoLegal() {
  return (
    <LegalPage
      testId="legal-aviso"
      title="Aviso Legal"
      updated="Febrero 2026"
      sections={[
        { h: "1. Datos identificativos", p: "En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la Información y Comercio Electrónico (LSSI-CE), informamos a los usuarios de los siguientes datos del titular del sitio web:", ul: [
          "Denominación social: Productos Ecoandes S.L.",
          "CIF: B-XXXXXXXX",
          "Domicilio social: C. Ferrocarril, 16, Edificio 12 Nave 4, 28880 Meco, Madrid (España)",
          "Email de contacto: info@productosecoandes.com",
          "Teléfono: 918 30 72 66",
          "Sitio web: productosecoandes.com",
        ]},
        { h: "2. Objeto", p: "El presente aviso legal regula el uso del sitio web productosecoandes.com (en adelante, el Sitio Web), que Productos Ecoandes S.L. pone a disposición de los usuarios de Internet. La utilización del Sitio Web atribuye la condición de usuario e implica la aceptación plena de todas las cláusulas aquí descritas." },
        { h: "3. Propiedad intelectual e industrial", p: "Todos los contenidos del Sitio Web (textos, fotografías, gráficos, imágenes, iconos, tecnología, software y diseño) son propiedad de Productos Ecoandes S.L. o de terceros que han autorizado su uso. Queda prohibida la reproducción total o parcial sin autorización expresa." },
        { h: "4. Responsabilidad", p: "Productos Ecoandes S.L. no se hace responsable de los daños o perjuicios derivados del acceso al Sitio Web ni del uso de la información contenida en él. El titular se reserva el derecho a modificar el contenido o suspender el servicio en cualquier momento." },
        { h: "5. Legislación aplicable y jurisdicción", p: "El presente aviso legal se rige por la legislación española. Cualquier controversia se someterá a los Juzgados y Tribunales del domicilio del consumidor (en consumo) o de la ciudad sede del titular (en relaciones B2B), salvo lo que disponga la normativa imperativa." }
      ]}
    />
  );
}

export function PoliticaCookies() {
  return (
    <LegalPage
      testId="legal-cookies"
      title="Política de Cookies"
      updated="Febrero 2026"
      sections={[
        { h: "1. ¿Qué son las cookies?", p: "Las cookies son pequeños archivos de texto que los sitios web envían al navegador del usuario para almacenar información que puede ser recuperada posteriormente. Son útiles para que el sitio recuerde tus preferencias o realice estadísticas de uso." },
        { h: "2. Tipos de cookies que usamos", p: "En este sitio utilizamos las siguientes categorías de cookies, conforme a la Guía de la AEPD sobre el uso de cookies:", ul: [
          "Necesarias: indispensables para el funcionamiento del sitio (sesión, carrito de compra, idioma). No requieren consentimiento.",
          "Analíticas: nos permiten medir y analizar el comportamiento de los usuarios para mejorar el servicio. Datos agregados y anonimizados.",
          "Marketing: utilizadas para mostrar contenidos y publicidad personalizados en función de tus intereses."
        ]},
        { h: "3. Gestión del consentimiento", p: "Al acceder al Sitio Web por primera vez, te mostramos un banner para que aceptes, rechaces o configures el uso de cookies no esenciales. Puedes modificar tus preferencias en cualquier momento eliminando los datos almacenados por tu navegador." },
        { h: "4. Cookies de terceros", p: "Algunas cookies pueden ser gestionadas por terceros (Stripe, PayPal y proveedores de analítica). Estos terceros se rigen por sus propias políticas de cookies y privacidad." },
        { h: "5. Cómo desactivar las cookies en tu navegador", p: "Puedes configurar tu navegador para bloquear o eliminar las cookies en cualquier momento. Los principales navegadores (Chrome, Firefox, Safari, Edge) ofrecen guías oficiales en sus secciones de ayuda." }
      ]}
    />
  );
}

export function PoliticaPrivacidad() {
  return (
    <LegalPage
      testId="legal-privacidad"
      title="Política de Privacidad"
      updated="Febrero 2026"
      sections={[
        { h: "1. Responsable del tratamiento", p: "Productos Ecoandes S.L., con CIF B-XXXXXXXX, domicilio en C. Ferrocarril, 16, Edificio 12 Nave 4, 28880 Meco (Madrid) y email info@productosecoandes.com, es el responsable del tratamiento de tus datos personales conforme al Reglamento (UE) 2016/679 (RGPD) y la Ley Orgánica 3/2018 (LOPDGDD)." },
        { h: "2. Finalidades del tratamiento", p: "Tratamos tus datos para las siguientes finalidades:", ul: [
          "Gestión de tu cuenta de usuario y de los pedidos realizados.",
          "Facturación y cumplimiento de las obligaciones contables y fiscales.",
          "Atención al cliente y resolución de incidencias.",
          "Envío de comunicaciones comerciales (solo si lo has consentido expresamente)."
        ]},
        { h: "3. Base legal", p: "La base legal del tratamiento es la ejecución del contrato de compraventa, el cumplimiento de obligaciones legales y, en su caso, el consentimiento del interesado." },
        { h: "4. Conservación de los datos", p: "Conservamos tus datos durante el tiempo necesario para la finalidad para la que fueron recabados y, posteriormente, durante los plazos de prescripción legal aplicables (hasta 6 años para datos contables)." },
        { h: "5. Destinatarios", p: "Tus datos podrán ser comunicados a Stripe y PayPal (proveedores de pago), Resend (envío de emails transaccionales) y Cloudinary (alojamiento de imágenes), todos ellos con contratos de encargo de tratamiento conforme al art. 28 RGPD." },
        { h: "6. Derechos", p: "Puedes ejercer en cualquier momento tus derechos de acceso, rectificación, supresión, oposición, limitación y portabilidad escribiendo a info@productosecoandes.com adjuntando copia de un documento identificativo. También puedes presentar reclamación ante la Agencia Española de Protección de Datos (www.aepd.es)." }
      ]}
    />
  );
}

export function Condiciones() {
  return (
    <LegalPage
      testId="legal-condiciones"
      title="Condiciones Generales de Contratación"
      updated="Febrero 2026"
      sections={[
        { h: "1. Objeto", p: "Las presentes Condiciones Generales regulan la compraventa de productos a través del sitio web productosecoandes.com, conforme al Real Decreto Legislativo 1/2007 (Ley General para la Defensa de los Consumidores y Usuarios) y la Ley 34/2002 (LSSI-CE)." },
        { h: "2. Productos y precios", p: "Todos los precios indicados incluyen el IVA aplicable, salvo que se indique lo contrario para las cuentas profesionales B2B. Los gastos de envío se calculan automáticamente en el checkout y se muestran antes de finalizar la compra." },
        { h: "3. Proceso de compra y pago", p: "El usuario selecciona los productos, indica los datos de envío y elige un método de pago (tarjeta vía Stripe, PayPal, o transferencia bancaria para clientes B2B). El contrato se perfecciona con la confirmación del pago." },
        { h: "4. Envío y entrega", p: "Los plazos de entrega son orientativos: 24-72 horas en península, plazos especiales para Baleares, Canarias, Ceuta y Melilla. Si la entrega se retrasara más de 30 días por causas imputables al vendedor, el cliente podrá resolver el contrato y obtener el reembolso." },
        { h: "5. Derecho de desistimiento", p: "El cliente dispone de 14 días naturales desde la recepción para desistir del contrato sin necesidad de justificación, salvo en productos perecederos abiertos o personalizados. Para ejercer este derecho, escríbenos a info@productosecoandes.com." },
        { h: "6. Garantía", p: "Conforme al art. 120 RDL 1/2007, los productos cuentan con garantía legal de tres años. Los productos alimentarios responden únicamente por defectos de calidad reclamados antes de la fecha de consumo preferente." },
        { h: "7. Resolución de litigios", p: "Conforme al Reglamento (UE) 524/2013, te informamos de la existencia de la plataforma de resolución de litigios de la Comisión Europea: https://ec.europa.eu/consumers/odr." }
      ]}
    />
  );
}
