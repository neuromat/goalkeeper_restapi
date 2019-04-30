/**************************************************************************************/
//  Module written by scaroni <renato.scaroni@gmail.com>
//  Rewrited by Josi Perez <josiperez.neuromat@gmail.com>, keeping the original code in comment
//
/**************************************************************************************/
using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;
//using System.Text;                       //to use StringBuilder
//using UnityEngine.EventSystems;          //170308 to know which was last button clicked - did not work ...


//170623 only valids for Windows (to call inpout32.dll)
#if UNITY_STANDALONE_WIN  || UNITY_EDITOR_WIN
using System.Runtime.InteropServices;    //[DLLimport para envio ao EEG pela porta paralela
#endif
using System;                            //180201 para declara Byte[0] e buildar para linux
using System.IO.Ports;                   //180104 to use serialPort; works in linux and mac?



//------------------------------------------------------------------------------------
public class RandomEvent            //Josi: result matrix to save experiment results
{
    public int resultInt;           //defense waited: 0, 1 or 2 (if choices=3), or 1,2 (if choices=2)
    public char ehRandom;           //170215 JG: random play? Y, or n; in any other module it is "n" (AQ/AR is random...)
    public int optionChosenInt;     //defense choosed by player; numeric format
    public string result;           //defense waited in string format: dir, esq, cen
    public string optionChosen;     //defense choosed  in string format: dir, esq, cen
    public bool correct;            //correct (true) or no (false)
    public string state;
    public float time;
    public float decisionTime;       //170113 tempo de decisao
    public float pauseTime;          //170919 tempo em pausa (do Play/Pause) nesta jogada
    public float realTime;           //180418 tempo corrido (para analisar com os marcadores)
}


//------------------------------------------------------------------------------------
public class UIManager : MonoBehaviour
{
    public Text eventsLog;
    public GKAnimController[] gkAnim;
    public int eventWindow = 10;
    public float successRate = 0;
    public ScoreMonitor scoreMonitor;
    public GameObject btnsAndQuestion;

    //visual and audio animations for player hit/error
    public Animator anim321;         //170108 changed to Animator by Thom
    public Animator pegoal;          //Defendeu 
                                     //recognize all idioms and keep just one after player to select language interface
    public Animator pegoalEnUs;      //171031 Defended! 
    public Animator pegoalPtBr;      //171031 defendeu!
    public Animator pegoalEsEs;      //171222 defendió!

    public Animator perdeu;          //170102 anim Thom; "perdeeu..." para fazer par com "defendeu!!"
                                     //recognize all idioms and keep just one after player to select language interface
    public Animator perdeuEnUs;      //171031 Lost... 
    public Animator perdeuPtBr;      //171031 Perdeu... sendo "..." um único caracter
    public Animator perdeuEsEs;      //171031 Perdió... 

    public AudioSource cheer;        //som para o defendeu
    public AudioSource cheerShort;   //170315 som para o defendeu short
    public AudioSource lament;       //som para o perdeu
    public AudioSource lamentShort;  //som para o perdeu short

    public AudioSource sound321;     //170825 to synchronyze with 321animation
    public AudioSource sound321ptbr; //171031 voice talking pt-br
    public AudioSource sound321enus; //171031 voice talking en-us
    public AudioSource sound321eses; //171222 voice talking es-es
    private string locale;           //171031 save locale selected

    public Sprite neutralUISprite;
    public Sprite[] rightUISprite;
    public Sprite[] wrongUISprite;

    public List<GameObject> optBtns;

    public float decisionTimeA;      //170113 tempo que o user fica pensando o que fazer
    public float decisionTimeB;      //170113 tempo que o user fica pensando o que fazer
    public float movementTimeA;      //170309 tempo de movimento: desde que aparecem as setas de defesa até que player seleciona uma delas

    public int eventCount = 0;       //170106 para ser acessado no gameFlow.onAnimationEnded
    public bool BtwnLvls = false;

    private ProbCalculator probs;
    private GameFlowManager gameFlow;

    public int success = 0;
	// @ale
	// successTotal : somatorio de todos os sucessos
	public int successTotal = 0;
    public Text placar;              //muda do tipo string para StringBuilder (reserva espaco de antemao, sem garbage collection
    //public Text placarFirstScreen;   //170103 Base Memoria //170125 basta o placar.text

    public GameObject setaEsq;      //mainScene/gameScene/GameUICanvas/bmIndicaChute/chutaEsq
    public GameObject setaDir;      //mainScene/gameScene/GameUICanvas/bmIndicaChute/chutaDir
    public GameObject setaCen;      //mainScene/gameScene/GameUICanvas/bmIndicaChute/chutaCen

    //public int jogadasFirstScreen = 0;       //170104: MD numero de tentativas na firstScreen
    //public int acertosFirstScreen = 0;       //170102: MD: necessario acertar 3x a sequ para avancar para MD (JG fase 3)
    public int teclaMDinput;        //170125 para avancar ou nao no idx da sequencia; se o goleiro errou não avanca ate acertar

    /* ale comment
    public GameObject mdFrameIndicaChute1;   //170102
    public GameObject mdFrameIndicaChute2;   //170102
    public GameObject mdFrameIndicaChute3;   //170102
    public GameObject mdFrameIndicaChute4;   //170102

    public List<GameObject> mdSequChute1;   //170102
    public List<GameObject> mdSequChute2;   //170102
    public List<GameObject> mdSequChute3;   //170102
    public List<GameObject> mdSequChute4;   //170102
    */

    public GameObject mdMsg;                 //170124 Jogo da memoria: aperte uma tecla quando pronto
    public GameObject mostrarSequ;           //170124 Jogo da memoria: botao mostrar sequencia (estará escondida)
    public GameObject jogar;                 //170124 Jogo da memoria: botao jogar
    public GameObject menuJogos;             //170311 JM: botao Menu Jogos, para desistir do EXIT
    public GameObject btnExit;               //170313 JM: botao EXIT de todos os jogos; objeto para mostrar/nao mostrar o Exit

    /* ale comment
    public bool aguardandoTeclaBMcomTempo = false;  //161229 
    public bool aguardandoTeclaMemoria = false;     //170124
    public bool aguardandoTeclaPosRelax = false;    //170222 descanso dos pacientes LPB
    */

    public bool animCountDown = false;        //170111 para determinar continuacao ao fim das animacoes anim321, pegoal e perdeu
    public bool animResult = false;           //170111 para determinar continuacao ao fim das animacoes anim321, pegoal e perdeu

    private List<RandomEvent> _events = new List<RandomEvent>();
    public List<RandomEvent> _eventsFirstScreen = new List<RandomEvent>();  //170108 salvar experimentos da fase MD testes de memoria

    public GameObject buttonPlay;             //170906 botões Play/Pause
    public GameObject buttonPause;            //170906
    public bool pausePressed;                 //170906
    //public GameObject mdButtonPlay;           //170912 botões Play/Pause no Jogo da Memória
    //public GameObject mdButtonPause;          //170912

    private LocalizationManager translate;    //171010 trazer script das rotinas de translation
    //public SerialPort serialp = null;         //180104 define a serial port to send markers to EEG, if necessary
    //public Byte[] data = { (Byte)0 };         //180104 to send data to the serial port; used also on gameFlow
    public int diagSerial;                    //180108 serial diagnostic


    //170626
    //public int timeBetweenMarkers = 100000000;        //QG para dar um tempico entre envios à paralela;
                                                      //public  int  timeBetweenMarkersSerial = 10000000; //180129 10^7 time between sendMarkersToSerial on BrainProductsEEG connected to TriggerBox
                                                      //       can see markers on vmrk and sobreposition on recorder screen at the moment
                                                      //public  int  timeBetweenMarkersSerial = 100000;   //180131 10^5, com samplrate 5000, samplInterval 200; ok!
                                                      //public  int  timeBetweenMarkersSerial = 10000;    //180131 10^4, com samplrate 5000, samplInterval 200; ok!
                                                      //public  int  timeBetweenMarkersSerial = 100;      //180131 10^2, com samplrate 5000, samplInterval 200; perdeu 1 em 48mkr...
    //public int timeBetweenMarkersSerial = 100000;      //180131

    public bool userAbandonModule = false;              //180326 not more possible to decide considering the numPlays (if gamer hits before, it goes out)

    //public GameObject attentionPoint;                   //180410 in the middle screen to fix player attention (EEG experiments)
    public float[] keyboardTimeMarkers;                 //180418 markers from experimenter (keyboard F1 until F9)


    //170623 DLLs inpout32.dll from http://highrez.co.uk/
    //171017 DLls inpoutx64.dll
	#if UNITY_STANDALONE_WIN || UNITY_EDITOR_WIN
    [DllImport("inpout32")]
    private static extern UInt32 IsInpOutDriverOpen();

    [DllImport("inpout32")]
    private static extern void Out32(short PortAddress, short Data);

    [DllImport("inpoutx64", EntryPoint = "IsInpOutDriverOpen")]
    private static extern UInt32 IsInpOutDriverOpen_x64();

    [DllImport("inpoutx64", EntryPoint = "Out32")]
    private static extern void Out32_x64(short PortAddress, short Data);
	#endif

    public delegate void AnimationEnded();
    public static event AnimationEnded OnAnimationEnded;

    public delegate void AnimationStarted();
    public static event AnimationStarted OnAnimationStarted;


    public List<RandomEvent> events
    {
        get
        {
            return _events;
        }
    }

    static private UIManager _instance;
    static public UIManager instance
    {
        get
        {
            if (_instance == null)
            {
                _instance = GameObject.Find("UIManager").GetComponent<UIManager>();
            }

            return _instance;
        }
    }

 


    //--------------------------------------------------------------------------------------------------------
    //Josi: arquiva os dados do experimento; verifica se acerto ou erro;
    //      esta função é tbem chamada no onClick do mainScene/.../Pergunta/<em cada uma das direcoes de chute>
    public void BtnActionGetEvent(string input)
    {
        
        //170915 para impedir o click se está em modo pausa
        if (!pausePressed)
        {
            btnsAndQuestion.SetActive(false);  //170112 importante manter aqui e nao noUpdate, quando perderah a espera de teclas

            //170920 o PlayPause só vai valer entre o mostrar a seta e o user selecionar;
            //       interromper fora desse gap é só para arranjar problema com as sobras de animacao na tela
            buttonPlay.SetActive(false);
            buttonPause.SetActive(false);


            //170320 trocado para ca para tentar isolar a diferenca entre o tempo total de jogo e o tempo de movimento menos animacoes
            RandomEvent eLog = new RandomEvent();

            //170309 acertar tempo no JG descontando o tempo das animacoes e o tempo de relax se houver (senao valem zero)
            //eLog.time = Time.realtimeSinceStartup - movementTimeA -  (gameFlow.endRelaxTime - gameFlow.startRelaxTime);
            //170413
            //estava dando erro de tempo negativo no move logo após a tela de relax; nao entendi porque - mudei a estrategia
            //170919 descontar os possiveis tempos de pausa do Play/Pause
            //eLog.time = Time.realtimeSinceStartup - movementTimeA;
            eLog.time = Time.realtimeSinceStartup - movementTimeA - gameFlow.otherPausesTime;
			Debug.Log("UIManager.cs --> f:BtnActionGetEvent --> eLog.Time = "+eLog.time);
            eLog.pauseTime = gameFlow.otherPausesTime;
            eLog.realTime = Time.realtimeSinceStartup - gameFlow.startSessionTime;    //180418 to accomplish marker time by keyboard
			Debug.Log("UIManager.cs --> f:BtnActionGetEvent --> eLog.realTime = " + eLog.realTime);


            //170919
            gameFlow.otherPausesTotalTime = gameFlow.otherPausesTotalTime + gameFlow.otherPausesTime;
            gameFlow.otherPausesTime = 0;

            //gameFlow.endRelaxTime = 0.0f;
            //gameFlow.startRelaxTime = 0.0f;
            

            //170216
            int e = probs.GetEvent(teclaMDinput);  //170130 teclaMDinput param para nao precisar instanciar uiManager no probCalc

            string dirEsq = System.String.Empty;    //170110 Use System.String.Empty instead of "" when dealing with lots of strings;

            if (OnAnimationStarted != null)
                OnAnimationStarted();
            btnsAndQuestion.SetActive(false);
            eLog.decisionTime = eLog.time;     //170113: tempo que o jogador está pensando; no BM equivale ao TMovimento
                                               /* ale comment } */

            
            eLog.resultInt = e;
            if (e == 0)
            { //esquerda
                dirEsq = "esquerda";
            }
            else if (e == 1)
            {
                dirEsq = "centro";
            }
            else
            {
                dirEsq = "direita";
            }
            
			Debug.Log("UIManager.cs --> f:BtnActionGetEvent --> dirEsq = " + dirEsq);

            eLog.result = dirEsq;
            eLog.optionChosen = input;

			Debug.Log("UIManager.cs --> f:BtnActionGetEvent --> eLog.optionChosen = " + eLog.optionChosen);

            if (input.Equals(dirEsq))
            {
                eLog.correct = true;
                success++;
				successTotal++;
            }
            else
            {
                eLog.correct = false;
            }

			Debug.Log("UIManager.cs --> f:BtnActionGetEvent --> success = " + success);
			Debug.Log ("UIManager.cs --> f:BtnActionGetEvent --> successTotal = " + successTotal);

            
            if (eLog.correct)
            {
                ++gameFlow.minHitsInSequence;
            }
            else
            {
                gameFlow.minHitsInSequence = 0;
            }

			Debug.Log ("UIManager.cs --> f:BtnActionGetEvent --> minHitsInSequence = " + gameFlow.minHitsInSequence);

            //170215 gravar se a jogada, no JG, é randomizada ou não; nos demais é sempre n
            if (PlayerPrefs.GetInt("gameSelected") != 2)
            {
                eLog.ehRandom = 'n';
				Debug.Log ("UIManager.cs --> f:BtnActionGetEvent --> eLog.ehRandom = " + eLog.ehRandom);
            }
            else
            {
                if (probs.ehRandomKick)
                {
                    eLog.ehRandom = 'Y';
                }
                else
                {
                    eLog.ehRandom = 'n';
                }
            }


            int targetAnim = probs.GetCurrMachineIndex();
			Debug.Log ("UIManager.cs --> f:BtnActionGetEvent --> targetAnim = " + targetAnim);
			Debug.Log ("UIManager.cs --> f:BtnActionGetEvent --> gkAnim.Length = " + gkAnim.Length);

           
            if ((targetAnim >= gkAnim.Length) || (gameFlow.jogarMDfase3 && ((PlayerPrefs.GetInt("gameSelected") == 3) || (PlayerPrefs.GetInt("gameSelected") == 5))))
            {  //170125 MD ou Memoria usam a fase3 do JG
                targetAnim = gkAnim.Length - 1;
            }
            

            if (input == "esquerda")
            {
                eLog.optionChosenInt = 0;
                if (!gameFlow.firstScreen)
                {     //170102 nao eh MD primeira tela, onde nao existe o gk, apenas uma tela limpa
                    if (eLog.correct)
                    {
                        gkAnim[targetAnim].Play("esq", dirEsq.Substring(0, 3));
                    }
                    else
                    {
                        gkAnim[targetAnim].Play("esq_goal", dirEsq.Substring(0, 3) + "_goal");
                    }
                }
            }
            else if (input == "direita")
            {
                eLog.optionChosenInt = 2;
                if (!gameFlow.firstScreen)
                {     //170102 nao eh MD primeira tela, onde nao existe o gk, apenas uma tela limpa
                    if (eLog.correct)
                    {
                        gkAnim[targetAnim].Play("dir", dirEsq.Substring(0, 3));
                    }
                    else
                    {
                        gkAnim[targetAnim].Play("dir_goal", dirEsq.Substring(0, 3) + "_goal");
                    }
                }
            }
            else
            {
                eLog.optionChosenInt = 1;
                if (!gameFlow.firstScreen)
                {  //170102 nao eh MD primeira tela
                    if (eLog.correct)
                    {
                        gkAnim[targetAnim].Play("cen", dirEsq.Substring(0, 3));
                    }
                    else
                    {
                        gkAnim[targetAnim].Play("cen_goal", dirEsq.Substring(0, 3) + "_goal");
                    }
                }
            }


            _events.Add(eLog);

            eventCount++;

			Debug.Log ("UIManager.cs --> f:BtnActionGetEvent --> eventCount = " + eventCount);
            

            //============================================================

            int successCountInWindow = 0;
            for (int i = 0; i < eventWindow; i++)
            {
                if (eventCount - 1 - i < 0)
                {
					Debug.Log ("UIManager.cs --> f:BtnActionGetEvent --> eventWindow = " + eventWindow);
                    break;
                }
                if (_events[eventCount - 1 - i].correct)
                {
                    successCountInWindow++;
					Debug.Log ("UIManager.cs --> f:BtnActionGetEvent --> successCountInWindow = " + successCountInWindow);
                }
            }

            successRate = ((float)successCountInWindow) / ((float)eventWindow);
			Debug.Log ("UIManager.cs --> f:BtnActionGetEvent --> successRate = " + successRate);

            //#####################################################################################
        }
    }



    //--------------------------------------------------------------------------------------------------------
    //Josi: ao trocar de nivel, envia os dados do experimento para arquivo local (a thread se encarrega de enviar o arquivo para o server)
    //170109 nasce jogoJogado como parametro
    public void SendEventsToServer(int gameSelected)
    {
		Debug.Log ("UIManager.cs ----------------- f:SendEventsToServer -----------------------------------------");



        if ((_events != null && eventCount > 0) || (_eventsFirstScreen.Count > 0))
        {   //170108 pode estar na mdFirstScreen que acumula _events dos testes de memoria (eventCount)  ou estar no JM 5 na firstScreen
            //Josi: era assim
            //ServerOperations.instance.RegisterPlay (GameFlowManager.instance, probs.CurrentMachineID(), success, successRate, _events);
            //Josi: 161205: inclui o parametro do modo de operacao do jogo: por sequOtima ou por arvore
            //              inclui saber se o nivel foi interrompido ou nao

            if (PlayerInfo.agree)
            {   //170830 if player agree to give his results, prepare to write file results
                //       else... lost the data (even without identification... that occurs in NES)

                //170316 tempo da sessao (para comparar com os tempos de decisao/movto);
                //       se houve tempo de relax, descontar
                //float relaxTime = gameFlow.endRelaxTime - gameFlow.startRelaxTime;   pode haver mais do que uma parada...
                float endSessionTime = Time.realtimeSinceStartup - gameFlow.startSessionTime;

                //Josi 161229 nao precisa mais do primeiro parametro
                //     170108 resultados da firstScreen do MD
                //     170109 total de jogadas (se interrompido ia o total de vezes jogado)
                int jogadas = probs.GetCurrentPlayLimit(gameSelected);
				Debug.Log ("UIManager.cs --> f:SendEventsToServer --> jogadas = " + jogadas);
                int acertos = success;
				Debug.Log ("UIManager.cs --> f:SendEventsToServer --> acertos = " + acertos);

                //170310 curto e grosso: isto está fixo no restante do script... faltaria pensar um grid que permitisse aumentar os quadros iniciais
                if (gameSelected == 5)
                {
                    jogadas = 12;
                }

				/* ale comment
                //170217 melhor colocar o num jogadas original; no numLinhas do arquivo de resultados se verah que foi necessario gerar mais jogadas para atender minHits
                if ((gameSelected == 1) || (gameSelected == 4))
                {
                    jogadas = probs.saveOriginalBMnumPlays;
                }
				*/

                //170216 na phase0 do JG, o gameMode (ler da sequ ou da arvore) é readSequ
                bool gameMode = probs.getCurrentReadSequ(gameSelected);
				Debug.Log ("UIManager.cs --> f:SendEventsToServer --> gameMode = " + gameMode);

                //170310 acrescentar a fase do jogo: no AQ, AR, JM há apenas uma fase; no JG pode haver de 0 a 8
                int phaseNumber = 0;
                if (gameSelected == 2)
                {
                    phaseNumber = probs.GetCurrMachineIndex() + 1; //comeca de zero
					Debug.Log ("UIManager.cs --> f:SendEventsToServer --> phaseNumber = " + phaseNumber);
					Debug.Log ("UIManager.cs ----------------- CONCLUIU A FASE : "+ phaseNumber);
                }


                string animationType;
                if (gameSelected == 2)
                {
                    animationType = ProbCalculator.machines[probs.currentStateMachineIndex].animationTypeJG;
                }
                else
                {
                    animationType = ProbCalculator.machines[probs.currentStateMachineIndex].animationTypeOthers;
                }


                //170417 montar string para apresentar no arquivo de resultados;
                //       tree="context;prob0;prob1 | context;prob0;prob1 | ...
                string treeContextsAndProbabilities = probs.stringTree();

				Debug.Log ("UIManager.cs --> f:SendEventsToServer --> treeContextsAndProbabilities = " + treeContextsAndProbabilities);


                //170126 getCurrentReadSequ(do jogo selecionado) + param numHits (num minimo de jogadas corretas)
                //170216 gameMode lido do arq config, excepto na phase0 do JG onde o jogo lê a sequ dada, espelhada entre grupo1-v1 e grupo2-v1
                //ServerOperations.instance.RegisterPlay (GameFlowManager.instance, probs.CurrentMachineID (), probs.getCurrentReadSequ (gameSelected), jogadas, acertos, successRate, probs.getMinHits(), _events, interrupted, _eventsFirstScreen);		
                //170310 enviar phaseNumber
                //170413 enviar machines[currentState] para gravar animationType, scoreboard, finalScoreboard, playsToRelax
                //170417 enviar tree no formato (["context"; "prob0"; "prob1"] ... ["context"; "prob0"; "prob1"])
                //170622 enviar showHistory
                //171025 enviar choices (até agora 3 mas poderá ser 2) e showPlaypauseButton
                //180105 send new parameter getPortEEGserial()
                //180117 send locale selected by player
                //180326 new parameters: minHitsInSequenceForJG, ForJM, mdMaxPlays
                //180417 send speedAnim
                //180418 keyboard markers
                ServerOperations.instance.RegisterPlay(GameFlowManager.instance, locale, endSessionTime, probs.CurrentMachineID(),
                    gameMode, phaseNumber, jogadas, acertos, successRate,
                    probs.getMinHits(), ProbCalculator.machines[0].bmMaxPlays, ProbCalculator.machines[0].bmMinHitsInSequence,
                    _events, userAbandonModule,
                    _eventsFirstScreen, animationType,
                    ProbCalculator.machines[probs.currentStateMachineIndex].playsToRelax,
                    ProbCalculator.machines[probs.currentStateMachineIndex].showHistory,
                    probs.getSendMarkersToEEG(),
                    probs.getPortEEGserial(),
                    ProbCalculator.machines[0].groupCode,
                    ProbCalculator.machines[probs.currentStateMachineIndex].scoreboard,
                    ProbCalculator.machines[probs.currentStateMachineIndex].finalScoreboard,
                    treeContextsAndProbabilities,
                    ProbCalculator.machines[0].choices,
                    ProbCalculator.machines[0].showPlayPauseButton,
                    ProbCalculator.machines[probs.currentStateMachineIndex].minHitsInSequence,
                    ProbCalculator.machines[0].mdMinHitsInSequence,
                    ProbCalculator.machines[0].mdMaxPlays,
                    ProbCalculator.machines[0].institution,
                    ProbCalculator.machines[0].attentionPoint,
                    ProbCalculator.machines[0].attentionDiameter,
                    ProbCalculator.machines[0].attentionColorStart,
                    ProbCalculator.machines[0].attentionColorCorrect,
                    ProbCalculator.machines[0].attentionColorWrong,
                    ProbCalculator.machines[probs.currentStateMachineIndex].speedGKAnim,
                    keyboardTimeMarkers
                );

            } //170830 só vai para gravar o arquivo se aprovada a participação na pesquisa...
        }
    }


    //--------------------------------------------------------------------------------------------------------
    //161214 change lawn/trave/ball for the new phase
    public void CorrectPhaseArt(int gameSelected)
    {
		Debug.Log ("UIManager.cs --------------------------CorrectPhaseArt ------------------------------------");
        int targetAnim = probs.GetCurrMachineIndex();
		Debug.Log ("UIManager.cs --> f:CorrectPhaseArt --> targetAnim = " + targetAnim);
        //there is only 3 different football field; if more phases, for now use the last
       
        if ((targetAnim >= gkAnim.Length) || (gameFlow.jogarMDfase3 && ((gameSelected == 3) || (gameSelected == 5))))
        {
            targetAnim = gkAnim.Length - 1;
        }
       
        //enable the correct animation and disable others
        for (int i = 0; i < gkAnim.Length; i++)
        {
            if (i != targetAnim)
            {
                gkAnim[i].gameObject.SetActive(false);
            }
            else
            {
                gkAnim[i].gameObject.SetActive(true);
            }
        }

    }


    //--------------------------------------------------------------------------------------------------------
    //count total gkAnim phases; now are three: land field, semiprofessional, professional;
    //a designer could paint a champion field, with announces, public, etc
    public int GetTotalLevelArts()
    {
		Debug.Log ("UIManager.cs --> f:GetTotalLevelArts --> gkAnim.Length (NUMERO DE FASES) = " + gkAnim.Length);
        return gkAnim.Length;
    }

 

    //--------------------------------------------------------------------------------------------------------
    //Josi: inicializa listas, variáveis, histórico de jogadas (setas verdes e pretas), placar
    public void ResetEventList(int gameSelected)
    {
		Debug.Log ("UIManager.cs ---------------ResetEventList --------------------------------- ");
        _events = new List<RandomEvent>();    //inicializar vetor com dados das fases
                                              //nao inicia a _eventsFirstScreen do MD porque pode estar acumulando uma nova jogada


		eventCount = 0;
        success = 0;
        successRate = 0;
        if ((gameSelected == 2) || (((gameSelected == 3) || (gameSelected == 5)) && (!gameFlow.firstScreen)))  //161214: se JG ou MD ou JMemoria, resetar o painel do resultado das jogadas (setas em verde ou em preto)
        {
            scoreMonitor.Reset();
        };

        //Josi: iniciar placar cf o jogo
        updateScore(gameSelected);
    }



    //--------------------------------------------------------------------------------------------------------
    //Josi: activate animations: perdeu/defendeu (visual) and lamento/alegria (sonoro)
    public void PostAnimThings()
    {
		Debug.Log ("UIManager.cs -------------------- PostAnimThings ---------------------------");
        //Josi: nao executar se ultim jogo
        if (events.Count > 0)
        {
            btnsAndQuestion.SetActive(false);

            //170112 se eh ultima animacao defendeu/perdeu antes da tela de betweenLevels, nao fazer
            //170205 IMEjr FAZER animacao msmo na ultima antes do mudar de fase
            if (eventCount <= probs.GetCurrentPlayLimit(PlayerPrefs.GetInt("gameSelected")))
            {  //170216 limitPlays no JG (diferente se fase0 ou 1,2 ou 3)
                if (probs.getCurrentAnimationType() == "long")
                { //long anim, sound and visual

                    if (events[events.Count - 1].correct)
                    {     //if correct, animations cheer+defendeu
                        cheer.gameObject.SetActive(true);
                        pegoal.speed = 1.0f;                     //171031 needed to keep the normal speed
                        pegoal.enabled = true;
                        pegoal.SetTrigger("pegoal");

                        //170818 se Android, vibrar ao acertar
                        //170828 ao compilar, reclamou do Handheld mesmo com using UnityEngine
                        #if UNITY_ANDROID || UNITY_IOS
                        //if (Application.platform == RuntimePlatform.Android) { 
                        Handheld.Vibrate();
                        //}
                        #endif

                    }
                    else
                    {                                     //if wrong defense, animations lament+perdeu
                        lament.gameObject.SetActive(true);
                        perdeu.speed = 1.0f;                     //171031 needed to keep the normal speed
                        perdeu.enabled = true;
                        perdeu.SetTrigger("goal");              //170204 anim Thom
                    }
                    //170111 como as animacoes tem o mesmo tempo pode vir para ca
                    animResult = true;
                    //170322 StartCoroutine (WaitThenDoThings (2.4f)); 

                }
                else
                {                                         //170215 mas falta ter as animacoes
                    if (probs.getCurrentAnimationType() == "short")
                    {     //short anim, sound and visual
                        if (events[events.Count - 1].correct)
                        { //if correct, animations cheer+defendeu
                            cheerShort.gameObject.SetActive(true);

                            //171031 removed short animations: it is enough to change the speed
                            pegoal.speed = 2.0f;
                            pegoal.enabled = true;
                            pegoal.SetTrigger("pegoal");

                            //170818 se Android, vibrar ao acertar
                            //170828 ao compilar, reclamou do Handheld mesmo com using UnityEngine
                            #if UNITY_ANDROID || UNITY_IOS
                            //if (Application.platform == RuntimePlatform.Android) { 
                            Handheld.Vibrate();
                            //}
                            #endif

                        }
                        else
                        {                                     //if wrong, animations lament+perdeu
                            lamentShort.gameObject.SetActive(true);

                            //171031 removed short animations: it is enough to change the speed
                            perdeu.speed = 2.0f;                     //171031 needed to keep the normal speed
                            perdeu.enabled = true;
                            perdeu.SetTrigger("goal");              //170204 anim Thom

                        }
                        //170111 como as animacoes tem o mesmo tempo pode vir para ca
                        animResult = true;
                        //170322 StartCoroutine (WaitThenDoThings (1.4f)); 
                    }
                    else
                    {
                        if (probs.getCurrentAnimationType() == "none")
                        {  //sem anim som e visual
                           //170111 como as animacoes tem o mesmo tempo pode vir para ca
                            animResult = true;
                        }
                    }
                }


                //btnsAndQuestion.SetActive(true);  //180416 try to increase speed for activate the btns before
                //will this generate animations freezed?... an empty history block

                //170323 passar para ca para nao repetir em cada tipo de animacao
                //170418 o animationTime foi criado para esperar acabar uma animacao, que ja comecou, logo devolve tempos menores;
                //       aqui se acerta para garantir que nao havera sobreposicao com o proximo evento;
                //       no jogo AR, melhor esperar um pouco mais antes de colocar o "aperte uma tecla"
                float extraTime = 0.2f;
                if (PlayerPrefs.GetInt("gameSelected") == 4)
                {
                    extraTime = 0.5f;
                }
                StartCoroutine(WaitThenDoThings(probs.animationTime() + extraTime));  //170322 centralizado em uma rotina os tempos de animacao


                //Score here, else shows up before play
                updateScore(PlayerPrefs.GetInt("gameSelected"));
            }
        } //Josi: fim do if events.count
    }



    //--------------------------------------------------------------------------------------------------------
    //170126 inicializar e atualizar placar
    public void updateScore(int gameSelected)
    {
		Debug.Log ("UIManager.cs --------------------f:updateScore --------------------");
        placar.text = System.String.Empty;    //170216 Use System.String.Empty instead of "" when dealing with lots of strings;
        if (probs.getCurrentScoreboard())
        {
            if (eventCount > 0)
            {
                //180323 not reset the counter if error in sequence (Amparo request)
                // original : placar.text = success.ToString().PadLeft(3) + " / " + probs.GetCurrentPlayLimit(gameSelected).ToString(); 

				// 190322 - Mostra o no. de acerto / o no.Min que ele deve ter de acertos
				placar.text = success.ToString().PadLeft(3) + " / " + probs.getJGminHitsInSequence().ToString();  //170216


				Debug.Log ("UIManager.cs --> f:updateScore --> placar.text = " + placar.text);
				Debug.Log ("UIManager.cs --> f:updateScore --> probs.GetCurrentPlayLimit(gameSelected) = " + probs.GetCurrentPlayLimit(gameSelected));
				Debug.Log ("UIManager.cs --> f:updateScore --> success = " + success);
            }
            else
            {
                // original placar.text = "  0 / " + probs.GetCurrentPlayLimit(gameSelected).ToString().PadLeft(3).Trim();  //170216
				placar.text = "  0 / " + probs.getJGminHitsInSequence().ToString().PadLeft(3).Trim();
            }
        }
    }


    //--------------------------------------------------------------------------------------------------------
    //Josi: function para acertar na tela o proximo chute a indicar
    public void showNextKick(string direcaoAindicar)
    {
        //acertar a seta da próxima jogada
        setaEsq.SetActive((direcaoAindicar == "0"));
        setaCen.SetActive((direcaoAindicar == "1"));
        setaDir.SetActive((direcaoAindicar == "2"));

        gameFlow.frameChute.SetActive(true);
        btnsAndQuestion.SetActive(true);

    

        movementTimeA = Time.realtimeSinceStartup; //170309 para nao precisar descontar tempo das animacoes (impreciso)
		Debug.Log ("UIManager.cs --> f:showNextKick --> movementTimeA = " + movementTimeA);
        decisionTimeB = Time.realtimeSinceStartup; //170113 apareceu "aperte tecla": inicia-se a contagem do tempo de decisão
		Debug.Log ("UIManager.cs --> f:showNextKick --> decisionTimeB = " + decisionTimeB);

        //170915 se está nesta rotina, não está pausado, logo, garantir os botoes Play/Pause
        if (probs.getShowPlayPauseButton())
        {
            if (!pausePressed)
            {
                buttonPause.SetActive(true);
                buttonPlay.SetActive(false);
            }
        }

        //170311 remove "aperteTecla" after EXIT cancelado
        gameFlow.bmMsg.SetActive(false);                  //BM msg tutorial ou aperteTecla
        gameFlow.aperteTecla.SetActive(false);            //BM msg aperteTecla
    }





    //--------------------------------------------------------------------------------------------------------
    //170327 acrescentar param para indicar se o Quit veio da BetweenLevels (1) ou pelo botao de Exit do canto superior direito
    public void QuitGame(int whatScreen)
    {
		Debug.Log ("UIManager.cs ---------------------------f:QuitGame ----------------------------------------");
		Debug.Log ("UIManager.cs --> f:QuitGame --> whatScreen = " + whatScreen);
        if (whatScreen == 2)
        {
            //170417 estava demorando muito tempo se o user apenas quisesse olhar a primeira tela e Exitar
            //170418 se Exit no anim321 deve-se aguardar terminar a animacao
            float stopTime;
			Debug.Log ("UIManager.cs --> f:QuitGame --> animCountDown = " + animCountDown);
            if (animCountDown)
            {
                //170824 calcular o tempo que falta para acabar a animação;
                //       normalizedTime = % de tempo que já rodou (módulo 1.0f para remover a primeira parte: #vezes que rodou)
                //       tempo que já rodou = tempo total da animação * % de tempo que já rodou
                //       tempo que falta para acabar = tempo total da animação - tempo que já rodou
                float timeToEnd = 3.1f - (3.1f * (this.anim321.GetCurrentAnimatorStateInfo(0).normalizedTime % 1.0f));
                stopTime = timeToEnd;
				Debug.Log ("UIManager.cs --> f:QuitGame --> timeToEnd = " + timeToEnd);

            }
            else
            {
                if (eventCount == 0)
                {
                    stopTime = 0.0f;
                }
                else
                {
                    stopTime = probs.animationTime();
                }
            }

            //StartCoroutine (gameFlow.waitTime(PlayerPrefs.GetInt ("gameSelected"), probs.animationTime (), whatScreen));
            StartCoroutine(gameFlow.waitTime(PlayerPrefs.GetInt("gameSelected"), stopTime, whatScreen));
        }
    }



    //--------------------------------------------------------------------------------------------------------
    public void Sair()
    {
		Debug.Log ("UIManager.cs -----------------------------f:Sair ------------------------- ");
        //170322 unity3d tem erro ao usar application.Quit
        //       workaround: http://unity3dtrenches.blogspot.com.br/2015/10/unity-3d-compiled-game-freezes-or.html
        //Application.Quit ();
        if (!Application.isEditor)
        {  //if in the editor, this command would kill unity...
            if (Application.platform == RuntimePlatform.WebGLPlayer)
            {
                Application.OpenURL(PlayerPrefs.GetString("gameURL"));
            }
            else
            {
                //171121 not working kill()
                if ((Application.platform == RuntimePlatform.IPhonePlayer) ||
                    (SystemInfo.deviceModel.Contains("iPad")))
                {           //try #IF UNITY_IOS
                    Application.Quit();
                }
                else
                {
                    System.Diagnostics.Process.GetCurrentProcess().Kill();
                }
            }
        }
    }


    //--------------------------------------------------------------------------------------------------------
    public void OnEnable()
    {
		Debug.Log ("UIManager.cs -------------------------OnEnable ---------------------------");
        OnAnimationEnded += PostAnimThings;
    }


    //--------------------------------------------------------------------------------------------------------
    public void OnDisable()
    {
        OnAnimationEnded -= PostAnimThings;
    }


    //--------------------------------------------------------------------------------------------------------
    int centerStateHash;
    int currentState;
    void Start()
    {
        probs = ProbCalculator.instance;
        gameFlow = GameFlowManager.instance;             //161230 para fechar objetos

        //171005 declarar a instance para permitir chamar rotinas do outro script
        translate = LocalizationManager.instance;

        //171006 textos a alterar na interface
        setaCen.GetComponentInChildren<Text>().text = translate.getLocalizedValue("cen");
        setaEsq.GetComponentInChildren<Text>().text = translate.getLocalizedValue("esq");
        setaDir.GetComponentInChildren<Text>().text = translate.getLocalizedValue("dir");

        //171010 botoes MD (Jogo da Memoria)
        mostrarSequ.GetComponentInChildren<Text>().text = translate.getLocalizedValue("mdBack");
        jogar.GetComponentInChildren<Text>().text = translate.getLocalizedValue("mdPlay");
        menuJogos.GetComponentInChildren<Text>().text = translate.getLocalizedValue("mdMenu").Replace("\\n", "\n");


        //171031 to decide what sound/animation to choose 
        locale = translate.getLocalizedValue("locale");

        //171031 based on locale, select the correct animation/sound and remove unused
        //171222 created Spanish/Spain locale
        if (locale == "pt_br")
        {
            pegoal = pegoalPtBr;
            perdeu = perdeuPtBr;
            sound321 = sound321ptbr;

            Destroy(pegoalEnUs); Destroy(pegoalEsEs);
            Destroy(perdeuEnUs); Destroy(perdeuEsEs);
        }
        else
        {
            if (locale == "en_us")
            {
                pegoal = pegoalEnUs;
                perdeu = perdeuEnUs;
                sound321 = sound321enus;

                Destroy(pegoalPtBr); Destroy(pegoalEsEs);
                Destroy(perdeuPtBr); Destroy(perdeuEsEs);
            }
            else
            {
                if (locale == "es_es")
                {
                    pegoal = pegoalEsEs;
                    perdeu = perdeuEsEs;
                    sound321 = sound321eses;

                    Destroy(pegoalPtBr); Destroy(pegoalEnUs);
                    Destroy(perdeuPtBr); Destroy(perdeuEnUs);
                }
            }
        }


        int targetAnim = probs.GetCurrMachineIndex();
		Debug.Log ("UIManager.cs --> f:Start --> targetAnim = " + targetAnim);
        
        if ((targetAnim >= gkAnim.Length) || (gameFlow.jogarMDfase3 && ((PlayerPrefs.GetInt("gameSelected") == 3) || (PlayerPrefs.GetInt("gameSelected") == 5))))   //170125 
        {
            targetAnim = gkAnim.Length - 1;
			Debug.Log ("UIManager.cs --> f:Start --> gkAnim.Length = " + gkAnim.Length);
        }
        
        centerStateHash = gkAnim[targetAnim].gk.GetCurrentAnimatorStateInfo(0).shortNameHash;

		Debug.Log ("UIManager.cs --> f:Start --> centerStateHas = " + centerStateHash);

        currentState = centerStateHash;

        
        //180418 to resize the array and initialize
        keyboardTimeMarkers = new float[10];
        initKeyboardTimeMarkers();


    }



    //--------------------------------------------------------------------------------------------------------
    void Update()
    {
		Debug.Log ("UIManager.cs ------------------------ f:Update -------------------------");
        int currAnim = probs.GetCurrMachineIndex();
		Debug.Log ("UIManager.cs --> f:Update --> currAnim = " + currAnim);

        bool estouNoPegaQualquerTecla = false;  //170223170110 para aceitar qualquer tecla, inclusive as do jogo
        int number; //180419 to facilitate the routine

        //161226 nunca entra aqui por ser >= gkAnim... 
        //170130 mas eh obrigatorio para acertar o gkAnim correto nos hashes, no caso de pular direto paa campo profissional
        
        if ((currAnim >= gkAnim.Length) || (gameFlow.jogarMDfase3 && ((PlayerPrefs.GetInt("gameSelected") == 3) || (PlayerPrefs.GetInt("gameSelected") == 5))))
        {
            currAnim = gkAnim.Length - 1;
        }
      
 


        //170915 encebolar o pegaInput para valer se nao está pausado
        if (!pausePressed)
        {
            //============================================================================
            //180402 accept pausePlay key (on/off), but only when permitted
            if (Input.GetKeyDown(probs.playPauseKey()))
            {
                if (probs.getShowPlayPauseButton() && !gameFlow.firstScreen && buttonPause.activeSelf)
                {
                    //clickPausePlay ();
                }
            }



            //============================================================================
            AnimatorStateInfo currentBaseState = gkAnim[currAnim].gk.GetCurrentAnimatorStateInfo(0);

            if (BtwnLvls)
                return;
            if (currentState != currentBaseState.shortNameHash)
            {
                if (currentBaseState.shortNameHash == centerStateHash)
                {
                    if (OnAnimationEnded != null)
                        OnAnimationEnded();
                }
            }


            

            currentState = currentBaseState.shortNameHash;
			Debug.Log ("UIManager.cs --> f:Update --> currentState = " + currentState);

        }
        else
        {
            //============================================================================
            //180402 accept pausePlay key (on/off), but only if permitted
            if (Input.GetKeyDown(probs.playPauseKey()))
            {
                if (probs.getShowPlayPauseButton() && !gameFlow.firstScreen && buttonPlay.activeSelf)
                {
                    //clickPausePlay ();
                }
            }
        }
    }


    //--------------------------------------------------------------------------------------
    //170111 coroutine para aguardar tempo enquanto a animacao nao termina
    public IEnumerator WaitThenDoThings(float time)   //170203 publica, para ser acessada no gameFlow.
    {
        yield return new WaitForSeconds(time);

        //acabou de aparecer a imagem, faca isto
        if (animCountDown)
        {
            //print("acabou 321"); 
            //se houver um Exit pendente, aparecerah o simbolo e logo a seguir a tela (abandonar?)
            showNextKick(probs.GetNextKick());
            animCountDown = false;

            //170915
            if (probs.getShowPlayPauseButton())
            {
                buttonPause.SetActive(true);
                buttonPlay.SetActive(false);
            }

            //171031 select pt-br or en-us sound
            if (locale == "pt_br")
            {
                sound321.enabled = false; //170825 para resetar o som (aparentemente
            }
            else
            {
                if (locale == "en_us")
                {
                    sound321enus.enabled = false; //171031 to reset the sound
                }
                else
                {
                    if (locale == "es_es")
                    {
                        sound321eses.enabled = false; //171222 to reset the sound
                    }
                }
            }
        }

        if (animResult)
        {
            animResult = false;
            //print("acabou defendeu ou perdeu");
            //170112 se estah para ir para a tela de betweenlevels nao fazer os acertos de objetos
            if (!BtwnLvls)
            {

               
                btnsAndQuestion.SetActive(true);

                //170920 voltando de uma animação; se for o caso, ativar Play/Pause
                if (probs.getShowPlayPauseButton())
                {
                    buttonPause.SetActive(true);
                    buttonPlay.SetActive(false);
                }

                //170307 reiniciar contagem do tempo: desde que aparecem as teclas de defesa
                movementTimeA = Time.realtimeSinceStartup; //170309 para nao precisar descontar tempo das animacoes (impreciso)

				Debug.Log ("UIManager.cs --> IE:WaitThenDoThings --> movementTimeA = " + movementTimeA);

                decisionTimeA = Time.realtimeSinceStartup;  //170307 apareceram as setas de defesa: inicia-se a contagem do tempo de movimento
                                                            /* ale comment }
                                                        } 

                                                  
                                                        */
				Debug.Log ("UIManager.cs --> IE:WaitThenDoThings --> decisionTimeA = " + decisionTimeA);

            }
        }
    }

    

    //---------------------------------------------------------------------------------------
    //180418 reset array
    public void initKeyboardTimeMarkers()
    {
        for (int i = 0; i <= 9; i++)
        {
            keyboardTimeMarkers[i] = 0.0f;
        }
    }


    //---------------------------------------------------------------------------------------
    //180510 apply correct phase speedGKAnim; there is only 3 field scenarios -
    //       when there is more than 3 phases, the scenario is always the last: professional (until do more);
    //       the speed is the same for all: player, ball and goalkeeper
    public void initSpeedGKAnim()
    {
        int aux;
        aux = (probs.GetCurrMachineIndex() >= gkAnim.Length) ? gkAnim.Length - 1 : probs.GetCurrMachineIndex();
        gkAnim[aux].player.speed = probs.speedGKAnim(probs.GetCurrMachineIndex());
        gkAnim[aux].ball.speed = gkAnim[aux].player.speed;
        gkAnim[aux].gk.speed = gkAnim[aux].player.speed;
    }

    

}