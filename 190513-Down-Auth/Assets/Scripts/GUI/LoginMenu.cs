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

using System;
using UnityEngine;
using UnityEngine.UI; 

public class LoginMenu : BaseMenu {
    
    private LocalizationManager translate;
    
    public delegate void LoggedIn();
    public LoggedIn HasLoggedIn;

    private string user;
    private string pass;
    private string titJanLogin;
    private string labelin;
    
    
    private const float LABEL_WIDTH = 110;
    private bool loggingIn = false;
    private bool rememberMe = false;
    private bool hasFocussed = false;
    private int dotNumber = 1;
    private float nextStatusChange;
    private string status = "";
    private string username = "", password = "";
    private SignupMenu signupMenu;

    private void Start() {
        windowRect = new Rect(Screen.width /2 + 60 , Screen.height /2 - 25, 300, 200);

        translate = LocalizationManager.instance;
        user = translate.getLocalizedValue ("userName");	
        pass = translate.getLocalizedValue ("passWd");	
        titJanLogin = translate.getLocalizedValue ("titWinLogin");
        labelin = translate.getLocalizedValue ("inputLabelLogin");
        
        backendManager.OnLoggedIn += OnLoggedIn;
        backendManager.OnLoginFailed += OnLoginFailed;
        
        signupMenu = gameObject.GetOrCreateComponent<SignupMenu>();
        signupMenu.enabled = false;
        signupMenu.OnCancel += OnSignupCancelOrSuccess;
        signupMenu.OnSignedUp += OnSignupCancelOrSuccess;

        if (PlayerPrefs.HasKey("x1")) {
            username = PlayerPrefs.GetString("x2").FromBase64();
            password = PlayerPrefs.GetString("x1").FromBase64();
            rememberMe = true;
        }
    }

    private void OnSignupCancelOrSuccess() {
        enabled = true;
    }
    
    private void SaveCredentials() {
        PlayerPrefs.SetString("x2", username.ToBase64());
        PlayerPrefs.SetString("x1", password.ToBase64());
    }

    private void RemoveCredentials() {
        if (PlayerPrefs.HasKey("x1")) {
            PlayerPrefs.DeleteAll();
        }
    }

    private void OnLoginFailed(string error) {
//        status = "Login error: " + error;
        status = "Erro no login: " + error;
        loggingIn = false;
    }

    private void OnLoggedIn() {
//        status = "Logged in!";
        status = "Logado!";
        loggingIn = false;

        if (rememberMe) {
            SaveCredentials();
        } else {
            RemoveCredentials();
        }

        if (HasLoggedIn != null) {
            HasLoggedIn();
        }
    }


    private void DoLogin() {
        if (loggingIn) {
            Debug.LogWarning("Already logging in, returning.");
            return;
        }
        loggingIn = true;
        Debug.Log("@ale : Acessando a tela de login...");
        backendManager.Login(username, password);
        Debug.Log("@ale : Passou pela tela de login...");
    }

    private void ShowWindow(int id) {
        GUILayout.BeginVertical();

        GUILayout.BeginHorizontal();
        GUILayout.Label("    ");
        GUILayout.EndHorizontal();


        GUILayout.Label(labelin);
     //   bool filledIn = (username != "" && password != "" && rememberMe.Equals(true) );
        bool filledIn = (username != "" && password != "");
        filledIn = true;
        /*
        GUILayout.BeginHorizontal(); 
        GUILayout.Label("      ");
        GUILayout.EndHorizontal();
        */

        GUILayout.BeginHorizontal();
        GUI.SetNextControlName("usernameField");
//       GUILayout.Label("Usuário", GUILayout.Width(LABEL_WIDTH));
        GUILayout.Label(user, GUILayout.Width(LABEL_WIDTH));
        username = GUILayout.TextField(username, 30);
        GUILayout.EndHorizontal();
        
        GUILayout.BeginHorizontal();
//        GUILayout.Label("Senha", GUILayout.Width(LABEL_WIDTH));
        GUILayout.Label(pass, GUILayout.Width(LABEL_WIDTH));
        password = GUILayout.PasswordField(password, '*', 30);
        GUILayout.EndHorizontal();


 //       GUILayout.BeginHorizontal();
 //       GUILayout.Label("", GUILayout.Width(LABEL_WIDTH));
 //       rememberMe = GUILayout.Toggle(rememberMe, "Lembrar");
 //       GUILayout.EndHorizontal();

        GUILayout.BeginHorizontal();
        GUILayout.Label("      ");
        GUILayout.EndHorizontal();


        GUILayout.FlexibleSpace();
        GUILayout.Label("Status: " + status);
              

        GUI.enabled = filledIn;
        Event e = Event.current;
        if (filledIn && e.isKey && e.keyCode == KeyCode.Return) {
            DoLogin();
        }

        GUILayout.BeginHorizontal();
        if (GUILayout.Button("Entrar")) {
            DoLogin();

        }
        if (GUILayout.Button("Novo Cadastro")) {
            enabled = false;
            signupMenu.enabled = true;
        }
        GUILayout.EndHorizontal();

        GUI.enabled = true;
         
        GUILayout.EndVertical();

        if (!hasFocussed) {
            GUI.FocusControl("usernameField");
            hasFocussed = true;
        }
    }

    private void Update() {
        if(!loggingIn) {
            return;
        }

        if (Time.time > nextStatusChange) {
            nextStatusChange = Time.time + 0.5f;
//            status = "Logging in";
            status = "Logado";
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
        windowRect = GUILayout.Window(2, windowRect, ShowWindow, titJanLogin);
    }
}
