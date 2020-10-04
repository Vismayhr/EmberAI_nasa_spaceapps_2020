import { Component, OnInit } from '@angular/core';
import 'node_modules/leaflet-choropleth/dist/choropleth.js'
import { StoreService } from '../store.service';
import * as $ from 'jquery';
import Chart from 'chart.js';

declare let L;

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.scss']
})
export class PredictionComponent implements OnInit {

  geojsonData: any;
  map: any;
  year: number;
  week: number;


  constructor(private store: StoreService) {

  }

  convertTOGeoJSON(polygons) {
    let features = [];
    let totalValues = [];

    for (var i = 0; i < polygons.result.length; i++) {
      let polygon = polygons.result[i];
      if (polygon.predicted_value > 0) {

        let properties = { density: polygon.predicted_value };
        let geometry = {
          "type": "Polygon",
          "coordinates": [[[polygon.lon1, polygon.lat1], [polygon.lon2, polygon.lat2], [polygon.lon3, polygon.lat3], [polygon.lon4, polygon.lat4]]]
        }

        features.push({
          "type": "Feature",
          properties,
          geometry
        });
      }
    }

    return {
      "type": "FeatureCollection",
      "features": features
    }

  }


  ngOnInit() {
    this.map = L.map('mapid').setView([32.00118, -87.359296], 4);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      minZoom: 3,
      maxZoom: 6
    }).addTo(this.map);


    const formData = new FormData();
    let dateStr = $("#date").val();
    formData.append('predict_year', dateStr.substring(0, 4));
    formData.append('predict_week', dateStr.substring(dateStr.length - 2, dateStr.length));

    this.store.post('/fishing-vessel-presence', formData).subscribe((res) => {

      this.geojsonData = this.convertTOGeoJSON(res);
      this.initMap();
    });
  }

  initMap() {
    var map = this.map;
    var geojsonLayer;

    geojsonLayer = L.choropleth(this.geojsonData, {
      valueProperty: 'density', // which property in the features to use
      scale: ['white', 'blue'], // chroma.js scale - include as many as you like
      mode: 'q', // q for quantile, e for equidistant, k for k-means
      style: {
        color: '#fff', // border color
        weight: 0,
        fillOpacity: 0.9
      },
      onEachFeature: ((feature, layer) => {
        layer.on({
          mouseover: ((e) => {
            var layer = e.target;

            layer.setStyle({
              weight: 2,
              fillOpacity: 1
            });

            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
              layer.bringToFront();
            }
          }),
          mouseout: ((e) => {
            geojsonLayer.resetStyle(e.target);
          }),
        });
        layer.bindPopup('Density Value: ' + feature.properties.density);
      })
    }).addTo(map)

  }


  submitQuery(e) {
    e.preventDefault();

    const formData = new FormData();
    let dateStr = $("#date").val();
    formData.append('predict_year', dateStr.substring(0, 4));
    formData.append('predict_week', dateStr.substring(dateStr.length - 2, dateStr.length));

    this.store.post('/fishing-vessel-presence', formData).subscribe((res) => {

      this.geojsonData = this.convertTOGeoJSON(res);
      this.initMap();
    });
  }


}
