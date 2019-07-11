// CALL API`S SKETCH

/**
 * 1. Consumir dados da api...quantos endpoints e chamadas?
 * 2. Atualizar view passando os dados
 * 3. Repetir req`s em intervalo
 */

/**
 * BASE URL:
 */

var url = window.location.href
var arr = url.split("/");
const api = arr[0] + "//" + arr[2] + "/api/results/";
let labels = ["Partidas", "Acertos", "Erros"];

/**
 * FILTER KICKER:
 */

function select_kicker_to_filter_phase(kicker_id) {
    $("#fase").html('<option value="">Loading...</option>');
    $.ajax({
        type: "GET",
        url: "/game/select_kicker_to_filter_phase",
        dataType: "json",
        data: {'kicker':kicker_id},
        success: function(retorno) {
            $("#fase").empty();
            $.each(retorno[0], function(i, item){
                $("#fase").append('<option value="'+item.pk+'">'+item.phase+'</option>');
            });
        },
        error: function(erro) {
            alert('Ops, we have a problem!');
        }
    });
}

/**
 * CRIA GRÁFICO:
 */

function createChart(metrics){
    // Habilita a visualização de todos os gráficos
    $('canvas').removeAttr('style');
    let myChart = new Chart($('#barChart'), {
        type: 'horizontalBar',
        data: {
            labels: labels,

            datasets: [{
                label: 'Total',
                data: [metrics.totalGames, metrics.wins, metrics.fail],
                backgroundColor: [
                    'rgba(0, 102,153, .6)',
                    'rgba(52, 168, 83, .6)',
                    'rgba(153, 0, 0, .6)',
                ],
                borderColor: [
                    '#069',
                    '#34a853',
                    '#900',
                ],
                borderWidth: 2
            }]
        },
        options: {
            layout: {
              padding: {
                  left: 10,
                  right: 30,
                  top: 10,
                  bottom: 10
              }
            },
            scales: {
                xAxes: [{

                    barThickness: 4,
                    maxBarThickness: 8,
                    minBarLength: 0,
                    gridLines: {
                        offsetGridLines: true
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }]
            }
        }
    });
}

/**
 *  Controla a exibição do preloader
 */

function loaderManager(flag){
    console.log($('#preloader'));
    console.log('loaderManager()');
    if(flag){
        $('#preloader').css('display', 'flex')
    } else {
        $('#preloader').css('display', 'none');
    }
}


function filtrar(){
    let params = {
        adversario: $('#adversario').val(),
        fase: $('#fase').val()
    };
    console.log(params);
    loadCharts();
}

 function resultMetrics(arr){
     let corrects = 0;
     let fails = 0;

     arr.map((shot) => {
         if(shot.correct){
             corrects++
         } else {
             fails++
         }
     });

     return {
         corrects: corrects,
         fails: fails
     }
 }

function loadCharts(labels){
     loaderManager(true);
     fetch(api)
         .then(res => res.json())
         .then((data)=> {
             let results = resultMetrics(data);
             let chartInfo = {
                 totalGames: data.length,
                 wins: results.corrects,
                 fail: results.fails
             };

             // ATUALIZA QUANTIDADE DE JOGOS
            //$('#totalGames').html(chartInfo.totalGames);

             console.log('resultMetrics', results);
             console.log('chartInfo: ', chartInfo);
             console.log('Loading: False');

             loaderManager(false);
             createChart(chartInfo);
         })
         .catch(err => alert('Algo deu errado ', err))
 }


/**
 * Atualiza dados para determinado intervalo
 * Valor default definido para 20s


function updateData(interval = 20000){
    console.log('updateData()');
    setInterval(loadCharts(), interval);
}*/

$(document).ready(() => {
     loaderManager(false);

     let title = $('title').html();

     // Verifica se a tradução para inglês foi ativada
     if(title == 'Goalkeeper game'){
         labels = ["Games", "Hits", "Errors"]
     }

    console.log(labels);
     // Inicializa os tooltip's bootstrap.
     $('label i').tooltip();

     // Inicializa gráfico
     loadCharts();
     //updateData(4000);
 });