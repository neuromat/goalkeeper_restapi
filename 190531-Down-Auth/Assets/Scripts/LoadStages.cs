/************************************************************************************/
// Module written by scaroni <renato.scaroni@gmail.com>
// Rewrited by Josi Perez <josiperez.neuromat@gmail.com>
//
// Module responsible for loading teams and its configuration phases 
// from a local directory or from the web (server neuroMat)
/************************************************************************************/

using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;
using Newtonsoft.Json;


public delegate void OnLoadPkgExternal(string path);
public delegate void OnLoadPkgInternal();
public delegate void OnMenuTimeout();


public class LoadStages : MonoBehaviour
{
    List<SourcePath> treeSourcePaths = new List<SourcePath>();


    public GridLayoutGroup g;                    //scene Configuration/Canvas/Menu/menuPacotes - grid de 1 coluna para receber os botoes dinamicos
    public GameObject btnPrefab;
    public Text warning;
    public OnMenuTimeout OnMenuTimeOutHandler;
    public OnLoadPkgExternal OnLoadPkgExternalHandler;
    public OnLoadPkgInternal OnLoadPkgInternalHandler;

    //  private Button firstPacketButton;            //161207: salvar PRIMEIRO botao dinamico de pacotes e invocar onClick forcado

    private Button[] buttons;                    //170921 para chamar posteriormente os botõs dinamicos e dar um destaque ao selecionado
    private byte dynamicButtonDefaultAlpha = 70; //170921 chamado 2x; sóara nao esquecer um deles algum dia

    private LocalizationManager translate;       //171005 trazer script das rotinas de translation

    //171006 translations
    //public Text Creditos;                      //180614 goes out from Team Screen and goes to Menu Screen
    public Text headTitle;
    //public Text txtVersion;                    //180402 to save version used
    public Text selectTeam;
    public Text txtNext;
    public Text txtSair;

    public Text txtVersion;                      //180627 put at the first scene, available for all

    //171114 read CustomTrees from webServer neuromat if Android
    //171124 same for iOS
    public static readonly string androidTreesServerLocation = "game.numec.prp.usp.br/game/CustomTreesANDROID/";
    public static readonly string iosTreesServerLocation = "game.numec.prp.usp.br/game/CustomTreesIOS/";
    public static readonly string webProtocol = "http://";


    //180126 Link https://www.myip.com/api-docs/
    //       {"ip":"66.249.75.9","country":"United States","cc":"US"}
    static readonly string getMyIP = "https://api.myip.com";
    [Serializable]
    public class webIPinfo
    {
        public string ip;
        public string country;
        public string cc;
    }

    //170417 aumentar num de fases
    public static string[] files = new string[] {
     "tree1",
       "tree2",
       "tree3",
       "tree4",
       "tree5",
       "tree6",
       "tree7",
       "tree8"
    };

    public int level;

    public Text Mensagem;

    public Dictionary<string, int> games_ids = new Dictionary<string, int>();


    // -----------------------------------------------------------------------------------------------------
    void AddSourcePath(string url)
    {
        SourceType st;          // web or file

        if (url.StartsWith("http"))
        {
            st = SourceType.web;
        }
        else
        {
            st = SourceType.file;
        }

        SourcePath sp = new SourcePath();
        sp.url = url;
        sp.sourceType = st;
        treeSourcePaths.Add(sp);
    }

    // -----------------------------------------------------------------------------------------------------
    // Where to get trees from?
    void DefaultTreeSourceInit()
    {
        string url;
        SourceType st;

        if (Application.dataPath.StartsWith("http"))
        {
            url = Application.dataPath + "/CustomTrees/";
            st = SourceType.web;
        }
        else
        {
            //StreamingAssets is packed in the build
            //171124 also for iOS
            string c_trees;
            if ((Application.platform == RuntimePlatform.Android) ||
              (Application.platform == RuntimePlatform.IPhonePlayer) || (SystemInfo.deviceModel.Contains("iPad")))
            {
                c_trees = Application.streamingAssetsPath + "/CustomTrees/index.info";
            }
            else
            {
                c_trees = Application.dataPath + "/CustomTrees/";
            }


            //171124 includes iOS
            if ((Application.platform != RuntimePlatform.Android) &&
                (Application.platform != RuntimePlatform.IPhonePlayer) && (!SystemInfo.deviceModel.Contains("iPad")))
            {
                if (!Directory.Exists(c_trees))
                {
                    //print("Nã achei, criando o default!");

                    Directory.CreateDirectory(c_trees);
                    Directory.CreateDirectory(c_trees + "/Pacote1");       //G1
                    File.AppendAllText(c_trees + "/index.info", "Pacote1");   //G1

                    TextAsset texto;
                    texto = (TextAsset)Resources.Load("CustomTrees/Pacote1/tree1");   //G1
                    File.AppendAllText(c_trees + "/Pacote1/tree1.txt", texto.text);      //G1

                    texto = (TextAsset)Resources.Load("CustomTrees/Pacote1/tree2");  //G1
                    File.AppendAllText(c_trees + "/Pacote1/tree2.txt", texto.text);     //G1

                    texto = (TextAsset)Resources.Load("CustomTrees/Pacote1/tree3");  //G1
                    File.AppendAllText(c_trees + "/Pacote1/tree3.txt", texto.text);     //G1
                }
                url = "file://" + c_trees;
                st = SourceType.file;
            }
            else
            {
                url = c_trees; //"file://"+c_trees;
                st = SourceType.file;
            }
        }


        SourcePath sp = new SourcePath();
        sp.url = url;
        sp.sourceType = st;
        treeSourcePaths.Add(sp);
    }


    //--------------------------------------------------------------------------------------
    // Use this for initialization
    void Start()
    {
        //171005 instance declaration to allow calling scripts from another script
        translate = LocalizationManager.instance;

        // Apaga e cria o diretório Custom Trees (ou equivalente)
        var path = CreateCustomTreesDirectory();

        // define o nível do jogador
        level = GetPlayerLevel();

        if (level == 0)
        {
            Mensagem.text = translate.getLocalizedValue("errorConnection");
        }
        else
        {
            var gamesconfigs = GetGamesConfig(level);

            // Salva a lista de times no arquivo index.info
            SaveIndexInfo(path, gamesconfigs);

            // Guarda o jogo associado a cada configuração
            foreach (GameConfigJson config in gamesconfigs)
            {
                var games = GetGame(config.id);

                foreach (GameJson game in games)
                {
                    // Salva os ids de cada fase de cada jogo em uma lista, para ser
                    // acessada no momento de salvar os resultados de cada jogada
                    SaveIDsofGamesforResults(config.name, game);

                    // Lê os contextos e probabilidades da base e cria as árvores com base nesses objetos
                    var contexts = GetContexts(game.id);

                    if (game.phase == 0)
                    {
                        var tree = CreateFirstTree(config, game, contexts);
                        // Salva as árvores em arquivos dentro do diretório correspondente a cada time
                        CreateTreeDirAndFile(path + config.name, "/tree" + (game.phase + 1).ToString() + ".txt", tree);
                    }
                    else
                    {
                        var tree = CreateTree(config, game, contexts);
                        // Salva as árvores em arquivos dentro do diretório correspondente a cada time
                        CreateTreeDirAndFile(path + config.name, "/tree" + (game.phase + 1).ToString() + ".txt", tree);
                    }
                }
            }

            //StartCoroutine(CriaMenu(gamesconfigs));

            //180209 to avoid delays in LocalizationManager (original place); here have enough time
            StartCoroutine(readMachineIP());

            int i = 0;

            //171006 texts to change on the interface
            //Creditos.text = translate.getLocalizedValue ("creditos");
            headTitle.text = translate.getLocalizedValue("jogo");
            selectTeam.text = translate.getLocalizedValue("escolha");
            txtNext.text = translate.getLocalizedValue("avancar");
            txtSair.text = translate.getLocalizedValue("sair").Replace("\\n", "\n");

            //170310 delete PlayerPrefs; be careful: LoadStages loaded the packet name to use later
            //180130 PlayerPrefs.DeleteAll ();     deleted at beginning, on LocalizationManager

            //170622 in webGL mode, define the page to go when the user select Exit/ESC
            //180627 goes out from here and goes to Localization
            PlayerPrefs.SetString("gameURL", "http://game.numec.prp.usp.br");
            PlayerPrefs.SetString("version", txtVersion.text);       //180402 to save version game in results file
            txtVersion.text = PlayerPrefs.GetString("version");         //180627 taked from Localization


            warning.color = new Color32(255, 255, 255, 0);
            if (warning != null)
            {
                warning.text = System.String.Empty;   //170110 era ""; Use System.String.Empty instead of "" when dealing with lots of strings
            }

            // No path found, use default
            if (i == 0)
            {
                DefaultTreeSourceInit();      //carrega as arvores do diretorio CustomTrees
            }
            else
            {
                if (warning != null)
                {
                    //warning.text = "Carregado das preferencias de usuario:\n";
                    warning.text = translate.getLocalizedValue("loadPrefs");  //171006
                }
            }

            // read the trees in coroutines
            foreach (SourcePath s in treeSourcePaths)
            {
                StartCoroutine(ReadSource(s.url, s.sourceType));
            }
        }
    }

    /// <summary>
    /// Create the menu of adversaries teams and saves at the PlayerPrefs the id of the selected one.
    /// </summary>
    /// <returns>The menu.</returns>
    /// <param name="teams">list of teams of a level equal or less than the player level.</param>
    IEnumerator CriaMenu(List<GameConfigJson> teams)
    {
        // For each team, create an button with its name
        foreach (GameConfigJson team in teams)
        {
            // Define the exhibition params of the buttons.
            g.GetComponent<RectTransform>().localScale = Vector3.one;
            float xCellWidth = g.GetComponent<RectTransform>().rect.width / 1.5f;  //not occupy all cell 180315 from 1.5 to 1.1f
            float xCellHeight = g.GetComponent<RectTransform>().rect.height;

            if (teams.Count <= 10)  //180403 to better adapt Amparo experiment
            {
                g.constraintCount = 1;  //1column
                xCellHeight = xCellHeight / files.Length;
                xCellHeight -= g.spacing.x;
                g.cellSize = new Vector2(xCellWidth, ((files.Length == 1) ? xCellHeight / 3.0f : xCellHeight / 0.9f));
            }
            else
            {
                g.constraintCount = 2;  //2 columns
                xCellHeight = xCellHeight / (files.Length / 2);
                xCellHeight -= g.spacing.x;
                g.cellSize = new Vector2(xCellWidth / 1.3f, xCellHeight / 1.3f);   //180315 size in Android was very small
            }

            // Effectivelly create the button with the neme of the team on it
            GameObject go = Instantiate(btnPrefab);      //the image button; a prefab to repeat each new team
            go.transform.SetParent(g.transform);
            go.GetComponentInChildren<Text>().text = team.name;

            //180316 better separate the cases: standalone/web and mobiles for a letter more compatible
#if UNITY_STANDALONE || UNITY_WEBGL || UNITY_EDITOR
            go.GetComponentInChildren<Text>().resizeTextMaxSize = 40;
#endif

            go.name = team.name;

            //170921 clarear a imagem de fundo do botão, para destacar depois, o escolhido
            go.GetComponent<Image>().color = new Color32(255, 255, 255, dynamicButtonDefaultAlpha);
            go.GetComponent<RectTransform>().localScale = Vector3.one;

            // Change color of the selected team and save the information in the PlayerPrefs
            Button b = go.GetComponent<Button>();
            b.onClick.AddListener(() => TimeSelecionado(team.id, team.name));
        }
        yield break;
    }

    // Change color of the selected team and save the information in the PlayerPrefs
    void TimeSelecionado(int id, string name)
    {
        buttons = g.GetComponentsInChildren<Button>();

        foreach (Button btn in buttons)
        {
            if (btn.name == name)
            {
                btn.GetComponentInChildren<Text>().color = new Color32(255, 255, 0, 255);
                btn.GetComponentInChildren<Image>().color = new Color32(255, 255, 255, 255);
            }
            else
            {
                btn.GetComponentInChildren<Text>().color = Color.white;
                btn.GetComponent<Image>().color = new Color32(255, 255, 255, dynamicButtonDefaultAlpha);
            }
        }

        PlayerPrefs.SetInt("teamSelected", id);
    }


    //--------------------------------------------------------------------------------------
    //leitura do index.info que contem os nomes dos times, separados por ";"
    IEnumerator ReadSource(string url, SourceType st)
    {
        //170815 era assim: WWW www = new WWW (url+"index.info");
        string fileToAccess;
        //android
        if (Application.platform == RuntimePlatform.Android)
        {
            //=================================================
            //try to read from the server, mainly
            //171127 else read local CustomTrees
            fileToAccess = webProtocol + androidTreesServerLocation + "index.info";
            WWW internet = new WWW(fileToAccess);
            yield return internet;
            if ((internet.error != null) && (internet.error != ""))
            {
                //if not connection, read CustomTrees local
                fileToAccess = url;
            }
            //=================================================


            //171124 iOS (iPad/iPhone)
        }
        else
        {
            if ((Application.platform == RuntimePlatform.IPhonePlayer) || (SystemInfo.deviceModel.Contains("iPad")))
            {
                //=================================================
                //try to read from the server, mainly
                //171127 else read local CustomTrees
                fileToAccess = webProtocol + iosTreesServerLocation + "index.info";
                WWW internet = new WWW(fileToAccess);
                yield return internet;
                if ((internet.error != null) && (internet.error != ""))
                {
                    //if not connection, read CustomTrees local
                    fileToAccess = st + "://" + url;
                }
                //=================================================

                //standalone
            }
            else
            {
                fileToAccess = url + "index.info";
            }
        }

        //read index.info content: the team names
        WWW www = new WWW(fileToAccess);
        yield return www;


        if ((www.error != null) && (www.error != ""))
        {   //180411 was left transparent to avoid show "debug" messages for user; error messages should appear
            //warning.color = new Color32(255,255,255,255); 

            if (warning != null)
                warning.text += "url: " + url + " Status: " + www.error + "\n";
            else
                warning.text = "url: " + url + "\nError: " + www.error + "\n";  //171005 generic msg
        }
        else
        {
            if (warning != null)
            {
                warning.text += warning.text = "url: " + url + " Status: Success\n";
            }


            //put the team names in a vector
            if (www.text != null)
            {
                string[] files = www.text.Split(';'); // package list  

                if (LoadedPackage.packages == null)
                {
                    LoadedPackage.packages = new Dictionary<string, Package>();
                }

                //create a button for each team name ========================================================================

                //170817 android keep index.info in the variable - remove
                //171124 ios idem
                if ((Application.platform == RuntimePlatform.Android) ||
                     (Application.platform == RuntimePlatform.IPhonePlayer) || (SystemInfo.deviceModel.Contains("iPad")))
                {
                    url = fileToAccess.Replace("index.info", "");
                }


                //170920 changing dynamic grid to accept until 20 teams
                //171129 refactoring the cellSizes to adapt to iPad
                //180315 changing text size to increase size in Android and others
                g.GetComponent<RectTransform>().localScale = Vector3.one;              //let the parent with initial size (1,1,1)
                float xCellWidth = g.GetComponent<RectTransform>().rect.width / 1.5f;  //not occupy all cell 180315 from 1.5 to 1.1f
                float xCellHeight = g.GetComponent<RectTransform>().rect.height;

                if (files.Length <= 10)
                {                                               //180403 to better adapt Amparo experiment
                    g.constraintCount = 1;                                              //1column
                    xCellHeight = xCellHeight / files.Length;
                    xCellHeight -= g.spacing.x;
                    g.cellSize = new Vector2(xCellWidth, ((files.Length == 1) ? xCellHeight / 3.0f : xCellHeight / 0.9f));
                }
                else
                {
                    g.constraintCount = 2;                                             //2 columns
                    xCellHeight = xCellHeight / (files.Length / 2);
                    xCellHeight -= g.spacing.x;
                    //g.cellSize = new Vector2 (xCellWidth/1.5f, xCellHeight/((files.Length >11)?1.1f:1.4f)); 
                    g.cellSize = new Vector2(xCellWidth / 1.3f, xCellHeight / 1.3f);     //180315 size in Android was very small
                }                                                                      //180403 change from 1.5

                int i = 0;  //salvar dados do primeiro botao de pacotes; se houver apenas um e o user avancar sem selecionar, fica valendo este
                foreach (string f in files)
                {
                    if (g != null) // is there a layout?
                    {              // it is a grid defined in LoadStages.cs refering scene Configuration/Canvas/menu/menuPacotes
                        LoadedPackage.packages[url + f] = new Package(url, f);

                        GameObject go = Instantiate(btnPrefab);      //the image button; a prefab to repeat each new team

                        go.transform.SetParent(g.transform);
                        go.GetComponentInChildren<Text>().text = f;

                        //180316 better separate the cases: standalone/web and mobiles for a letter more compatible
                        #if UNITY_STANDALONE || UNITY_WEBGL || UNITY_EDITOR
                            go.GetComponentInChildren<Text>().resizeTextMaxSize = 40;
                        #else
                            go.GetComponentInChildren<Text>().resizeTextMaxSize  = 80;
                        #endif

                        go.name = f;

                        //170921 clarear a imagem de fundo do botã, para destacar depois, o escolhido
                        go.GetComponent<Image>().color = new Color32(255, 255, 255, dynamicButtonDefaultAlpha);

                        //171129
                        go.GetComponent<RectTransform>().localScale = Vector3.one;

                        Button b = go.GetComponent<Button>();
                        AddListener(b, url + f);

                        //Josi: 161207: salvar botao para onClick simulado do primeiro pacote na lista
                        if (i == 0)
                        {
                            //firstPacketButton = go.GetComponent<Button>(); //botao
                            //AddListener (firstPacketButton, url + f);      //e conteudo do que fazer em onClick
                            b.onClick.Invoke();                              //nao deu certo chamar ao sair... fica assim...

                            //teamSelected = f;                           //170310 salvar nome do primeiro pacote e mudar depois se user clicar outro
                            //170310 save teamSelected in PlayerPrefs to use after
                            PlayerPrefs.SetString("teamSelected", f);

                            // Salva as fases do jogo escolhido nas preferências do usuário
                            SavePhasestoPlayPrefs(f);

                            // Salva o level do jogo escolhido nas preferências do usuário
                            SaveConfigLeveltoPlayPrefs(f);

                            i++;
                        }
                    }
                }
            }
        }
    }


    //--------------------------------------------------------------------------------------
    void AddListener(Button b, string value)
    {   //Load configuration file
        b.onClick.AddListener(() => LoadTreePackageFromExternalSource(value));
    }


    //--------------------------------------------------------------------------------------
    //aqui le os arquivos de configuracao do time selecionado
    IEnumerator LoadExternal(String url)
    {
        //170815 diferentes paths conforme o ambiente
        //       a url Android continha o index.info
        string fileToAccess;
        string url2mobiles;       //180220 to solve paths with accents in iOS/Android environments


        //170817 url android estáarregando o nome do arquivo
        if (Application.platform == RuntimePlatform.Android)
        {
            url = url.Replace("index.info", "");
        }
        warning.text = "***** LoadExternal url = " + url;


        // Antes de mais nada, limpamos o que jáxiste
        LoadedPackage.packages[url].stages.Clear();

        //180220 in iOS paths, necessary to change to HTML codes (HTML URL Encoding Reference);
        //    tip found in
        //    1) https://forum.unity.com/threads/resources-load-with-special-characters-in-the-file-name-ios-and-mac.372881/
        //    2) https://answers.unity.com/questions/546213/handling-special-characters-aeouuouo-in-unity.html 
        //    fileToAccess = fileToAccess.Normalize(System.Text.NormalizationForm.FormD);
        //    fileToAccess = WWW.EscapeURL(fileToAccess,System.Text.Encoding.UTF8);
        //    fileToAccess = fileToAccess.Replace("á,"%C3%A1");  //worked finally...
        //
#if UNITY_IOS || UNITY_EDITOR_OSX || UNITY_STANDALONE_OSX || UNITY_ANDROID
        url2mobiles = convertPathToMobiles(url);
#endif

        // para o total de fases (até) em um mesmo time, ler as configuracoes;
        // isto precisa melhorar e virar um unico arquivo...
        for (int i = 0; i < files.Length; i++)
        {
            //180220 use url2iOS only for www access; after that comes to the normal
#if UNITY_IOS || UNITY_EDITOR_OSX || UNITY_STANDALONE_OSX || UNITY_ANDROID
            warning.text = url2mobiles + "/" + files[i] + ".txt";
#else
          warning.text = url + "/" + files [i] + ".txt";
#endif
            fileToAccess = warning.text;

            WWW www = new WWW(fileToAccess);
            yield return www;

            if ((www.error != null) && (www.error != ""))   //170817 melhor "parentezar"
            {
                if (warning != null)
                {
                    warning.text = "Failed to upload file " + files[i] + ".txt\n" + www.error; //171005generic msg
                }
            }
            else
            {
                if (www.text != null)
                {
                    LoadedPackage.packages[url].stages.Add(www.text);
                }
            }

        }

        LoadedPackage.loaded = LoadedPackage.packages[url];

        if (warning != null)
        {    //171005 translation
            warning.text = translate.getLocalizedValue("loadPckgs") + "\n" + LoadedPackage.packages[url].name;

            //packetSelected = LoadedPackage.packages[url].name.ToString();  //170310 salvar nome do pacote selecionado pelo user
            //170310 salvar nome do pacote selecionado pelo user em PlayerPrefs
            PlayerPrefs.SetString("teamSelected", LoadedPackage.packages[url].name);

            // Salva as fases do jogo escolhido nas preferências do usuário
            SavePhasestoPlayPrefs(LoadedPackage.packages[url].name);

            // Salva o level do jogo escolhido nas preferências do usuário
            SaveConfigLeveltoPlayPrefs(LoadedPackage.packages[url].name);


            //170921 destacar o time selecionado
            //lembrar de repintar todos, por possiveis selecionados antes (o 1o escolhido programaticamente)
            buttons = g.GetComponentsInChildren<Button>();
            for (int xx = 0; xx < buttons.Length; xx++)
            {
                //buttons [xx].GetComponentInChildren<Text> ().SetNativeSize ();
                if (buttons[xx].name == LoadedPackage.packages[url].name)
                {
                    //buttons [xx].GetComponentInChildren<Text> ().fontStyle = FontStyle.Bold; ficou muito feio
                    buttons[xx].GetComponentInChildren<Text>().color = new Color32(255, 255, 0, 255);
                    buttons[xx].GetComponent<Image>().color = new Color32(255, 255, 255, 255);
                }
                else
                {
                    buttons[xx].GetComponentInChildren<Text>().color = Color.white;
                    buttons[xx].GetComponent<Image>().color = new Color32(255, 255, 255, dynamicButtonDefaultAlpha);
                }
            }
        }


        if (OnLoadPkgExternalHandler == null)
            OnLoadPkgExternalHandler = null;//StartCoroutine(MiscUtils.WaitAndLoadLevel("MainScene", 3));
        else
            OnLoadPkgExternalHandler(url);
    }


    //--------------------------------------------------------------------------------------
    public void LoadTreePackageFromExternalSource(string path)
    {
        StartCoroutine(LoadExternal(path));
    }



    //--------------------------------------------------------------------------------------
    public void LoadDefaultPackage()
    {
        LoadTreePackageFromResources();

        if (warning != null)
        {    //171011
             //warning.text = "Fases carregadas com sucesso de Pacote de fases padrao";
            warning.text = "Success loading Default Package Phases";
        }

        if (OnLoadPkgInternalHandler == null)
            StartCoroutine(MiscUtils.WaitAndLoadLevel("MainScene", 1));
        else
            OnLoadPkgInternalHandler();
    }



    //--------------------------------------------------------------------------------------
    static public void LoadTreePackageFromResources()
    {
        Package pkg;
        if (LoadedPackage.packages == null || !LoadedPackage.packages.ContainsKey("Resources/default"))
        {
            LoadedPackage.packages = new Dictionary<string, Package>();
            pkg = new Package("Resources", "default");
        }
        else
        {
            pkg = LoadedPackage.packages["Resources/default"];
        }

        foreach (string file in files)
        {
            var tree = Resources.Load("Trees/" + file) as TextAsset;
            if (tree == null)
            {
                Debug.Log(">>> error loading Resources/Trees");  //keep this error; goes to the output_log.txt
                return;
            }

            GameObject debugLoadedTrees = GameObject.FindGameObjectWithTag("debugLoadedTrees");
            if (debugLoadedTrees != null)
            {
                if (tree != null)
                    debugLoadedTrees.GetComponent<Text>().text += "Loaded: " + file + "\n";
                else
                    debugLoadedTrees.GetComponent<Text>().text += "Could not load: " + file + "\n";

            }

            string json = tree.text;
            pkg.stages.Add(json);
        }

        LoadedPackage.loaded = pkg;
    }


    // -----------------------------------------------------------------------------------------------------
    //180126 get machine/device IP and country from app by myip.com
    IEnumerator readMachineIP()
    {
        WWW myIPinfo = new WWW(getMyIP);
        yield return myIPinfo;

        if (string.IsNullOrEmpty(myIPinfo.error))
        {
            //Debug.Log ("info = " + myIPinfo.text); 
            webIPinfo IPdata = JsonUtility.FromJson<webIPinfo>(myIPinfo.text);
            PlayerPrefs.SetString("IP", IPdata.ip);
            PlayerPrefs.SetString("Country", IPdata.cc);

        }
        else
        {
            //Debug.Log ("erro ao ler myIP");  then, use Network or internetReachability
            //var ipaddress = Network.player.externalIP;  //return Intranet IP if is the case...
            //Application.internetReachability: not trustable
            PlayerPrefs.SetString("IP", "UNASSIGNED");
            PlayerPrefs.SetString("Country", "XX");
        }
    }


    // -----------------------------------------------------------------------------------------------------
    //Josi: botao SAIR na tela inicial de menu de jogos
    //180627 centralized at Localization
    //public void Sair ()   {
    //170322 unity3d tem erro ao usar application.Quit
    //       workaround: http://unity3dtrenches.blogspot.com.br/2015/10/unity-3d-compiled-game-freezes-or.html
    //Application.Quit ();
    //  if (!Application.isEditor) {  //if in the editor, this command would kill unity...
    //      if (Application.platform == RuntimePlatform.WebGLPlayer) {
    //          Application.OpenURL (PlayerPrefs.GetString ("gameURL"));
    //      }  else {
    //          //171121 not working kill()
    //          if ((Application.platform == RuntimePlatform.IPhonePlayer) || 
    //              (SystemInfo.deviceModel.Contains("iPad"))) {           //try #IF UNITY_IOS
    //              Application.Quit ();     
    //          }  else {
    //              System.Diagnostics.Process.GetCurrentProcess ().Kill (); 
    //          }
    //      }
    //  }
    //}



    // -----------------------------------------------------------------------------------------------------
    //170407 tela de créitos (pedido Carlos Ribas)
    //180614 out from team selection and goes to menu screen
    //public void showCreditos()    {
    //  SceneManager.LoadScene ("Credits");
    //}


    // -----------------------------------------------------------------------------------------------------
    //180220 to convert special characters into HTML reference code, using UTF-8
    //       https://answers.unity.com/questions/546213/handling-special-characters-aeouuouo-in-unity.html 
    //       https://www.w3schools.com/tags/ref_urlencode.asp
    public string convertPathToMobiles(string url2mobiles)
    {
        string[] symbol = new string[] { " ", "À", "Á", "Â", "Ã", "Ç", "È", "É", "Ê", "Ì", "Í", "Î", "Ñ", "Ò", "Ó", "Ô", "Õ", "Ù", "Ú", "Û", "à", "á", "â", "ã", "ç", "è", "é", "ê", "ì", "í", "î", "ñ", "ò", "ó", "ô", "õ", "ù", "ú", "û" };
        string[] symbolHTML = new string[] { "%20", "%C3%80", "%C3%81", "%C3%82", "%C3%83", "%C3%87", "%C3%88", "%C3%89", "%C3%8A", "%C3%8C", "%C3%8D", "%C3%8E", "%C3%91", "%C3%92", "%C3%93", "%C3%94", "%C3%95", "%C3%99", "%C3%9A", "%C3%9B", "%C3%A0", "%C3%A1", "%C3%A2", "%C3%A3", "%C3%A7", "%C3%A8", "%C3%A9", "%C3%AA", "%C3%AC", "%C3%AD", "%C3%AE", "%C3%B1", "%C3%B2", "%C3%B3", "%C3%B4", "%C3%B5", "%C3%B9", "%C3%BA", "%C3%BB" };

        for (var i = 0; i < symbol.Length; i++)
        {
            url2mobiles = url2mobiles.Replace(symbol[i], symbolHTML[i]);
        }
        return url2mobiles;
    }



    // -----------------------------------------------------------------------------------------------------
    public void ToGame(int error)             //170310 param error, vindo do probs.confValidation
    {
        SceneManager.LoadScene("MainScene");
    }



    // -----------------------------------------------------------------------------------------------------
    void Update()
    {
        //Josi: outra maneira de Sair, sem clicar no botã: apertar a tecla ESCAPE
        //      https://docs.unity3d.com/ScriptReference/Application.Quit.html
        //
        if (Input.GetKey("escape"))
        {
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
    }

    public class ProfileLevelJson
    {
        [JsonProperty(PropertyName = "user")]
        public int user { get; set; }

        [JsonProperty(PropertyName = "level")]
        public int level { get; set; }
    }

    public class LevelJson
    {
        [JsonProperty(PropertyName = "name")]
        public int name { get; set; }

        [JsonProperty(PropertyName = "id")]
        public int id { get; set; }
    }

    public class GameConfigJson
    {
        [JsonProperty(PropertyName = "name")]
        public string name { get; set; }

        [JsonProperty(PropertyName = "code")]
        public string groupCode { get; set; }

        [JsonProperty(PropertyName = "id")]
        public int id { get; set; }

        [JsonProperty(PropertyName = "level")]
        public int level { get; set; }
    }

    public class GameJson
    {
        [JsonProperty(PropertyName = "id")]
        public int id { get; set; }

        [JsonProperty(PropertyName = "config")]
        public int config { get; set; }

        [JsonProperty(PropertyName = "number_of_directions")]
        public int number_of_directions { get; set; }

        [JsonProperty(PropertyName = "number_of_plays")]
        public int? number_of_plays { get; set; }

        [JsonProperty(PropertyName = "min_hits")]
        public int? min_hits { get; set; }

        [JsonProperty(PropertyName = "min_hits_in_seq")]
        public int? min_hits_in_seq { get; set; }

        [JsonProperty(PropertyName = "sequence")]
        public string sequence { get; set; }

        [JsonProperty(PropertyName = "read_seq")]
        public bool read_seq { get; set; }

        [JsonProperty(PropertyName = "plays_to_relax")]
        public int plays_to_relax { get; set; }

        [JsonProperty(PropertyName = "play_pause")]
        public bool play_pause { get; set; }

        [JsonProperty(PropertyName = "play_pause_key")]
        public string play_pause_key { get; set; }

        [JsonProperty(PropertyName = "player_time")]
        public float speedGKAnim { get; set; }

        [JsonProperty(PropertyName = "celebration_time")]
        public float celebration_time { get; set; }

        [JsonProperty(PropertyName = "score_board")]
        public bool score_board { get; set; }

        [JsonProperty(PropertyName = "final_score_board")]
        public string final_score_board { get; set; }

        [JsonProperty(PropertyName = "game_type")]
        public string game_type { get; set; }

        [JsonProperty(PropertyName = "left_key")]
        public string left_key { get; set; }

        [JsonProperty(PropertyName = "center_key")]
        public string center_key { get; set; }

        [JsonProperty(PropertyName = "right_key")]
        public string right_key { get; set; }

        [JsonProperty(PropertyName = "phase")]
        public int phase { get; set; }

        [JsonProperty(PropertyName = "depth")]
        public int? depth { get; set; }

        [JsonProperty(PropertyName = "seq_step_det_or_prob")]
        public string seq_step_det_or_prob { get; set; }

        [JsonProperty(PropertyName = "show_history")]
        public bool show_history { get; set; }

        [JsonProperty(PropertyName = "send_markers_eeg")]
        public string send_markers_eeg { get; set; }

        [JsonProperty(PropertyName = "port_eeg_serial")]
        public string port_eeg_serial { get; set; }
    }

    public class ContextJson
    {
        [JsonProperty(PropertyName = "id")]
        public int id { get; set; }

        [JsonProperty(PropertyName = "path")]
        public string path { get; set; }

        [JsonProperty(PropertyName = "goalkeeper")]
        public int goalkeeper { get; set; }
    }

    public class ProbabilityJson
    {
        [JsonProperty(PropertyName = "id")]
        public int id { get; set; }

        [JsonProperty(PropertyName = "context")]
        public int context { get; set; }

        [JsonProperty(PropertyName = "direction")]
        public int direction { get; set; }

        [JsonProperty(PropertyName = "value")]
        public float value { get; set; }
    }

    public int GetPlayerLevel()
    {
        string address = string.Format("localhost:8000/api/getplayerlevel?format=json&token={0}", PlayerInfo.token);
        var request = new WWW(address);

        StartCoroutine(WaitForWWW(request));
        while (!request.isDone) { }

        var ObjList = new List<ProfileLevelJson>();
        ObjList = JsonConvert.DeserializeObject<List<ProfileLevelJson>>(request.text);

        if (ObjList != null)
        {
            PlayerInfo.level = ObjList[0].level;
            return PlayerInfo.level;
        }
        else
        {
            return 0;
        }
    }

    // Pega o objeto nível de acordo com o id (que é gravado no custom_user e na
    // configuração de um jogo) e/ou com o nome do nível. Nível não está relacionado
    // com a fase e sim com a dificuldade de um adversário.
    public List<LevelJson> GetLevel(int? level_id = null, int? level_name = null)
    {
        string address = "localhost:8000/api/getlevel?format=json";
        if (level_id != null)
        {
            address = address + string.Format("&id={0}", level_id);
        }
        if (level_name != null)
        {
            address = address + string.Format("&name={0}", level_name);
        }

        var request = new WWW(address);

        StartCoroutine(WaitForWWW(request));
        while (!request.isDone) { }

        var ObjList = new List<LevelJson>();
        ObjList = JsonConvert.DeserializeObject<List<LevelJson>>(request.text);
        return ObjList;
    }

    // Pega todas as configurações de jogos (tabela game.gameconfig) com level
    // menor ou igual ao level do jogador.
    public List<GameConfigJson> GetGamesConfig(int level=0, string name = null)
    {
        string address = "localhost:8000/api/getgamesconfig?format=json";
        if (level > 0)
        {
            address = address + string.Format("&level={0}", level);
            Debug.Log(level);
        }
        if (name != null)
        {
            address = address + string.Format("&name={0}", System.Uri.EscapeDataString(name));
            Debug.Log(address);
        }
        Debug.Log(address);

        var request = new WWW(address);

        StartCoroutine(WaitForWWW(request));
        while (!request.isDone) { }

        var ObjList = new List<GameConfigJson>();
        ObjList = JsonConvert.DeserializeObject<List<GameConfigJson>>(request.text);
        Debug.Log("serializou");
        return ObjList;
    }

    // Pega o jogo associado a uma configuração cujo id é dado
    public List<GameJson> GetGame(int config_id)
    {
        string address = string.Format("localhost:8000/api/getgames?format=json&config_id={0}", config_id);
        var request = new WWW(address);

        StartCoroutine(WaitForWWW(request));
        while (!request.isDone) { }

        var ObjList = new List<GameJson>();
        ObjList = JsonConvert.DeserializeObject<List<GameJson>>(request.text);
        return ObjList;
    }

    void SaveIDsofGamesforResults(string config_name, GameJson game)
    {
        games_ids.Add(config_name+game.phase.ToString(), game.id);
    }

    void SavePhasestoPlayPrefs(string config_name)
    {

        var i = 0;

        // Para cada valor gravado na lista de ids de fases de jogos, verifique
        // se faz parte do time que o jogador escolheu e caso positivo, grave-o
        foreach(KeyValuePair<string, int> game_id in games_ids)
        {
            if (game_id.Key == config_name + i.ToString())
            {
                PlayerPrefs.SetInt(config_name + i.ToString(), game_id.Value);
                i++;
            }
        }
    }

    void SaveConfigLeveltoPlayPrefs(string config_name)
    { 
        var game_config = GetGamesConfig(name: config_name);
        var level = GetLevel(game_config[0].level);
        PlayerPrefs.SetInt("game_level_name", level[0].name); // Salva o nome, que é o valor sequencial do level
    }

    void SaveIndexInfo(string path, List<GameConfigJson> games)
    {
        List<string> names = new List<string>();
        foreach (GameConfigJson game in games)
        {
            names.Add(game.name);
        }

        var teamslist = String.Join(";", names.ToArray());

        System.IO.File.WriteAllText(path+"/index.info", teamslist);
    }

    // Pega os contextos associados ao jogo, cujo id é dado
    public List<ContextJson> GetContexts(int game_id)
    {
        string address = string.Format("localhost:8000/api/getcontexts?format=json&game={0}", game_id);
        var request = new WWW(address);

        StartCoroutine(WaitForWWW(request));
        while (!request.isDone) { }

        var ObjList = new List<ContextJson>();
        ObjList = JsonConvert.DeserializeObject<List<ContextJson>>(request.text);
        return ObjList;
    }

    // Pega a probabilidade associada a um contexto em uma dada direção
    public float GetProb(int context_id, int direction)
    {
        string address = string.Format("localhost:8000/api/getprobs?format=json&context={0}&direction={1}", context_id, direction);
        var request = new WWW(address);

        StartCoroutine(WaitForWWW(request));
        while (!request.isDone) { }

        var ObjList = new List<ProbabilityJson>();
        ObjList = JsonConvert.DeserializeObject<List<ProbabilityJson>>(request.text);
        return ObjList[0].value;
    }

    IEnumerator WaitForWWW(WWW www)
    {
        yield return www;
    }

    //public TreeJson CreateTree(GameConfigJson config, GameJson game, List<ContextJson> contexts)
    //{
    //    var tree = 
    //    var states = new List<JsonStateInput>();

    //}

    public List<JsonStateInput> CreateStates(List<ContextJson> contexts)
    {
        var states = new List<JsonStateInput>();

        foreach (ContextJson context in contexts)
        {
            var state = new JsonStateInput();
            state.path = context.path;
            state.probEvent0 = GetProb(context.id, 0).ToString();
            state.probEvent1 = GetProb(context.id, 1).ToString();

            states.Add(state);
        }
        return states;
    }

    public FirstTreeJson CreateFirstTree(GameConfigJson config, GameJson game, List<ContextJson> contexts)
    {
        var tree = new FirstTreeJson();
        tree.id = config.name;
        tree.limitPlays = game.number_of_plays;
        tree.choices = game.number_of_directions;
        tree.depth = game.depth;
        tree.readSequ = game.read_seq;
        tree.sequ = game.sequence;
        tree.sequR = game.seq_step_det_or_prob;
        tree.minHits = game.min_hits;
        tree.minHitsInSequence = game.min_hits_in_seq;
        tree.animationTypeJG = "short";//game.celebration_time;
        tree.animationTypeOthers = "short";//game.celebration_time;
        tree.scoreboard = game.score_board;
        tree.finalScoreboard = game.final_score_board;
        tree.playsToRelax = game.plays_to_relax;
        tree.showHistory = game.show_history;
        tree.speedGKAnim = game.speedGKAnim;

        tree.states = CreateStates(contexts);

        tree.sendMarkersToEEG = game.send_markers_eeg;
        tree.portalEEGserial = game.port_eeg_serial;
        tree.showPlayPauseButton = game.play_pause;
        tree.leftInputKey = game.left_key;
        tree.centerInputKey = game.center_key;
        tree.rightInputKey = game.right_key;
        tree.pausePlayInputKey = game.play_pause_key;
        tree.institution = "neuromat";
        tree.attentionPoint = false;
        tree.attentionDiameter = 0.8;
        tree.attentionColorStart = "#FFF";
        tree.attentionColorCorrect = "#00F";
        tree.attentionColorWrong = "#333";
        tree.groupCode = config.groupCode;

        var menu = new List<MenuJson>();
        menu.Add(new MenuJson { game = 1, title = "Aquecimento", sequMenu = "0" }); // Adicionando dois tipos de jogo pois a tela de tutorial não exibe quando só tem um tipo
        menu.Add(new MenuJson { game = 2, title = "Jogo do Goleiro", sequMenu = "1" });

        tree.menus = menu;

        return tree;
    }

    public TreeJson CreateTree(GameConfigJson config, GameJson game, List<ContextJson> contexts)
    {
        var tree = new TreeJson();
        tree.id = config.name;
        tree.limitPlays = game.number_of_plays;
        tree.choices = game.number_of_directions;
        tree.depth = game.depth;
        tree.readSequ = game.read_seq;
        tree.sequ = game.sequence;
        tree.sequR = game.seq_step_det_or_prob;
        tree.minHits = game.min_hits;
        tree.minHitsInSequence = game.min_hits_in_seq;
        tree.animationTypeJG = "short"; //game.celebration_time;
        tree.animationTypeOthers = "short"; //game.celebration_time;
        tree.scoreboard = game.score_board;
        tree.finalScoreboard = game.final_score_board;
        tree.playsToRelax = game.plays_to_relax;
        tree.showHistory = game.show_history;
        tree.speedGKAnim = game.speedGKAnim;

        tree.states = CreateStates(contexts);

        return tree;
    }

    void DeleteCustomTrees()
    {
        string url;

        if (Directory.Exists(Application.streamingAssetsPath + "/CustomTrees/"))
        {
            url = Application.streamingAssetsPath + "/CustomTrees/";
        }
        else
        {
            url = Application.dataPath + "/CustomTrees/";
        }

        Directory.Delete(url, true);
    }

    string CreateCustomTreesDirectory()
    {
        string c_trees;

        if ((Application.platform == RuntimePlatform.Android) ||
              (Application.platform == RuntimePlatform.IPhonePlayer) || (SystemInfo.deviceModel.Contains("iPad")))
        {
            c_trees = Application.streamingAssetsPath + "/CustomTrees/";
        }
        else
        {
            c_trees = Application.dataPath + "/CustomTrees/";
        }

        if (!Directory.Exists(c_trees))
        {
            Directory.CreateDirectory(c_trees);
        }
        else
        {
            Directory.Delete(c_trees, true);
            Directory.CreateDirectory(c_trees);
        }

        return c_trees;
    }

    void CreateTreeDirAndFile(string path, string filename, object tree)
    {
        if (!Directory.Exists(path))
        {
            Directory.CreateDirectory(path);
        }

        using (StreamWriter file = File.CreateText(path + filename))
        {
            //JsonTextWriter writer = new JsonTextWriter(file);
            file.Write(JsonConvert.SerializeObject(tree));
        }
    }
}

public class Package
{
    public string path;
    public string name;

    // Initializes a new instance of the <see cref="Package"/> class.
    public Package(string _path, string _name)
    {
        path = _path;
        name = _name;
        stages = new List<string>();
    }

    public List<string> stages;
}

public static class LoadedPackage
{
    public static Dictionary<string, Package> packages;
    public static Package loaded;
}

public struct SourcePath
{
    public string url;
    public SourceType sourceType;
}


public enum SourceType { web, file };