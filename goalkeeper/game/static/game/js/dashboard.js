// CALL API`S SKETCH

/**
 * 1. Consumir dados da api...quantos endpoints e chamadas?
 * 2. Atualizar view passando os dados
 * 3. Repetir req`s em intervalo
 */

/**
 * BASE URL:
 */

let url = window.location.href
let arr = url.split("/");
const api = arr[0] + "//" + arr[2] + "/api/results/";
let labels = ["Partidas", "Acertos", "Erros"];
let myChart = {};

/**
 * FILTER KICKER:
 */

function select_kicker_to_filter_phase(kicker_id) {

    if(kicker_id === ""){
        disableFields();
    } else {
        $("#fase").html('<option value="">Loading...</option>');
        $.ajax({
            type: "GET",
            url: "/game/select_kicker_to_filter_phase",
            dataType: "json",
            data: {'kicker':kicker_id},
            success: function(retorno) {
                $("#fase, #filtroBtn").removeAttr('disabled');
                $("#fase").empty();
                $.each(retorno[0], function(i, item){
                    $("#fase").append('<option value="'+item.phase+'">'+item.phase+'</option>');
                });
            },
            error: function(erro) {
                console.log('Ops, we have a problem!');
            }
        });
    }
}

function disableFields(){
    $("#fase").html('<option value="">Primeiro escolha um adversário</option>');
    $('#fase, #filtroBtn').attr('disabled', 'disabled');
}

/**
 * CRIA GRÁFICO:
 */

function createChart(metrics){

    // Habilita a visualização de todos os gráficos
    $('canvas').removeAttr('style');

    myChart = new Chart($('#barChart'), {
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
    flag ? $('#preloader').css('display', 'flex') : $('#preloader').css('display', 'none');
}

function filtrar(){
    /**
     * Filtrar deve enviar a requisição, receber o retorno
     * e carregar novamente o gráfico com os dados
     *
     */

    let params = {
        adversario: $('#adversario').val(),
        fase: $('#fase').val()
    };

    myChart.destroy();
    loadCharts(params);
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

function loadCharts(params){

     loaderManager(true);

     let endpoint = '';

     if(params){
         endpoint = `?kicker=${params.adversario}&phase=${params.fase}`;
     }

     fetch(api + endpoint)
         .then(res => res.json())
         .then((data)=> {
             console.log('DATA: ', data);
             let results = resultMetrics(data);

             let chartInfo = {
                 totalGames: data.length,
                 wins: results.corrects,
                 fail: results.fails
             };

             loaderManager(false);

             createChart(chartInfo);
         })

         .catch(err => console.log('Algo deu errado ', err))
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
     if(title === 'Goalkeeper game'){
         labels = ["Games", "Hits", "Errors"]
     }

     // Inicializa os tooltip's bootstrap.
     $('label i').tooltip();

     // Inicializa gráfico
     loadCharts();
     //updateData(4000);
 });