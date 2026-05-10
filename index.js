document.querySelector('fieldset #total').checked = true;

var totalScale;
var homeAwayScale;
var heatmapScale;
var cogScale = d3
  .scaleLinear()
  .domain([3.9, 4.5, 6.1])
  .range(['white', '#003DA5', 'black']);
//   .range(['white', '#C50C26', 'black']);

const allInnings = Array.from({ length: 33 }, (_, i) => i + 1);
var totalScaleMax;
var homeAwayScaleMax;
var allScoresTotal;
var allScoresHomeAway;
var selVal;
var offData;
var defData;
var data;
var toggleVal;

d3.csv('offense.csv').then(function (csv) {
  offData = csv;
});

d3.csv('defense.csv').then(function (csv) {
  defData = csv;
});

function populate(csv) {
  toggleVal = document.querySelector('input#example').checked;
  var filename = !toggleVal ? 'offense.csv' : 'defense.csv';
  d3.select('#heatmap-table tbody').html('');
  d3.csv(filename)
    .then(function (csv) {
      selVal = document.querySelector('input[name="drone"]:checked').value;

      var totalData = csv
        .filter(d => d.status == 'Total')
        .sort(function (a, b) {
          return a['center_of_gravity'] < b['center_of_gravity'] ? 1 : -1;
        });
      allScoresTotal = [];

      for (let i = 0; i < totalData.length; i++) {
        allInnings.forEach(function (inning) {
          allScoresTotal.push(totalData[i][inning]);
        });
      }
      var midColor = !!toggleVal ? '#C50C26' : '#097969';
      totalScaleMax = Math.max(...allScoresTotal);
      totalScale = d3
        .scaleLinear()
        .domain([0, totalScaleMax / 2, totalScaleMax])
        .range(['white', midColor, 'black']);

      var homeAwayData = csv
        .filter(d => d.status == 'Away' || d.status == 'Home')
        .sort(function (a, b) {
          return a['center_of_gravity'] < b['center_of_gravity'] ? 1 : -1;
        });
      allScoresHomeAway = [];

      for (let i = 0; i < homeAwayData.length; i++) {
        allInnings.forEach(function (inning) {
          allScoresHomeAway.push(homeAwayData[i][inning]);
        });
      }
      var midColor = !!toggleVal ? '#C50C26' : '#097969';
      homeAwayScaleMax = Math.max(...allScoresHomeAway);
      homeAwayScale = d3
        .scaleLinear()
        .domain([0, homeAwayScaleMax / 2, homeAwayScaleMax])
        .range(['white', midColor, 'black']);

      var data = csv
        .filter(d => d.status == selVal)
        .sort(function (a, b) {
          return a['center_of_gravity'] < b['center_of_gravity'] ? 1 : -1;
        });

      heatmapScale = selVal === 'Total' ? totalScale : homeAwayScale;

      var tbody = d3.select('#heatmap-table tbody');

      tbody
        .selectAll('tr')
        .data(data)
        .enter()
        .append('tr')
        .attr('class', d => d['code'])
        .html(function (x) {
          return `
          <td class='rank'>${data.indexOf(x) + 1}.</td>
          <td class='team-name'>
      <div style='display:flex;'><span class='logo-holder' style='background-color:#${x['hex_bg']};'><img alt='${x['team_name']} cap logo' style='width:100%;' src='logos/${x['code']}.png'/></span><span class='team-name' style='background-color:#${x['hex_bg']};color:#${x['hex_text']};${!!x['hex_ol'] ? '-webkit-text-stroke:.4px #' + x['hex_ol'] + ';' : ''}'><span class='name-inner'>${x['team_name']}<br/><small style='font-size:10pt'>${numeral(x['runs']).format('0,0')} runs in ${numeral(x['1p']).format('0,0')} games (${x['w']}-${x['l']})</small></span></div>
      </td>
      <td class='center-of-gravity ${x['code']}'>${numeral(x['center_of_gravity']).format('0[.]00')}</td>
      <td class="inning inning-1 ${x['code']}">${!!x['1'] ? numeral(x['1']).format('0,0') : ''}</td>
      <td class="inning inning-2 ${x['code']}">${!!x['2'] ? numeral(x['2']).format('0,0') : ''}</td>
      <td class="inning inning-3 ${x['code']}">${!!x['3'] ? numeral(x['3']).format('0,0') : ''}</td>
      <td class="inning inning-4 ${x['code']}">${!!x['4'] ? numeral(x['4']).format('0,0') : ''}</td>
      <td class="inning inning-5 ${x['code']}">${!!x['5'] ? numeral(x['5']).format('0,0') : ''}</td>
      <td class="inning inning-6 ${x['code']}">${!!x['6'] ? numeral(x['6']).format('0,0') : ''}</td>
      <td class="inning inning-7 ${x['code']}">${!!x['7'] ? numeral(x['7']).format('0,0') : ''}</td>
      <td class="inning inning-8 ${x['code']}">${!!x['8'] ? numeral(x['8']).format('0,0') : ''}</td>
      <td class="inning inning-9 ${x['code']}">${!!x['9'] ? numeral(x['9']).format('0,0') : ''}</td>
      <td class="inning inning-10 ${x['code']}">${!!x['10'] ? numeral(x['10']).format('0,0') : ''}</td>
      <td class="inning inning-11 ${x['code']}">${!!x['11'] ? numeral(x['11']).format('0,0') : ''}</td>
      <td class="inning inning-12 ${x['code']}">${!!x['12'] ? numeral(x['12']).format('0,0') : ''}</td>
      <td class="inning inning-13 ${x['code']}">${!!x['13'] ? numeral(x['13']).format('0,0') : ''}</td>
      <td class="inning inning-x ${x['code']}">${!!x['x'] ? numeral(x['x']).format('0,0') : ''}</td>`;
        });
      return data;
    })
    .then(function (data) {
      d3.selectAll('td.inning')
        .style('background-color', function (inn) {
          return heatmapScale(this.innerText);
        })
        .style('color', function (inn) {
          return this.innerText > totalScale.domain()[1] * 0.75
            ? 'white'
            : 'black';
        });

      d3.selectAll('td.center-of-gravity')
        .style('background-color', function (inn) {
          return cogScale(this.innerText);
        })
        .style('color', function (inn) {
          return this.innerText < cogScale.domain()[1] ? 'black' : 'white';
        });

      data.forEach(function (d) {
        var cog = d['center_of_gravity'];
        var team = d['code'];
        var floor = Math.floor(cog);

        d3.select(`.inning-${floor}.${team}`)
          .data([d])
          .append('div')
          .attr('class', 'triangle')
          .style('position', 'absolute')
          .style('bottom', '0')
          .style('left', function (d) {
            var pct =
              d['center_of_gravity'] - Math.floor(d['center_of_gravity']);

            var pos = this.parentElement.getBoundingClientRect().width * pct;
            return pos - 5 + 'px';
          })
          //   .style('left', function (d) {
          //     var pct =
          //       d['center_of_gravity'] - Math.floor(d['center_of_gravity']);
          //     // var coeff = this.parentElement.getBoundingClientRect().width * 0.5;
          //     var coeff = 0;

          //     if (pct <= 0.5) {
          //       var pos = this.parentElement.getBoundingClientRect().width * pct;
          //     } else {
          //       var pos =
          //         this.parentElement.nextElementSibling.getBoundingClientRect()
          //           .width * pct;
          //     }
          //     return coeff + pos - 5 + 'px';
          //   })
          // .style('background-color', '#FFC425')
          .style('background-color', '#FFC425');

        // .style('z-index', 5);
      });
    });
}
populate();

d3.select('fieldset').on('change', populate);
