import { Component, OnInit } from '@angular/core';
import 'node_modules/leaflet-choropleth/dist/choropleth.js'
import { StoreService } from '../store.service';
import * as $ from 'jquery';
import Chart from 'chart.js';

declare let L;

@Component({
  selector: 'app-viz',
  templateUrl: './viz.component.html',
  styleUrls: ['./viz.component.scss']
})
export class VizComponent implements OnInit {

  geojsonData: any;
  myChart: any;
  map: any;
  year: number;
  week: number;
  median: number;
  medianPer: number;
  lineTrend: any;
  selectedDensity: any;
  selectedCoords: any;
  geojsonLayer: any;
  showLineChart = false;
  max = 0;

  constructor(private store: StoreService) {

  }

  convertTOGeoJSON(polygons) {

    console.log(polygons)
    let features = [];

    for (const [key, value] of Object.entries(polygons.data)) {
      let polygon = value;

      let properties = { density: polygon.fire_risk };
      let geometry = {
        "type": "Polygon",
        "coordinates": [[[polygon.coordinate_sw[1], polygon.coordinate_sw[0]], [polygon.coordinate_se[1], polygon.coordinate_se[0]], [polygon.coordinate_ne[1], polygon.coordinate_ne[0]], [polygon.coordinate_nw[1], polygon.coordinate_nw[0]]]]
      }

      var labels = [];
      let data = [];

      for (const [key, value] of Object.entries(polygon.fire_causes)) {
        labels.push(key);
        data.push(value)
      }


      let fireCauses = {
        labels,
        data
      }

      features.push({
        "type": "Feature",
        properties,
        geometry,
        fireCauses,
        ...polygon
      });
    }

    return {
      "type": "FeatureCollection",
      "features": features
    }

  }


  ngOnInit() {
    this.map = L.map('mapid').setView([35.00118, -117.359296], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      minZoom: 3
    }).addTo(this.map);

    this.store.get('/predict-wildfire').subscribe((res) => {

      let dateControl = document.querySelector('input[type="date"]');
      dateControl.value = res.date.replaceAll("/", "-");

      this.geojsonData = this.convertTOGeoJSON(res);
      this.initMap();
    });
  }

  initMap() {
    var map = this.map;
    if(this.geojsonLayer) {
      this.map.removeLayer(this.geojsonLayer);
    }

    var info = L.control();

    info.onAdd = function(map) {
      $(".info").remove();
      this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
      this.update();
      return this._div;
    };

    // method that we will use to update the control based on feature properties passed
    info.update = function(props) {
      this._div.innerHTML = '<h6>Forest Fire Likelihood</h6><div class="legend"><i style="background:#28a745;opacity: 0.4"></i>&nbsp;&nbsp;Low Risk<br><i style="background:#dc3545"></i>&nbsp;&nbsp;High Risk<br></div>';
    };

    info.addTo(map);


    this.geojsonLayer = L.choropleth(this.geojsonData, {
      valueProperty: 'density', // which property in the features to use
      scale: ['#28a745', '#dc3545'], // chroma.js scale - include as many as you like
      mode: 'q', // q for quantile, e for equidistant, k for k-means
      style: {
        color: '#fff', // border color
        weight: 0,
        fillOpacity: .9
      },
      onEachFeature: ((feature, layer) => {
        layer.on({
          mouseover: ((e) => {
            var layer = e.target;

            var popup = L.popup()
            .setLatLng(e.latlng)
            .setContent('<p>Coordinates:' + e.latlng + '</p><p>Average fire size: ' + feature.avg_fire_size + '</p>')
            .openOn(map);

            layer.setStyle({
              weight: 2,
              fillOpacity: 1
            });

            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
              layer.bringToFront();
            }
          }),
          mouseout: ((e) => {
            this.geojsonLayer.resetStyle(e.target);
          }),
          click: ((e) => {
            this.showLineChart = false;
            this.selectedDensity = feature.properties.density;
            this.selectedCoords = e.latlng;
            this.lineTrend = feature.fireCauses;

            setTimeout(() => {
              this.showLineChart = true;
              $('html, body').animate({
                scrollTop: $("#scroll-to").offset().top
              }, 1000);
            }, 300);
          })
        });
      })
    }).addTo(map)

    if (this.myChart == undefined) {
      info.update();
    }


    this.drawDoughnut();
  }

  drawDoughnut() {
    $("canvas#doughchartContainer").remove();

    $("div.chartreport").append('<canvas id="doughchartContainer" style="height: 170px; width: 210px;"></canvas>');

    var ctx = $("#doughchartContainer");
    let per = this.medianPer;
    let doughColor = '#ffc107';

    if (per < 25) {
      doughColor = "#28a745";
    }
    else if (per > 70) {
      doughColor = "#dc3545";
    }

    if (this.myChart != undefined) {
      this.myChart.destroy();
    }

    this.myChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Median', 'Max'],
        datasets: [{
          label: '# of Votes',
          data: [this.median, this.max],
          backgroundColor: [
            doughColor
          ],
          //cutoutPercentage : ,
          borderWidth: 5
        }]
      }
    });
  }

  submitQuery(e) {
    e.preventDefault();

    const dateControl = document.querySelector('input[type="date"]');
    const date= dateControl.value.replaceAll("-", "/");
    this.store.post(`/predict-wildfire?predict_date=${date}`).subscribe((res) => {

      this.geojsonData = this.convertTOGeoJSON(res);
      this.initMap();
    });
  }


}
