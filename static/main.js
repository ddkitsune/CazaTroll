// API Key para el servicio ipstack. Reemplaza con tu propia API key si es necesario.
const API_KEY = 'b6c5150bbe4c0e8b8c9e98cf588d446f';

/**
 * Función para obtener información de IP utilizando la API de ipstack.
 * @param {string} ip - La dirección IP para buscar información.
 * @returns {Promise<object>} - Una promesa que resuelve con un objeto JSON que contiene información de la IP.
 *                             En caso de error, captura el error y lo imprime en la consola.
 */
const fetchIpinfo = ip => {
  return fetch(`http://api.ipstack.com/${ip}?access_key=${API_KEY}`) // Realiza una petición GET a la API de ipstack para la IP dada.
    .then(res => res.json()) // Convierte la respuesta del servidor a formato JSON.
    .catch(err => console.error(err)) // Captura y muestra cualquier error que ocurra durante la petición o procesamiento.
};

/**
 * Función auxiliar para seleccionar un elemento del DOM utilizando un selector CSS.
 * @param {string} selector - Selector CSS para el elemento a seleccionar.
 * @returns {HTMLElement} - El primer elemento que coincide con el selector proporcionado.
 */
const $ = selector => document.querySelector(selector);

// Selecciona elementos del DOM y los almacena en variables para su uso posterior.
const $form = $('#form'); // Formulario de búsqueda de IP.
const $input = $('#input'); // Campo de entrada para la dirección IP.
const $submit = $('#submit'); // Botón de envío del formulario.
const $results = $('#results'); // Contenedor para mostrar los resultados de la búsqueda.
const $map = $('#map'); // Contenedor para mostrar el mapa.

let map = null; // Variable para almacenar la instancia del mapa de Leaflet, inicializada a null.

// Agrega un event listener al formulario para manejar el evento de envío (submit).
$form.addEventListener('submit', async (event) => {
  event.preventDefault(); // Previene el comportamiento por defecto del formulario de recargar la página.
  const { value } = $input; // Obtiene el valor del campo de entrada de IP.
  if (!value) return; // Si el campo de entrada está vacío, sale de la función.

  $submit.setAttribute('disabled', ''); // Deshabilita el botón de envío para evitar envíos múltiples mientras se procesa la petición.
  $submit.setAttribute('aria-busy', 'true'); // Establece el atributo aria-busy para indicar que el botón está en estado de carga (para accesibilidad).

  const ipInfo = await fetchIpinfo(value); // Llama a la función fetchIpinfo para obtener información de la IP ingresada. Espera a que la promesa se resuelva.

  if (ipInfo) { // Si se recibe información de la IP (es decir, ipInfo no es null o undefined).
    // Mostrar detalles de la IP en el contenedor de resultados.
    const { ip, city, region_name, country_name, latitude, longitude, zip, country_flag_emoji } = ipInfo; // Extrae las propiedades necesarias del objeto ipInfo.
    $results.innerHTML = `
      <div class="space-y-2">
        <p><strong>IP:</strong> ${ip}</p>
        <p><strong>Ubicación:</strong> ${city}, ${region_name}, ${country_name} ${country_flag_emoji}</p>
        <p><strong>Código Postal:</strong> ${zip}</p>
        <p><strong>Coordenadas:</strong> ${latitude}, ${longitude}</p>
      </div>
    `; // Actualiza el contenido HTML del contenedor de resultados con la información de la IP.

    // Mostrar el mapa utilizando Leaflet.
    if (map) {
      map.remove(); // Si ya existe una instancia del mapa, la elimina del DOM para reemplazarla con una nueva.
    }
    map = L.map('map').setView([latitude, longitude], 13); // Crea una nueva instancia del mapa de Leaflet en el elemento con ID 'map', centrada en las coordenadas de latitud y longitud obtenidas, con un nivel de zoom de 13.

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors' // Define la capa de teselas del mapa utilizando OpenStreetMap y añade la atribución requerida.
    }).addTo(map); // Añade la capa de teselas al mapa.

    L.marker([latitude, longitude]) // Crea un marcador en las coordenadas de latitud y longitud.
      .addTo(map) // Añade el marcador al mapa.
      .bindPopup(`<b>${city}</b><br>${region_name}, ${country_name}`) // Asocia una ventana emergente (popup) al marcador que muestra la ciudad, región y país al hacer clic en el marcador.
      .openPopup(); // Abre la ventana emergente inmediatamente después de crear el marcador.
  }

  $submit.removeAttribute('disabled'); // Remueve el atributo 'disabled' del botón de envío, habilitándolo nuevamente.
  $submit.removeAttribute('aria-busy'); // Remueve el atributo 'aria-busy' del botón de envío, indicando que ya no está en estado de carga.
});

// Funcionalidad para alternar el modo oscuro/claro de la página.
const toggleButton = $('#toggle-dark-mode'); // Selecciona el botón para alternar el modo oscuro.
toggleButton.addEventListener('click', () => {
  document.documentElement.classList.toggle('dark'); // Agrega o remueve la clase 'dark' del elemento html (documentElement), lo que activa o desactiva el modo oscuro definido en Tailwind CSS.
});