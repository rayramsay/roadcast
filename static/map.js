"use strict";

var directionsDisplay;

// This code is based on the demo for the Google Maps lecture and an example
// from the Google Maps JavaScript API docs
function initMap(){
    
    // Specify where the map is centered.
    // Defining this variable outside of the map options makes
    // it easier to dynamically change if you need to recenter.
    var myLatLng = {lat: 37.788668, lng: -122.411499}; // Hackbright

    directionsDisplay = new google.maps.DirectionsRenderer;

    // Create a map object and specify the DOM element for display.
    var map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 18,
    });
}
//

function displayDirections(result) {
    debugger;
    directionsDisplay.setDirections(result);
    directionsDisplay.setMap(map);
}

// This code is based on an example from the AJAX lecture.
function submitRequest(evt) {
    evt.preventDefault();

    var formInputs = {
        "start": $("#start").val(),
        "end": $("#end").val(),
        "departure": $("#departure").val(),
        "mode": $("#mode").val()
    };

    $.post("/request",
          formInputs,
          displayDirections
          );
}
//

google.maps.event.addDomListener(window, 'load', initMap);

$("#directions-request").on("submit", submitRequest);
