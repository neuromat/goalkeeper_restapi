/************************************************************************************/
// Module written by scaroni <renato.scaroni@gmail.com>
// Rewrited by Josi Perez <josiperez.neuromat@gmail.com>
//
// This module manages the data collection on the log. It initializes the form and
// saves the data on the PlayerInfo class for later persistance on remote DB
/************************************************************************************/

using UnityEngine;
using UnityEngine.UI;               //toggles
using System.Collections;
using UnityEngine.SceneManagement;  //171005 LoadScene
using TMPro;                        //171009 textMesh Pro (justified text and many other resources)

//using System.Media.Sounds;    //Josi: for SystemSounds (using UnityEditor; vale no editor não em build): https://forum.unity3d.com/threads/beep.180045/
//using UnityEngine.EventSystems; //Josi: para dar foco no apelido, ver em https://www.reddit.com/r/Unity3D/comments/2nom92/forcing_focus_on_input_field_in_46/

//@ale Save Data 
using System.Collections.Generic;
using System;
using System.Runtime.Serialization.Formatters.Binary;
using System.IO;



public class TCLE: MonoBehaviour 
{
	//public GameObject userData;                 //@@@Josi: IntroScene(1)/Canvas/LogBox/MenuGameMode
	public GameObject TCLEbox;	//@ale : para chamar a tela do termo;
	public GameObject userData; //@ale : para chamar a tela de entrada de dados do usuario;
	public GameObject botaoCarregaPerfil;




	public Text obrigaAlias;                    //Josi: para ligar msg apenas se apelido vazio 
	//@@private GameFlowManager gameFlowManager;    //Josi para continuar o jogo apos preencher dados


	//@ale Save data =========================================================================

	public string VariavelTexto; //Variavel que vai ser salva
	public bool VariavelBooleana1; //Variavel que vai ser salva
	public bool VariavelBooleana2; //Variavel que vai ser salva

	[Header("Configurações")]
	public string DiretorioDoArquivo;
	public string FormatoDoArquivo = "dat";
	public string NomeDoArquivo;

	[Header("Elementos da UI")]
	public InputField alias;
	public Text NomePerfilDoUsuario;
	public Toggle agree;                        //170829 TCLE concorda 
	public Toggle notAgree;                     //170830      ou não
	public ColorBlock agreeOriginalColors;      //170926 guardar as cores originais (qdo user muda de decisao)
	public ColorBlock notAgreeOriginalColors;   //170926 guardar as cores originais (qdo user muda de decisao)
	public InputField Diretorio;

	//public InputField CampoTexto;

	[Serializable] //Nessa parte nós meio que formatamos o nosso arquivo, criando uma classse para isso. Aqui criamos as variaveis que serão adicionadas ao arquivo, e vale notar que você pode repetir nome de variaveis, desde que uma delas esteja fora dessa classe.
	class DadosDoJogo
	{
		public string String;
		public bool Bool1;
		public bool Bool2;
	}

	//=========================================================================================

	static private TCLE _instance;
	static public TCLE instance
	{
		get
		{
			if (_instance == null)
			{
				_instance = GameObject.Find("TCLE").GetComponent<TCLE>();
			}

			return _instance;
		}
	}



	//Josi 170817
	#if UNITY_ANDROID || UNITY_IOS
	private TouchScreenKeyboard mobileKeyboard;     
	#endif
	public bool isKeyboardOpen = false;         //180220 start keyboard on mobile devices

	private LocalizationManager translate;      //171009 trazer script das rotinas de translation

	//171009 translation
    //180625 screen TCLE/alias comes after language selection, not more between gameMenu and gameModule
	public Text preenchaNome;
    public Text btnAvancar;
	public Text txtTermo;
	public Text txtSobre;
	public Text txtAvancar;
	public Text txtVoltarIdioma;
    //public Text btnJogar;
	//public Text btnJogarPausa;
	//public Text btnMenu;
	public Text placeholder;
	//public Text tcleHeader;
	public Text tcleNotAgree;
	public Text tcleAgree;
	public GameObject tcleText;                //180625 now, a TMPro justified, not TextUI



	// -----------------------------------------------------------------------------------------------------
	// Checks if there is anything entered into the input field.
	public void LockInput(InputField input)	
	{
		if (input.text.Trim().Length == 0)  {   
			obrigaAlias.text = translate.getLocalizedValue ("obrigaAlias"); //171011 necessary fill playerAlias
			alias.Select();
			alias.ActivateInputField();
		}
	}



	// -----------------------------------------------------------------------------------------------------
	public void EnterData()
	{   
		if (alias.text.Trim().Length == 0) {           //to avoid fill with spaces
			obrigaAlias.text = translate.getLocalizedValue ("obrigaAlias"); //171011 necessary fill playerAlias

			//180220 problem to open keyboard on iOS; navigation vertical on inspector
			#if UNITY_ANDROID || UNITY_IOS
			//		if (! isKeyboardOpen) {
			//			isKeyboardOpen = true;
			//			mobileKeyboard = TouchScreenKeyboard.Open(alias.text, TouchScreenKeyboardType.Default, false, false, false, false, "");
			//		}
			//		if(mobileKeyboard.done == true)	{
			//			alias.text = mobileKeyboard.text;
			//			mobileKeyboard = null;
			//		} else {
			//			alias.text = mobileKeyboard.text;
			//		}
			#else
			alias.Select();
			alias.ActivateInputField();
			#endif
		} else {
			//170830 necessary to inform if agree or not in participate of the search
			if (!(agree.isOn || notAgree.isOn)) {
				//171011 obrigaAlias.text = "Por favor, informe sua concordância!";  
				obrigaAlias.text = translate.getLocalizedValue ("obrigaTCLE");
			} else {
				PlayerInfo.alias = alias.text;
				//@@@userData.SetActive (false);

                //180625 logUsers was after select a game module and now, after select idiom
                //@@gameFlowManager.NewGame (PlayerPrefs.GetInt ("gameSelected"));    //Josi: antes havia esta continuidade no onClick Unity, agora passa para ca para poder reclamar do apelido vazio
                SceneManager.LoadScene("Configurations");
            }
		}
	}




	// -----------------------------------------------------------------------------------------------------
	void Start () 
	{   //161205 pedir apenas nome
		//PlayerInfo.gender = "M";
		//PlayerInfo.education = "Fundamental Completo";
		//PlayerInfo.destro = "D";


		//171009 declarar a instance para permitir chamar rotinas do outro script
		translate = LocalizationManager.instance;

		//171009 translate
		preenchaNome.text = translate.getLocalizedValue ("preenchaNome");
		//btnJogar.text = translate.getLocalizedValue ("btnJogar");
		//btnJogarPausa.text = translate.getLocalizedValue ("btnJogarPausa");
		//btnMenu.text = translate.getLocalizedValue ("btnMenu");
		placeholder.text = translate.getLocalizedValue ("placeholder");
		//tcleHeader.text = translate.getLocalizedValue ("tcleHeader");
		tcleNotAgree.text = translate.getLocalizedValue ("tcleNotAgree");
		tcleAgree.text = translate.getLocalizedValue ("tcleAgree");
		txtTermo.text = translate.getLocalizedValue ("txtTermo");
		txtSobre.text = translate.getLocalizedValue ("txtSobre");
		txtAvancar.text = translate.getLocalizedValue ("txtAvancar");
		txtVoltarIdioma.text = translate.getLocalizedValue ("txtVoltarIdioma");

        //180625 from UiText to TMPro
		//tcleText.text = translate.getLocalizedValue ("tcle").Replace("\\n","\n");
        tcleText.GetComponentInChildren<TMPro.TMP_Text>().text = translate.getLocalizedValue("tcle").Replace("\\n", "\n");


        //Josi: declare GameFlowManager to continue if data filled
        //@@gameFlowManager = GameFlowManager.instance;

        //170926 salvar as cores originais do toggle concorda/naoConcorda
        agreeOriginalColors = agree.colors;
		notAgreeOriginalColors = notAgree.colors;

		/* @ale - deixou de ter sentido em funcao de multiplos perfis, entao nao há como mostrar/nao mostrar o botao
		 * de carregar perfil. A verificao so tera sentido na proxima etapa, depois que o usuario clicar em Salvar
		if (verificaPerfil() != null) {
			Debug.Log ("NomePerfil"+verificaPerfil());
			botaoCarregaPerfil.SetActive (true);
			NomePerfilDoUsuario.text = verificaPerfil ();
		}
			else { 
			Debug.Log ("NomePerfil"+verificaPerfil());
			botaoCarregaPerfil.SetActive (false); 
		}
		*/

	}


	//@ale Save Data =============================================================================================

	public void Save() //Void que salva
	{
		/* @ale : Antes de Salvar o perfil, é necessario que o sistema verifique se já nao existe alguem com esse
		 * perfil. Se houver, entao nada é gravado. E se for um novo, entao o arquivo é criado. */



		PlayerPrefs.SetString("nomePerfil", VariavelTexto);


		/* Se usar um Perfil diferente, entao a tabela de Premios deve ser zerada ja que se trata de outro jogador
		if (verificaPerfil () != VariavelTexto) {
			ApagaSavePremios ();
		}
		*/

		if (verificaPerfil() != VariavelTexto)
		{
			Debug.Log ("Perfil NOVO salvo");
			BinaryFormatter binario = new BinaryFormatter();
			FileStream arquivo = File.Create(DiretorioDoArquivo); //Aqui, criamos o arquivo
			DadosDoJogo dados = new DadosDoJogo(); //"DadosDoJogo" é o nome da classe que iremos acessar, ao qual criamos anteriormente
			//dados.Int = VariavelInteira; //"dados.Int", é assim que acessamos uma variavel da nossa classe, para setar o valor dela, daí é só pegar e igualar com uma variavel do seu script.
			//dados.Float = VariavelDecimal;
			dados.String = VariavelTexto;
			dados.Bool1 = VariavelBooleana1;
			dados.Bool2 = VariavelBooleana2;

			binario.Serialize(arquivo, dados);
			arquivo.Close(); //Aqui terminamos a leitura do arquivo.

		}
		else {
			Debug.Log ("Perfil existente NAO salvo");
		}
	}

	/* @ale : tambem deixa de ter sentido, ja que nenhm perfil sera carregado
	public void Load() // Void que carrega
	{
		if (File.Exists(DiretorioDoArquivo) == true) //Aqui verificamos se existe um arquivo para ser carregado. se existir, prosseguimos
		{
			BinaryFormatter binario = new BinaryFormatter();
			FileStream arquivo = File.Open(DiretorioDoArquivo, FileMode.Open); //Aqui abrimos o arquivo
			DadosDoJogo dados = (DadosDoJogo)binario.Deserialize(arquivo); //Aqui meio que descriptografamos o arquivo

			//VariavelInteira = dados.Int; //Aqui pegamos o valor salvo no arquivo e trazemos para nosso script.
			//VariavelDecimal = dados.Float;
			VariavelTexto = dados.String;
			alias.text = VariavelTexto;

			VariavelBooleana1 = dados.Bool1;
			agree.isOn = VariavelBooleana1;

			VariavelBooleana2 = dados.Bool2;
			notAgree.isOn = VariavelBooleana2;

			arquivo.Close(); //Aqui fechamos a leitura
		}
	}
	*/


	public string verificaPerfil () // Verifica se existe o perfil gravado 
	{
		NomeDoArquivo = "salvaPerfil-" + VariavelTexto;
		DiretorioDoArquivo = Application.persistentDataPath + "/" + NomeDoArquivo + "." + FormatoDoArquivo; //Aqui é definido o local de save, para o jogo.

		if (File.Exists (DiretorioDoArquivo) == true) {
			Debug.Log ("Perfil Ja existe");
			BinaryFormatter binario = new BinaryFormatter ();
			FileStream arquivo = File.Open (DiretorioDoArquivo, FileMode.Open); //Aqui abrimos o arquivo
			DadosDoJogo dados = (DadosDoJogo)binario.Deserialize (arquivo); //Aqui meio que descriptografamos o arquivo
			string NomePerfil = dados.String;
			arquivo.Close (); //Aqui fechamos a leitura
			return NomePerfil;
		}

		else { 
			Debug.Log ("Perfil NAO existe"); 
			string NomePerfil = null;
			return NomePerfil;
		
		}
			

	}



	public void ApagaSavePremios () // Verifica se existe o perfil gravado 
	{
		//DiretorioDoArquivo = Application.persistentDataPath + "/" + NomeDoArquivo + "." + FormatoDoArquivo; //Aqui é definido o local de save, para o jogo.

		if (File.Exists (DiretorioDoArquivo) == true) { //Aqui verificamos se existe um arquivo para ser carregado. se existir, prosseguimos
			//BinaryFormatter binario = new BinaryFormatter ();
			//FileStream arquivo = File.Open (DiretorioDoArquivo, FileMode.Open); //Aqui abrimos o arquivo
			//arquivo.Close ();


			string apagaArquivo = Application.persistentDataPath + "/savePremios.dat"; 
			Debug.Log ("apagaArquivo --> " + apagaArquivo);

			File.Delete(apagaArquivo);


		}

	}

	// ========================================================================================


	// -----------------------------------------------------------------------------------------------------
	void Update () {
		//Josi 170817
		#if UNITY_ANDROID || UNITY_IOS
//		if (! isKeyboardOpen) {
//			isKeyboardOpen = true;
//			mobileKeyboard = TouchScreenKeyboard.Open(alias.text, TouchScreenKeyboardType.Default, false, false, false, false, "");
//		}
//		if(mobileKeyboard.done == true)	{
//			alias.text = mobileKeyboard.text;
//			mobileKeyboard = null;
//		} else {
//			alias.text = mobileKeyboard.text;
//		}
		#else
		alias.Select();
		alias.ActivateInputField();
		#endif

		//@ale Save Data ==========================================================================
		NomeDoArquivo = "salvaPerfil-" + VariavelTexto;
		DiretorioDoArquivo = Application.persistentDataPath + "/" + NomeDoArquivo + "." + FormatoDoArquivo; //Aqui é definido o local de save, para o jogo.
		//Detalhe: "Application.persistentDataPath" é o local base onde o arquivo é salvo. Ele varia de plataforma para plataforma e de dispositivo para dispositivo. A unica coisa que não muda é o nome e formato do arquivo do seu save.

		//Daqui para baixo são só scripts da UI

		//Inteira.text = VariavelInteira.ToString();
		//Decimal.text = VariavelDecimal.ToString();

		//VariavelBooleana = Marcador.isOn;
		VariavelTexto = alias.text;
		VariavelBooleana1 = agree.isOn;
		VariavelBooleana2 = notAgree.isOn;
		Diretorio.text = DiretorioDoArquivo;

		// ========================================================================================
	}


	// -----------------------------------------------------------------------------------------------------
	//170829 TCLE: setar Concordo/Não concordo; se N, não se podem gravar os resultados!
	public void tcleOptionChoosed() {

		//170830 save to ask before send to write file in uiManager.SendEventsToServer (if not isOn do not record!)
		PlayerInfo.agree = agree.isOn;

		//170925 bold selected option and it is necessary to think that user can change again
		ColorBlock tmp;
		if (agree.isOn) { 
			tmp = agreeOriginalColors;
			tmp.normalColor = tmp.highlightedColor;
			agree.colors = tmp;  //verde (ok)

			notAgree.colors = notAgreeOriginalColors;
		} else {
			tmp = notAgreeOriginalColors;
			tmp.normalColor = tmp.highlightedColor;
			notAgree.colors = tmp;  //vermelho (nok)

			agree.colors = agreeOriginalColors;
		}
	}




	// -----------------------------------------------------------------------------------------------------
	void OnEnable()
	{   
        //@@@@ como resolver agora....
		//if (PlayerInfo.alias == System.String.Empty) {      //170216 Use System.String.Empty instead of "" when dealing with lots of strings;)
		//	if (!PlayerPrefs.	HasKey ("gameSelected")) {
		//		userData.SetActive (false);
		//	} else {
		//		userData.SetActive (true);
		//	}
		//} else {
		//	userData.SetActive (false);
		//}
	}



	//@ale : chaama a tela do Termo de Consentimento

	public void Termo () {
		StartCoroutine (TermoOn ());
	}

	IEnumerator TermoOn() {
	
		//Canvas.SetActive (true);
		TCLEbox.SetActive (true);
		userData.SetActive (false);
		yield return new WaitForSeconds (2);	

	}

	//@ale : Sair do Termo

	public void SairTermo () {
		StartCoroutine (SairTermoOn ());
	}


	IEnumerator SairTermoOn() {

		TCLEbox.SetActive (false);
		userData.SetActive (true);
		yield return new WaitForSeconds (2);	

	}


}
