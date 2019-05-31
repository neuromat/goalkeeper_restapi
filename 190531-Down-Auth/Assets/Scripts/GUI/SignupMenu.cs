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

using UnityEngine;
using System.Collections;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;
using System.Linq;
using System;

public class SignupMenu : BaseMenu {
    public VoidDelegate OnSignedUp;
    public VoidDelegate OnCancel;

    private LocalizationManager translate;
    
    
    private string user;
    private string pass;
    private string titJanSignup;
    private string labelinfoSign;
    private string termAssigned;
    private string repeatSign;
    private string cadButton;
    private string newsignButton;
    private string statusSign;
    private string errorCad;
    private string statusnewSign;
    
    private const float LABEL_WIDTH = 110;

    private bool hasFocussed = false;
    private bool signingUp = false;
    private bool termOK = false;
    private int dotNumber = 1;
    private float nextStatusChange;
    private string status = "";
    private string username = "", email = "", password = "", password_confirm = "";
    
    private void Start() {

        windowRect = new Rect(Screen.width / 2 + 60, Screen.height / 2 - 25, 300, 200);

        translate = LocalizationManager.instance;
        user = translate.getLocalizedValue ("user");	
        pass = translate.getLocalizedValue ("pass");	
        titJanSignup = translate.getLocalizedValue ("titJanSignup");
        labelinfoSign = translate.getLocalizedValue("labelinfoSign");
        termAssigned= translate.getLocalizedValue("termAssigned");
        cadButton= translate.getLocalizedValue("cadButton");
        newsignButton= translate.getLocalizedValue("newsignButton");
        statusSign= translate.getLocalizedValue("statusSign");
        errorCad= translate.getLocalizedValue("errorCad");
        statusnewSign = translate.getLocalizedValue("statusnewSign");
        
        repeatSign= translate.getLocalizedValue("repeatSign");
        backendManager.OnSignupSuccess += OnSignupSuccess;
        backendManager.OnSignupFailed += OnSignupFailed;
    }

    private void OnSignupFailed(string error) {
//        status = "Erro no cadastro: \n\n" + error;
        status = errorCad + error;
        signingUp = false;
    }

    private void OnSignupSuccess() {
//        status = "Signup successful!";
        status = statusnewSign;
        signingUp = false;

        Invoke("FinishSignup", 1.5f);
    }

    private void FinishSignup() {
        if (OnSignedUp != null) {
            OnSignedUp();
        }
        enabled = false;
    }

    private void DoSignup() {
        if (signingUp) {
//            Debug.LogWarning("Already signing up, returning.");
            Debug.LogWarning("Já possui cadastro, retornar.");
            return;
        }
        backendManager.Signup(username, email, password);
        signingUp = true;
    }

    private void ShowWindow(int id) {
        GUILayout.BeginVertical();
//        GUILayout.Label("Please enter your details and signup");
        GUILayout.Label(labelinfoSign);
        bool filledIn = (username != "" && email != "" && password != "" && password_confirm != "" && termOK.Equals(true));
 //                                       filledIn = true;

        GUILayout.BeginHorizontal();
        GUI.SetNextControlName("usernameField");
        GUILayout.Label(user, GUILayout.Width(LABEL_WIDTH));
        username = GUILayout.TextField(username, 30);
        GUILayout.EndHorizontal();

        GUILayout.BeginHorizontal();
        GUILayout.Label("Email", GUILayout.Width(LABEL_WIDTH));
        email = GUILayout.TextField(email, 50);
        GUILayout.EndHorizontal();

        GUILayout.BeginHorizontal();
        GUILayout.Label(pass, GUILayout.Width(LABEL_WIDTH));
        password = GUILayout.PasswordField(password, '*', 30);
        GUILayout.EndHorizontal();

        GUILayout.BeginHorizontal();
        GUILayout.Label(repeatSign, GUILayout.Width(LABEL_WIDTH));
        password_confirm = GUILayout.PasswordField(password_confirm, '*', 30);
        GUILayout.EndHorizontal();

        GUILayout.BeginHorizontal();
        GUILayout.Label("", GUILayout.Width(LABEL_WIDTH));
        termOK = GUILayout.Toggle(termOK, termAssigned);
        GUILayout.EndHorizontal();
        
        GUILayout.Label("Status: " + status);
        GUI.enabled = filledIn;
        Event e = Event.current;
        if (filledIn && e.isKey && e.keyCode == KeyCode.Return) {
            DoSignup();
        }

        GUILayout.FlexibleSpace();
        GUILayout.BeginHorizontal();
        if (GUILayout.Button(cadButton)) {
            DoSignup();
        }
        GUI.enabled = true;
        if (GUILayout.Button(newsignButton)) {
            enabled = false;
            if (OnCancel != null) {
                OnCancel();
            }
        }
        GUILayout.EndHorizontal();
        GUILayout.EndVertical();

        if (!hasFocussed) {
            GUI.FocusControl("usernameField");
            hasFocussed = true;
        }
    }

    private void Update() {
        if(!signingUp) {
            return;
        }

        if (Time.time > nextStatusChange) {
            nextStatusChange = Time.time + 0.5f;
//            status = "Signing up";
            status = statusSign;
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
//        windowRect = GUILayout.Window(4, windowRect, ShowWindow, "Signup menu");
        windowRect = GUILayout.Window(4, windowRect, ShowWindow, titJanSignup);
    }
}
