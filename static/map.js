// This code is based on the demo for the Google Maps lecture.
"use strict";

function initMap(){
    
    // Specify where the map is centered.
    // Defining this variable outside of the map options makes
    // it easier to dynamically change if you need to recenter.
    var myLatLng = {lat: 37.788668, lng: -122.411499}; // Hackbright

    // Create a map object and specify the DOM element for display.
    var map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 18,
    });
}

// This code is based on example from the API docs.

function displayRoute(result) {
    var directionsDisplay;
    directionsDisplay = new google.maps.DirectionsRenderer();
    directionsDisplay.setDirections(result);
    directionsDisplay.setMap(map);
}

google.maps.event.addDomListener(window, 'load', initMap);
