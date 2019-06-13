// Copyright (c) 2015 Eamon Woortman
//
// Permission is hereby granted, free of charge, to any person
// obtaining a copy of this software and associated documentation
// files (the "Software"), to deal in the Software without
// restriction, including without limitation the rights to use,
// copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following
// conditions:
//
// The above copyright notice and this permission notice shall be
// included in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
// OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
// NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
// OTHER DEALINGS IN THE SOFTWARE.

#define UNITY_4_PLUS
#define UNITY_5_PLUS

#if UNITY_4_0 || UNITY_4_1 || UNITY_4_2 || UNITY_4_3 || UNITY_4_4 || UNITY_4_5 || UNITY_4_6 || UNITY_4_7 || UNITY_4_8 || UNITY_4_9
    #define UNITY_4_X
    #undef UNITY_5_PLUS
#elif UNITY_5_0 || UNITY_5_1 || UNITY_5_2 || UNITY_5_3 || UNITY_5_4 || UNITY_5_5 || UNITY_5_6 || UNITY_5_7 || UNITY_5_8 || UNITY_5_9
    #define UNITY_5_X
#endif

using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;
using UnityEngine.SceneManagement;
using UnityEngine.EventSystems;

public class LoginMenu : BaseMenu {
    
    public delegate void LoginFailed(string errorMsg);
    public delegate void SignupFailed(string errorMsg);
    public delegate void SignupSuccess();

    private LocalizationManager translate, translateAux;
    private EventSystem eventSystem;
    public InputField nextField;
    
    private string authenticationToken = "";
    
    public delegate void LoggedIn();
    public LoggedIn HasLoggedIn;
    public LoggedIn OnLoggedIn;
    public LoginFailed OnLoginFailed;
    public SignupSuccess OnSignupSuccess;
    public SignupFailed OnSignupFailed;

    private string user;
    private string pass;
    private string titJanLogin;
    private string labelInfoLog;
    private string errorLogin;
    private string errorSigns;
    private string errorOnReadTerm;
    public string errorOptAccess;
    private string statusLog;
    private string enterButton;
    private string newCadButton;
    
    private const float LABEL_WIDTH = 110;
    private bool loggingIn = false;
    private bool rememberMe = false;
    private bool hasFocussed = false;
    private int dotNumber = 1;
    private float nextStatusChange;
    private string status = "";
    private string username = "", password = "";
    //private SignupMenu signupMenu;

    public GameObject userLogin;
    public GameObject passwdLogin;
    public GameObject userRegister;
    public GameObject passwdRegister;
    public GameObject confpasswdRegister;
    public GameObject email;
    public GameObject labelNovaConta;
    public GameObject labelConcordo;

    [SerializeField]
    private string Username = null;
    [SerializeField]
    private string Password = null;
    [SerializeField]
    private string UsernameR = null;
    [SerializeField]
    private string PasswordR = null;
    [SerializeField]
    private string ConfPassword = null;
    [SerializeField]
    private string Email = null;
    [SerializeField]
    public Text Mensagem;
    [SerializeField]
    public Text txtTermo;
    [SerializeField]
    private Toggle remember = null;
    [SerializeField]
    private Toggle toggleC;
    [SerializeField]
    private string errorOptAccess;
    
    public Text txtAvancar;
    public Text txtVoltarIdioma;

    private string form;
    private bool EmailValid=false;

    public delegate void RequestResponseDelegate(ResponseType responseType, JToken jsonResponse, string callee);
    //---- Public Properties ----//
    public string BackendUrl {
        get {
            return UseProduction ? ProductionUrl : DevelopmentUrl;
        }
    }

    //---- URLS ----//
    public bool UseProduction = false;
    public bool Secure;
    public string ProductionUrl = "http://foobar:8000/api/";
    public string DevelopmentUrl = "http://localhost:8000/api/";


    private void Start() {
        
        translate = LocalizationManager.instance;
        this.eventSystem = EventSystem.current;
        
        user = translate.getLocalizedValue ("user");	
        pass = translate.getLocalizedValue ("pass");	
        titJanLogin = translate.getLocalizedValue ("titJanLogin");
        labelInfoLog = translate.getLocalizedValue ("labelInfoLog");
     
        statusLog = translate.getLocalizedValue ("statusLog");
        enterButton = translate.getLocalizedValue ("enterButton");
        newCadButton = translate.getLocalizedValue ("newCadButton");
        
     //   backendManager.OnLoggedIn += OnLoggedIn;
     //   backendManager.OnLoginFailed += OnLoginFailed;
        userLogin.GetComponent<InputField>().placeholder.GetComponent<Text>().text = translate.getLocalizedValue ("user");
        passwdLogin.GetComponent<InputField>().placeholder.GetComponent<Text>().text = translate.getLocalizedValue ("pass");
        userRegister.GetComponent<InputField>().placeholder.GetComponent<Text>().text = translate.getLocalizedValue ("user");
        passwdRegister.GetComponent<InputField>().placeholder.GetComponent<Text>().text = translate.getLocalizedValue ("pass");
        confpasswdRegister.GetComponent<InputField>().placeholder.GetComponent<Text>().text = translate.getLocalizedValue("repeatSign");
        labelNovaConta.GetComponent<Text>().text = translate.getLocalizedValue ("titJanSignup");
        labelConcordo.GetComponent<Text>().text = translate.getLocalizedValue ("termAssigned");
        txtTermo.GetComponent<Text>().text = translate.getLocalizedValue ("term");
        txtAvancar.GetComponent<Text>().text = translate.getLocalizedValue ("buttForward");
        txtVoltarIdioma.GetComponent<Text>().text = translate.getLocalizedValue ("buttBackward");
        errorLogin = translate.getLocalizedValue ("errorLogin");
        errorOnReadTerm = translate.getLocalizedValue ("errorOnReadTerm");
        errorOptAccess = translate.getLocalizedValue ("errorOptAccess");
        
        Debug.Log("errorOptAccess = " + errorOptAccess);

        if (PlayerPrefs.HasKey("x1")) {
//            username = PlayerPrefs.GetString("x2").FromBase64();
//            password = PlayerPrefs.GetString("x1").FromBase64();
            rememberMe = true;
        }
    }

    private void OnSignupCancelOrSuccess() {
        enabled = true;
    }
    
    private void SaveCredentials() {
 //       PlayerPrefs.SetString("x2", username.ToBase64());
 //       PlayerPrefs.SetString("x1", password.ToBase64());
    }

    private void RemoveCredentials() {
 //       if (PlayerPrefs.HasKey("x1")) {
 //           PlayerPrefs.DeleteAll();
 //       }
    }
//   private void OnLoginFailed(string error) {
////        status = "Login error: " + error;
////        status = errorLogin + error;
//        status = error;
//        loggingIn = false;
//   }

//    private void OnLoggedIn() {
////        status = "Logged in!";
//        StartCoroutine(statusMsg(statusLog));
//        loggingIn = false;
//
//        if (rememberMe) {
//            SaveCredentials();
//       } else {
//            RemoveCredentials();
//        }

//        if (HasLoggedIn != null) {
//            HasLoggedIn();
//        }
//    }

 
    public void DoLogin() {
        if (loggingIn) {
            Debug.LogWarning("Already logging in, returning.");
            StartCoroutine(statusMsg("Already logging in, returning."));
            return;
        }
        loggingIn = true;

        if (Input.GetKeyDown(KeyCode.Tab)){
            if (userLogin.GetComponent<InputField> ().isFocused) {
                passwdLogin.GetComponent<InputField> ().Select ();
                print("email");
            }
            if (passwdLogin.GetComponent<InputField> ().isFocused) {
                confpasswdRegister.GetComponent<InputField> ().Select ();
                print("password");
            }
            if (confpasswdRegister.GetComponent<InputField> ().isFocused) {
                email.GetComponent<InputField> ().Select ();
                print("confpassword");
            }
        }

        Username = userLogin.GetComponent<InputField> ().text;
        Password = passwdLogin.GetComponent<InputField> ().text;
        UsernameR = userRegister.GetComponent<InputField> ().text;
        PasswordR = passwdRegister.GetComponent<InputField> ().text;
        ConfPassword = confpasswdRegister.GetComponent<InputField> ().text;
        Email = email.GetComponent<InputField> ().text;
        
        
        Debug.Log("Username = " + Username);
        Debug.Log("Password = " + Password);
        Debug.Log("UsernameR = " + UsernameR);
        Debug.Log("PasswordR = " + PasswordR);
        Debug.Log("ConfPassword = " + ConfPassword);
        Debug.Log("Email = " + Email);

       
        if (Username == "" && Password == "" && UsernameR != "" && PasswordR != "" && Email != "" && ConfPassword != ""){
            if (PasswordR != ConfPassword)
                StartCoroutine(statusMsg(errorSigns));
            else if (toggleC.GetComponent<Toggle>().isOn)
                Signup(UsernameR, Email, PasswordR);
            else    
                StartCoroutine(statusMsg(errorOnReadTerm));
        }
        else
        {
            if (Username != "" && Password != "" && UsernameR == "" && PasswordR == "" && Email == "" &&
                ConfPassword == "")
                Login(Username, Password);
            else
            {
                Debug.Log("errorOptAccess1 = " + errorOptAccess);
                StartCoroutine(statusMsg(errorOptAccess));

            }
        }
    }

   
    public void Login(string username, string password) {
        WWWForm form = new WWWForm();
        form.AddField("username", username);
        form.AddField("password", password);
        Send(RequestType.Post, "getauthtoken", form, OnLoginResponse);

        //@ale : atribui o username ao Playinfo.alias
        PlayerInfo.alias = username;
        Debug.Log("***********************************Playinfo.alias = " + PlayerInfo.alias);
        Debug.Log("***********************************Playinfo.token = " + PlayerInfo.token);

        //@ale 190607
        PlayerPrefs.SetString ("usuarioTemp", username);
        Debug.Log ("LoginMenu.cs *********** usuarioTemp = " + PlayerPrefs.GetString("usuarioTemp"));
    }

    private void OnLoginResponse(ResponseType responseType, JToken responseData, string callee) {
        Debug.Log("ResponseType= " + responseType);
        if (responseType == ResponseType.Success) {
            authenticationToken = responseData.Value<string>("token");
            PlayerInfo.token = authenticationToken;
            if (OnLoggedIn != null) {
                OnLoggedIn(); 
                
            StartCoroutine(statusMsg("Conectado, carregando o jogo...."));
            
            SceneManager.LoadScene("Configurations");
            }
        } else if (responseType == ResponseType.ClientError)
        {
            Debug.Log("errorLogin 1= " + errorLogin);
            StartCoroutine(statusMsg(errorLogin));
            if (OnLoginFailed != null) {
                OnLoginFailed("@ale : nao pode acessar o servidor.");
//                 OnLoginFailed(errornoLogin); // responseType=ClientError
            }
        } else {
            JToken fieldToken = responseData["non_field_errors"];
            Debug.Log("fieldToken = " + fieldToken);
            if (fieldToken == null || !fieldToken.HasValues) {
                if (OnLoginFailed != null) {
                    OnLoginFailed("@ale : Login Falhou: unknown error.");
                }
            } else {
                string errors = "";
                JToken[] fieldValidationErrors = fieldToken.Values().ToArray();
                foreach (JToken validationError in fieldValidationErrors) {
                    errors += validationError.Value<string>();
                }
                if (OnLoginFailed != null) {
                    OnLoginFailed("@ale : Login Falhou " + errors);
                }
            }
            Debug.Log("errorLogin 2= " + errorLogin);
        }
        loggingIn = true;
        Debug.Log("@ale : Acessando a tela de login...");
        backendManager.Login(username, password);
        Debug.Log("@ale : Passou pela tela de login...");
    }

    
    public void Signup(string username, string email, string password) {
        WWWForm form = new WWWForm();
        form.AddField("username", username);
        form.AddField("email", email);
        form.AddField("password", password);
        Debug.Log("Vou cadastrar...");
        Send(RequestType.Post, "user", form, OnSignupResponse);
    }

    private void OnSignupResponse(ResponseType responseType, JToken responseData, string callee) {
        if (responseType == ResponseType.Success) {
            if (OnSignupSuccess != null) {
                OnSignupSuccess();
            }
        } else if (responseType == ResponseType.ClientError) {
            if (OnSignupFailed != null) {
                OnSignupFailed("Could not reach the server. Please try again later.");
            }
        } else if (responseType == ResponseType.RequestError) {
            string errors = "";
            JObject obj = (JObject)responseData;
            foreach (KeyValuePair<string, JToken> pair in obj) {
                errors += "[" + pair.Key + "] ";
                foreach (string errStr in pair.Value) {
                    errors += errStr;
                }
                errors += '\n';
            }
            if (OnSignupFailed != null) {
                OnSignupFailed(errors);
            }
        }
    }
    
    private IEnumerator  statusMsg(string msg)
    {
//        Mensagem.CrossFadeAlpha (100f, 0f, false);
//        Mensagem.color = Color.green;

        Mensagem.text = msg;
        yield return new WaitForSeconds (2.0f);
//        Mensagem.CrossFadeAlpha (0f, 2f, false);
        SceneManager.LoadScene("TCLE");
    }

    public void OnBotaoVoltar()
    {
        Debug.Log("OnBotaoVoltar...");
        SceneManager.LoadScene("Localization");
    }

    public void Send(RequestType type, string command, WWWForm wwwForm, RequestResponseDelegate onResponse = null, string authToken = "") {
        WWW request;
#if UNITY_5_PLUS
        Dictionary<string, string> headers;
#else
        Hashtable headers;
#endif
        byte[] postData;
        string url = BackendUrl + command;
        Debug.Log("url..." + url);
        
        if (Secure) {
            url = url.Replace("http", "https");
        }

        if (wwwForm == null) {
            wwwForm = new WWWForm();
            postData = new byte[] { 1 };

        } else {
            postData = wwwForm.data;

        }

        headers = wwwForm.headers;
        Debug.Log("headers..." + headers);

        //make sure we get a json response
        headers.Add("Accept", "application/json");

        //also add the correct request method
        headers.Add("X-UNITY-METHOD", type.ToString().ToUpper());

        //also, add the authentication token, if we have one
        if (authToken != "") {
            //for more information about token authentication, see: http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
            headers.Add("Authorization", "Token " + authToken);
        }
        request = new WWW(url, postData, headers);

        System.Diagnostics.StackTrace stackTrace = new System.Diagnostics.StackTrace();
        string callee = stackTrace.GetFrame(1).GetMethod().Name;
        StartCoroutine(HandleRequest(request, onResponse, callee));
        Debug.Log("request..." + request);
        Debug.Log("onResponse..." + onResponse);
        Debug.Log("callee..." + callee);
    }
    
    private IEnumerator HandleRequest(WWW request, RequestResponseDelegate onResponse, string callee) {
            //Wait till request is done
            while (true) {
                if (request.isDone) {
                    break;
                }
                yield return new WaitForEndOfFrame();
            }

            //catch proper client errors(eg. can't reach the server)
            if (!String.IsNullOrEmpty(request.error)) {
                if (onResponse != null) {
                    onResponse(ResponseType.ClientError, null, callee);
                }
                yield break;
            }
            int statusCode = 200;
            
            if (request.responseHeaders.ContainsKey("REAL_STATUS")) {
                string status = request.responseHeaders["REAL_STATUS"];
                statusCode = int.Parse(status.Split(' ')[0]);
            }
            //if any other error occurred(probably 4xx range), see http://www.django-rest-framework.org/api-guide/status-codes/
            bool responseSuccessful = (statusCode >= 200 && statusCode <= 206);
            JToken responseObj = null;

            try {
                if (request.text.StartsWith("[")) { 
                    responseObj = JArray.Parse(request.text); 
                } else { 
                    responseObj = JObject.Parse(request.text); 
                }
            } catch (Exception ex) {
                if (onResponse != null) {
                    if (!responseSuccessful) {
                        if (statusCode == 404) {
                            //404's should not be treated as unparsable
                            Debug.LogWarning("Page not found: " + request.url);
                            onResponse(ResponseType.PageNotFound, null, callee);
                        } else {
                            Debug.Log("Could not parse the response, request.text=" + request.text);
                            Debug.Log("Exception=" + ex.ToString());
                            onResponse(ResponseType.ParseError, null, callee);
                        }
                    } else {
                        if (request.text == "") {
                            onResponse(ResponseType.Success, null, callee);
                        } else {
                            Debug.Log("Could not parse the response, request.text=" + request.text);
                            Debug.Log("Exception=" + ex.ToString());
                            onResponse(ResponseType.ParseError, null, callee);
                        }
                    }
                }
                yield break;
            }

            if (!responseSuccessful) {
                if (onResponse != null) {
                    onResponse(ResponseType.RequestError, responseObj, callee);
                }
                yield break;
            }
             
            //deal with successful responses
            if (onResponse != null) {
                Debug.Log("Foi belezinha....." + callee);
                onResponse(ResponseType.Success, responseObj, callee);
            }
            
            SceneManager.LoadScene("Configurations");
            
    }
    

  private void Update() {
 
        if(!loggingIn) {
            return;
        }

        // When TAB is pressed, we should select the next selectable UI element
        if (Input.GetKeyDown(KeyCode.Tab)) {
            Selectable next = null;
            Selectable current = null;
 
            // Figure out if we have a valid current selected gameobject
            if (eventSystem.currentSelectedGameObject != null) {
                // Unity doesn't seem to "deselect" an object that is made inactive
                if (eventSystem.currentSelectedGameObject.activeInHierarchy) {
                    current = eventSystem.currentSelectedGameObject.GetComponent<Selectable>();
                }
            }
             
            if (current != null) {
                // When SHIFT is held along with tab, go backwards instead of forwards
                if (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift)) {
                    next = current.FindSelectableOnLeft();
                    if (next == null) {
                        next = current.FindSelectableOnUp();
                    }
                } else {
                    next = current.FindSelectableOnRight();
                    if (next == null) {
                        next = current.FindSelectableOnDown();
                    }
                }
            } else {
                // If there is no current selected gameobject, select the first one
                if (Selectable.allSelectables.Count > 0) {
                    next = Selectable.allSelectables[0];
                }
            }
             
            if (next != null)  {
                next.Select();
            }
        }
        
        if (Time.time > nextStatusChange) {
            nextStatusChange = Time.time + 0.5f;
//            status = "Logging in";
            status = statusLog;
            for (int i = 0; i < dotNumber; i++) {
                status += ".";
            }
            if (++dotNumber > 3) {
                dotNumber = 1;
            }
        }
    }

    private void OnGUI() {
        GUI.skin = Skin;
//        windowRect = GUILayout.Window(2, windowRect, ShowWindow, "Acesso ao Jogo do Goleiro");
//        windowRect = GUILayout.Window(2, windowRect, ShowWindow, titJanLogin);
    }
}
