// static/js/ride.js
// Shared client JS for ride pages
// ride.js — small helper file (keeps static route happy)
(function () {
  // helper to get JWT token (two common keys used in your project)
  window.getAuthToken = function() {
    return localStorage.getItem('access_token') || localStorage.getItem('token') || null;
  };

  // small helper: fetch wrapper with JWT
  window.authFetch = async function(url, opts = {}) {
    const token = window.getAuthToken();
    opts.headers = opts.headers || {};
    if (token) opts.headers['Authorization'] = 'Bearer ' + token;
    opts.credentials = opts.credentials || 'same-origin';
    return fetch(url, opts);
  };

  console.log("ride.js loaded");
})();

(function () {
  window._ride = window._ride || {};

  function getToken() {
    return localStorage.getItem('access_token') || localStorage.getItem('token') || null;
  }

  // Create and manage websocket connection for a ride
  window.startRideSocket = function (rideId, onMessage) {
    const protocol = (window.location.protocol === 'https:') ? 'wss' : 'ws';
    const host = window.location.host;
    const socketUrl = `${protocol}://${host}/ws/ride/${rideId}/`;

    let socket = new WebSocket(socketUrl);

    socket.onopen = function () {
      console.log('WS connected to', socketUrl);
    };

    socket.onmessage = function (evt) {
      let data;
      try {
        data = JSON.parse(evt.data);
      } catch (e) {
        data = evt.data;
      }
      if (onMessage && typeof onMessage === 'function') onMessage(data);
    };

    socket.onclose = function () {
      console.log('WS closed, attempting reconnect in 2s');
      setTimeout(() => startRideSocket(rideId, onMessage), 2000);
    };

    socket.onerror = function (err) {
      console.error('WS error', err);
      socket.close();
    };

    // expose socket for other functions
    window._ride.socket = socket;
    return socket;
  };

  // helper used by templates to update markers
  window.updateDriverMarker = function (lat, lng) {
    if (window.driverMarker && typeof window.driverMarker.setLatLng === 'function') {
      window.driverMarker.setLatLng([lat, lng]);
    }
  };

  // Helper to create ride via API and save to localStorage (call from book ride)
  window.createRide = async function (payload) {
    const token = getToken();
    const res = await fetch('/api/rides/create/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': 'Bearer ' + token } : {})
      },
      body: JSON.stringify(payload)
    });

    if (res.status === 201 || res.status === 200) {
      const data = await res.json();
      // store ride data (for later pages)
      localStorage.setItem('currentRideId', data.id);
      localStorage.setItem('lastRide', JSON.stringify({
        pickup: payload.pickup_text || '',
        dropoff: payload.drop_text || '',
        pickup_lat: payload.pickup_lat,
        pickup_lng: payload.pickup_lng,
        drop_lat: payload.drop_lat,
        drop_lng: payload.drop_lng
      }));
      return data;
    } else {
      const err = await res.json();
      throw err;
    }
  };

})();
