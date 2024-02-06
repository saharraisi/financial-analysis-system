var es2;

async function chartComponent (stock_symbol=null) {
  if (stock_symbol){
    var response = await fetch(`http://127.0.0.1:8000/data/stock-data/?stock_symbol=${stock_symbol}`)

  }
  else{
    var response = await fetch(`http://127.0.0.1:8000/data/stock-data/`)
  }
  
  const dataRes = await response.json()
  console.log(dataRes);
    const options = {
        series: [{
          name: 'candle',
          data : dataRes.map(item => (
            {
              x : item.timestamp,
              y : [item.opening_price , item.closing_price , item.high , item.low]
            }
          ))
        }],
        chart: {
          height: 600,
          type: 'candlestick',
        },
      
        annotations: {
          xaxis: [
            {
              x: 'Oct 06 14:00',
              borderColor: '#00E396',
              label: {
                borderColor: '#00E396',
                style: {
                  fontSize: '12px',
                  color: '#fff',
                  background: '#00E396'
                },
                orientation: 'horizontal',
                offsetY: 7,
                text: 'Annotation Test'
              }
            }
          ]
        },
        tooltip: {
          enabled: true,
        },
        xaxis: {
          type: 'category',
          labels: {
            formatter: function(val) {
              return dayjs(val).format('MMM DD HH:mm')
            }
          }
        },
        yaxis: {
          tooltip: {
            enabled: true
          }
        }
        };
        document.querySelector('#area-chart').innerHTML =''
      const areaChart = new ApexCharts(document.querySelector('#area-chart'),options);
      areaChart.render();
      if (stock_symbol) {
        if(es2){
          es2.close()
        }
        var uri = '/stocks/' + encodeURIComponent(stock_symbol) + '/events/';
          var es2 = new EventSource(uri);


          es2.onopen = function () {
              console.log('*** stock connected');

          };

          es2.onerror = function () {
              console.log('*** stock connection lost, reconnecting...');
          };

          es2.addEventListener('stock_updated', function (e) {
              const data = JSON.parse(e.data)

              console.log("append data")

              var newData = [
                {
                  x : data.timestamp,
                  y : [data.opening_price , data.closing_price , data.high , data.low]
                }
            ];

              areaChart.appendData([{
                data: newData
            }]);
          });
      }
}

export default chartComponent;