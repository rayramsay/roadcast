"use strict";

// This code is based on the demo for the Google Maps lecture, an example
// from the Google Maps JavaScript API docs, and an example from the AJAX
// lecture.

function initMap(){
    
    // Specify where the map is centered.
    // Defining this variable outside of the map options makes
    // it easier to dynamically change if you need to recenter.
    var myLatLng = {lat: 37.788668, lng: -122.411499}; // Hackbright

    var directionsDisplay = new google.maps.DirectionsRenderer;
    var directionsService = new google.maps.DirectionsService;

    // Create a map object and specify the DOM element for display.
    var map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 10,
    });

    directionsDisplay.setMap(map);
    
    var onSubmitHandler = function(evt) {
        evt.preventDefault();
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    };

    $("#directions-request").on("submit", onSubmitHandler);
}

function calculateAndDisplayRoute(directionsService, directionsDisplay) {
    var start = document.getElementById('start').value;
    var end = document.getElementById('end').value;
    var mode = document.getElementById('mode').value;
    directionsService.route({
      origin: start,
      destination: end,
      travelMode: mode
    }, function(response, status) {
      if (status === 'OK') {
        directionsDisplay.setDirections(response);

        var formInputs = {
            "start": start,
            "end": end,
            "departure": $("#departure").val(),
            "mode": mode,
        };

        $.post("/request",
               formInputs,
               function (response) { alert("Hi"); }
              );
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    });
}



google.maps.event.addDomListener(window, 'load', initMap);
