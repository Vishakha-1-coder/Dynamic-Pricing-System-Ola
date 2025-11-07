let map, directionsService, directionsRenderer;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 19.076, lng: 72.8777 },
    zoom: 11,
    disableDefaultUI: false,
  });

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({ map });

  new google.maps.places.Autocomplete(document.getElementById("origin"));
  new google.maps.places.Autocomplete(document.getElementById("destination"));

  document
    .getElementById("estimate")
    .addEventListener("click", handleEstimate);
}

async function handleEstimate() {
  const origin = document.getElementById("origin").value.trim();
  const destination = document.getElementById("destination").value.trim();
  const vehicle = document.getElementById("vehicle").value;
  const riders = parseInt(document.getElementById("riders").value);
  const drivers = parseInt(document.getElementById("drivers").value);

  if (!origin || !destination) {
    alert("Please enter both pickup and destination.");
    return;
  }

  try {
    const API_BASE = "https://dynamic-pricing-system-ola.onrender.com";

const API_BASE = "https://dynamic-pricing-system-ola-1.onrender.com";

const response = await fetch(`${API_BASE}/predict`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    origin,
    destination,
    vehicle_type: vehicle,
    number_of_riders: riders,
    number_of_drivers: drivers,
  }),
});



    if (!response.ok) throw new Error(await response.text());

    const data = await response.json();

    document.getElementById("result").classList.remove("hidden");
    document.getElementById("fare").textContent = `₹ ${data.predicted_dynamic_price}`;
    document.getElementById("meta").textContent = `${data.vehicle_type} • ${data.distance_km} km • ${data.duration_min} min`;

    drawRoute(origin, destination);
  } catch (err) {
    console.error("Error:", err);
    alert("Something went wrong. Make sure the backend is running.");
  }
}

function drawRoute(origin, destination) {
  directionsService.route(
    { origin, destination, travelMode: google.maps.TravelMode.DRIVING },
    (res, status) => {
      if (status === "OK") directionsRenderer.setDirections(res);
    }
  );
}

window.initMap = initMap;
